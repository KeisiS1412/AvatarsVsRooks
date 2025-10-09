import pygame
from PersonalizationScene import PersonalizationScene

pygame.init()

BASE_W, BASE_H = 1920, 1080

# Detecta tamaño inicial de ventana y permite redimensionar
info = pygame.display.Info()
screen_w, screen_h = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_w, screen_h), pygame.RESIZABLE)
pygame.display.set_caption("Avatars vs Rooks - Personalización")

# Superficie base donde todo se dibuja
base_surface = pygame.Surface((BASE_W, BASE_H))

clock = pygame.time.Clock()
font = pygame.font.Font("Avenir.ttf", 32)
scene = PersonalizationScene(font)

def to_base_coords(pos_window):
    """Convierte (x,y) de la ventana a coordenadas base 1920x1080."""
    xw, yw = pos_window
    # factores de ventana->base
    sx = BASE_W / max(screen_w, 1)
    sy = BASE_H / max(screen_h, 1)
    return (int(xw * sx), int(yw * sy))

running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            # actualizar tamaño de ventana
            screen_w, screen_h = event.w, event.h
            screen = pygame.display.set_mode((screen_w, screen_h), pygame.RESIZABLE)

        # Re-mapear eventos con posición a coords base
        elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            bx, by = to_base_coords(event.pos)
            # recrear evento con la nueva pos, preservando atributos
            if event.type == pygame.MOUSEMOTION:
                event = pygame.event.Event(
                    pygame.MOUSEMOTION,
                    {"pos": (bx, by), "rel": event.rel, "buttons": event.buttons, "touch": getattr(event, "touch", False), "window": getattr(event, "window", None)}
                )
            else:  # BUTTONDOWN / BUTTONUP
                event = pygame.event.Event(
                    event.type,
                    {"pos": (bx, by), "button": event.button, "touch": getattr(event, "touch", False), "window": getattr(event, "window", None)}
                )

        # Pasar SIEMPRE el evento (ya mapeado si tenía pos)
        scene.handleEvent(event)

    scene.update(dt)

    # LIMPIA y dibuja en la base
    base_surface.fill((0, 0, 0))  # o tu color de fondo
    scene.draw(base_surface)

    # Escala la base a la ventana actual
    scaled = pygame.transform.smoothscale(base_surface, (screen_w, screen_h))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

pygame.quit()
