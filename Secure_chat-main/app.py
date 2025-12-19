import base64
import hashlib
import json
import os
import time
from typing import Any, Dict, List

from flask import Flask, Response, jsonify, render_template, request
from flask_socketio import SocketIO, emit
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", os.urandom(32))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

participants: Dict[str, Dict[str, Any]] = {}
sessions: Dict[str, str] = {}
logs: List[Dict[str, str]] = []

LOG_KEY_B64 = os.getenv("SERVER_LOG_KEY_B64")
if LOG_KEY_B64:
    LOG_KEY = base64.b64decode(LOG_KEY_B64)
else:
    LOG_KEY = AESGCM.generate_key(bit_length=256)
    app.logger.warning(
        "Generated ephemeral log key; set SERVER_LOG_KEY_B64 to persist logs across restarts."
    )
log_cipher = AESGCM(LOG_KEY)


def compute_fingerprint(public_key_b64: str) -> str:
    der = base64.b64decode(public_key_b64)
    digest = hashlib.sha256(der).hexdigest()
    return ":".join(digest[i : i + 2] for i in range(0, len(digest), 2))


def participant_snapshot() -> List[Dict[str, str]]:
    return [
        {
            "username": username,
            "fingerprint": info["fingerprint"],
            "public_key": info["public_key"],
        }
        for username, info in sorted(participants.items(), key=lambda item: item[0].lower())
    ]


def broadcast_participants() -> None:
    socketio.emit("participants", {"participants": participant_snapshot()})


def store_encrypted_log(payload: Dict[str, Any]) -> None:
    entry_payload = dict(payload)
    entry_payload.setdefault("stored_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    nonce = os.urandom(12)
    serialized = json.dumps(entry_payload, separators=(",", ":")).encode()
    ciphertext = log_cipher.encrypt(nonce, serialized, associated_data=None)
    logs.append(
        {
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
        }
    )


def collect_encrypted_logs() -> List[Dict[str, str]]:
    return list(logs)


def remove_participant(sid: str) -> None:
    username = sessions.pop(sid, None)
    if not username:
        return

    info = participants.pop(username, None)
    if not info:
        return

    socketio.emit(
        "user_left",
        {"username": username, "fingerprint": info["fingerprint"]},
        include_self=False,
    )
    broadcast_participants()


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.route("/api/users")
def api_users() -> Response:
    return jsonify({"participants": participant_snapshot()})


@app.route("/logs", methods=["GET"])
def get_logs() -> Response:
    token_required = os.getenv("LOG_EXPORT_TOKEN")
    supplied = request.headers.get("X-Log-Token")
    if token_required and supplied != token_required:
        return jsonify({"error": "unauthorized"}), 401

    return jsonify({"entries": collect_encrypted_logs()})


@socketio.on("register")
def handle_register(data: Dict[str, Any]) -> None:
    username = (data.get("username") or "").strip()
    public_key = data.get("public_key")
    if not username or not public_key:
        emit("register_error", {"message": "Username and public key are required."})
        return

    if len(username) < 2:
        emit("register_error", {"message": "Username must be at least 2 characters."})
        return

    existing = participants.get(username)
    if existing and existing.get("sid") != request.sid:
        emit("register_error", {"message": "That username is already in use."})
        return

    fingerprint = compute_fingerprint(public_key)

    remove_participant(request.sid)

    participants[username] = {
        "public_key": public_key,
        "fingerprint": fingerprint,
        "sid": request.sid,
        "joined_at": time.time(),
    }
    sessions[request.sid] = username
    app.logger.info("%s joined the chat", username)

    payload = {
        "username": username,
        "fingerprint": fingerprint,
        "participants": participant_snapshot(),
    }
    emit("register_success", payload)

    socketio.emit(
        "user_joined",
        {"username": username, "fingerprint": fingerprint},
        include_self=False,
    )
    broadcast_participants()


@socketio.on("send_message")
def handle_send_message(data: Dict[str, Any]) -> None:
    sender = data.get("from")
    ciphertext = data.get("ciphertext")
    iv = data.get("iv")
    timestamp = data.get("timestamp")
    envelopes = data.get("envelopes") or {}

    if not sender:
        emit("delivery_error", {"message": "Missing sender username."})
        return

    member = participants.get(sender)
    if not member or member.get("sid") != request.sid:
        app.logger.warning(
            "Message rejected: sender %s not registered (sid %s)", sender, request.sid
        )
        emit("delivery_error", {"message": "Sender not registered."})
        return

    expected_recipients = set(participants.keys())
    actual_recipients = set(envelopes.keys())
    missing = expected_recipients - actual_recipients
    if missing:
        app.logger.warning(
            "Message rejected: missing envelopes %s from %s",
            sorted(missing),
            sender,
        )
        emit("delivery_error", {"message": f"Missing envelopes for: {', '.join(sorted(missing))}"})
        return

    payload = {
        "from": sender,
        "ciphertext": ciphertext,
        "iv": iv,
        "timestamp": timestamp,
        "envelopes": envelopes,
    }

    store_encrypted_log(payload)
    socketio.emit("receive_message", payload)


@socketio.on("request_public_key")
def handle_request_public_key(data: Dict[str, Any]) -> None:
    username = data.get("username")
    if not username:
        emit("public_key", {"username": None, "public_key": None})
        return
    member = participants.get(username)
    emit(
        "public_key",
        {
            "username": username,
            "public_key": member.get("public_key") if member else None,
            "fingerprint": member.get("fingerprint") if member else None,
        },
    )


@socketio.on("leave_chat")
def handle_leave_chat() -> None:
    remove_participant(request.sid)


@socketio.on("disconnect")
def handle_disconnect() -> None:
    remove_participant(request.sid)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
