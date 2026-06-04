from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text
import os
import sys
from werkzeug.exceptions import HTTPException

# Ensure backend package imports work whether the app is run from the repo root
# or from inside the backend folder.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from backend.config import Config
    from backend.models import db, Message
    from backend.routes.reply import reply_bp
except ImportError:
    from config import Config
    from models import db, Message
    from routes.reply import reply_bp

# ---------------------------
# LOAD ENV VARIABLES
# ---------------------------
load_dotenv()

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# secret key for sessions (change in production)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

# session cookie settings
# Use SameSite=None + Secure=True on deployed HTTPS hosts like Render,
# while keeping Lax/Secure=False for local development.
use_secure_cookies = os.getenv("SESSION_COOKIE_SECURE")
if use_secure_cookies is None:
    if os.getenv("RENDER") == "true" or os.getenv("ENV") == "production":
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
        app.config["SESSION_COOKIE_SECURE"] = True
    else:
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_SECURE"] = False
else:
    app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "None")
    app.config["SESSION_COOKIE_SECURE"] = use_secure_cookies.lower() == "true"

# ---------------------------
# ALLOWED ORIGINS (CORS)
# ---------------------------
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    "https://portifolio-clouds-zlqf.vercel.app",
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

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

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

@app.route("/<path:path>")
def serve_frontend(path):
    if path.startswith("api/"):
        return jsonify({"status": "error", "message": "Not found"}), 404
    return send_from_directory(frontend_dir, path)

# ---------------------------
# CONTACT FORM API
@app.route("/api/contact", methods=["POST"])
def contact():
    try:
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

        print(f"✅ Message saved - ID: {new_msg.id}, From: {email}")
        
        return jsonify({
            "status": "success",
            "message": "Message sent successfully",
            "id": new_msg.id
        }), 200
    
    except Exception as e:
        print(f"❌ Error saving message: {str(e)}")
        app.logger.exception("Error in contact route")
        db.session.rollback()
        return jsonify({
            "status": "error", 
            "message": "Failed to save message. Please try again.",
            "debug": str(e) if app.debug else None
        }), 500

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

# Global error handler: return JSON for API routes to avoid HTML error pages
@app.errorhandler(Exception)
def handle_unhandled_exception(e):
    # If the error is an HTTPException and the request is to the API,
    # return JSON so the frontend can parse it instead of HTML.
    if isinstance(e, HTTPException):
        if request.path.startswith("/api/"):
            payload = {"status": "error", "message": e.description}
            return jsonify(payload), e.code
        return e

    # Log the exception
    app.logger.exception("Unhandled exception")

    # If request was to the API, return JSON so frontend can parse it
    if request.path.startswith("/api/"):
        payload = {"status": "error", "message": "Internal Server Error"}
        if app.debug:
            payload["debug"] = str(e)
        return jsonify(payload), 500

    # Fallback for non-API requests
    return jsonify({"status": "error", "message": "Internal Server Error"}), 500


# ---------------------------
# RUN SERVER
if __name__ == "__main__":
    app.run(debug=True)
