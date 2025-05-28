# Make a virtual environment with test_requirements.txt...run the development Docker containers for MongoDB
import os
import pytest
from backend.app import app

""" Useful resource: https://testdriven.io/blog/flask-pytest/ """

@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

def test__validate_request_object(test_client):
    response = test_client.post("/create_quiz", json=[])
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object["success"] == False
    message = response_object.get("message")
    assert message == "Request must be in JSON"

    response = test_client.post("/create_quiz", json={})
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object["success"] == False
    message = response_object.get("message")
    assert message == "Request needs 4 fields exactly"

    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_private": True
    })
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object["success"] == False
    message = response_object.get("message")
    assert message == "Request missing field 'is_public'"

    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": "True"
    })
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object["success"] == False
    message = response_object.get("message")
    assert message == "Field 'is_public' is supposed to be a bool"

def test_create_quiz(test_client):
    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": True
    })
    assert response.status_code == 201
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object["success"] == True
    quiz = response_object.get("quiz")
    assert len(quiz) == 6
    assert "title" in quiz and quiz.get("title") == "Testing"
    assert "description" in quiz and quiz.get("description") == "Testing is important."
    assert "creator_username" in quiz and quiz.get("creator_username") == "tester"
    assert "is_public" in quiz and quiz.get("is_public") == True
    assert "date_created" in quiz and isinstance(quiz.get("date_created"), str)
    assert "_id" in quiz and isinstance(quiz.get("_id"), str)