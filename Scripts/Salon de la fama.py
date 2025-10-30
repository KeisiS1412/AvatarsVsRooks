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
# FUNCIÓN PARA GUARDAR PUNTAJE
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
    datos = sorted(datos, key=lambda x: x["puntaje"], reverse=True)[:5]  # Top 10

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
    boton_salir = pygame.Rect(ANCHO // 2 - 100, ALTO - 80, 200, 50)
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_salir.collidepoint(evento.pos):
                    ejecutando = False

        VENTANA.fill((20, 20, 60))
        titulo = FUENTE_TEXTO.render("SALÓN DE LA FAMA", True, BLANCO)
        VENTANA.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))

        # Mostrar puntajes
        y = 150
        for i, jugador in enumerate(datos):
            texto = FUENTE_LISTA.render(
                f"{i+1}. {jugador['username']} — {jugador['puntaje']} pts", True, BLANCO
            )
            VENTANA.blit(texto, (ANCHO // 2 - texto.get_width() // 2, y))
            y += 40

        pygame.draw.rect(VENTANA, NEGRO, boton_salir, border_radius=10)
        texto_salir = FUENTE_BOTON.render("Volver", True, BLANCO)
        VENTANA.blit(
            texto_salir,
            (boton_salir.centerx - texto_salir.get_width() // 2,
             boton_salir.centery - texto_salir.get_height() // 2),
        )

        pygame.display.update()
        reloj.tick(30)


# ================================
# FUNCIÓN DE PANTALLA DE VICTORIA
# ================================
def pantalla_victoria(username="Jugador", puntaje=100):
    """Pantalla de victoria con dos botones"""
    ruta_sonido = os.path.join(CARPETA_RECURSOS, "victoria.mp3")
    sonido = pygame.mixer.Sound(ruta_sonido)
    sonido.play()

    frames = []
    for i in range(1, 5):
        ruta = os.path.join(CARPETA_RECURSOS, f"{i}.png")
        imagen = pygame.image.load(ruta).convert_alpha()
        imagen = pygame.transform.smoothscale(imagen, (200, 200))
        frames.append(imagen)

    frame_actual = 0
    contador_frame = 0
    reloj = pygame.time.Clock()

    # Botones
    boton_salir = pygame.Rect(ANCHO // 2 - 250, ALTO - 100, 200, 60)
    boton_fama = pygame.Rect(ANCHO // 2 + 50, ALTO - 100, 200, 60)

    guardar_en_fama(username, puntaje)

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_salir.collidepoint(evento.pos):
                    sonido.stop()
                    pygame.quit()
                    sys.exit()
                elif boton_fama.collidepoint(evento.pos):
                    sonido.stop()
                    salon_de_la_fama()

        VENTANA.fill(COLOR_VICTORIA)
        texto = FUENTE_TEXTO.render("¡VICTORIA!", True, BLANCO)
        VENTANA.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 60))

        # Animación
        VENTANA.blit(frames[frame_actual], (ANCHO // 2 - 100, ALTO // 2 - 100))
        contador_frame += 1
        if contador_frame >= 10:
            frame_actual = (frame_actual + 1) % len(frames)
            contador_frame = 0

        # Botones
        pygame.draw.rect(VENTANA, NEGRO, boton_salir, border_radius=10)
        pygame.draw.rect(VENTANA, NEGRO, boton_fama, border_radius=10)

        texto_salir = FUENTE_BOTON.render("Salir", True, BLANCO)
        texto_fama = FUENTE_BOTON.render("Salón de la Fama", True, BLANCO)

        VENTANA.blit(
            texto_salir,
            (boton_salir.centerx - texto_salir.get_width() // 2,
             boton_salir.centery - texto_salir.get_height() // 2),
        )
        VENTANA.blit(
            texto_fama,
            (boton_fama.centerx - texto_fama.get_width() // 2,
             boton_fama.centery - texto_fama.get_height() // 2),
        )

        pygame.display.update()
        reloj.tick(30)


# ================================
# PROGRAMA PRINCIPAL DE PRUEBA
# ================================
def main():
    usuario = input("Ingrese su nombre de jugador: ")
    puntaje = int(input("Ingrese su puntaje: "))
    pantalla_victoria(usuario, puntaje)


if __name__ == "__main__":
    main()
