from flask.testing import FlaskClient

from tests.helpers import fill_mock

# Happy Path
def test_can_get_list(mock: FlaskClient):
    assets = fill_mock()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
    }
    url = f"/list/{assets['user']['id']}"
    ret = mock.get(url, headers=headers)
    assert ret.status_code == 200
