import secrets

from flask.testing import FlaskClient

from project.app import db
from project.globals import ACCEPTED_SYMBOLS
from project.helpers import convert_to_crypto
from project.models import Users
from tests.helpers import fill_mock, send_transaction, send_user

# Happy path
def test_client_can_sell_currency(mock: FlaskClient):
    print("test_client_can_sell_currency")
    assets = fill_mock()
    user = Users.query.with_for_update().get(assets["user"]["id"])
    expected = {}
    for sym in ACCEPTED_SYMBOLS:
        starting_amount = convert_to_crypto(1_000_000.00, sym)
        setattr(user, sym, starting_amount)
        expected[sym] = starting_amount
    db.session.commit()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
    }
    for sym in ACCEPTED_SYMBOLS:
        for sell in [0.01, 0.05, 0.1, 0.19, 1.99]:
            headers["transaction_id"] = secrets.token_urlsafe()
            url = f"/sell/{assets['user']['id']}/{sym}/{sell}"
            ret = mock.post(url, headers=headers)
            assert ret.status_code == 204
            user = Users.query.get(assets["user"]["id"])
            updated = expected[sym] - sell
            assert getattr(user, sym) == updated
            expected[sym] = updated


# negative tests
def test_invalid_methods(mock: FlaskClient):
    print("test_invalid_methods")
    assets = fill_mock()
    user = Users.query.with_for_update().get(assets["user"]["id"])
    user.BTC = convert_to_crypto(1_000_000.00, "BTC")
    db.session.commit()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": secrets.token_urlsafe(),
    }   
    url = f"/sell/{assets['user']['id']}/BTC/0.01"
    success = mock.post(url, headers=headers)
    assert success.status_code == 204
    for method in ["get", "put", "delete"]:
        call = getattr(mock, method)
        ret = call(url, headers=headers)
        assert ret.status_code == 405
        assert b'method is not allowed' in ret.data

def test_missing_headers(mock: FlaskClient):
    print('TODO: test_missing_headers')
    assets = fill_mock()
    user = Users.query.with_for_update().get(assets["user"]["id"])
    user.BTC = convert_to_crypto(1_000_000.00, "BTC")
    db.session.commit()
    headers_list = [
        {},
        {"client_id": assets["client"]["id"]},
        {"authorization": assets["client"]["key"]},
        {"transaction_id": secrets.token_urlsafe()},
        {
            "authorization": assets["client"]["key"],
            "transaction_id": secrets.token_urlsafe(),
        },
        {
            "client_id": assets["client"]["id"],
            "transaction_id": secrets.token_urlsafe(),
        },
        {
            "client_id": assets["client"]["id"],
            "authorization": assets["client"]["key"],
        },
    ]
    url = f"/sell/{assets['user']['id']}/BTC/100.0"
    for headers in headers_list:
        ret = mock.post(url, headers=headers)
        assert ret.status_code == 400
        assert b'header required' in ret.data

def test_missing_args(mock: FlaskClient):
    print('test_missing_args')
    assets = fill_mock()
    user = Users.query.with_for_update().get(assets["user"]["id"])
    user.BTC = convert_to_crypto(1_000_000.00, "BTC")
    db.session.commit()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": secrets.token_urlsafe()
    }
    urls = [
        f"/sell",
        f"/sell/{assets['user']['id']}",
        f"/sell/{assets['user']['id']}/BTC",
        f"/sell//BTC/10.0",
        f"/sell/{assets['user']['id']}//10.0",
        f"/sell/{assets['user']['id']}/BTC/",
    ]
    for url in urls:
        ret = mock.post(url, headers=headers)
        assert ret.status_code == 404

def test_insufficient_currency(mock: FlaskClient):
    print('test_insufficient_currency')
    assets = fill_mock()
    user = Users.query.with_for_update().get(assets["user"]["id"])
    AMOUNT = 1_000_000.00
    user.BTC = convert_to_crypto(AMOUNT, "BTC")
    db.session.commit()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": secrets.token_urlsafe()
    }
    url = f"/sell/{assets['user']['id']}/BTC/{AMOUNT+.01}"
    ret = mock.post(url, headers=headers)
    assert ret.status_code == 401
    assert b'Insufficient BTC' in ret.data

def test_duplicate_transaction(mock: FlaskClient):
    print('test_duplicate_transaction')
    assets = fill_mock()
    user = Users.query.with_for_update().get(assets["user"]["id"])
    AMOUNT = 1_000_000.00
    user.BTC = convert_to_crypto(AMOUNT, "BTC")
    db.session.commit()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": secrets.token_urlsafe()
    }
    url = f"/sell/{assets['user']['id']}/BTC/{.01}"
    success = mock.post(url, headers=headers)
    assert success.status_code == 204
    fail = mock.post(url, headers=headers)
    assert fail.status_code == 401
    assert b"Sell order already submitted" in fail.data

def test_invalid_token(mock: FlaskClient):
    print('test_invalid_token')
    assets = fill_mock()
    user = Users.query.with_for_update().get(assets["user"]["id"])
    AMOUNT = 1_000_000.00
    user.BTC = convert_to_crypto(AMOUNT, "BTC")
    db.session.commit()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"] + "wrong",
        "transaction_id": secrets.token_urlsafe(),
    }
    url = f"/sell/{assets['user']['id']}/BTC/{.01}"
    bad_token = mock.post(url, headers=headers)
    assert bad_token.status_code == 401
    assert b"invalid API key" in bad_token.data

def test_user_is_not_authorized_for_currency(mock: FlaskClient):
    print('TODO: test_user_is_not_authorized_for_currency')
    assets = fill_mock()
    user = Users.query.with_for_update().get(assets["user"]["id"])
    AMOUNT = 1_000_000.00
    user.BTC = convert_to_crypto(AMOUNT, "BTC")
    user.BTC_auth = False
    db.session.commit()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": secrets.token_urlsafe(),
    }
    url = f"/sell/{assets['user']['id']}/BTC/{.01}"
    not_auth = mock.post(url, headers=headers)
    assert not_auth.status_code == 401
    assert b"not authorized to purchase" in not_auth.data
