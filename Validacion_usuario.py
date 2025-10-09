import os
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.backends import default_backend

# === CONFIGURACIÓN ===
KEY_FILE = "clave_chacha20.key"
USERS_DIR = "usuarios_encriptados"

if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)


# === DESCIFRADO ===

def generar_clave():
    """Lee la clave maestra para descifrar datos ya existentes."""
    if not os.path.exists(KEY_FILE):
        return None
    with open(KEY_FILE, "rb") as f:
        return f.read()


def descifrar_datos(ciphertext: bytes, key: bytes):
    """Descifra datos cifrados con ChaCha20."""
    nonce = ciphertext[:16]
    ct = ciphertext[16:]
    algorithm = algorithms.ChaCha20(key, nonce)
    cipher = Cipher(algorithm, mode=None, backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(ct)
    return decrypted.decode("utf-8")


# === VERIFICACIÓN DE USUARIOS ===

def usuario_existe(username):
    """Verifica si el usuario existe en la carpeta encriptada."""
    filename = os.path.join(USERS_DIR, f"{username.lower()}.dat")
    return os.path.exists(filename)


def verificar_credenciales(username=None, password=None, facial=False):
    """
    Verifica credenciales según el tipo de login:
    - Login normal: requiere username + password
    - Login facial: requiere solo facial=True (sin contraseña)
    """
    key = generar_clave()
    if not key:
        return False, "No se encontró la clave de descifrado."

    # === LOGIN FACIAL ===
    if facial:
        # Buscar usuario con registro facial
        for archivo in os.listdir(USERS_DIR):
            ruta = os.path.join(USERS_DIR, archivo)
            try:
                with open(ruta, "rb") as f:
                    encrypted = f.read()
                decrypted = descifrar_datos(encrypted, key)
                datos = json.loads(decrypted)

                if datos.get("facial_id"):
                    return True, datos
            except Exception:
                continue
        return False, "No se encontró ningún usuario con registro facial."

    # === LOGIN NORMAL ===
    if not username or not password:
        return False, "Debe ingresar usuario y contraseña."

    username = username.strip().lower()
    filename = os.path.join(USERS_DIR, f"{username}.dat")

    if not usuario_existe(username):
        return False, "El usuario no está registrado."

    try:
        with open(filename, "rb") as f:
            encrypted = f.read()
        decrypted = descifrar_datos(encrypted, key)
        datos = json.loads(decrypted)

        if datos.get("password") == password:
            return True, datos
        else:
            return False, "Contraseña incorrecta."

    except Exception as e:
        return False, f"Error al verificar usuario: {e}"
