import pygame
import sys
import os
import json

pygame.init()

# ================================
# CONFIGURACIÓN GENERAL
# ================================
ANCHO, ALTO = 800, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pantallas de Victoria y Derrota")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
COLOR_VICTORIA = (120, 30, 30)
COLOR_DERROTA = (40, 120, 40)

# Fuentes
FUENTE_TEXTO = pygame.font.SysFont("Arial", 60)
FUENTE_BOTON = pygame.font.SysFont("Arial", 35)
FUENTE_LISTA = pygame.font.SysFont("Arial", 28)

# Carpeta de recursos
CARPETA_RECURSOS = os.path.join(os.path.dirname(__file__), "Imagenes-sonidos")
ARCHIVO_FAMA = os.path.join(CARPETA_RECURSOS, "salon_fama.json")


# ================================
# FUNCIÓN PARA GUARDAR EN SALÓN DE LA FAMA
# ================================
def guardar_en_fama(username, puntaje):
    """Guarda el puntaje en un archivo JSON"""
    if not os.path.exists(ARCHIVO_FAMA):
        datos = []
    else:
        with open(ARCHIVO_FAMA, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                datos = []

    datos.append({"username": username, "puntaje": puntaje})
    datos = sorted(datos, key=lambda x: x["puntaje"], reverse=True)[:10]  # top 10

    with open(ARCHIVO_FAMA, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)


# ================================
# FUNCIÓN PARA MOSTRAR EL SALÓN DE LA FAMA
# ================================
def salon_de_la_fama():
    """Muestra los mejores puntajes"""
    if os.path.exists(ARCHIVO_FAMA):
        with open(ARCHIVO_FAMA, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                datos = []
    else:
        datos = []

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

        VENTANA.fill((20, 20, 60))
        titulo = FUENTE_TEXTO.render("SALÓN DE LA FAMA", True, BLANCO)
        VENTANA.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))

        y = 150
        for i, jugador in enumerate(datos):
            texto = FUENTE_LISTA.render(
                f"{i+1}. {jugador['username']} — {jugador['puntaje']} pts", True, BLANCO
            )
            VENTANA.blit(texto, (ANCHO // 2 - texto.get_width() // 2, y))
            y += 40

        pygame.draw.rect(VENTANA, NEGRO, boton_volver, border_radius=10)
        texto_volver = FUENTE_BOTON.render("Volver", True, BLANCO)
        VENTANA.blit(
            texto_volver,
            (boton_volver.centerx - texto_volver.get_width() // 2,
             boton_volver.centery - texto_volver.get_height() // 2),
        )

        pygame.display.update()
        reloj.tick(30)


# ================================
# FUNCIÓN GENÉRICA PARA CARGAR ANIMACIONES
# ================================
def cargar_animacion(prefix, cantidad_frames, tam_x, tam_y):
    """Carga imágenes 1.png, 2.png... o 1Game.png, 2Game.png... según el prefijo"""
    frames = []
    for i in range(1, cantidad_frames + 1):
        ruta = os.path.join(CARPETA_RECURSOS, f"{i}{prefix}.png")
        if os.path.exists(ruta):
            imagen = pygame.image.load(ruta).convert_alpha()
            imagen = pygame.transform.smoothscale(imagen, (tam_x, tam_y))
            frames.append(imagen)
        else:
            print(f" No se encontró: {ruta}")
    return frames


# ================================
# PANTALLA DE VICTORIA
# ================================
def pantalla_victoria(username="Jugador", puntaje=100):
    # ---------- SONIDO ----------
    ruta_sonido = os.path.join(CARPETA_RECURSOS, "victoria.mp3")
    if os.path.exists(ruta_sonido):
        sonido = pygame.mixer.Sound(ruta_sonido)
        sonido.play()

    # ---------- ANIMACIÓN ----------
    frames_victoria = cargar_animacion("", 4, 200, 200)
    frame_actual = 0
    contador_frame = 0
    reloj = pygame.time.Clock()

    # ---------- BOTONES ----------
    boton_continuar = pygame.Rect(ANCHO // 2 - 250, ALTO - 100, 200, 60)
    boton_fama = pygame.Rect(ANCHO // 2 + 50, ALTO - 100, 200, 60)

    guardar_en_fama(username, puntaje)

    # ---------- LOOP PRINCIPAL ----------
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_continuar.collidepoint(evento.pos):
                    sonido.stop()
                    ejecutando = False
                elif boton_fama.collidepoint(evento.pos):
                    sonido.stop()
                    salon_de_la_fama()

        VENTANA.fill(COLOR_VICTORIA)
        texto = FUENTE_TEXTO.render("¡VICTORIA!", True, BLANCO)
        VENTANA.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 60))

        if frames_victoria:
            VENTANA.blit(frames_victoria[frame_actual], (ANCHO // 2 - 100, ALTO // 2 - 100))
            contador_frame += 1
            if contador_frame >= 10:
                frame_actual = (frame_actual + 1) % len(frames_victoria)
                contador_frame = 0

        # Botones
        pygame.draw.rect(VENTANA, NEGRO, boton_continuar, border_radius=10)
        pygame.draw.rect(VENTANA, NEGRO, boton_fama, border_radius=10)

        texto_continuar = FUENTE_BOTON.render("Continuar", True, BLANCO)
        texto_fama = FUENTE_BOTON.render("Salón de la Fama", True, BLANCO)

        VENTANA.blit(
            texto_continuar,
            (boton_continuar.centerx - texto_continuar.get_width() // 2,
             boton_continuar.centery - texto_continuar.get_height() // 2),
        )
        VENTANA.blit(
            texto_fama,
            (boton_fama.centerx - texto_fama.get_width() // 2,
             boton_fama.centery - texto_fama.get_height() // 2),
        )

        pygame.display.update()
        reloj.tick(30)


# ================================
# PANTALLA DE DERROTA
# ================================
def pantalla_derrota():
    ruta_sonido = os.path.join(CARPETA_RECURSOS, "gameover.mp3")
    if os.path.exists(ruta_sonido):
        sonido = pygame.mixer.Sound(ruta_sonido)
        sonido.play()

    frames_derrota = cargar_animacion("Game", 4, 300, 150)
    frame_actual = 0
    contador_frame = 0
    reloj = pygame.time.Clock()
    boton_rect = pygame.Rect(ANCHO // 2 - 100, ALTO - 100, 200, 60)
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_rect.collidepoint(evento.pos):
                    ejecutando = False

        VENTANA.fill(COLOR_DERROTA)
        if frames_derrota:
            VENTANA.blit(frames_derrota[frame_actual], (ANCHO // 2 - 150, ALTO // 2 - 100))
            contador_frame += 1
            if contador_frame >= 10:
                frame_actual = (frame_actual + 1) % len(frames_derrota)
                contador_frame = 0

        pygame.draw.rect(VENTANA, NEGRO, boton_rect, border_radius=10)
        texto_boton = FUENTE_BOTON.render("Continuar", True, BLANCO)
        VENTANA.blit(
            texto_boton,
            (boton_rect.centerx - texto_boton.get_width() // 2,
             boton_rect.centery - texto_boton.get_height() // 2),
        )
        pygame.display.update()
        reloj.tick(30)


