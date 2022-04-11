import os
from tempfile import TemporaryDirectory

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_migrate import init, migrate, upgrade

from project.app import create_app
from project.helpers import db_session
from project.models import Clients, Keys, Transactions, Users


@pytest.fixture(scope="session", autouse=True)
def temp_dir():
    with TemporaryDirectory() as tdp:
        yield tdp


@pytest.fixture(scope="session", autouse=True)
def app():
    yield create_app(testing=True)


@pytest.fixture(scope="session")
def test_client(app: Flask):
    """test client"""
    with app.app_context(), app.test_request_context():
        with app.test_client() as testing_client:
            yield testing_client


@pytest.fixture(scope="session", autouse=True)
def set_database(temp_dir, test_client: FlaskClient):
    """database setup."""
    init(directory=os.path.join(temp_dir, "migrations"))
    migrate(directory=os.path.join(temp_dir, "migrations"))
    upgrade(directory=os.path.join(temp_dir, "migrations"))
    yield


@pytest.fixture(autouse=True)
def mock(test_client: FlaskClient):
    yield test_client
    models = [Users, Clients, Transactions, Keys]
    with db_session() as sess:
        for m in models:
            sess.query(m).delete()
    for m in models:
        assert len(m.query.all()) == 0
