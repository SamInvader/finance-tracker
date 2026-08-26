import pytest

from backend.app import create_app
from backend.app.extensions import db
# no top-level model imports needed in this test
import werkzeug

# compatibility: older Flask test helpers expect werkzeug.__version__
if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "3.0.0"


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app


def test_register_and_login(app):
    client = app.test_client()
    # register
    r = client.post(
        "/api/auth/register",
        json={"email": "x@example.com", "password": "secret", "name": "X"},
    )
    assert r.status_code == 201
    data = r.get_json()
    assert "access_token" in data

    # login
    r2 = client.post(
        "/api/auth/login", json={"email": "x@example.com", "password": "secret"}
    )
    assert r2.status_code == 200
    data2 = r2.get_json()
    assert "access_token" in data2
