from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json
from sqlalchemy.orm import Session

def evaluate_rule_a_stock_reconciliation(
    opening_stock: float,
    received_quantity: float,
    distributed_quantity: float,
    recorded_closing_stock: float,
    documented_adjustments: float = 0.0,
    tolerance: float = 0.01,
    commodity: str = "Commodity",
    reporting_period: str = "N/A"
) -> Optional[Dict[str, Any]]:
    """
    Rule A: Stock Reconciliation Audit.
    Expected Closing Stock = Opening Stock + Received Quantity - Distributed Quantity - Documented Adjustments.
    Compares expected closing stock with recorded closing stock.
    """
    expected_closing_stock = round(
        opening_stock + received_quantity - distributed_quantity - documented_adjustments, 2
    )
    diff = round(recorded_closing_stock - expected_closing_stock, 2)

    if abs(diff) <= tolerance:
        return None  # Reconciled within acceptable tolerance

    # If recorded is less than expected, it's an unexplained shortfall.
    # If recorded is greater than expected, it's an unexplained surplus.
    if diff < 0:
        shortfall = abs(diff)
        severity = "CRITICAL" if shortfall >= 500 else ("HIGH" if shortfall >= 100 else "MEDIUM")
        reason = (
            f"Unaccounted physical shortfall of {shortfall:.2f} kg detected for {commodity} in period {reporting_period}. "
            f"Calculated expected balance was {expected_closing_stock:.2f} kg, but recorded closing stock was only {recorded_closing_stock:.2f} kg."
        )
    else:
        surplus = diff
        severity = "HIGH" if surplus >= 500 else ("MEDIUM" if surplus >= 100 else "LOW")
        reason = (
            f"Unaccounted surplus inventory of {surplus:.2f} kg detected for {commodity} in period {reporting_period}. "
            f"Calculated expected balance was {expected_closing_stock:.2f} kg, but recorded closing stock indicates {recorded_closing_stock:.2f} kg."
        )

    calc_details = json.dumps({
        "rule": "RULE_A_STOCK_RECONCILIATION",
        "formula": "Expected_Closing = Opening + Received - Distributed - Adjustments",
        "inputs": {
            "opening_stock": opening_stock,
            "received_quantity": received_quantity,
            "distributed_quantity": distributed_quantity,
            "documented_adjustments": documented_adjustments,
            "recorded_closing_stock": recorded_closing_stock
        },
        "calculation": f"{opening_stock:.2f} + {received_quantity:.2f} - {distributed_quantity:.2f} - {documented_adjustments:.2f} = {expected_closing_stock:.2f}",
        "expected_value": expected_closing_stock,
        "observed_value": recorded_closing_stock,
        "difference": diff,
        "unit": "kg"
    }, indent=2)

    evidence_summary = (
        f"Reconciliation disparity: Expected {expected_closing_stock:.2f} kg vs Recorded {recorded_closing_stock:.2f} kg "
        f"(Net Variance: {diff:+.2f} kg). Tolerance: {tolerance} kg."
    )

    return {
        "rule_triggered": "RULE_A_STOCK_RECONCILIATION",
        "category": "STOCK_RECONCILIATION",
        "severity": severity,
        "expected_value": expected_closing_stock,
        "observed_value": recorded_closing_stock,
        "difference": diff,
        "unit": "kg",
        "calculation_details": calc_details,
        "reason": reason,
        "evidence_summary": evidence_summary
    }


def evaluate_rule_b_negative_stock(
    opening_stock: float,
    received_quantity: float,
    distributed_quantity: float,
    recorded_closing_stock: float,
    documented_adjustments: float = 0.0,
    commodity: str = "Commodity",
    reporting_period: str = "N/A"
) -> Optional[Dict[str, Any]]:
    """
    Rule B: Negative Stock Anomaly Detection.
    Flags impossible negative quantities in opening, received, distributed, recorded, or expected stock.
    """
    violations = []
    if opening_stock < 0:
        violations.append(f"Opening stock is negative ({opening_stock:.2f} kg)")
    if received_quantity < 0:
        violations.append(f"Received quantity is negative ({received_quantity:.2f} kg)")
    if distributed_quantity < 0:
        violations.append(f"Distributed quantity is negative ({distributed_quantity:.2f} kg)")
    if recorded_closing_stock < 0:
        violations.append(f"Recorded closing stock is negative ({recorded_closing_stock:.2f} kg)")

    available_stock = round(opening_stock + received_quantity - documented_adjustments, 2)
    expected_closing = round(available_stock - distributed_quantity, 2)
    if expected_closing < 0:
        violations.append(
            f"Distributed quantity ({distributed_quantity:.2f} kg) exceeds total available inventory "
            f"({available_stock:.2f} kg), resulting in negative balance ({expected_closing:.2f} kg)"
        )

    if not violations:
        return None

    negative_val = min(recorded_closing_stock, expected_closing, opening_stock, received_quantity, distributed_quantity)
    calc_details = json.dumps({
        "rule": "RULE_B_NEGATIVE_STOCK",
        "formula": "Stock quantities must be >= 0.0; Distributed <= (Opening + Received - Adjustments)",
        "inputs": {
            "opening_stock": opening_stock,
            "received_quantity": received_quantity,
            "distributed_quantity": distributed_quantity,
            "documented_adjustments": documented_adjustments,
            "recorded_closing_stock": recorded_closing_stock,
            "expected_closing_stock": expected_closing
        },
        "violations": violations,
        "expected_value": 0.0,
        "observed_value": negative_val,
        "difference": round(negative_val, 2),
        "unit": "kg"
    }, indent=2)

    reason = (
        f"Critical physical impossibility detected for {commodity} in period {reporting_period}: "
        + "; ".join(violations) + "."
    )
    evidence_summary = f"Negative inventory violation: {'; '.join(violations)}."

    return {
        "rule_triggered": "RULE_B_NEGATIVE_STOCK",
        "category": "NEGATIVE_STOCK",
        "severity": "CRITICAL",
        "expected_value": 0.0,
        "observed_value": negative_val,
        "difference": round(negative_val, 2),
        "unit": "kg",
        "calculation_details": calc_details,
        "reason": reason,
        "evidence_summary": evidence_summary
    }


