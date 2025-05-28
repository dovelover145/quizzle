# Make a virtual environment with test_requirements.txt...start the MongoDB container before testing
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
    assert response_object.get("success") == True
    quiz = response_object.get("quiz")
    assert len(quiz) == 6
    assert "title" in quiz and quiz.get("title") == "Testing"
    assert "description" in quiz and quiz.get("description") == "Testing is important."
    assert "creator_username" in quiz and quiz.get("creator_username") == "tester"
    assert "is_public" in quiz and quiz.get("is_public") == True
    assert "date_created" in quiz and isinstance(quiz.get("date_created"), str)
    assert "_id" in quiz and isinstance(quiz.get("_id"), str)

def test_update_quiz(test_client):
    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": True
    })
    response_object = response.get_json().get("quiz")
    response_object["is_public"] = False # Change one of the fields
    response = test_client.post("/update_quiz", json=response_object)
    assert response.status_code == 200
    temp_response_object = response.get_json()
    assert len(temp_response_object) == 2
    assert temp_response_object.get("success") == True
    assert temp_response_object.get("message") == "Successful update"

    response_object["_id"] = ""
    response = test_client.post("/update_quiz", json=response_object)
    assert response.status_code == 400
    temp_response_object = response.get_json()
    assert len(temp_response_object) == 2
    assert temp_response_object.get("success") == False
    assert temp_response_object.get("message") == "Field '_id' is invalid"

    response_object["_id"] = "6569f84b0c8b0f15c7a4f8b3" # Here is an ID that is unlikely to be in the database
    response = test_client.post("/update_quiz", json=response_object)
    assert response.status_code == 404
    temp_response_object = response.get_json()
    assert len(temp_response_object) == 2
    assert temp_response_object.get("success") == False
    assert temp_response_object.get("message") == "Record not found"

def test_delete_quiz(test_client):
    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": True
    })
    response_object = response.get_json().get("quiz")
    response = test_client.post("/delete_quiz", json={
        "_id": response_object.get("_id")
    })
    assert response.status_code == 200
    temp_response_object = response.get_json()
    assert len(temp_response_object) == 2
    assert temp_response_object.get("success") == True
    assert temp_response_object.get("message") == "Successful delete"

    response = test_client.post("/delete_quiz", json={
        "_id": ""
    })
    assert response.status_code == 400
    temp_response_object = response.get_json()
    assert len(temp_response_object) == 2
    assert temp_response_object.get("success") == False
    assert temp_response_object.get("message") == "Field '_id' is invalid"

    response = test_client.post("/delete_quiz", json={
        "_id": "6569f84b0c8b0f15c7a4f8b3"
    })
    assert response.status_code == 404
    temp_response_object = response.get_json()
    assert len(temp_response_object) == 2
    assert temp_response_object.get("success") == False
    assert temp_response_object.get("message") == "Record not found"

def test_get_user_quizzes(test_client):
    response = test_client.post("/get_user_quizzes", json={
        "creator_username": "tester"
    })
    response_object = response.get_json()
    assert len(response_object) == 3
    assert response_object.get("success") == True
    assert len(response_object.get("public_quizzes")) == 1
    assert len(response_object.get("private_quizzes")) == 1

def test_get_public_quizzes(test_client):
    response = test_client.get("/get_public_quizzes")
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert len(response_object.get("public_quizzes")) == 1