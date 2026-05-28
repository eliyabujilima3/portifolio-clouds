from flask import Blueprint, request, jsonify, session, current_app
from models import db, Message
import os
import smtplib
import ssl
from email.message import EmailMessage

reply_bp = Blueprint("reply", __name__)


def send_reply_email(to_email: str, subject: str, body: str) -> None:
    """Send an email using SMTP server configured via environment variables.

    Required env vars: SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
    """
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_server or not smtp_user or not smtp_password:
        raise RuntimeError("SMTP not configured: set SMTP_SERVER/SMTP_USER/SMTP_PASSWORD")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


@reply_bp.route("/api/reply", methods=["POST"])
def reply():
    if "admin" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    data = request.get_json()
    message_id = data.get("id")
    reply_text = data.get("message")

    if not message_id or not reply_text:
        return jsonify({"status": "error", "message": "Message ID and reply text required"}), 400

    msg = Message.query.get(message_id)
    if not msg:
        return jsonify({"status": "error", "message": "Message not found"}), 404

    msg.reply = reply_text
    db.session.commit()

    # Try to send reply by email (optional). Log but don't fail the request if email sending fails.
    try:
        subject = f"Reply to your message (id: {msg.id})"
        send_reply_email(msg.email, subject, reply_text)
    except Exception as e:
        current_app.logger.exception("Failed to send reply email")
        # In debug mode include the exception message in the response to help troubleshooting
        if current_app.debug:
            return jsonify({"status": "success", "message": "Reply stored; email send failed", "error": str(e), "reply": msg.reply}), 200
        return jsonify({"status": "success", "message": "Reply stored; email send failed", "reply": msg.reply}), 200

    return jsonify({"status": "success", "message": "Reply stored and emailed successfully", "reply": msg.reply}), 200
