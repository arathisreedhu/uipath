"""Utility to decrypt stored message logs using the shared server key."""

import base64
import json
import os
import sys
from typing import Any, Dict, List

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def load_key() -> bytes:
    key_b64 = os.getenv("SERVER_LOG_KEY_B64")
    if not key_b64:
        raise RuntimeError("SERVER_LOG_KEY_B64 environment variable is required")
    key = base64.b64decode(key_b64)
    if len(key) != 32:
        raise RuntimeError("SERVER_LOG_KEY_B64 must decode to 32 bytes (256 bits)")
    return key


def decrypt_entries(entries: List[Dict[str, Any]], aes: AESGCM) -> List[Dict[str, Any]]:
    decrypted = []
    for entry in entries:
        nonce = base64.b64decode(entry["nonce"])
        ciphertext = base64.b64decode(entry["ciphertext"])
        plaintext = aes.decrypt(nonce, ciphertext, associated_data=None)
        decrypted.append(json.loads(plaintext.decode()))
    return decrypted


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/decrypt_logs.py <logs.json>")
        raise SystemExit(1)

    log_path = sys.argv[1]
    with open(log_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    entries = payload.get("entries", [])
    aes = AESGCM(load_key())
    results = decrypt_entries(entries, aes)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
