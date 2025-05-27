import os
import pytest
from backend.app import app

""" Useful resource: https://testdriven.io/blog/flask-pytest/ """

@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

def test_create_quiz_success(test_client):
    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": True
    })
    assert response.code == 201
    response_object = response.get_json()
    assert response_object["success"] == True
    assert response_object["quiz"]
    quiz = response_object.get("quiz")
    assert "title" in quiz and quiz.get("title") == "Testing"
    assert "description" in quiz and quiz.get("description") == "Testing is important."
    assert "creator_username" in quiz and quiz.get("creator_username") == "tester"
    assert "is_public" in quiz and quiz.get("is_public") == True
    assert "date_created" in quiz and isinstance(quiz.get("date_created"), str)
    assert "_id" in quiz and isinstance(quiz.get("_id"), str)
    assert len(quiz) == 6