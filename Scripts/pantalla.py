import pygame
import sys
import os
import json

pygame.init()

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
info = pygame.display.Info()
ANCHO, ALTO = info.current_w, info.current_h
VENTANA = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption("Pantallas del Juego")

# ==============================
# PALETA DE COLORES
# ==============================
COLOR_FONDO = (10, 10, 25)
COLOR_TEXTO = (240, 240, 240)
COLOR_TITULO = (230, 180, 50)
COLOR_BOTON = (30, 30, 50)
COLOR_BOTON_SALIR = (150, 30, 30)
COLOR_BOTON_TEXTO = (255, 255, 255)

# ==============================
# FUENTES
# ==============================
FUENTE_TITULO = pygame.font.SysFont("Arial", int(ALTO * 0.10))
FUENTE_SUB = pygame.font.SysFont("Arial", int(ALTO * 0.06))
FUENTE_LISTA = pygame.font.SysFont("Arial", int(ALTO * 0.045))
FUENTE_BOTON = pygame.font.SysFont("Arial", int(ALTO * 0.05))

# ==============================
# ARCHIVOS
# ==============================
CARPETA = os.path.join(os.path.dirname(__file__), "Imagenes-sonidos")
ARCHIVO_FAMA = os.path.join(CARPETA, "salon_fama.json")

if not os.path.exists(ARCHIVO_FAMA):
    with open(ARCHIVO_FAMA, "w", encoding="utf-8") as f:
        json.dump([], f)


