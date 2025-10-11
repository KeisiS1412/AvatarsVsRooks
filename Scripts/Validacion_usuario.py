import os
import re
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.backends import default_backend

# === CONFIGURACIÓN DE RUTAS ===
KEY_FILE = "clave_chacha20.key"
USERS_DIR = "usuarios_encriptados"

if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)



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


# === VALIDACIONES DE CAMPOS ===

def cargar_malas_palabras():
    """Carga malas palabras desde un archivo TXT (si existe)."""
    archivo = "malas_palabras.txt"
    if not os.path.exists(archivo):
        return []
    with open(archivo, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]


def validar_contraseña(password: str):
    """Valida la seguridad de una contraseña."""
    malas = cargar_malas_palabras()
    for bad in malas:
        if bad in password.lower():
            return False, f"La contraseña contiene una palabra inapropiada: '{bad}'"

    if not re.match(r"^[A-Za-z0-9]+$", password):
        return False, "La contraseña solo puede contener letras y números."

    if len(password) < 8:
        return False, "Debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "Debe incluir al menos una letra mayúscula."
    if not re.search(r"[0-9]", password):
        return False, "Debe incluir al menos un número."

    return True, "Contraseña válida."


def validar_informacion(nombre, apellidos, nacimiento, password):
    """Valida que los datos personales sean correctos."""
    if not nombre or not apellidos or not nacimiento or not password:
        return False, "Todos los campos son obligatorios."

    if not re.match(r"^\d{2}/\d{2}/\d{4}$", nacimiento):
        return False, "La fecha debe tener el formato DD/MM/AAAA."

    valido, msg = validar_contraseña(password)
    if not valido:
        return False, msg

    return True, "Información válida."


# VERIFICACIÓN DE USUARIOS EXISTENTES (para login o registro)

def usuario_existe(nombre):
    """Comprueba si el archivo del usuario existe."""
    filename = os.path.join(USERS_DIR, f"{nombre.lower()}.dat")
    return os.path.exists(filename)


def verificar_credenciales(nombre, password):
    """
    Verifica si el usuario existe y si la contraseña coincide con la guardada.
    Solo lectura (no crea ni guarda nada).
    """
    nombre = nombre.strip().lower()
    if not usuario_existe(nombre):
        return False, "El usuario no está registrado."

    key = generar_clave()
    if not key:
        return False, "No se encontró la clave de descifrado."

    filename = os.path.join(USERS_DIR, f"{nombre}.dat")
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
