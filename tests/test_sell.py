import secrets

from flask.testing import FlaskClient

from project.app import db
from project.globals import ACCEPTED_SYMBOLS
from project.helpers import convert_to_crypto
from project.models import Users
from tests.helpers import fill_mock

# Happy path
def test_client_can_sell_currency(mock: FlaskClient):
    assets = fill_mock()
    user = Users.query.with_for_update().get(assets["user"]["id"])
    expected = {}
    for sym in ACCEPTED_SYMBOLS:
        starting_amount = convert_to_crypto(1_000_000_00, sym)
        setattr(user, sym, starting_amount)
        expected[sym] = starting_amount
    db.session.commit()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
    }
    for sym in ACCEPTED_SYMBOLS:
        for sell in [0.01, 0.05, 0.1, 0.19, 1.99]:
            token = secrets.token_urlsafe()
            url = f"/sell/{assets['user']['id']}/{sym}/{sell}/{token}"
            ret = mock.post(url, headers=headers)
            assert ret.status_code == 204
            user = Users.query.get(assets["user"]["id"])
            updated = expected[sym] - sell
            assert getattr(user, sym) == updated
            expected[sym] = updated
