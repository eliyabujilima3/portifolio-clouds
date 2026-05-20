from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from backend.config import Config
import os

# ---------------------------
# LOAD ENV VARIABLES
# ---------------------------
load_dotenv()

app = Flask(__name__)

# secret key for sessions (change in production)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

# allow frontend (Vercel)
CORS(app, supports_credentials=True)

# ---------------------------
# DATABASE CONFIG
# ---------------------------
app.config.from_object(Config)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    if "***" in DATABASE_URL:
        print("Ignoring invalid DATABASE_URL placeholder; using local SQLite database.")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

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
        "status": "success",
        "message": "Flask Contact API is running 🚀"
    })

# ---------------------------
# CONTACT FORM API
# ---------------------------
@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not name or not email or not message:
        return jsonify({"status": "error", "message": "All fields required"}), 400

    new_msg = Message(name=name, email=email, message=message)
    db.session.add(new_msg)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Message sent successfully"
    }), 200

# ---------------------------
# GET ALL MESSAGES (ADMIN DASHBOARD)
# ---------------------------
@app.route("/api/messages", methods=["GET"])
def get_messages():
    messages = Message.query.order_by(Message.id.desc()).all()

    return jsonify([
        {
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "message": m.message
        } for m in messages
    ])

# ---------------------------
# ADMIN LOGIN
# ---------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # simple admin credentials (assignment purpose)
    if username == "admin" and password == "1234":
        session["admin"] = True
        return jsonify({"status": "success", "message": "Login successful"}), 200

    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# ---------------------------
# ADMIN LOGOUT
# ---------------------------
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logout successful"})

# ---------------------------
# INIT DATABASE
# ---------------------------
with app.app_context():
    db.create_all()

# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)