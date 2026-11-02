# engine.py
# All first-principles calculation logic.
# No database access here - this file is pure math.

from config import Config


class EstimatingEngine:
    """The calculation engine - all first-principles math lives here."""

    def __init__(self, config=Config):
        self.cfg = config

    # -- Single-component costs --
    def gang_hourly_cost(self, gang) -> float:
        """Total hourly cost of a labour gang."""
        return sum(m.trade.hourly_cost() * m.headcount for m in gang.members)

    def material_hourly_cost(self, boq_item) -> float:
        """Total material cost per hour."""
        total = 0.0
        for bm in boq_item.materials:
            hourly_qty = bm.quantity_per_unit * boq_item.hourly_yield
            total += hourly_qty * bm.material.landed_cost()
        return total

    def labour_hourly_cost(self, boq_item) -> float:
        return sum(self.gang_hourly_cost(bg.gang) for bg in boq_item.labour_gangs)

    def equipment_hourly_cost(self, boq_item) -> float:
        return sum(
            be.equipment.operating_cost(self.cfg.DIESEL_PRICE_ETB)
            for be in boq_item.equipment_list
        )

    # -- Aggregate & markups --
    def direct_unit_cost(self, boq_item) -> float:
        if boq_item.hourly_yield <= 0:
            raise ValueError(
                f"Item {boq_item.code} has zero or negative hourly_yield."
            )
        hourly = (
            self.material_hourly_cost(boq_item)
            + self.labour_hourly_cost(boq_item)
            + self.equipment_hourly_cost(boq_item)
        )
        return hourly / boq_item.hourly_yield

    def net_rate(self, direct: float) -> float:
        markup = 1 + (self.cfg.OVERHEAD_PCT + self.cfg.PROFIT_PCT + self.cfg.RISK_PCT) / 100
        return direct * markup

    def final_rate(self, net: float) -> float:
        return net * (1 + self.cfg.VAT_PCT / 100)

    # -- Full recalc for one BOQ item --
    def recalculate(self, boq_item) -> dict:
        direct = self.direct_unit_cost(boq_item)
        net = self.net_rate(direct)
        final = self.final_rate(net)

        boq_item.direct_unit_cost = round(direct, 2)
        boq_item.net_rate = round(net, 2)
        boq_item.final_rate = round(final, 2)

        return {
            "code": boq_item.code,
            "description": boq_item.description,
            "unit": boq_item.unit,
            "direct_unit_cost": boq_item.direct_unit_cost,
            "net_rate": boq_item.net_rate,
            "final_rate": boq_item.final_rate,
            "material_hourly": round(self.material_hourly_cost(boq_item), 2),
            "labour_hourly": round(self.labour_hourly_cost(boq_item), 2),
            "equipment_hourly": round(self.equipment_hourly_cost(boq_item), 2),
        }

    def recalculate_all(self, boq_items) -> list:
        return [self.recalculate(item) for item in boq_items]