def run_stock_audit_for_record(db: Session, stock_record) -> List[Any]:
    """
    Evaluates Rule B and Rule A for a given StockRecord and persists any discrepancies idempotently.
    """
    from backend.app.models.models import Discrepancy

    discrepancies_created = []

    # 1. First evaluate Rule B (Negative Stock)
    rule_b_result = evaluate_rule_b_negative_stock(
        opening_stock=stock_record.opening_stock,
        received_quantity=stock_record.received_quantity,
        distributed_quantity=stock_record.distributed_quantity,
        recorded_closing_stock=stock_record.recorded_closing_stock,
        documented_adjustments=stock_record.documented_adjustments or 0.0,
        commodity=stock_record.commodity,
        reporting_period=stock_record.reporting_period
    )
    if rule_b_result:
        existing = db.query(Discrepancy).filter(
            Discrepancy.related_stock_record_id == stock_record.id,
            Discrepancy.rule_triggered == "RULE_B_NEGATIVE_STOCK"
        ).first()
        if not existing:
            disc = Discrepancy(
                category=rule_b_result["category"],
                severity=rule_b_result["severity"],
                status="OPEN",
                related_shop_id=stock_record.shop_id,
                related_stock_record_id=stock_record.id,
                commodity=stock_record.commodity,
                reporting_period=stock_record.reporting_period,
                expected_value=rule_b_result["expected_value"],
                observed_value=rule_b_result["observed_value"],
                difference=rule_b_result["difference"],
                unit=rule_b_result["unit"],
                rule_triggered=rule_b_result["rule_triggered"],
                calculation_details=rule_b_result["calculation_details"],
                reason=rule_b_result["reason"],
                evidence_summary=rule_b_result["evidence_summary"],
                created_at=datetime.now(timezone.utc)
            )
            db.add(disc)
            discrepancies_created.append(disc)

    # 2. Evaluate Rule A (Stock Reconciliation)
    rule_a_result = evaluate_rule_a_stock_reconciliation(
        opening_stock=stock_record.opening_stock,
        received_quantity=stock_record.received_quantity,
        distributed_quantity=stock_record.distributed_quantity,
        recorded_closing_stock=stock_record.recorded_closing_stock,
        documented_adjustments=stock_record.documented_adjustments or 0.0,
        commodity=stock_record.commodity,
        reporting_period=stock_record.reporting_period
    )
    if rule_a_result:
        existing = db.query(Discrepancy).filter(
            Discrepancy.related_stock_record_id == stock_record.id,
            Discrepancy.rule_triggered == "RULE_A_STOCK_RECONCILIATION"
        ).first()
        if not existing:
            disc = Discrepancy(
                category=rule_a_result["category"],
                severity=rule_a_result["severity"],
                status="OPEN",
                related_shop_id=stock_record.shop_id,
                related_stock_record_id=stock_record.id,
                commodity=stock_record.commodity,
                reporting_period=stock_record.reporting_period,
                expected_value=rule_a_result["expected_value"],
                observed_value=rule_a_result["observed_value"],
                difference=rule_a_result["difference"],
                unit=rule_a_result["unit"],
                rule_triggered=rule_a_result["rule_triggered"],
                calculation_details=rule_a_result["calculation_details"],
                reason=rule_a_result["reason"],
                evidence_summary=rule_a_result["evidence_summary"],
                created_at=datetime.now(timezone.utc)
            )
            db.add(disc)
            discrepancies_created.append(disc)

    db.commit()
    return discrepancies_created


def run_full_database_audit(db: Session) -> int:
    """
    Runs audit engine across all stock records in the database.
    """
    from backend.app.models.models import StockRecord
    records = db.query(StockRecord).all()
    count = 0
    for record in records:
        created = run_stock_audit_for_record(db, record)
        count += len(created)
    return count
