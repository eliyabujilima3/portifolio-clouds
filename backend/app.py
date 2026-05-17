from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import session
import os

app = Flask(__name__)
app.secret_key = "mysecretkey"
CORS(app)

# ---------------------------
# DATABASE CONFIG
# ---------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------------------
# DATABASE MODEL
# ---------------------------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# ---------------------------
# HOME ROUTE
# ---------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "Flask Contact API is running"
    })

# ---------------------------
# CONTACT API (SAVE TO DB)
# ---------------------------
@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON payload"
        }), 400

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    # validation
    if not name or not email or not message:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    # save to database
    new_message = Message(name=name, email=email, message=message)
    db.session.add(new_message)
    db.session.commit()

    print("New message saved:", name, email)

    return jsonify({
        "status": "success",
        "message": "Message received successfully"
    }), 200

# ---------------------------
# ADMIN: GET ALL MESSAGES
# ---------------------------
@app.route("/api/messages", methods=["GET"])
def get_messages():
    messages = Message.query.all()

    return jsonify([
        {
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "message": m.message
        } for m in messages
    ])
    
# -------ADMIN LOGIN-------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # simple hardcoded login (for assignment)
    if username == "admin" and password == "1234":
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"message": "Invalid credentials"}), 401

# -------ADMIN LOGOUT-------
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200
# ---------------------------
# INIT DATABASE (AUTO CREATE TABLES)
# ---------------------------
with app.app_context():
    db.create_all()

# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)