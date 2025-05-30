# Make a virtual environment with test_requirements.txt...start the MongoDB container before testing
import os
import pytest
from backend.app import app

# Useful resource: https://testdriven.io/blog/flask-pytest/






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

    response = test_client.post("/add_question", json={
        "quiz_id": "",
        "question": "Who?",
        "answers": ["Yes"],
        "correct_answer": "Yes",
        "explanation": "Yes is the right answer."
    })
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    question = response_object.get("message") == "Field 'quiz_id' is invalid"

    response = test_client.post("/add_question", json={
        "quiz_id": "6569f84b0c8b0f15c7a4f8b3",
        "question": "Who?",
        "answers": ["Yes"],
        "correct_answer": "Yes",
        "explanation": "Yes is the right answer."
    })
    assert response.status_code == 404
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    question = response_object.get("message") == "Field 'quiz_id' doesn't exist"

    # Cleanup (implicit testing also with questions getting automatically deleted)
    _ = test_client.post("/delete_quiz", json={
        "_id": quiz.get("_id")
    })






def test_update_question(test_client):
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
    question = response.get_json().get("question")
    
    question["explanation"] = "Yes is the answer!!!"
    response = test_client.post("/update_question", json=question)
    assert response.status_code == 200
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert response_object.get("message") == "Successful update"

    question["_id"] = ""
    response = test_client.post("/update_question", json=question)
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Field '_id' is invalid"

    question["_id"] = "6569f84b0c8b0f15c7a4f8b3"
    response = test_client.post("/update_question", json=question)
    assert response.status_code == 404
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Record not found"

    # Cleanup (implicit testing also with questions getting automatically deleted)
    _ = test_client.post("/delete_quiz", json={
        "_id": quiz.get("_id")
    })






def test_delete_question(test_client):
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
    question = response.get_json().get("question")

    response = test_client.post("/delete_question", json={
        "_id": question.get("_id")
    })
    assert response.status_code == 200
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert response_object.get("message") == "Successful delete"
    
    response = test_client.post("/delete_question", json={
        "_id": ""
    })
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Field '_id' is invalid"

    response = test_client.post("/delete_question", json={
        "_id": question.get("_id")
    })
    assert response.status_code == 404
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Record not found"

    # Cleanup (implicit testing also with questions getting automatically deleted)
    _ = test_client.post("/delete_quiz", json={
        "_id": quiz.get("_id")
    })






def test_get_questions(test_client):
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
    
    response = test_client.post("/get_questions", json={
        "quiz_id": quiz.get("_id")
    })
    assert response.status_code == 200
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert len(response_object.get("questions")) == 1

    response = test_client.post("/get_questions", json={
        "quiz_id": ""
    })
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Field 'quiz_id' is invalid"

    response = test_client.post("/get_questions", json={
        "quiz_id": "6569f84b0c8b0f15c7a4f8b3"
    })
    assert response.status_code == 200
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert len(response_object.get("questions")) == 0

    # Cleanup (implicit testing also with questions getting automatically deleted)
    _ = test_client.post("/delete_quiz", json={
        "_id": quiz.get("_id")
    })






def test_add_user(test_client):
    response = test_client.post("/add_user", json={
        "username": "tester",
        "email": "tester@gmail.com",
        "score_history": []
    })
    assert response.status_code == 201
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    user = response_object.get("user")
    assert len(user) == 4
    assert user.get("username") == "tester"
    assert user.get("email") == "tester@gmail.com"
    assert user.get("score_history") == []
    assert isinstance(user.get("_id"), str)

    response = test_client.post("/add_user", json={
        "username": "tester",
        "email": "tester@gmail.com",
        "score_history": []
    })
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Field 'username' already exists"

    # Cleanup
    _ = test_client.post("/delete_user", json={
        "_id": user.get("_id")
    })






def test_update_user(test_client):
    response = test_client.post("/add_user", json={
        "username": "tester",
        "email": "tester@gmail.com",
        "score_history": []
    })
    user = response.get_json().get("user")
    _id = user.get("_id")
    
    user["score_history"] = [{"quiz_name": "Svelte Trivia", "score": 90, "date_taken": ""}] # Leaving the last one blank out of laziness
    response = test_client.post("/update_user", json=user)
    assert response.status_code == 200
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert response_object.get("message") == "Successful update"

    user["_id"] = ""
    response = test_client.post("/update_user", json=user)
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Field '_id' is invalid"

    user["_id"] = "6569f84b0c8b0f15c7a4f8b3"
    response = test_client.post("/update_user", json=user)
    assert response.status_code == 404
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Record not found"

    # Cleanup
    _ = test_client.post("/delete_user", json={
        "_id": _id
    })






def test_delete_user(test_client):
    response = test_client.post("/add_user", json={
        "username": "tester",
        "email": "tester@gmail.com",
        "score_history": []
    })
    user = response.get_json().get("user")

    response = test_client.post("/delete_user", json={
        "_id": user.get("_id")
    })
    assert response.status_code == 200
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert response_object.get("message") == "Successful delete"

    response = test_client.post("/delete_user", json={
        "_id": ""
    })
    assert response.status_code == 400
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Field '_id' is invalid"

    response = test_client.post("/delete_user", json={
        "_id": "6569f84b0c8b0f15c7a4f8b3"
    })
    assert response.status_code == 404
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Record not found"






def test_get_user(test_client):
    response = test_client.post("/add_user", json={
        "username": "tester",
        "email": "tester@gmail.com",
        "score_history": []
    })
    user = response.get_json().get("user")

    response = test_client.post("/get_user", json={
        "username": user.get("username")
    })
    assert response.status_code == 200
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == True
    assert len(response_object.get("user")) == 4

    response = test_client.post("/get_user", json={
        "username": "impostor"
    })
    assert response.status_code == 404
    response_object = response.get_json()
    assert len(response_object) == 2
    assert response_object.get("success") == False
    assert response_object.get("message") == "Record not found"

    # Cleanup
    _ = test_client.post("/delete_user", json={
        "_id": user.get("_id")
    })