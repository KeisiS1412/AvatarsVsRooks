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