# ============================================================
# SALÓN DE LA FAMA
# ============================================================
def guardar_en_fama(username, puntaje):
    try:
        with open(ARCHIVO_FAMA, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except:
        datos = []

    datos.append({"username": username, "puntaje": puntaje})
    datos = sorted(datos, key=lambda x: x["puntaje"], reverse=True)[:5]

    with open(ARCHIVO_FAMA, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)


def obtener_puntajes_locales():
    try:
        with open(ARCHIVO_FAMA, "r", encoding="utf-8") as f:
            datos = json.load(f)
            datos = sorted(datos, key=lambda x: x["puntaje"], reverse=True)[:5]
            return datos
    except:
        return []


def mostrar_lista_puntajes(datos):
    reloj = pygame.time.Clock()
    boton_volver = pygame.Rect(ANCHO//2 - 200, ALTO - 150, 400, 90)
    medallas = ["🥇", "🥈", "🥉"]

    ejecutando = True
    while ejecutando:

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN and boton_volver.collidepoint(e.pos):
                ejecutando = False

        VENTANA.fill(COLOR_FONDO)

        titulo = FUENTE_TITULO.render("SALÓN DE LA FAMA", True, COLOR_TITULO)
        VENTANA.blit(titulo, titulo.get_rect(center=(ANCHO//2, 120)))

        y = 250
        for i, j in enumerate(datos):
            icono = medallas[i] if i < 3 else f"{i+1}."
            linea = f"{icono}  {j['username']} — {j['puntaje']} pts"
            render = FUENTE_LISTA.render(linea, True, COLOR_TEXTO)
            VENTANA.blit(render, render.get_rect(center=(ANCHO//2, y)))
            y += 60

        pygame.draw.rect(VENTANA, COLOR_BOTON, boton_volver, border_radius=15)
        btn_text = FUENTE_BOTON.render("Volver", True, COLOR_BOTON_TEXTO)
        VENTANA.blit(btn_text, btn_text.get_rect(center=boton_volver.center))

        pygame.display.update()
        reloj.tick(30)


def salon_de_la_fama():
    datos = obtener_puntajes_locales()
    mostrar_lista_puntajes(datos)


# ============================================================
# CARGAR ANIMACIÓN
# ============================================================
def cargar_frames(lista_archivos):
    frames = []
    for archivo in lista_archivos:
        ruta = os.path.join(CARPETA, archivo)
        if os.path.exists(ruta):
            img = pygame.image.load(ruta).convert()
            img = pygame.transform.scale(img, (ANCHO, ALTO))
            frames.append(img)
    return frames


# ============================================================
#  PANTALLA DE VICTORIA (con sonido restaurado)
# ============================================================
def pantalla_victoria(username, puntaje):

    # Música de victoria
    ruta_audio = os.path.join(CARPETA, "victoria.mp3")
    if os.path.exists(ruta_audio):
        pygame.mixer.music.load(ruta_audio)
        pygame.mixer.music.play()

    frames = cargar_frames(["1.png", "2.png", "3.png", "4.png"])
    frame_index = 0
    clock = pygame.time.Clock()

    boton_fama = pygame.Rect(ANCHO//2 - 220, int(ALTO*0.70), 440, 90)
    boton_salir = pygame.Rect(ANCHO//2 - 220, int(ALTO*0.82), 440, 90)

    while True:

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                if boton_fama.collidepoint(e.pos):
                    pygame.mixer.music.stop()
                    salon_de_la_fama()

                if boton_salir.collidepoint(e.pos):
                    pygame.mixer.music.stop()
                    pygame.quit()
                    sys.exit()

        VENTANA.blit(frames[frame_index], (0, 0))
        frame_index = (frame_index + 1) % len(frames)

        titulo = FUENTE_TITULO.render("¡VICTORIA!", True, COLOR_TITULO)
        VENTANA.blit(titulo, titulo.get_rect(center=(ANCHO//2, int(ALTO*0.18))))

        sub = FUENTE_SUB.render(f"{username} — {puntaje} pts", True, COLOR_TEXTO)
        VENTANA.blit(sub, sub.get_rect(center=(ANCHO//2, int(ALTO*0.32))))

        pygame.draw.rect(VENTANA, COLOR_BOTON, boton_fama, border_radius=20)
        pygame.draw.rect(VENTANA, COLOR_BOTON_SALIR, boton_salir, border_radius=20)

        txt_fama = FUENTE_BOTON.render("Salón de la Fama", True, COLOR_BOTON_TEXTO)
        txt_salir = FUENTE_BOTON.render("Salir", True, COLOR_BOTON_TEXTO)

        VENTANA.blit(txt_fama, txt_fama.get_rect(center=boton_fama.center))
        VENTANA.blit(txt_salir, txt_salir.get_rect(center=boton_salir.center))

        pygame.display.update()
        clock.tick(8)


# ============================================================
#  PANTALLA DE DERROTA (con sonido restaurado)
# ============================================================
def pantalla_derrota(username):

    ruta_audio = os.path.join(CARPETA, "derrota.mp3")
    if os.path.exists(ruta_audio):
        pygame.mixer.music.load(ruta_audio)
        pygame.mixer.music.play()

    frames = cargar_frames(["1Game.png", "2Game.png", "3Game.png", "4Game.png"])
    frame_index = 0
    clock = pygame.time.Clock()

    boton_fama = pygame.Rect(ANCHO//2 - 220, int(ALTO*0.70), 440, 90)
    boton_salir = pygame.Rect(ANCHO//2 - 220, int(ALTO*0.82), 440, 90)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                if boton_fama.collidepoint(e.pos):
                    pygame.mixer.music.stop()
                    salon_de_la_fama()

                if boton_salir.collidepoint(e.pos):
                    pygame.mixer.music.stop()
                    pygame.quit()
                    sys.exit()

        VENTANA.blit(frames[frame_index], (0, 0))
        frame_index = (frame_index + 1) % len(frames)

        titulo = FUENTE_TITULO.render("DERROTA", True, COLOR_TITULO)
        VENTANA.blit(titulo, titulo.get_rect(center=(ANCHO//2, int(ALTO*0.18))))

        sub = FUENTE_SUB.render(f"Ánimo {username}, ¡puedes mejorar!", True, COLOR_TEXTO)
        VENTANA.blit(sub, sub.get_rect(center=(ANCHO//2, int(ALTO*0.32))))

        pygame.draw.rect(VENTANA, COLOR_BOTON, boton_fama, border_radius=20)
        pygame.draw.rect(VENTANA, COLOR_BOTON_SALIR, boton_salir, border_radius=20)

        txt_fama = FUENTE_BOTON.render("Salón de la Fama", True, COLOR_BOTON_TEXTO)
        txt_salir = FUENTE_BOTON.render("Salir", True, COLOR_BOTON_TEXTO)

        VENTANA.blit(txt_fama, txt_fama.get_rect(center=boton_fama.center))
        VENTANA.blit(txt_salir, txt_salir.get_rect(center=boton_salir.center))

        pygame.display.update()
        clock.tick(8)


# ============================================================
# MAIN PARA PROBAR (V y D)
# ============================================================
if __name__ == "__main__":
    while True:
        VENTANA.fill(COLOR_FONDO)

        msg = FUENTE_LISTA.render("Presiona V (Victoria), D (Derrota) o ESC para salir", True, COLOR_TEXTO)
        VENTANA.blit(msg, msg.get_rect(center=(ANCHO//2, ALTO//2)))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if e.key == pygame.K_v:
                    pantalla_victoria("JugadorTest", 1234)

                if e.key == pygame.K_d:
                    pantalla_derrota("JugadorTest")

        pygame.display.update()
