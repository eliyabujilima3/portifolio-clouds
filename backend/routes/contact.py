from flask import Blueprint, request, jsonify
from backend.models import db, Message

contact_bp = Blueprint("contact", __name__)

@contact_bp.route("/api/contact", methods=["POST"])
def contact():
    data = request.json

    new_msg = Message(
        name=data["name"],
        email=data["email"],
        message=data["message"]
    )

    db.session.add(new_msg)
    db.session.commit()

    return jsonify({"message": "Message received successfully"})