from flask.testing import FlaskClient
from project.globals import ACCEPTED_SYMBOLS
from project.helpers import convert_to_crypto
from tests.helpers import fill_mock, send_transaction

# Happy path
def test_balance_is_accurate(mock: FlaskClient):
    AMOUNT = 1000
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