# Scripts/api_client.py
import requests
import os 
import base64

BASE_URL = "http://localhost:3007"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
ASSETS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "Assets"))  
AVATAR_CACHE_DIR = os.path.join(ASSETS_DIR, "avatars_cache")  

os.makedirs(AVATAR_CACHE_DIR, exist_ok=True)  


def register_user(payload: dict, timeout: float = 5.0) -> dict:
    url = f"{BASE_URL}/auth/register"
    r = requests.post(url, json=payload, timeout=timeout)
    return r.json()

def login_user(username_or_email: str, password: str, timeout: float = 5.0) -> dict:
    url = f"{BASE_URL}/auth/login"
    body = {"username_or_email": username_or_email, "password": password}
    r = requests.post(url, json=body, timeout=timeout)
    return r.json()

def get_user(username: str, timeout: float = 3.0) -> dict: # Obtiene los datos del usuario por su nombre de usuario
    try:
        from api_client import BASE_URL  
    except Exception:
        BASE_URL = "http://localhost:3007"

    try:
        r = requests.get(f"{BASE_URL}/users/{username}", timeout=timeout)
        data = r.json()
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    
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

def update_user_preferences(
    username: str,
    color: str = None,
    theme: str = None,
    song: str = None,
    hobbie: str = None,
    timeout: float = 5.0,
) -> dict:
    """Actualiza las preferencias del usuario (color, tema, canción, hobbie)"""
    url = f"{BASE_URL}/users/{username}/preferences"
    payload: dict = {}

    if color is not None:
        payload["color"] = color
    if theme is not None:
        payload["theme"] = theme
    if song is not None:
        payload["song"] = song
    if hobbie is not None:
        payload["hobbie"] = hobbie

    try:
        r = requests.patch(url, json=payload, timeout=timeout)
        return r.json()
    except Exception as e:
        print(f"Error actualizando preferencias: {e}")
        return {"ok": False, "error": str(e)}


def download_avatar(username: str, timeout: float = 5.0) -> str | None:  
    """Descarga el avatar del usuario desde el backend a un archivo local y devuelve la ruta."""  
    url = f"{BASE_URL}/users/{username}/avatar"  
    try:  
        r = requests.get(url, timeout=timeout)  
        if r.status_code != 200:  
            print(f"Avatar no disponible para {username}: {r.status_code}")  
            return None  
        ext = ".png"  
        content_type = r.headers.get("Content-Type", "")  
        if "jpeg" in content_type:  
            ext = ".jpg"  
        elif "bmp" in content_type:  
            ext = ".bmp"  
        elif "gif" in content_type:  
            ext = ".gif"  
        filename = f"{username}_avatar{ext}"  
        local_path = os.path.join(AVATAR_CACHE_DIR, filename)  
        with open(local_path, "wb") as f:  
            f.write(r.content)  
        return local_path  
    except Exception as e:  
        print(f"Error descargando avatar de {username}: {e}")  
        return None  

def upload_avatar(username: str, image_path: str, timeout: float = 10.0) -> dict:  
    """Sube una nueva imagen de avatar para el usuario."""  
    try:  
        if not image_path or not os.path.exists(image_path):  
            return {"ok": False, "error": "invalid_path"}  
        with open(image_path, "rb") as f:  
            raw = f.read()  
        avatar_b64 = base64.b64encode(raw).decode("ascii")  
        ext = os.path.splitext(image_path)[1].lower()  
        mime = "image/png"  
        if ext in (".jpg", ".jpeg"):  
            mime = "image/jpeg"  
        elif ext == ".gif":  
            mime = "image/gif"  
        elif ext == ".bmp":  
            mime = "image/bmp"  
 
        url = f"{BASE_URL}/users/{username}/avatar"  
        payload = {"avatar_b64": avatar_b64, "avatar_mime": mime}  
        r = requests.post(url, json=payload, timeout=timeout)  
        try:  
            return r.json()  
        except Exception:  
            return {"ok": False, "error": f"bad_response_{r.status_code}"}  
    except Exception as e:  
        print(f"Error subiendo avatar: {e}")  
        return {"ok": False, "error": str(e)}  
