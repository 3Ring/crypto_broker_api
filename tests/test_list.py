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


# negative tests
def test_invalid_methods(mock: FlaskClient):
    print("test_invalid_methods")
    assets = fill_mock()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
    }
    url = f"/list/{assets['user']['id']}"
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
    url = f"/list/{assets['user']['id']}"
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
    url = f"/list/"
    ret = mock.post(url, headers=headers)
    assert ret.status_code == 404


def test_user_does_not_exist(mock: FlaskClient):
    print("test_user_does_not_exist")
    assets = fill_mock()
    headers = {
        "client_id": assets["client"]["id"],
        "authorization": assets["client"]["key"],
    }
    url = f"/list/{assets['user']['id'] + 1}"
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
    url = f"/list/{assets1['user']['id']}"
    ret = mock.get(url, headers=headers)
    assert ret.status_code == 401
    assert b"unauthorized client" in ret.data
