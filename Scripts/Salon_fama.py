import pygame
import sys
import os
import json
from publicationManager import publicationManager
pygame.init()

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
info = pygame.display.Info()
ANCHO, ALTO = info.current_w, info.current_h
VENTANA = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
COLOR_FONDO = (20, 20, 60)

FUENTE_TEXTO = pygame.font.SysFont("Avenir", 85)
FUENTE_BOTON = pygame.font.SysFont("Avenir", 45)
FUENTE_LISTA = pygame.font.SysFont("Avenir", 36)

# ==============================
# ARCHIVO LOCAL
# ==============================
CARPETA_RECURSOS = os.path.join(os.path.dirname(__file__), "Imagenes-sonidos")
ARCHIVO_FAMA = os.path.join(CARPETA_RECURSOS, "salon_fama.json")

if not os.path.exists(ARCHIVO_FAMA):
    with open(ARCHIVO_FAMA, "w", encoding="utf-8") as f:
        json.dump([], f)

# ==============================================================
#  UTILIDAD: LIMPIAR JSON DAÑADO -> QUITA DUPLICADOS Y CORRIGE
# ==============================================================

def limpiar_archivo_fama():
    try:
        with open(ARCHIVO_FAMA, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except:
        datos = []

    tabla = {}

    for d in datos:
        if isinstance(d, dict) and "username" in d and "puntaje" in d:
            u = d["username"]
            p = d["puntaje"]
            # guardar solo el MEJOR puntaje para cada usuario
            if u not in tabla or p > tabla[u]:
                tabla[u] = p

    lista = [{"username": u, "puntaje": p} for u, p in tabla.items()]
    lista = sorted(lista, key=lambda x: x["puntaje"], reverse=True)[:5]

    with open(ARCHIVO_FAMA, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4)

    return lista


# ==============================================================
#  GUARDAR PUNTAJE (SIN DUPLICADOS)
# ==============================================================

def guardar_en_fama(username, puntaje):
    print("fama abierto")

    tabla = {}

    # leer archivo y limpiarlo
    try:
        with open(ARCHIVO_FAMA, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except:
        datos = []

    # procesar datos existentes
    for d in datos:
        if isinstance(d, dict) and "username" in d and "puntaje" in d:
            u, p = d["username"], d["puntaje"]
            if u not in tabla or p > tabla[u]:
                tabla[u] = p

    # actualizar el puntaje del usuario actual
    top_cambio = False
    if username not in tabla or puntaje > tabla[username]:
        tabla[username] = puntaje
        top_cambio = True

    # convertir a lista
    lista = [{"username": u, "puntaje": p} for u, p in tabla.items()]
    lista = sorted(lista, key=lambda x: x["puntaje"], reverse=True)[:5]

    # guardar archivo limpio
    with open(ARCHIVO_FAMA, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4)

    if top_cambio:
        scores = {item["username"]: item["puntaje"] for item in lista}
        manager = publicationManager(scores)
        manager.makePosts()
        print("📢 PUBLICADO: top 5 actualizado.")
    else:
        print("ℹ️ No se publica: el top 5 no cambió.")


# ==============================================================
#  LEER PUNTAJES (JSON LIMPIO SIEMPRE)
# ==============================================================

def obtener_puntajes_locales():
    return limpiar_archivo_fama()


# ==============================================================
#  MOSTRAR LISTA
# ==============================================================

def mostrar_lista_puntajes(datos, titulo_texto="SALÓN DE LA FAMA"):
    reloj = pygame.time.Clock()
    boton_volver = pygame.Rect(ANCHO // 2 - 120, ALTO - 90, 240, 60)
    medallas = ["🥇", "🥈", "🥉"]
    line_spacing = 85

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_volver.collidepoint(evento.pos):
                    ejecutando = False

        VENTANA.fill(COLOR_FONDO)

        titulo = FUENTE_TEXTO.render(titulo_texto, True, BLANCO)
        VENTANA.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 80)))

        y_start = 170

        for i, jugador in enumerate(datos):
            username = jugador["username"]
            puntaje = jugador["puntaje"]

            if i < 3:
                linea = f"{medallas[i]}  {i+1}. {username} — {puntaje} pts"
            else:
                linea = f"{i+1}. {username} — {puntaje} pts"

            texto = FUENTE_LISTA.render(linea, True, BLANCO)
            rect = texto.get_rect(center=(ANCHO // 2, y_start + i * line_spacing))
            VENTANA.blit(texto, rect)

        pygame.draw.rect(VENTANA, NEGRO, boton_volver, border_radius=10)
        txt_volver = FUENTE_BOTON.render("Volver", True, BLANCO)
        VENTANA.blit(txt_volver, txt_volver.get_rect(center=boton_volver.center))

        pygame.display.update()
        reloj.tick(30)


# ==============================================================
#  MENÚ
# ==============================================================

def salon_de_la_fama():
    datos = obtener_puntajes_locales()
    mostrar_lista_puntajes(datos, "SALÓN DE LA FAMA")


if __name__ == "__main__":
    salon_de_la_fama()
