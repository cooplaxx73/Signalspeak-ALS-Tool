"""
Pair this computer with a patient account on the SignalSpeak server.

Pairing signs in once as the patient and asks the server for a device
token. Only the token is saved (in device.json), never the password.

Two ways to use it:
- From the Windows app: the sign-in window (pairing_window.py) calls pair().
- From source:  python connect.py  (asks in the terminal)

Libraries: Requests for HTTP: https://requests.readthedocs.io
Integration assistance: OpenAI Codex. Window support added with the
assistance of Claude Code (Anthropic).
"""

import getpass
import json

import requests

from paths import APP_FOLDER

DEVICE_FILE = APP_FOLDER / "device.json"
DEFAULT_SERVER = "http://127.0.0.1:3000"


def pair(server: str, email: str, password: str) -> dict:
    """Sign in as the patient and save a device token. Returns the account
    details. Raises requests.RequestException or ValueError on failure."""
    server = (server.strip() or DEFAULT_SERVER).rstrip("/")
    with requests.Session() as session:
        response = session.post(server + "/api/login",
                                json={"email": email, "password": password}, timeout=10)
        if response.status_code in (400, 401):
            raise ValueError("Wrong email or password.")
        response.raise_for_status()
        if response.json()["role"] != "patient":
            raise ValueError("Use the patient account to pair this computer.")
        paired = session.post(server + "/api/device-pair", json={}, timeout=10)
        paired.raise_for_status()
        data = paired.json()
        data["backend_url"] = server
        DEVICE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        session.post(server + "/api/logout", json={}, timeout=10)
    return data


def main():
    server = input(f"Account server [{DEFAULT_SERVER}]: ")
    email = input("Patient email: ").strip()
    password = getpass.getpass("Patient password: ")
    data = pair(server, email, password)
    print(f"Paired with {data['name']} ({data['patientId']}). Run python main.py next.")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, ValueError) as error:
        print(f"Pairing failed: {error}")
        raise SystemExit(1)
