# seed_data.py
# Seeds the SQLite database with realistic Ethiopian BC-1 data.
# Run once: python seed_data.py

from app import create_app
from models import (
    db, Material, LabourTrade, Equipment, LabourGang, GangMember,
    BOQItem, BOQMaterial, BOQLabourGang, BOQEquipment,
)


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # 1. Materials (Q2 2024 Ethiopian prices, ETB)
        # NOTE: M-STL-01 is priced per kg because the BOQ item B-STL-01
        # is measured in kg. A ton-based price would inflate steel by 1000x.
        materials = [
            Material(code="M-CEM-01", description="OPC Cement 42.5N",
                     unit="Quintal", base_price=1850, freight=120,
                     handling=30, wastage_factor=1.02),
            Material(code="M-AGG-02", description='Crushed Aggregate 3/4"',
                     unit="m3", base_price=1350, freight=100,
                     handling=0, wastage_factor=1.05),
            Material(code="M-SND-01", description="Coarse River Sand",
                     unit="m3", base_price=1050, freight=150,
                     handling=0, wastage_factor=1.05),
            Material(code="M-STL-01", description="Ribbed Rebar Grade 40",
                     unit="kg", base_price=135, freight=2.5,
                     handling=0.5, wastage_factor=1.05),
            Material(code="M-WIR-01", description="Binding Wire 18g",
                     unit="kg", base_price=160, freight=10,
                     handling=0, wastage_factor=1.02),
            Material(code="M-WTR-01", description="Construction Water",
                     unit="m3", base_price=150, freight=0,
                     handling=0, wastage_factor=1.00),
        ]
        db.session.add_all(materials)

        # 2. Labour trades
        trades = [
            LabourTrade(code="L-FRM-02", name="Concrete Foreman",
                        basic_rate=110, benefit_multiplier=1.25),
            LabourTrade(code="L-FRM-03", name="Steel Foreman",
                        basic_rate=110, benefit_multiplier=1.25),
            LabourTrade(code="L-MAS-01", name="Master Mason",
                        basic_rate=85, benefit_multiplier=1.25),
            LabourTrade(code="L-BND-01", name="Master Bar Bender",
                        basic_rate=85, benefit_multiplier=1.25),
            LabourTrade(code="L-BND-02", name="Steel Fixer",
                        basic_rate=80, benefit_multiplier=1.25),
            LabourTrade(code="L-MIX-01", name="Mixer Operator",
                        basic_rate=85, benefit_multiplier=1.25),
            LabourTrade(code="L-VIB-01", name="Vibrator Operator",
                        basic_rate=75, benefit_multiplier=1.25),
            LabourTrade(code="L-LAB-01", name="Unskilled Helper",
                        basic_rate=45, benefit_multiplier=1.20),
        ]
        db.session.add_all(trades)
        db.session.flush()

        # 3. Equipment
        equipment = [
            Equipment(code="E-MIX-01", description="Concrete Mixer 750L Diesel",
                      dry_rate=350, fuel_litres_per_hour=3.5, maintenance=45),
            Equipment(code="E-VIB-01", description="Electric Vibrator",
                      dry_rate=70, fuel_litres_per_hour=0, maintenance=10),
            Equipment(code="E-HST-01", description="Material Hoist 1-Ton",
                      dry_rate=380, fuel_litres_per_hour=2.5, maintenance=50),
            Equipment(code="E-CUT-01", description="Rebar Cutter (Electric)",
                      dry_rate=70, fuel_litres_per_hour=0, maintenance=8),
            Equipment(code="E-BND-01", description="Rebar Bender (Electric)",
                      dry_rate=70, fuel_litres_per_hour=0, maintenance=8),
        ]
        db.session.add_all(equipment)
        db.session.flush()

        # 4. Gangs
        concrete_gang = LabourGang(code="G-CON-01",
                                   description="Concrete Placing & Compaction Gang")
        steel_gang = LabourGang(code="G-STL-01",
                                description="Steel Fixing Gang")
        db.session.add_all([concrete_gang, steel_gang])
        db.session.flush()

        for trade_code, count in [
            ("L-FRM-02", 1), ("L-MIX-01", 1), ("L-VIB-01", 2),
            ("L-MAS-01", 2), ("L-LAB-01", 12),
        ]:
            trade = LabourTrade.query.filter_by(code=trade_code).one()
            db.session.add(GangMember(gang_id=concrete_gang.id,
                                      trade_id=trade.id, headcount=count))

        for trade_code, count in [
            ("L-FRM-03", 1), ("L-BND-01", 2),
            ("L-BND-02", 2), ("L-LAB-01", 4),
        ]:
            trade = LabourTrade.query.filter_by(code=trade_code).one()
            db.session.add(GangMember(gang_id=steel_gang.id,
                                      trade_id=trade.id, headcount=count))

        # 5. BOQ Items
        boq_concrete = BOQItem(code="B-CON-01",
                               description="C-30 Cast-in-Place Concrete",
                               unit="m3", hourly_yield=2.50)
        boq_steel = BOQItem(code="B-STL-01",
                            description="Ribbed Rebar Fixing",
                            unit="kg", hourly_yield=65.00)
        db.session.add_all([boq_concrete, boq_steel])
        db.session.flush()

        for mat_code, qty in [
            ("M-CEM-01", 3.25), ("M-AGG-02", 2.15),
            ("M-SND-01", 1.15), ("M-WTR-01", 0.50),
        ]:
            mat = Material.query.filter_by(code=mat_code).one()
            db.session.add(BOQMaterial(boq_item_id=boq_concrete.id,
                                       material_id=mat.id,
                                       quantity_per_unit=qty))
        db.session.add(BOQLabourGang(boq_item_id=boq_concrete.id,
                                     gang_id=concrete_gang.id))
        for eq_code in ["E-MIX-01", "E-VIB-01", "E-HST-01"]:
            eq = Equipment.query.filter_by(code=eq_code).one()
            db.session.add(BOQEquipment(boq_item_id=boq_concrete.id,
                                        equipment_id=eq.id))

        for mat_code, qty in [("M-STL-01", 1.05), ("M-WIR-01", 0.015)]:
            mat = Material.query.filter_by(code=mat_code).one()
            db.session.add(BOQMaterial(boq_item_id=boq_steel.id,
                                       material_id=mat.id,
                                       quantity_per_unit=qty))
        db.session.add(BOQLabourGang(boq_item_id=boq_steel.id,
                                     gang_id=steel_gang.id))
        for eq_code in ["E-CUT-01", "E-BND-01"]:
            eq = Equipment.query.filter_by(code=eq_code).one()
            db.session.add(BOQEquipment(boq_item_id=boq_steel.id,
                                        equipment_id=eq.id))

        db.session.commit()

        # 6. Initial calculation
        from engine import EstimatingEngine
        engine = EstimatingEngine()
        for item in BOQItem.query.all():
            engine.recalculate(item)
        db.session.commit()

        print("DB SEEDED SUCCESSFULLY")
        print("Materials:", Material.query.count())
        print("Labour trades:", LabourTrade.query.count())
        print("Equipment:", Equipment.query.count())
        print("BOQ items:", BOQItem.query.count())


if __name__ == "__main__":
    seed()