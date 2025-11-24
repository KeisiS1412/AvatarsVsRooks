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

FUENTE_TEXTO = pygame.font.SysFont("Arial", 60)
FUENTE_BOTON = pygame.font.SysFont("Arial", 35)
FUENTE_LISTA = pygame.font.SysFont("Arial", 28)

# ==============================
# ARCHIVO LOCAL (ABSOLUTO)
# ==============================
CARPETA_RECURSOS = os.path.join(os.path.dirname(__file__), "Imagenes-sonidos")
ARCHIVO_FAMA = os.path.join(CARPETA_RECURSOS, "salon_fama.json")

# Crear si no existe
if not os.path.exists(ARCHIVO_FAMA):
    with open(ARCHIVO_FAMA, "w", encoding="utf-8") as f:
        json.dump([], f)


# ==============================
# GUARDAR TOP 5 (ELIMINA EXCESO)
# ==============================
from publicationManager import publicationManager

def guardar_en_fama(username, puntaje):
    """Guarda el puntaje, limita top 5, y publica SOLO si el top 5 cambia."""
    try:
        with open(ARCHIVO_FAMA, "r", encoding="utf-8") as f:
            datos_antes = json.load(f)
    except:
        datos_antes = []

    # Ordenarlos antes por puntaje
    datos_antes = sorted(datos_antes, key=lambda x: x["puntaje"], reverse=True)[:5]

    # Agregar nuevo puntaje
    nuevos_datos = datos_antes.copy()
    nuevos_datos.append({"username": username, "puntaje": puntaje})

    # Ordenar y mantener solo top 5
    nuevos_datos = sorted(nuevos_datos, key=lambda x: x["puntaje"], reverse=True)[:5]

    # === Detectar si el nuevo puntaje ALTERA el top 5 ===
    top_cambio = False

    # Caso 1: el top 5 tenía menos de 5 elementos, siempre cambia
    if len(datos_antes) < 5:
        top_cambio = True
    else:
        # Caso 2: comparar listas — si son diferentes, hubo cambio
        if nuevos_datos != datos_antes:
            # Confirmar que el nuevo puntaje es el responsable del cambio
            # Es decir: que realmente entró al top 5 o movió posiciones
            menor_antes = datos_antes[-1]["puntaje"]
            if puntaje > menor_antes:
                top_cambio = True

    # Guardar archivo final
    with open(ARCHIVO_FAMA, "w", encoding="utf-8") as f:
        json.dump(nuevos_datos, f, indent=4)

    # === Solo publicar si hubo cambio REAL del top 5 ===
    if top_cambio:
        scores = {item["username"]: item["puntaje"] for item in nuevos_datos}
        manager = publicationManager(scores)
        manager.makePosts()
        print("📢 PUBLICADO porque hubo un nuevo puntaje dentro del TOP 5.")
    else:
        print("ℹ️ No se publica porque el top 5 no cambió.")

# ==============================
# LEER PUNTAJES (YA TOP 5)
# ==============================
def obtener_puntajes_locales():
    try:
        with open(ARCHIVO_FAMA, "r", encoding="utf-8") as f:
            datos = json.load(f)
            # Aseguramos que si alguien editó el archivo, igual lo recortamos
            datos = sorted(datos, key=lambda x: x["puntaje"], reverse=True)[:5]
            return datos
    except:
        return []


# ==============================
# MOSTRAR LISTA
# ==============================
def mostrar_lista_puntajes(datos, titulo_texto="SALÓN DE LA FAMA"):
    reloj = pygame.time.Clock()
    boton_volver = pygame.Rect(ANCHO // 2 - 120, ALTO - 90, 240, 60)

    medallas = ["🥇", "🥈", "🥉"]

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

        # Título
        titulo = FUENTE_TEXTO.render(titulo_texto, True, BLANCO)
        VENTANA.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 80)))

        # Lista centrada
        y_start = 170

        if datos:
            for i, jugador in enumerate(datos):
                username = jugador.get("username", "Jugador")
                puntaje = jugador.get("puntaje", 0)

                if i < 3:
                    linea = f"{medallas[i]}  {i+1}. {username} — {puntaje} pts"
                else:
                    linea = f"{i+1}. {username} — {puntaje} pts"

                texto = FUENTE_LISTA.render(linea, True, BLANCO)
                rect = texto.get_rect(center=(ANCHO // 2, y_start + i * 40))
                VENTANA.blit(texto, rect)
        else:
            msg = FUENTE_LISTA.render("No hay puntajes registrados.", True, (255, 80, 80))
            VENTANA.blit(msg, msg.get_rect(center=(ANCHO // 2, ALTO // 2)))

        # Botón Volver
        pygame.draw.rect(VENTANA, NEGRO, boton_volver, border_radius=10)
        txt_volver = FUENTE_BOTON.render("Volver", True, BLANCO)
        VENTANA.blit(txt_volver, txt_volver.get_rect(center=boton_volver.center))

        pygame.display.update()
        reloj.tick(30)


# ==============================
# MENÚ SALÓN DE LA FAMA
# ==============================
def salon_de_la_fama():
    datos = obtener_puntajes_locales()

    # IMPORTANTE → Limpiar el archivo a ONLY top 5
    with open(ARCHIVO_FAMA, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

    mostrar_lista_puntajes(datos, "SALÓN DE LA FAMA")


# ==============================
# PRUEBA DIRECTA
# ==============================
if __name__ == "__main__":
    salon_de_la_fama()
