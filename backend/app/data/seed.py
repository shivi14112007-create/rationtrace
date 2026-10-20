import os
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal, engine, Base
from backend.app.core.security import get_password_hash
from backend.app.models.models import (
    User,
    FairPriceShop,
    BeneficiaryProfile,
    DataSource,
    ExtractionJob,
    SourceRecord,
    StockRecord,
    DistributionTransaction,
    Complaint,
    InvestigationEvent
)
from backend.app.services.audit_service import run_full_database_audit

def seed_database():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).filter(User.username == "admin_demo").first():
            print("Database already contains seed data. Checking audit status...")
            run_full_database_audit(db)
            print("Audit verification complete.")
            return

        print("Seeding demo users...")
        demo_pwd_hash = get_password_hash("Demo123!")

        # 1. Users for each role
        admin_user = User(
            full_name="Rajesh Sharma (Admin)",
            username="admin_demo",
            email="admin@rationtrace.gov.in",
            password_hash=demo_pwd_hash,
            role="ADMIN",
            preferred_language="en",
            status="ACTIVE"
        )
        official_user = User(
            full_name="Ananya Verma (Inspector)",
            username="official_demo",
            email="inspector.delhi@rationtrace.gov.in",
            password_hash=demo_pwd_hash,
            role="OFFICIAL",
            preferred_language="en",
            status="ACTIVE"
        )
        dealer_user = User(
            full_name="Manoj Kumar (Dealer)",
            username="dealer_demo",
            email="manoj.fps@rationtrace.gov.in",
            password_hash=demo_pwd_hash,
            role="DEALER",
            preferred_language="hi",
            status="ACTIVE"
        )
        beneficiary_user = User(
            full_name="Sunita Devi (Beneficiary)",
            username="beneficiary_demo",
            email="sunita.devi@rationtrace.gov.in",
            password_hash=demo_pwd_hash,
            role="BENEFICIARY",
            preferred_language="hi",
            status="ACTIVE"
        )

        db.add_all([admin_user, official_user, dealer_user, beneficiary_user])
        db.commit()
        db.refresh(admin_user)
        db.refresh(official_user)
        db.refresh(dealer_user)
        db.refresh(beneficiary_user)

        # 2. Fair Price Shops
        print("Seeding Fair Price Shops across states...")
        shop_dl_1 = FairPriceShop(
            shop_identifier="FPS-DL-0142",
            shop_name="Manoj Ration Kendra (Shop #142)",
            dealer_user_id=dealer_user.id,
            state="Delhi",
            district="South Delhi",
            address="Plot 18, Block B, Mehrauli Badarpur Road, New Delhi",
            status="ACTIVE"
        )
        shop_dl_2 = FairPriceShop(
            shop_identifier="FPS-DL-0219",
            shop_name="Janata PDS Center #219",
            dealer_user_id=None,
            state="Delhi",
            district="East Delhi",
            address="Main Market, Preet Vihar, Delhi",
            status="ACTIVE"
        )
        shop_up_1 = FairPriceShop(
            shop_identifier="FPS-UP-0881",
            shop_name="Adarsh Upbhokta Bhandar",
            dealer_user_id=None,
            state="Uttar Pradesh",
            district="Lucknow",
            address="Hazratganj PDS Depot, Lucknow",
            status="ACTIVE"
        )
        shop_mp_1 = FairPriceShop(
            shop_identifier="FPS-MP-0435",
            shop_name="Gramin Seva Sahakari FPS",
            dealer_user_id=None,
            state="Madhya Pradesh",
            district="Bhopal",
            address="Kolar Road, Bhopal",
            status="ACTIVE"
        )

        db.add_all([shop_dl_1, shop_dl_2, shop_up_1, shop_mp_1])
        db.commit()
        db.refresh(shop_dl_1)
        db.refresh(shop_dl_2)
        db.refresh(shop_up_1)
        db.refresh(shop_mp_1)

        # 3. Beneficiary Profile
        print("Seeding Beneficiary Profile...")
        beneficiary_profile = BeneficiaryProfile(
            user_id=beneficiary_user.id,
            masked_beneficiary_identifier="RC-DL-XXXX-4912",
            state="Delhi",
            district="South Delhi",
            ration_card_type="PHH",
            family_members=4,
            assigned_shop_id=shop_dl_1.id
        )
        db.add(beneficiary_profile)
        db.commit()

        # 4. Data Sources
        print("Seeding Official Data Sources...")
        ds_nfsa = DataSource(
            name="NFSA Public Allocation Portal",
            source_url="https://nfsa.gov.in/public/nfsadashboard/PublicAllocationDashboard.aspx",
            jurisdiction="National (Central)",
            source_type="PORTAL",
            is_approved=True,
            is_enabled=True,
            last_checked_at=datetime.now(timezone.utc)
        )
        ds_delhi = DataSource(
            name="Delhi Food Security PDS Portal",
            source_url="https://nfs.delhigovt.nic.in/",
            jurisdiction="Delhi",
            source_type="PORTAL",
            is_approved=True,
            is_enabled=True,
            last_checked_at=datetime.now(timezone.utc)
        )
        ds_impds = DataSource(
            name="IMPDS National Allocation Service",
            source_url="https://impds.nic.in/sale/",
            jurisdiction="National (Inter-State)",
            source_type="API",
            is_approved=True,
            is_enabled=True,
            last_checked_at=datetime.now(timezone.utc)
        )
        db.add_all([ds_nfsa, ds_delhi, ds_impds])
        db.commit()
        db.refresh(ds_nfsa)
        db.refresh(ds_delhi)

        # 5. Extraction Job (TinyFish Demo)
        job_demo = ExtractionJob(
            source_id=ds_nfsa.id,
            job_status="COMPLETED",
            started_at=datetime.now(timezone.utc) - timedelta(hours=2),
            completed_at=datetime.now(timezone.utc) - timedelta(hours=1, minutes=58),
            records_extracted=32,
            records_validated=32,
            mode="DEMO"
        )
        db.add(job_demo)
        db.commit()

        # Seed SourceRecords for Demo Extraction Job
        from backend.app.integrations.tinyfish_client import DEMO_NFSA_ALLOCATION_FIXTURE
        import hashlib
        for rec in DEMO_NFSA_ALLOCATION_FIXTURE["state_allocations"]:
            raw_hash = f"{rec['state']}:{rec['commodity']}:{rec['allocated_quantity']}:{DEMO_NFSA_ALLOCATION_FIXTURE['reporting_period']}"
            rec_hash = hashlib.sha256(raw_hash.encode()).hexdigest()
            sr = SourceRecord(
                source_id=ds_nfsa.id,
                extraction_job_id=job_demo.id,
                region=rec["state"],
                commodity=rec["commodity"],
                metric_name="Allocated Quantity",
                quantity=float(rec["allocated_quantity"]),
                unit=rec["unit"],
                reporting_period=DEMO_NFSA_ALLOCATION_FIXTURE["reporting_period"],
                evidence_reference="DEMO_FIXTURE: NFSA Public Allocation Dashboard",
                extracted_at=job_demo.completed_at,
                record_hash=rec_hash,
                validation_status="VALID"
            )
            db.add(sr)
        db.commit()

        # 6. Stock Records with DELIBERATE Discrepancies
        print("Seeding Stock Records (including deliberate test anomalies)...")
        stock_records = [
            # Shop 1 (Delhi): Normal balanced Wheat in August
            StockRecord(
                shop_id=shop_dl_1.id,
                commodity="Wheat",
                reporting_period="2026-08",
                opening_stock=400.0,
                received_quantity=1800.0,
                distributed_quantity=1650.0,
                recorded_closing_stock=550.0,
                documented_adjustments=0.0
            ),
            # Shop 1 (Delhi): Normal balanced Rice in August
            StockRecord(
                shop_id=shop_dl_1.id,
                commodity="Rice",
                reporting_period="2026-08",
                opening_stock=300.0,
                received_quantity=1200.0,
                distributed_quantity=1100.0,
                recorded_closing_stock=400.0,
                documented_adjustments=0.0
            ),
            # Shop 1 (Delhi): DELIBERATE RULE A SHORTFALL in September Wheat
            # Opening: 550, Received: 2000, Distributed: 1750 => Expected = 800 kg.
            # Recorded closing stock = 550 kg => Net shortage: -250 kg!
            StockRecord(
                shop_id=shop_dl_1.id,
                commodity="Wheat",
                reporting_period="2026-09",
                opening_stock=550.0,
                received_quantity=2000.0,
                distributed_quantity=1750.0,
                recorded_closing_stock=550.0,
                documented_adjustments=0.0
            ),
            # Shop 1 (Delhi): Balanced Rice in September
            StockRecord(
                shop_id=shop_dl_1.id,
                commodity="Rice",
                reporting_period="2026-09",
                opening_stock=400.0,
                received_quantity=1300.0,
                distributed_quantity=1250.0,
                recorded_closing_stock=450.0,
                documented_adjustments=0.0
            ),
            # Shop 1 (Delhi): Normal Wheat in October
            StockRecord(
                shop_id=shop_dl_1.id,
                commodity="Wheat",
                reporting_period="2026-10",
                opening_stock=550.0,
                received_quantity=2200.0,
                distributed_quantity=1900.0,
                recorded_closing_stock=850.0,
                documented_adjustments=0.0
            ),
            # Shop 2 (East Delhi): Balanced Wheat & Rice
            StockRecord(
                shop_id=shop_dl_2.id,
                commodity="Wheat",
                reporting_period="2026-10",
                opening_stock=600.0,
                received_quantity=2500.0,
                distributed_quantity=2300.0,
                recorded_closing_stock=800.0,
                documented_adjustments=0.0
            ),
            # Shop 3 (UP): DELIBERATE RULE B NEGATIVE INVENTORY in October Rice
            # Opening: 120, Received: 200 => Available: 320 kg.
            # Distributed: 480 kg => Expected: -160 kg! Recorded: -160 kg.
            StockRecord(
                shop_id=shop_up_1.id,
                commodity="Rice",
                reporting_period="2026-10",
                opening_stock=120.0,
                received_quantity=200.0,
                distributed_quantity=480.0,
                recorded_closing_stock=-160.0,
                documented_adjustments=0.0
            ),
            # Shop 4 (MP): Balanced Wheat & Rice in October
            StockRecord(
                shop_id=shop_mp_1.id,
                commodity="Wheat",
                reporting_period="2026-10",
                opening_stock=500.0,
                received_quantity=3000.0,
                distributed_quantity=2700.0,
                recorded_closing_stock=800.0,
                documented_adjustments=0.0
            ),
            StockRecord(
                shop_id=shop_mp_1.id,
                commodity="Rice",
                reporting_period="2026-10",
                opening_stock=350.0,
                received_quantity=1800.0,
                distributed_quantity=1600.0,
                recorded_closing_stock=550.0,
                documented_adjustments=0.0
            )
        ]
        db.add_all(stock_records)
        db.commit()

        # 7. Beneficiary Transactions
        print("Seeding Beneficiary Transactions...")
        now = datetime.now(timezone.utc)
        transactions = [
            DistributionTransaction(
                beneficiary_reference="RC-DL-XXXX-4912",
                beneficiary_id=beneficiary_user.id,
                shop_id=shop_dl_1.id,
                transaction_date=now - timedelta(days=45),
                reporting_period="2026-09",
                commodity="Wheat",
                recorded_quantity=12.0,
                entitlement_quantity=12.0,
                unit="kg"
            ),
            DistributionTransaction(
                beneficiary_reference="RC-DL-XXXX-4912",
                beneficiary_id=beneficiary_user.id,
                shop_id=shop_dl_1.id,
                transaction_date=now - timedelta(days=45),
                reporting_period="2026-09",
                commodity="Rice",
                recorded_quantity=8.0,
                entitlement_quantity=8.0,
                unit="kg"
            ),
            DistributionTransaction(
                beneficiary_reference="RC-DL-XXXX-4912",
                beneficiary_id=beneficiary_user.id,
                shop_id=shop_dl_1.id,
                transaction_date=now - timedelta(days=12),
                reporting_period="2026-10",
                commodity="Wheat",
                recorded_quantity=8.0,  # Shortfall: entitled to 12kg, recorded 8kg
                entitlement_quantity=12.0,
                unit="kg"
            ),
            DistributionTransaction(
                beneficiary_reference="RC-DL-XXXX-4912",
                beneficiary_id=beneficiary_user.id,
                shop_id=shop_dl_1.id,
                transaction_date=now - timedelta(days=12),
                reporting_period="2026-10",
                commodity="Rice",
                recorded_quantity=8.0,
                entitlement_quantity=8.0,
                unit="kg"
            )
        ]
        db.add_all(transactions)
        db.commit()

        # 8. Complaints with Status Timelines
        print("Seeding Complaints with Investigation Timelines...")
        c1 = Complaint(
            reference_number="RT-2026-COMP-1042",
            beneficiary_id=beneficiary_user.id,
            related_shop_id=shop_dl_1.id,
            category="UNDER_DISTRIBUTION",
            description="POS slip recorded 8kg wheat for October quota, but physical delivery received was only 5kg. Dealer claimed stock shortage.",
            status="INVESTIGATION",
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=2)
        )
        c2 = Complaint(
            reference_number="RT-2026-COMP-2081",
            beneficiary_id=beneficiary_user.id,
            related_shop_id=shop_dl_1.id,
            category="OVERCHARGING",
            description="Dealer charged Rs. 15 extra for handling fee outside mandated NFSA zero-charge policy for priority households.",
            status="RESOLVED",
            resolution_summary="Shop warned. Unauthorized handling fee refunded to beneficiary. Warning letter issued by Food Inspector.",
            created_at=now - timedelta(days=25),
            updated_at=now - timedelta(days=15)
        )
        c3 = Complaint(
            reference_number="RT-2026-COMP-3190",
            beneficiary_id=beneficiary_user.id,
            related_shop_id=shop_dl_1.id,
            category="QUALITY_ISSUE",
            description="Grain quality in current lot contains excessive moisture and foreign matter.",
            status="SUBMITTED",
            created_at=now - timedelta(hours=8),
            updated_at=now - timedelta(hours=8)
        )
        db.add_all([c1, c2, c3])
        db.commit()
        db.refresh(c1)
        db.refresh(c2)
        db.refresh(c3)

        # Timeline events for Complaint 1
        e1_1 = InvestigationEvent(
            complaint_id=c1.id,
            actor_id=beneficiary_user.id,
            event_type="STATUS_CHANGE",
            note="Complaint lodged by beneficiary via RationTrace portal.",
            created_at=now - timedelta(days=10)
        )
        e1_2 = InvestigationEvent(
            complaint_id=c1.id,
            actor_id=official_user.id,
            event_type="INFO_REQUESTED",
            note="Official Inspector assigned case. Notice dispatched to Shop #142 for electronic POS ledger reconciliation.",
            created_at=now - timedelta(days=8)
        )
        e1_3 = InvestigationEvent(
            complaint_id=c1.id,
            actor_id=dealer_user.id,
            event_type="DEALER_RESPONSE",
            note="Dealer responded: Scale calibration error during peak morning distribution hours on 12th Oct.",
            created_at=now - timedelta(days=5)
        )
        e1_4 = InvestigationEvent(
            complaint_id=c1.id,
            actor_id=official_user.id,
            event_type="STATUS_CHANGE",
            note="Case escalated to INVESTIGATION. Physical audit scheduled by District Food Supply Officer.",
            created_at=now - timedelta(days=2)
        )

        # Timeline events for Complaint 2
        e2_1 = InvestigationEvent(
            complaint_id=c2.id,
            actor_id=beneficiary_user.id,
            event_type="STATUS_CHANGE",
            note="Complaint lodged regarding overcharging.",
            created_at=now - timedelta(days=25)
        )
        e2_2 = InvestigationEvent(
            complaint_id=c2.id,
            actor_id=official_user.id,
            event_type="RESOLUTION_RECORDED",
            note="Verification complete: Extra charge substantiated. Dealer issued strict warning and refund completed.",
            created_at=now - timedelta(days=15)
        )

        # Timeline event for Complaint 3
        e3_1 = InvestigationEvent(
            complaint_id=c3.id,
            actor_id=beneficiary_user.id,
            event_type="STATUS_CHANGE",
            note="Complaint submitted with sample batch details.",
            created_at=now - timedelta(hours=8)
        )

        db.add_all([e1_1, e1_2, e1_3, e1_4, e2_1, e2_2, e3_1])
        db.commit()

        # 9. Execute Audit Engine to populate Discrepancies
        print("Executing audit engine on seed records...")
        flagged = run_full_database_audit(db)
        print(f"Audit completed: {flagged} discrepancies identified and persisted.")

        print("Seed script completed successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
