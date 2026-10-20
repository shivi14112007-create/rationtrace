import json
import pytest
from backend.app.services.audit_service import (
    evaluate_rule_a_stock_reconciliation,
    evaluate_rule_b_negative_stock
)

def test_rule_a_balanced_stock_no_discrepancy():
    """Balanced stock should return None within tolerance."""
    result = evaluate_rule_a_stock_reconciliation(
        opening_stock=100.0,
        received_quantity=500.0,
        distributed_quantity=450.0,
        recorded_closing_stock=150.0,
        documented_adjustments=0.0,
        commodity="Wheat",
        reporting_period="2026-10"
    )
    assert result is None

def test_rule_a_detects_unaccounted_shortfall():
    """Opening 500 + Received 2000 - Distributed 1700 = Expected 800.
    Recorded 550 => Shortfall of -250 kg.
    """
    result = evaluate_rule_a_stock_reconciliation(
        opening_stock=500.0,
        received_quantity=2000.0,
        distributed_quantity=1700.0,
        recorded_closing_stock=550.0,
        documented_adjustments=0.0,
        commodity="Wheat",
        reporting_period="2026-09"
    )
    assert result is not None
    assert result["rule_triggered"] == "RULE_A_STOCK_RECONCILIATION"
    assert result["category"] == "STOCK_RECONCILIATION"
    assert result["severity"] == "HIGH"
    assert result["expected_value"] == 800.0
    assert result["observed_value"] == 550.0
    assert result["difference"] == -250.0
    assert "Unaccounted physical shortfall" in result["reason"]

    # Verify JSON calculation details
    calc = json.loads(result["calculation_details"])
    assert calc["rule"] == "RULE_A_STOCK_RECONCILIATION"
    assert calc["expected_value"] == 800.0
    assert calc["observed_value"] == 550.0
    assert calc["inputs"]["opening_stock"] == 500.0
    assert calc["inputs"]["received_quantity"] == 2000.0

def test_rule_a_detects_unaccounted_surplus():
    """Opening 100 + Received 400 - Distributed 300 = Expected 200.
    Recorded 280 => Surplus of +80 kg.
    """
    result = evaluate_rule_a_stock_reconciliation(
        opening_stock=100.0,
        received_quantity=400.0,
        distributed_quantity=300.0,
        recorded_closing_stock=280.0,
        commodity="Rice",
        reporting_period="2026-10"
    )
    assert result is not None
    assert result["rule_triggered"] == "RULE_A_STOCK_RECONCILIATION"
    assert result["difference"] == 80.0
    assert "surplus inventory" in result["reason"].lower()

def test_rule_a_with_documented_adjustments():
    """Documented adjustments (e.g. moisture loss/transit damage) should adjust expected balance."""
    # Expected: 200 + 1000 - 900 - 10 = 290
    result = evaluate_rule_a_stock_reconciliation(
        opening_stock=200.0,
        received_quantity=1000.0,
        distributed_quantity=900.0,
        recorded_closing_stock=290.0,
        documented_adjustments=10.0,
        commodity="Wheat"
    )
    assert result is None

def test_rule_b_negative_stock_detected_when_distributed_exceeds_available():
    """Opening 100 + Received 200 = 300 available. Distributed 450 => -150 kg."""
    result = evaluate_rule_b_negative_stock(
        opening_stock=100.0,
        received_quantity=200.0,
        distributed_quantity=450.0,
        recorded_closing_stock=-150.0,
        commodity="Rice",
        reporting_period="2026-10"
    )
    assert result is not None
    assert result["rule_triggered"] == "RULE_B_NEGATIVE_STOCK"
    assert result["category"] == "NEGATIVE_STOCK"
    assert result["severity"] == "CRITICAL"
    assert result["difference"] == -150.0
    assert "Critical physical impossibility" in result["reason"]

    calc = json.loads(result["calculation_details"])
    assert "violations" in calc
    assert len(calc["violations"]) > 0

def test_rule_b_negative_opening_stock():
    """Negative opening stock is an immediate violation."""
    result = evaluate_rule_b_negative_stock(
        opening_stock=-50.0,
        received_quantity=200.0,
        distributed_quantity=100.0,
        recorded_closing_stock=50.0,
        commodity="Wheat"
    )
    assert result is not None
    assert result["severity"] == "CRITICAL"
    assert any("Opening stock is negative" in v for v in json.loads(result["calculation_details"])["violations"])

def test_rule_b_normal_stock_returns_none():
    """Normal positive stock triggers no Rule B alert."""
    result = evaluate_rule_b_negative_stock(
        opening_stock=100.0,
        received_quantity=500.0,
        distributed_quantity=400.0,
        recorded_closing_stock=200.0,
        commodity="Wheat"
    )
    assert result is None
