import os
from flask import Flask, jsonify, request, redirect, session
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
from bson.objectid import ObjectId
from datetime import datetime, timezone
from pymongo import MongoClient, DESCENDING






app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"]) # CORS will allow the origin to send a cookie when making request_objects

oauth = OAuth(app)
nonce = generate_token()
oauth.register(
    name=os.getenv("OIDC_CLIENT_NAME"),
    client_id=os.getenv("OIDC_CLIENT_ID"),
    client_secret=os.getenv("OIDC_CLIENT_SECRET"),
    # server_metadata_url="http://dex:5556/.well-known/openid-configuration",
    authorization_endpoint="http://localhost:5556/auth",
    token_endpoint="http://dex:5556/token",
    jwks_uri="http://dex:5556/keys",
    userinfo_endpoint="http://dex:5556/userinfo",
    device_authorization_endpoint="http://dex:5556/device/code",
    client_kwargs={"scope": "openid email profile"}
)

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://$root:rootpassword@mongo:27017/mydatabase?authSource=admin")
mongo = MongoClient(mongo_uri)
db = mongo.get_default_database()






@app.route("/")
def home(): # Basically discarded this
    user = session.get("user")
    if user:
        return f"<h2>Logged in as {user['email']}</h2><a href='/logout'>Logout</a>"
    return "<a href='/login'>Login with Dex</a>" # Can use login and /login






@app.route("/login")
def login():
    session["nonce"] = nonce
    redirect_uri = "http://localhost:8000/authorize"
    return oauth.flask_app.authorize_redirect(redirect_uri, nonce=nonce)






@app.route("/authorize")
def authorize():
    token = oauth.flask_app.authorize_access_token()
    nonce = session.get("nonce")
    user_info = oauth.flask_app.parse_id_token(token, nonce=nonce) # or use .get('userinfo').json()
    session["user"] = user_info
    return redirect("http://localhost:5173") # Go back to the web page (now being logged in)






@app.route("/logout")
def logout():
    session.clear()
    return redirect("http://localhost:5173") # Go back to the web page (now being logged out)






@app.route("/get_user")
def user():
    user = session.get("user")
    if user:
        return jsonify({"username": user["email"], "valid": True})
    return jsonify({"username": "", "valid": False})






def _validate_request_object(request_object, request_object_fields):
    if not isinstance(request_object, dict): # The request_object must be a dictionary (i.e. in JSON)
        return "Failed to receive request"
    if len(request_object) != len(request_object_fields): # The request_object must have this many fields; no more, no less
        return f"Request needs {len(request_object_fields)} fields"
    for request_object_field, request_object_field_type in request_object_fields.items(): # The request_object must have these fields, and they must be of these types
        if request_object_field not in request_object:
            return f"Request missing field '{request_object_field}'"
        if not isinstance(request_object[request_object_field], request_object_field_type):
            return f"Field '{request_object_field}' supposed to be a {request_object_field_type.__name__}"
    return "" # Successful parsing






@app.route("/create_quiz", methods=["POST"])
def create_quiz():
    iso_date = datetime.now(timezone.utc).isoformat()
    request_object = request.get_json()
    request_object_fields = {
        "title": str,
        "description": str,
        "creator_username": str,
        "is_public": bool
    }
    message = _validate_request_object(request_object, request_object_fields)
    if message:
        return jsonify({"success": False, "message": message}), 400
    request_object["date_created"] = iso_date
    request_object["_id"] = str(db.quizzes.insert_one(request_object).inserted_id)
    return jsonify({"success": True, "quiz": request_object}), 201 # A new record was created, so don't use 200






@app.route("/update_quiz", methods=["POST"])
def update_quiz():
    request_object = request.get_json()
    request_object_fields = {
        "title": str,
        "description": str,
        "creator_username": str,
        "is_public": bool,
        "date_created": str,
        "_id": str
    }
    message = _validate_request_object(request_object, request_object_fields)
    if message:
        return jsonify({"success": False, "message": message}), 400
    # _id is used to find the record; creator_username and date_created are static
    try:
        _id = ObjectId(request_object.get("_id"))
    except Exception as _:
        message = "Field '_id' is invalid"
        return jsonify({"success": False, "message": message}), 400
    result = db.quizzes.update_one(
        {"_id": _id},
        {"$set": {"title": request_object.get("title"), "description": request_object.get("description"), "is_public": request_object.get("is_public")}}
    )
    if result.matched_count == 0:
        message = "Record not found"
        return jsonify({"success": False, "message": message}), 404 # 404 means not found
    message = "Successful update"
    return jsonify({"success": True, "message": message}), 200






