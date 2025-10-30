import pygame
import sys
import os
from Salon_fama import guardar_en_fama, enviar_puntaje_al_servidor, salon_de_la_fama

pygame.init()

# ================================
# CONFIGURACIÓN GENERAL
# ================================
ANCHO, ALTO = 800, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pantallas del Juego: Victoria, Derrota y Salón de la Fama")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
COLOR_VICTORIA = (120, 30, 30)
COLOR_DERROTA = (40, 120, 40)

# Fuentes
FUENTE_TEXTO = pygame.font.SysFont("Arial", 60)
FUENTE_BOTON = pygame.font.SysFont("Arial", 35)

# Carpeta de recursos
CARPETA_RECURSOS = os.path.join(os.path.dirname(__file__), "Imagenes-sonidos")


# ================================
# FUNCIÓN PARA CARGAR ANIMACIONES
# ================================
def cargar_animacion(prefijo, cantidad_frames, tam_x, tam_y):
    """Carga imágenes 1.png, 2.png... o 1Game.png, 2Game.png... según el prefijo"""
    frames = []
    for i in range(1, cantidad_frames + 1):
        ruta = os.path.join(CARPETA_RECURSOS, f"{i}{prefijo}.png")
        if os.path.exists(ruta):
            imagen = pygame.image.load(ruta).convert_alpha()
            imagen = pygame.transform.smoothscale(imagen, (tam_x, tam_y))
            frames.append(imagen)
    return frames


# ================================
# PANTALLA DE VICTORIA
# ================================
def pantalla_victoria(username="Jugador", puntaje=100):
    """Pantalla de victoria: guarda y envía puntaje, con opción a Salón de la Fama"""
    ruta_sonido = os.path.join(CARPETA_RECURSOS, "victoria.mp3")
    sonido = None
    if os.path.exists(ruta_sonido):
        sonido = pygame.mixer.Sound(ruta_sonido)
        sonido.play()

    frames = cargar_animacion("", 4, 200, 200)
    frame_actual = 0
    contador_frame = 0
    reloj = pygame.time.Clock()

    boton_continuar = pygame.Rect(ANCHO // 2 - 250, ALTO - 100, 200, 60)
    boton_fama = pygame.Rect(ANCHO // 2 + 50, ALTO - 100, 200, 60)

    # Guardar localmente y enviar al servidor
    guardar_en_fama(username, puntaje)
    enviar_puntaje_al_servidor(username, puntaje)

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                # Botón "Continuar"
                if boton_continuar.collidepoint(evento.pos):
                    if sonido:
                        sonido.stop()
                    ejecutando = False
                # Botón "Salón de la Fama"
                elif boton_fama.collidepoint(evento.pos):
                    if sonido:
                        sonido.stop()
                    salon_de_la_fama()

        # Fondo y título
        VENTANA.fill(COLOR_VICTORIA)
        texto = FUENTE_TEXTO.render("¡VICTORIA!", True, BLANCO)
        VENTANA.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 60))

        # Animación
        if frames:
            VENTANA.blit(frames[frame_actual], (ANCHO // 2 - 100, ALTO // 2 - 100))
            contador_frame += 1
            if contador_frame >= 10:
                frame_actual = (frame_actual + 1) % len(frames)
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
    """Pantalla de derrota con animación y botón de continuar"""
    ruta_sonido = os.path.join(CARPETA_RECURSOS, "gameover.mp3")
    sonido = None
    if os.path.exists(ruta_sonido):
        sonido = pygame.mixer.Sound(ruta_sonido)
        sonido.play()

    frames = cargar_animacion("Game", 4, 300, 150)
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
                    if sonido:
                        sonido.stop()
                    ejecutando = False

        VENTANA.fill(COLOR_DERROTA)
        if frames:
            VENTANA.blit(frames[frame_actual], (ANCHO // 2 - 150, ALTO // 2 - 100))
            contador_frame += 1
            if contador_frame >= 10:
                frame_actual = (frame_actual + 1) % len(frames)
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


# ================================
# PRUEBA DIRECTA
# ================================
if __name__ == "__main__":
    usuario = input("Nombre del jugador: ")
    puntaje = int(input("Puntaje obtenido: "))
    pantalla_victoria(usuario, puntaje)
