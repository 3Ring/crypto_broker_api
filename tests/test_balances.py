from flask.testing import FlaskClient
from project.globals import ACCEPTED_SYMBOLS
from project.helpers import convert_to_crypto
from tests.helpers import fill_mock, send_transaction

# Happy path
def test_balance_is_accurate(mock: FlaskClient):
    AMOUNT = 10.00
    assets = fill_mock()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
    }
    url = f"/balances/{assets['user']['id']}"
    ret = mock.get(url, headers=headers)
    assert ret.status_code == 200
    check(ret.get_json(), assets["user"])
    for sym in ACCEPTED_SYMBOLS:
        tran = send_transaction(AMOUNT, assets["user"]["id"], assets["client"]["id"])
        headers["transaction_id"] = tran.id
        url2 = f"/buy/{assets['user']['id']}/{sym}/{AMOUNT}"
        ret2 = mock.post(url2, headers=headers)
        assert ret2.status_code == 204
        assets["user"][sym] = assets["user"][sym] + convert_to_crypto(AMOUNT, sym)
        ret3 = mock.get(url, headers=headers)
        assert ret.status_code == 200
        check(ret3.get_json(), assets["user"])


def check(balance: dict, user: dict):
    for k, v in user.items():
        if k != "id" and k != "client_id" and v != 0.0:
            assert balance["balances"][k] == v


# negative tests
def test_invalid_methods(mock: FlaskClient):
    print("test_invalid_methods")
    assets = fill_mock()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
    }
    url = f"/balances/{assets['user']['id']}"
    for method in ["post", "put", "delete"]:
        call = getattr(mock, method)
        ret = call(url, headers=headers)
        assert ret.status_code == 405
        assert b"method is not allowed" in ret.data


def test_missing_headers(mock: FlaskClient):
    print("test_missing_headers")
    assets = fill_mock()
    headers_list = [
        {},
        {"client_id": assets["client"]["id"]},
        {"authorization": assets["client"]["key"]},
    ]
    url = f"/balances/{assets['user']['id']}"
    for headers in headers_list:
        ret = mock.get(url, headers=headers)
        assert ret.status_code == 400
        assert b"header required" in ret.data


def test_missing_args(mock: FlaskClient):
    print("test_missing_args")
    assets = fill_mock()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
    }
    url = f"/balances/"
    ret = mock.post(url, headers=headers)
    assert ret.status_code == 404


def test_user_does_not_exist(mock: FlaskClient):
    print("test_user_does_not_exist")
    assets = fill_mock()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
    }
    url = f"/balances/{assets['user']['id'] + 1}"
    ret = mock.get(url, headers=headers)
    assert ret.status_code == 404


def test_user_does_not_belong_to_client(mock: FlaskClient):
    print("test_user_does_not_belong_to_client")
    assets1 = fill_mock()
    assets2 = fill_mock()
    headers = {
        "client_id": assets2["client"]["id"],
        "authorization": assets1["client"]["key"],
    }
    url = f"/balances/{assets1['user']['id']}"
    ret = mock.get(url, headers=headers)
    assert ret.status_code == 401
    assert b"unauthorized client" in ret.data
