import os
import pytest
from backend.app import app
from app import app as flask_app

""" Useful resource: https://testdriven.io/blog/flask-pytest/ """

@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client