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
    quiz = response.get_json()
    assert len(quiz) == 2
    assert quiz["success"] == False
    message = quiz.get("message")
    assert message == "Request must be in JSON"

    response = test_client.post("/create_quiz", json={})
    assert response.status_code == 400
    quiz = response.get_json()
    assert len(quiz) == 2
    assert quiz["success"] == False
    message = quiz.get("message")
    assert message == "Request needs 4 fields exactly"

    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_private": True
    })
    assert response.status_code == 400
    quiz = response.get_json()
    assert len(quiz) == 2
    assert quiz["success"] == False
    message = quiz.get("message")
    assert message == "Request missing field 'is_public'"

    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": "True"
    })
    assert response.status_code == 400
    quiz = response.get_json()
    assert len(quiz) == 2
    assert quiz["success"] == False
    message = quiz.get("message")
    assert message == "Field 'is_public' is supposed to be a bool"






def test_create_quiz(test_client):
    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": True
    })
    assert response.status_code == 201
    quiz = response.get_json()
    assert len(quiz) == 2
    assert quiz.get("success") == True
    quiz = quiz.get("quiz")
    assert len(quiz) == 6
    assert quiz.get("title") == "Testing"
    assert quiz.get("description") == "Testing is important."
    assert quiz.get("creator_username") == "tester"
    assert quiz.get("is_public") == True
    assert isinstance(quiz.get("date_created"), str)
    assert isinstance(quiz.get("_id"), str)

    # Cleanup
    response = test_client.post("/delete_quiz", json={
        "_id": quiz.get("_id")
    })

    assert response.get_json()["success"] == True






def test_update_quiz(test_client):
    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": True
    })
    quiz = response.get_json().get("quiz")
    _id = quiz.get("_id")
    quiz["is_public"] = False # Change one of the fields
    response = test_client.post("/update_quiz", json=quiz)
    assert response.status_code == 200
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert response_object.get("message") == "Successful update"

    quiz["_id"] = ""
    response = test_client.post("/update_quiz", json=quiz)
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Field '_id' is invalid"

    quiz["_id"] = "6569f84b0c8b0f15c7a4f8b3" # Here is an ID that is unlikely to be in the database
    response = test_client.post("/update_quiz", json=quiz)
    assert response.status_code == 404
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Record not found"

    # Cleanup
    _ = test_client.post("/delete_quiz", json={
        "_id": _id
    })






def test_delete_quiz(test_client):
    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": True
    })
    quiz = response.get_json().get("quiz")
    response = test_client.post("/delete_quiz", json={
        "_id": quiz.get("_id")
    })
    assert response.status_code == 200
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert response_object.get("message") == "Successful delete"

    response = test_client.post("/delete_quiz", json={
        "_id": ""
    })
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Field '_id' is invalid"

    response = test_client.post("/delete_quiz", json={
        "_id": "6569f84b0c8b0f15c7a4f8b3"
    })
    assert response.status_code == 404
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Record not found"






def test_get_user_quizzes(test_client):
    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": True
    })
    _id = response.get_json().get("quiz").get("_id")
    response = test_client.post("/get_user_quizzes", json={
        "creator_username": "tester"
    })
    response_object = response.get_json()
    assert len(response_object) == 3
    assert response_object.get("success") == True
    assert len(response_object.get("public_quizzes")) == 1
    assert len(response_object.get("private_quizzes")) == 0
    
    # Cleanup
    _ = test_client.post("/delete_quiz", json={
        "_id": _id
    })






def test_get_public_quizzes(test_client):
    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": True
    })
    _id = response.get_json().get("quiz").get("_id")
    response = test_client.get("/get_public_quizzes")
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert len(response_object.get("public_quizzes")) == 1
    
    # Cleanup
    _ = test_client.post("/delete_quiz", json={
        "_id": _id
    })






def test_add_question(test_client):
    response = test_client.post("/create_quiz", json={
        "title": "Testing",
        "description": "Testing is important.",
        "creator_username": "tester",
        "is_public": True
    })
    quiz = response.get_json().get("quiz")
    response = test_client.post("/add_question", json={
        "quiz_id": quiz.get("_id"),
        "question": "Who?",
        "answers": ["Yes"],
        "correct_answer": "Yes",
        "explanation": "Yes is the right answer."
    })
    assert response.status_code == 201
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    question = response_object.get("question")
    assert len(question) == 6
    assert question.get("quiz_id") == quiz.get("_id")
    assert question.get("question") == "Who?"
    assert question.get("answers") == ["Yes"]
    assert question.get("correct_answer") == "Yes"
    assert question.get("explanation") == "Yes is the right answer."
    assert isinstance(question.get("_id"), str)

    # Cleanup (implicit testing also with questions getting automatically deleted)
    _ = test_client.post("/delete_quiz", json={
        "_id": quiz.get("_id")
    })