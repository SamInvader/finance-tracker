from backend.run import app
from backend.app.extensions import db

with app.app_context():
    db.create_all()
    print("OK: db.create_all() executed")
