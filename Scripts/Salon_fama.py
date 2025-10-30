import pygame
import sys
import os
import json
import requests

pygame.init()

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
ANCHO, ALTO = 800, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
BLANCO, NEGRO = (255, 255, 255), (0, 0, 0)
COLOR_FONDO = (20, 20, 60)
FUENTE_TEXTO = pygame.font.SysFont("Arial", 60)
FUENTE_BOTON = pygame.font.SysFont("Arial", 35)
FUENTE_LISTA = pygame.font.SysFont("Arial", 28)

CARPETA_RECURSOS = os.path.join(os.path.dirname(__file__), "Imagenes-sonidos")
ARCHIVO_FAMA = os.path.join(CARPETA_RECURSOS, "salon_fama.json")


# ==============================
# GUARDAR Y ENVIAR PUNTAJES
# ==============================
def guardar_en_fama(username, puntaje):
    """Guarda el puntaje en un archivo JSON local."""
    if not os.path.exists(ARCHIVO_FAMA):
        datos = []
    else:
        with open(ARCHIVO_FAMA, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                datos = []

    # Agrega nuevo puntaje
    datos.append({"username": username, "puntaje": puntaje})
    # Ordena y mantiene los 10 mejores
    datos = sorted(datos, key=lambda x: x["puntaje"], reverse=True)[:10]

    # Guarda el archivo
    with open(ARCHIVO_FAMA, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)


def enviar_puntaje_al_servidor(username, puntaje):
    """Envía el nombre de usuario y el puntaje al servidor Node.js."""
    url = "http://localhost:3007/scoreboard"
    data = {"username": username, "score": puntaje}
    try:
        r = requests.post(url, json=data, timeout=5)
        if r.status_code == 200:
            print(f"Puntaje de {username} enviado correctamente ({puntaje} pts)")
        else:
            print(f" Error al guardar puntaje: {r.status_code} → {r.text}")
    except Exception as e:
        print("No se pudo conectar con el servidor:", e)


# ==============================
# FUNCIONES AUXILIARES
# ==============================
def obtener_puntajes_locales():
    """Lee el JSON local con puntajes guardados."""
    if os.path.exists(ARCHIVO_FAMA):
        with open(ARCHIVO_FAMA, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def obtener_puntajes_servidor():
    """Obtiene los puntajes desde el servidor Node.js."""
    url = "http://localhost:3007/scoreboard"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json().get("ok"):
            return r.json()["scores"]
    except Exception as e:
        print(" No se pudo conectar con el servidor:", e)
    return []


def mostrar_lista_puntajes(datos, titulo_texto):
    """Muestra la lista de puntajes en pantalla con un título."""
    reloj = pygame.time.Clock()
    boton_volver = pygame.Rect(ANCHO // 2 - 100, ALTO - 80, 200, 50)
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
        VENTANA.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))

        y = 150
        if datos:
            for i, jugador in enumerate(datos):
                username = jugador.get("username", "Jugador")
                puntaje = jugador.get("puntaje", jugador.get("score", 0))
                texto = FUENTE_LISTA.render(f"{i+1}. {username} — {puntaje} pts", True, BLANCO)
                VENTANA.blit(texto, (ANCHO // 2 - texto.get_width() // 2, y))
                y += 40
        else:
            mensaje = FUENTE_LISTA.render("No hay puntajes disponibles.", True, (200, 50, 50))
            VENTANA.blit(mensaje, (ANCHO // 2 - mensaje.get_width() // 2, ALTO // 2))

        pygame.draw.rect(VENTANA, NEGRO, boton_volver, border_radius=10)
        texto_volver = FUENTE_BOTON.render("Volver", True, BLANCO)
        VENTANA.blit(
            texto_volver,
            (boton_volver.centerx - texto_volver.get_width() // 2,
             boton_volver.centery - texto_volver.get_height() // 2),
        )

        pygame.display.update()
        reloj.tick(30)


# ==============================
# MENÚ PRINCIPAL DEL SALÓN
# ==============================
def salon_de_la_fama():
    """Permite elegir entre ver puntajes locales o del servidor."""
    reloj = pygame.time.Clock()
    boton_local = pygame.Rect(ANCHO // 2 - 250, ALTO // 2 - 40, 200, 60)
    boton_servidor = pygame.Rect(ANCHO // 2 + 50, ALTO // 2 - 40, 200, 60)
    boton_salir = pygame.Rect(ANCHO // 2 - 100, ALTO - 80, 200, 50)

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_local.collidepoint(evento.pos):
                    datos = obtener_puntajes_locales()
                    mostrar_lista_puntajes(datos, "PUNTAJES LOCALES")
                elif boton_servidor.collidepoint(evento.pos):
                    datos = obtener_puntajes_servidor()
                    mostrar_lista_puntajes(datos, "PUNTAJES DEL SERVIDOR")
                elif boton_salir.collidepoint(evento.pos):
                    ejecutando = False

        VENTANA.fill(COLOR_FONDO)
        titulo = FUENTE_TEXTO.render("SALÓN DE LA FAMA", True, BLANCO)
        VENTANA.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 80))

        # Dibujar botones
        pygame.draw.rect(VENTANA, NEGRO, boton_local, border_radius=10)
        pygame.draw.rect(VENTANA, NEGRO, boton_servidor, border_radius=10)
        pygame.draw.rect(VENTANA, NEGRO, boton_salir, border_radius=10)

        texto_local = FUENTE_BOTON.render("Locales", True, BLANCO)
        texto_servidor = FUENTE_BOTON.render("Servidor", True, BLANCO)
        texto_salir = FUENTE_BOTON.render("Volver", True, BLANCO)

        VENTANA.blit(texto_local, (boton_local.centerx - texto_local.get_width() // 2, boton_local.centery - texto_local.get_height() // 2))
        VENTANA.blit(texto_servidor, (boton_servidor.centerx - texto_servidor.get_width() // 2, boton_servidor.centery - texto_servidor.get_height() // 2))
        VENTANA.blit(texto_salir, (boton_salir.centerx - texto_salir.get_width() // 2, boton_salir.centery - texto_salir.get_height() // 2))

        pygame.display.update()
        reloj.tick(30)


# ==============================
# PRUEBA DIRECTA
# ==============================
if __name__ == "__main__":
    salon_de_la_fama()
