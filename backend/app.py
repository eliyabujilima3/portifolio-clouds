from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from config import Config
from models import db, Message
from routes.reply import reply_bp
from sqlalchemy import text
import os

# ---------------------------
# LOAD ENV VARIABLES
# ---------------------------
load_dotenv()

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# secret key for sessions (change in production)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

# session cookie settings for local development
app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
secure_cookie = os.getenv("SESSION_COOKIE_SECURE")
if secure_cookie is None:
    app.config["SESSION_COOKIE_SECURE"] = False
else:
    app.config["SESSION_COOKIE_SECURE"] = secure_cookie.lower() == "true"

# ---------------------------
# ALLOWED ORIGINS (CORS)
# ---------------------------
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    "https://portifolio-clouds-zlqf-git-main-eliya-bujilima-s-projects.vercel.app",
    "https://portifolio-clouds.onrender.com"
]

# allow frontend requests from allowed origins only, with credentials
CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}}, supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS"])

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# ---------------------------
# DATABASE CONFIG
app.config.from_object(Config)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    if "***" in DATABASE_URL:
        print("Ignoring invalid DATABASE_URL placeholder; using local SQLite database.")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(reply_bp)

# ---------------------------
# HOME ROUTE
@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "Flask Contact API is running 🚀"
    })

# ---------------------------
# CONTACT FORM API
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
        "message": "Message sent successfully",
        "id": new_msg.id
    }), 200

# ---------------------------
# GET ALL MESSAGES (ADMIN DASHBOARD)
@app.route("/api/messages", methods=["GET"])
def get_messages():
    try:
        email = request.args.get("email")
        if email:
            messages = Message.query.filter_by(email=email).order_by(Message.id.desc()).all()
        else:
            messages = Message.query.order_by(Message.id.desc()).all()
        return jsonify([m.to_dict() for m in messages])
    except Exception as e:
        app.logger.exception("Error fetching messages")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/message/<int:msg_id>", methods=["GET"])
def get_message(msg_id):
    msg = Message.query.get(msg_id)
    if not msg:
        return jsonify({"status": "error", "message": "Message not found"}), 404
    return jsonify(msg.to_dict()), 200

# ---------------------------
# ADMIN LOGIN
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # Get credentials from environment variables (more secure)
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "1234")

    if username == admin_username and password == admin_password:
        session["admin"] = True
        return jsonify({"status": "success", "message": "Login successful"}), 200

    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# ---------------------------
# ADMIN LOGOUT
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logout successful"})

# ---------------------------
# INIT DATABASE
with app.app_context():
    db.create_all()

    # auto-add reply column if this DB was created before the reply field existed
    inspector = db.inspect(db.engine)
    if inspector.has_table("message"):
        columns = [col["name"] for col in inspector.get_columns("message")]
        if "reply" not in columns:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE message ADD COLUMN reply TEXT"))
                conn.commit()

# ---------------------------
# RUN SERVER
if __name__ == "__main__":
    app.run(debug=True)
