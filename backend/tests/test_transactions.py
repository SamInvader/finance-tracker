import pytest

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Account
import werkzeug

# compatibility for Flask test helpers
if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "3.0.0"


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app


def setup_user_and_account(client):
    # register & login
    r = client.post(
        "/api/auth/register", json={"email": "t@example.com", "password": "pwd"}
    )
    token = r.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # create an account directly via DB (tests avoid relying on accounts endpoint)
    from backend.app.models import Account, User

    u = User.query.filter_by(email="t@example.com").first()
    acct = Account(user_id=u.id, name="Main")
    db.session.add(acct)
    db.session.commit()
    aid = acct.id
    return headers, aid


def test_create_read_update_delete_transaction(app):
    client = app.test_client()
    headers, aid = setup_user_and_account(client)

    # create transaction
    r = client.post(
        "/api/transactions/",
        json={
            "account_id": aid,
            "amount": 12.34,
            "type": "expense",
            "description": "coffee",
        },
        headers=headers,
    )
    if r.status_code != 201:
        print("CREATE TX RESPONSE:", r.status_code, r.get_data(as_text=True))
    assert r.status_code == 201
    txid = r.get_json()["id"]

    # get transaction
    g = client.get(f"/api/transactions/{txid}", headers=headers)
    assert g.status_code == 200
    assert g.get_json()["description"] == "coffee"

    # update
    u = client.put(
        f"/api/transactions/{txid}",
        json={"description": "latte", "amount": 15.0},
        headers=headers,
    )
    assert u.status_code == 200

    g2 = client.get(f"/api/transactions/{txid}", headers=headers)
    assert g2.get_json()["description"] == "latte"

    # delete
    d = client.delete(f"/api/transactions/{txid}", headers=headers)
    assert d.status_code == 200
