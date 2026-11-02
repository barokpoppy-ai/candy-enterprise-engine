# models.py
# All SQLAlchemy database models for the Candy Estimating Engine.
# Imported by seed_data.py and app/routes.py.

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Material(db.Model):
    """A purchasable material (cement, steel, sand, etc.)."""
    __tablename__ = "materials"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    base_price = db.Column(db.Float, nullable=False, default=0.0)
    freight = db.Column(db.Float, nullable=False, default=0.0)
    handling = db.Column(db.Float, nullable=False, default=0.0)
    wastage_factor = db.Column(db.Float, nullable=False, default=1.0)

    def landed_cost(self) -> float:
        """(base + freight + handling) x wastage - landed cost per unit."""
        return (self.base_price + self.freight + self.handling) * self.wastage_factor


class LabourTrade(db.Model):
    """A single labour trade (mason, carpenter, etc.)."""
    __tablename__ = "labour_trades"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    basic_rate = db.Column(db.Float, nullable=False)
    benefit_multiplier = db.Column(db.Float, nullable=False, default=1.25)

    def hourly_cost(self) -> float:
        return self.basic_rate * self.benefit_multiplier


class Equipment(db.Model):
    """A piece of plant/equipment (mixer, vibrator, etc.)."""
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    dry_rate = db.Column(db.Float, nullable=False, default=0.0)
    fuel_litres_per_hour = db.Column(db.Float, nullable=False, default=0.0)
    maintenance = db.Column(db.Float, nullable=False, default=0.0)

    def operating_cost(self, diesel_price: float) -> float:
        return self.dry_rate + (self.fuel_litres_per_hour * diesel_price) + self.maintenance


class LabourGang(db.Model):
    """A crew of workers."""
    __tablename__ = "labour_gangs"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)

    members = db.relationship("GangMember", backref="gang", cascade="all, delete-orphan")


class GangMember(db.Model):
    """One trade inside a gang + headcount."""
    __tablename__ = "gang_members"

    id = db.Column(db.Integer, primary_key=True)
    gang_id = db.Column(db.Integer, db.ForeignKey("labour_gangs.id"), nullable=False)
    trade_id = db.Column(db.Integer, db.ForeignKey("labour_trades.id"), nullable=False)
    headcount = db.Column(db.Integer, nullable=False)

    trade = db.relationship("LabourTrade")


class BOQItem(db.Model):
    """One line item in the Bill of Quantities."""
    __tablename__ = "boq_items"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    hourly_yield = db.Column(db.Float, nullable=False)

    direct_unit_cost = db.Column(db.Float, default=0.0)
    net_rate = db.Column(db.Float, default=0.0)
    final_rate = db.Column(db.Float, default=0.0)
    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)

    materials = db.relationship("BOQMaterial", backref="boq_item", cascade="all, delete-orphan")
    labour_gangs = db.relationship("BOQLabourGang", backref="boq_item", cascade="all, delete-orphan")
    equipment_list = db.relationship("BOQEquipment", backref="boq_item", cascade="all, delete-orphan")


class BOQMaterial(db.Model):
    """Links a BOQ item to a material with a quantity per unit of work."""
    __tablename__ = "boq_materials"

    id = db.Column(db.Integer, primary_key=True)
    boq_item_id = db.Column(db.Integer, db.ForeignKey("boq_items.id"), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False)
    quantity_per_unit = db.Column(db.Float, nullable=False)

    material = db.relationship("Material")


class BOQLabourGang(db.Model):
    """Links a BOQ item to a labour gang."""
    __tablename__ = "boq_labour_gangs"

    id = db.Column(db.Integer, primary_key=True)
    boq_item_id = db.Column(db.Integer, db.ForeignKey("boq_items.id"), nullable=False)
    gang_id = db.Column(db.Integer, db.ForeignKey("labour_gangs.id"), nullable=False)

    gang = db.relationship("LabourGang")


class BOQEquipment(db.Model):
    """Links a BOQ item to a piece of equipment."""
    __tablename__ = "boq_equipment"

    id = db.Column(db.Integer, primary_key=True)
    boq_item_id = db.Column(db.Integer, db.ForeignKey("boq_items.id"), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)

    equipment = db.relationship("Equipment")