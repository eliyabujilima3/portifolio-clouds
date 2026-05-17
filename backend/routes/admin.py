from flask import Blueprint, jsonify
from models import Message

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/api/messages", methods=["GET"])
def get_messages():
    messages = Message.query.all()
    return jsonify([m.to_dict() for m in messages])