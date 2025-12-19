# Secure Chat

Secure Chat is a lightweight Flask + Socket.IO demo that lets anyone with the link join an encrypted group conversation right in the browser. Every message is encrypted in the client with AES-GCM and the AES session key is wrapped for each participant using their RSA-OAEP public key, so only the intended recipients can decrypt the content.

## Features

- 🔐 **End-to-end encryption** – RSA-2048 key pairs per browser, AES-256-GCM for message bodies.
- 👥 **Shared room by link** – no codes; anyone who visits the page and picks a username can join.
- 📜 **Participant roster** – live list of connected users plus their key fingerprints.
- 📦 **Encrypted server logs** – ciphertext-only audit trail for debugging.

## Tech Stack

- Python 3.11+
- Flask 3 + Flask-SocketIO
- WebCrypto API (RSA-OAEP, AES-GCM)
- Vanilla JavaScript / HTML / CSS

## Getting Started

### 1. Clone or download

```powershell
cd D:\Secure Chat
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the development server

```powershell
python app.py
```

The app listens on port `5000` by default.

### 5. Open the client

> ⚠️ The WebCrypto API requires a **secure context**. Use "http://localhost:5000" in your browser. Plain LAN IPs like `http://192.168.x.x` are considered insecure and WebCrypto will refuse to run.

## Usage

1. Load the page and type a username.
2. Click **Join chat**; the browser generates an RSA key pair locally and registers your public key.
3. Start typing messages. Each send operation:
   - Generates a fresh AES-256 key and IV.
   - Encrypts the message with AES-GCM.
   - Wraps the AES key for each participant using their RSA public key.
   - Emits only ciphertext + encrypted envelopes to the backend.
4. Close the tab or click **Leave chat** to disappear from the roster.

Refresh the page: notice that previous messages cannot be reloaded because the server never sees plaintext.

## Deploying or Sharing

- For local demos across devices, run the Flask app and front it with an HTTPS reverse proxy (Caddy, Nginx with certs, Cloudflare Tunnel, etc.).
- A production deployment should use a proper WSGI server (Gunicorn, uWSGI) behind a TLS termination proxy.

## Project Structure

```
Secure Chat/
├── app.py                # Flask + Socket.IO server
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/styles.css    # UI styling
│   └── js/main.js        # WebCrypto + Socket.IO client logic
└── templates/index.html  # Single-page chat UI
```

## Security Notes

- Private keys never leave the browser.
- The server only stores encrypted payloads; the `/logs` endpoint returns ciphertext.
- Browsers must support WebCrypto (modern Chrome, Firefox, Edge, Safari). Older or insecure contexts will refuse to run cryptography.

## License

Add your preferred license here before publishing publicly.
