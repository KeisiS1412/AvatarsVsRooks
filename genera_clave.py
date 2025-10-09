# genera_clave.py
import os, binascii

# Genera 32 bytes (256 bits) de clave aleatoria y la muestra en formato HEX
key = os.urandom(32)
print("Tu clave HEX es:\n")
print(binascii.hexlify(key).decode())
