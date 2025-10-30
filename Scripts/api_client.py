# Scripts/api_client.py
import requests

BASE_URL = "http://localhost:3007"

def register_user(payload: dict, timeout: float = 5.0) -> dict:
    url = f"{BASE_URL}/auth/register"
    r = requests.post(url, json=payload, timeout=timeout)
    return r.json()

def login_user(username_or_email: str, password: str, timeout: float = 5.0) -> dict:
    url = f"{BASE_URL}/auth/login"
    body = {"username_or_email": username_or_email, "password": password}
    r = requests.post(url, json=body, timeout=timeout)
    return r.json()

def request_password_reset(email: str) -> str | None:
    r = requests.post(f"{BASE_URL}/auth/request-reset", json={"email": email})
    data = r.json()
    return data.get("token")

def confirm_password_reset(email: str, token: str, new_password: str) -> bool: #Confirma el token y cambia la contraseña
    r = requests.post(
        f"{BASE_URL}/auth/confirm-reset",
        json={"email": email, "token": token, "newPassword": new_password}
    )
    data = r.json()
    return data.get("ok", False)


