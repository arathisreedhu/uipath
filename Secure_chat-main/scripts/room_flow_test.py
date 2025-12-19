"""Quick manual flow test for room creation and joining via Socket.IO client."""

import asyncio
import base64
import json
from typing import Any, Dict, List, Tuple

import socketio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_public_key_b64() -> str:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return base64.b64encode(der).decode()


async def connect_and_listen(name: str, events: List[Tuple[str, Any]]) -> socketio.AsyncClient:
    client = socketio.AsyncClient()

    @client.event
    def connect() -> None:  # pragma: no cover
        events.append((f"{name}:connect", None))

    @client.on("room_created")
    def on_room_created(payload: Any) -> None:
        events.append((f"{name}:room_created", payload))

    @client.on("register_success")
    def on_register_success(payload: Any) -> None:
        events.append((f"{name}:register_success", payload))

    await client.connect("http://localhost:5000")
    return client


async def main() -> None:
    events: List[Tuple[str, Any]] = []

    host = await connect_and_listen("host", events)
    await host.emit("create_room")
    await asyncio.sleep(0.2)

    created = next((p for name, p in events if name.endswith("room_created")), None)
    if not created:
        raise RuntimeError("room_created payload missing")
    code = created["code"]

    await host.emit(
        "register",
        {"username": "host", "public_key": generate_public_key_b64(), "room_code": code},
    )
    await asyncio.sleep(0.2)

    guest = await connect_and_listen("guest", events)
    await guest.emit(
        "register",
        {"username": "guest", "public_key": generate_public_key_b64(), "room_code": code},
    )
    await asyncio.sleep(0.2)

    print(json.dumps(events, indent=2))
    await host.disconnect()
    await guest.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
