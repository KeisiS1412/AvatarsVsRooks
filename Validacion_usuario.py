import os
import json
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.backends import default_backend

# === CONFIGURACIÓN DE RUTAS ===
KEY_FILE = "clave_chacha20.key"
USERS_DIR = "usuarios_encriptados"

if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)



# FUNCIONES DE CIFRADO CHACHA20

def generar_clave():
    """Genera una clave maestra de 256 bits para ChaCha20 y la guarda si no existe."""
    if not os.path.exists(KEY_FILE):
        key = os.urandom(32)
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key


def cifrar_datos(data_json: str, key: bytes):
    """Cifra datos JSON con ChaCha20 (devuelve nonce + cifrado)."""
    nonce = os.urandom(16)
    algorithm = algorithms.ChaCha20(key, nonce)
    cipher = Cipher(algorithm, mode=None, backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data_json.encode("utf-8"))
    return nonce + ciphertext


def descifrar_datos(ciphertext: bytes, key: bytes):
    """Descifra datos cifrados con ChaCha20."""
    nonce = ciphertext[:16]
    ct = ciphertext[16:]
    algorithm = algorithms.ChaCha20(key, nonce)
    cipher = Cipher(algorithm, mode=None, backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(ct)
    return decrypted.decode("utf-8")



# CARGA DE MALAS PALABRAS

def cargar_malas_palabras():
    """Carga la lista de malas palabras desde un archivo TXT."""
    archivo = "malas_palabras.txt"
    if not os.path.exists(archivo):
        print("No se encontró el archivo 'malas_palabras.txt'.")
        return []
    with open(archivo, "r", encoding="utf-8") as f:
        palabras = [
            line.strip().lower()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]
    return palabras



# VALIDACIÓN DE CONTRASEÑA

def validar_contraseña(password: str):
    """
    Verifica que la contraseña sea segura, solo alfanumérica,
    y que no contenga malas palabras.
    """
    malas = cargar_malas_palabras()
    for bad in malas:
        if bad in password.lower():
            return False, f" La contraseña contiene una palabra inapropiada: '{bad}'"

    # Solo letras y números
    if not re.match(r"^[A-Za-z0-9]+$", password):
        return False, " La contraseña solo puede contener letras y números (sin símbolos)."

    if len(password) < 6:
        return False, " La contraseña debe tener al menos 6 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, " Debe incluir al menos una letra mayúscula."
    if not re.search(r"[0-9]", password):
        return False, " Debe incluir al menos un número."

    return True, " Contraseña válida."



#  VALIDACIÓN DE INFORMACIÓN PERSONAL

def validar_informacion(nombre, apellidos, nacimiento, password):
    """Valida nombre, apellidos, fecha (DD/MM/AAAA) y contraseña."""
    if not nombre or not apellidos or not nacimiento or not password:
        return False, " Todos los campos son obligatorios."

    if not re.match(r"^\d{2}/\d{2}/\d{4}$", nacimiento):
        return False, "La fecha debe tener el formato DD/MM/AAAA."

    valido, msg = validar_contraseña(password)
    if not valido:
        return False, msg

    return True, " Información válida."



# GUARDAR Y CARGAR USUARIOS CIFRADOS

def guardar_usuario(nombre, apellidos, nacimiento, password):
    """Guarda la información cifrada del usuario."""
    key = generar_clave()
    usuario = {
        "nombre": nombre.strip().lower(),
        "apellidos": apellidos.strip().lower(),
        "nacimiento": nacimiento.strip(),
        "password": password
    }
    json_data = json.dumps(usuario)
    encrypted = cifrar_datos(json_data, key)

    filename = os.path.join(USERS_DIR, f"{usuario['nombre']}.dat")
    with open(filename, "wb") as f:
        f.write(encrypted)

    print(f" Usuario '{usuario['nombre']}' guardado cifrado en '{filename}'")
    return filename


def cargar_usuario(nombre):
    """Descifra los datos de un usuario si existe."""
    key = generar_clave()
    filename = os.path.join(USERS_DIR, f"{nombre.lower()}.dat")
    if not os.path.exists(filename):
        return None
    with open(filename, "rb") as f:
        encrypted = f.read()
    decrypted = descifrar_datos(encrypted, key)
    return json.loads(decrypted)


def usuario_existe(nombre):
    """Verifica si el usuario ya está registrado."""
    filename = os.path.join(USERS_DIR, f"{nombre.lower()}.dat")
    return os.path.exists(filename)
