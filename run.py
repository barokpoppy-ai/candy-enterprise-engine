# run.py
# Entry point. Run: python run.py

from app import create_app
from models import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    print()
    print("=" * 60)
    print("  CANDY ENGINE - Ethiopian BC-1 Estimating Engine")
    print("  Open:  http://127.0.0.1:5000")
    print("  Stop:  Ctrl + C")
    print("=" * 60)
    print()

    app.run(debug=True, host="127.0.0.1", port=5000)