# config.py
# Central configuration for the Candy Estimating Engine.
# All editable parameters live here.

import os


class Config:
    # -- Database --
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///candy_engine.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -- Flask secret (required for forms and flash messages) --
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

    # -- Ethiopian Global Parameters (edit these to match current market) --
    DIESEL_PRICE_ETB = 110.00
    USD_TO_ETB      = 125.50
    OVERHEAD_PCT    = 12.00
    PROFIT_PCT      = 10.00
    RISK_PCT        = 3.00
    VAT_PCT         = 15.00