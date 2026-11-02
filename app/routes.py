# app/routes.py
# All URL routes for the Candy Estimating Engine.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Material, BOQItem
from engine import EstimatingEngine

bp = Blueprint("main", __name__)
engine = EstimatingEngine()


@bp.route("/")
def index():
    items = BOQItem.query.all()
    summaries = engine.recalculate_all(items)
    db.session.commit()

    total_direct = sum(s["direct_unit_cost"] for s in summaries)
    total_net = sum(s["net_rate"] for s in summaries)
    total_final = sum(s["final_rate"] for s in summaries)

    return render_template(
        "index.html",
        summaries=summaries,
        total_direct=round(total_direct, 2),
        total_net=round(total_net, 2),
        total_final=round(total_final, 2),
        material_count=Material.query.count(),
    )


@bp.route("/materials")
def materials():
    return render_template(
        "materials.html",
        materials=Material.query.order_by(Material.code).all(),
    )


@bp.route("/materials/<int:material_id>/update", methods=["POST"])
def update_material(material_id):
    mat = Material.query.get_or_404(material_id)
    new_price = float(request.form["new_price"])
    old_price = mat.base_price
    mat.base_price = new_price
    db.session.commit()

    # Cascade: recalculate every BOQ item
    for item in BOQItem.query.all():
        engine.recalculate(item)
    db.session.commit()

    flash(
        f"{mat.code} updated: {old_price:.2f} -> {new_price:.2f} ETB. "
        f"All BOQ items recalculated.",
        "success",
    )
    return redirect(url_for("main.materials"))


@bp.route("/boq")
def boq():
    items = BOQItem.query.order_by(BOQItem.code).all()
    summaries = engine.recalculate_all(items)
    db.session.commit()
    return render_template("boq.html", items=items, summaries=summaries)


@bp.route("/boq/<int:item_id>")
def boq_detail(item_id):
    item = BOQItem.query.get_or_404(item_id)
    summary = engine.recalculate(item)
    db.session.commit()

    mat_rows = [
        {
            "code": bm.material.code,
            "desc": bm.material.description,
            "qty": bm.quantity_per_unit,
            "landed": round(bm.material.landed_cost(), 2),
            "hourly": round(
                bm.quantity_per_unit * item.hourly_yield * bm.material.landed_cost(), 2
            ),
        }
        for bm in item.materials
    ]

    lab_rows = []
    for bg in item.labour_gangs:
        for m in bg.gang.members:
            lab_rows.append(
                {
                    "trade": m.trade.name,
                    "count": m.headcount,
                    "rate": round(m.trade.hourly_cost(), 2),
                    "total": round(m.trade.hourly_cost() * m.headcount, 2),
                }
            )

    eq_rows = [
        {
            "code": be.equipment.code,
            "desc": be.equipment.description,
            "hourly": round(
                be.equipment.operating_cost(engine.cfg.DIESEL_PRICE_ETB), 2
            ),
        }
        for be in item.equipment_list
    ]

    return render_template(
        "boq_detail.html",
        item=item,
        summary=summary,
        mat_rows=mat_rows,
        lab_rows=lab_rows,
        eq_rows=eq_rows,
    )