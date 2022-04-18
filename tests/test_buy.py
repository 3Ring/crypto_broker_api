from flask.testing import FlaskClient

from project.globals import ACCEPTED_SYMBOLS
from project.helpers import convert_to_crypto
from project.models import Users
from tests.helpers import fill_mock, send_transaction, send_user

# happy path
def test_client_can_buy_currency(mock: FlaskClient):
    assets = fill_mock()
    expected = {}
    for sym in ACCEPTED_SYMBOLS:
        expected[sym] = assets["user"][sym]
        for buy in [.01, 0.1, 1.00, 10.00, 99_999.99]:
            tran = send_transaction(buy, assets["user"]["id"], assets["client"]["id"])
            headers = {
                "client_id": assets["client"]["id"],
                "authorization": assets["client"]["key"],
                "transaction_id": tran.id,
            }
            url = f"/buy/{assets['user']['id']}/{sym}/{buy}"
            ret = mock.post(url, headers=headers)
            assert ret.status_code == 204
            user = Users.query.get(assets["user"]["id"])
            updated = expected[sym] + convert_to_crypto(buy, sym)
            assert getattr(user, sym) == updated
            expected[sym] = updated


# negative tests
def test_invalid_methods(mock: FlaskClient):
    print("test_invalid_methods")
    assets = fill_mock()
    tran = send_transaction(1, assets["user"]["id"], assets["client"]["id"])
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": tran.id,
    }
    url = f"/buy/{assets['user']['id']}/BTC/1.0"
    success = mock.post(url, headers=headers)
    assert success.status_code == 204
    for method in ["get", "put", "delete"]:
        call = getattr(mock, method)
        ret = call(url, headers=headers)
        assert ret.status_code == 405
        assert b'method is not allowed' in ret.data


def test_missing_args(mock: FlaskClient):
    print("test_missing_args")
    assets = fill_mock()
    tran = send_transaction(1, assets["user"]["id"], assets["client"]["id"])
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": tran.id,
    }
    urls = [
        f"/buy",
        f"/buy/{assets['user']['id']}",
        f"/buy/{assets['user']['id']}/BTC/",
        f"/buy//BTC/1",
        f"/buy/{assets['user']['id']}//1.0",
        f"/buy/{assets['user']['id']}/BTC/",
    ]
    for url in urls:
        ret = mock.post(url, headers=headers)
        assert ret.status_code == 404


def test_missing_headers(mock: FlaskClient):
    print("test_missing_headers")
    assets = fill_mock()
    tran = send_transaction(1, assets["user"]["id"], assets["client"]["id"])
    headers_list = [
        {},
        {"client_id": assets["client"]["id"]},
        {"authorization": assets["client"]["key"]},
        {"transaction_id": tran.id},
        {
            "authorization": assets["client"]["key"],
            "transaction_id": tran.id,
        },
        {
            "client_id": assets["client"]["id"],
            "transaction_id": tran.id,
        },
        {
            "client_id": assets["client"]["id"],
            "authorization": assets["client"]["key"],
        },
    ]
    url = f"/buy/{assets['user']['id']}/BTC/1.0"
    for headers in headers_list:
        ret = mock.post(url, headers=headers)
        assert ret.status_code == 400
        assert b'header required' in ret.data


def test_no_payment(mock: FlaskClient):
    print("test_no_payment")
    assets = fill_mock()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": 10000,
    }
    url = f"/buy/{assets['user']['id']}/BTC/1.0"
    ret = mock.post(url, headers=headers)
    assert ret.status_code == 401
    assert b'Transaction not found' in ret.data


def test_duplicate_transaction(mock: FlaskClient):
    print("test_duplicate_transaction")
    assets = fill_mock()
    tran = send_transaction(1, assets["user"]["id"], assets["client"]["id"])
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": tran.id,
    }
    url = f"/buy/{assets['user']['id']}/BTC/1.0"
    success = mock.post(url, headers=headers)
    assert success.status_code == 204
    fail = mock.post(url, headers=headers)
    assert fail.status_code == 401
    assert b"Already completed." in fail.data


def test_payment_attached_to_different_user(mock: FlaskClient):
    print("test_payment_attached_to_different_user")
    assets = fill_mock()
    user = send_user(assets["client"]["id"])
    tran = send_transaction(1, assets["user"]["id"], assets["client"]["id"])
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": tran.id,
    }
    url = f"/buy/{user['id']}/BTC/1.0"
    wrong_user = mock.post(url, headers=headers)
    assert wrong_user.status_code == 401
    assert b'Transaction details do not match' in wrong_user.data


def test_invalid_token(mock: FlaskClient):
    print("test_invalid_token")
    assets = fill_mock()
    tran = send_transaction(1, assets["user"]["id"], assets["client"]["id"])
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"] + "wrong",
        "transaction_id": tran.id,
    }
    url = f"/buy/{assets['user']['id']}/BTC/1.0"
    bad_token = mock.post(url, headers=headers)
    assert bad_token.status_code == 401
    assert b"invalid API key" in bad_token.data


def test_unsupported_currency(mock: FlaskClient):
    print("test_unsupported_currency")
    assets = fill_mock()
    tran = send_transaction(1, assets["user"]["id"], assets["client"]["id"])
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
        "transaction_id": tran.id,
    }
    url = f"/buy/{assets['user']['id']}/WRONG/1.0"
    bad_symbol = mock.post(url, headers=headers)
    assert bad_symbol.status_code == 404
    assert b"not a valid symbol" in bad_symbol.data


def test_user_is_not_authorized_for_currency(mock: FlaskClient):
    print("test_user_is_not_authorized_for_currency")
    assets = fill_mock()
    users = [
        send_user(assets["client"]["id"], BTC_auth=False),
        send_user(assets["client"]["id"], ETH_auth=False),
        send_user(assets["client"]["id"], DOGE_auth=False),
        send_user(assets["client"]["id"], USDT_auth=False),
        send_user(assets["client"]["id"], BNB_auth=False),
    ]
    for user, sym in zip(users, ACCEPTED_SYMBOLS):
        tran = send_transaction(1, user["id"], assets["client"]["id"])
        headers = {
            "client_id": assets["client"]["id"],
            "authorization": assets["client"]["key"],
            "transaction_id": tran.id,
        }
        url = f"/buy/{user['id']}/{sym}/1.0"
        not_authorized = mock.post(url, headers=headers)
        assert not_authorized.status_code == 401
        assert b"not authorized to purchase" in not_authorized.data