@app.route("/delete_quiz", methods=["POST"])
def delete_quiz():
    request_object = request.get_json()
    request_object_fields = {
        "title": str,
        "description": str,
        "creator_username": str,
        "is_public": bool,
        "date_created": str,
        "_id": str
    }
    message = _validate_request_object(request_object, request_object_fields)
    if message:
        return jsonify({"success": False, "message": message}), 400
    try:
        _id = ObjectId(request_object.get("_id"))
    except Exception as _:
        message = "Field '_id' is invalid"
        return jsonify({"success": False, "message": message}), 400
    result = db.quizzes.delete_one({"_id": _id})
    if result.deleted_count == 0:
        message = "Record not found"
        return jsonify({"success": False, "message": message}), 404
    _ = db.questions.delete_many({"quiz_id": _id}) # It doesn't matter how many questions are deleted, as the quiz could have a variable amount (even 0)
    message = "Successful delete"
    return jsonify({"success": True, "message": message}), 200






@app.route("/get_user_quizzes", methods=["POST"])
def get_user_quizzes():
    request_object = request.get_json()
    request_object_fields = {
        "creator_username": str,
    }
    message = _validate_request_object(request_object, request_object_fields)
    if message:
        return jsonify({"success": False, "message": message}), 400
    public_quizzes = list(db.quizzes.find({"$and": [{"creator_username": request_object.get("creator_username")}, 
                                   {"is_public": True}]}).sort("_id", DESCENDING))
    private_quizzes = list(db.quizzes.find({"$and": [{"creator_username": request_object.get("creator_username")}, 
                                   {"is_public": False}]}).sort("_id", DESCENDING))
    return jsonify({"success": True, "public_quizzes": public_quizzes, "private_quizzes": private_quizzes})






@app.route("/get_public_quizzes")
def get_public_quizzes():
    public_quizzes = list(db.quizzes.find({"is_public": True}).sort("_id", DESCENDING))
    return jsonify({"success": True, "public_quizzes": public_quizzes})






@app.route("/add_question", methods=["POST"])
def add_question():
    request_object = request.get_json()
    request_object_fields = {
        "quiz_id": str,
        "question": str,
        "answers": list(str),
        "correct_answer": str,
        "explanation": str
    }
    message = _validate_request_object(request_object, request_object_fields)
    if message:
        return jsonify({"success": False, "message": message}), 400
    try:
        quiz_id = ObjectId(request_object.get("quiz_id"))
    except Exception as _:
        message = "Field 'quiz_id' is invalid"
        return jsonify({"success": False, "message": message}), 400
    if not list(db.quizzes.find({"_id": quiz_id})):
        message = "Field 'quiz_id' doesn't exist"
        return jsonify({"success": False, "message": message}), 404
    request_object["_id"] = str(db.questions.insert_one(request_object).inserted_id)
    return jsonify({"success": True, "quiz": request_object}), 201






@app.route("/update_question", methods=["POST"])
def update_question():
    request_object = request.get_json()
    request_object_fields = {
        "quiz_id": str,
        "question": str,
        "answers": list(str),
        "correct_answer": str,
        "explanation": str,
        "_id": str
    }
    message = _validate_request_object(request_object, request_object_fields)
    if message:
        return jsonify({"success": False, "message": message}), 400
    try:
        _id = ObjectId(request_object.get("_id"))
    except Exception as _:
        message = "Field '_id' is invalid"
        return jsonify({"success": False, "message": message}), 400
    result = db.questions.update_one(
        {"_id": _id},
        {"$set": {"question": request_object.get("question"), "answers": request_object.get("answers"), "correct_answer": request_object.get("correct_answer"), "explanation": request_object.get("explanation")}}
    )
    if result.matched_count == 0:
        message = "Record not found"
        return jsonify({"success": False, "message": message}), 404 # 404 means not found
    message = "Successful update"
    return jsonify({"success": True, "message": message}), 200






@app.route("/delete_question", methods=["POST"])
def delete_question():
    request_object = request.get_json()
    request_object_fields = {
        "quiz_id": str,
        "question": str,
        "answers": list,
        "correct_answer": str,
        "explanation": str,
        "_id": str
    }
    message = _validate_request_object(request_object, request_object_fields)
    if message:
        return jsonify({"success": False, "message": message}), 400
    try:
        _id = ObjectId(request_object.get("_id"))
    except Exception as _:
        message = "Field '_id' is invalid"
        return jsonify({"success": False, "message": message}), 400
    result = db.questions.delete_one({"_id": _id})
    if result.deleted_count == 0:
        message = "Record not found"
        return jsonify({"success": False, "message": message}), 404
    return jsonify({"success": True, "message": message}), 200






@app.route("/get_questions", methods=["POST"])
def get_questions():
    request_object = request.get_json()
    request_object_fields = {
        "quiz_id": str,
    }
    message = _validate_request_object(request_object, request_object_fields)
    if message:
        return jsonify({"success": False, "message": message}), 400
    try:
        quiz_id = ObjectId(request_object.get("quiz_id"))
    except Exception as _:
        message = "Field 'quiz_id' is invalid"
        return jsonify({"success": False, "message": message}), 400
    questions = list(db.questions.find({"quiz_id": quiz_id}).sort("_id", DESCENDING))
    return jsonify({"success": True, "questions": questions})






if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)