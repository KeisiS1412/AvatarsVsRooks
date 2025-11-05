import pygame
from LoginScene import LoginScene
from PersonalizationScene import PersonalizationScene
from SceneManager import SceneManager

"""Archivo principal del programa. Gestiona la ventana, escenas y ciclo principal del juego."""

pygame.init()

BASE_W, BASE_H = 1920, 1080  # Resolución base

info = pygame.display.Info()
win_w, win_h = info.current_w, info.current_h
screen = pygame.display.set_mode((win_w, win_h))
pygame.display.set_caption("Login")

clock = pygame.time.Clock()
font = pygame.font.Font("Assets/Avenir.ttf", 32)
sceneManager = SceneManager(font, (BASE_W, BASE_H))
bg = (218, 41, 28)
fps = 30
running = True

canvas = pygame.Surface((BASE_W, BASE_H))

while running:  # Ciclo principal del programa
    dt = clock.tick(fps)

    for event in pygame.event.get():  # Manejo de eventos
        if event.type == pygame.QUIT:
            running = False

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION) and hasattr(event, "pos"):
            x, y = event.pos
            lx = int(x * BASE_W / win_w)
            ly = int(y * BASE_H / win_h)
            event = pygame.event.Event(event.type, {**event.dict, "pos": (lx, ly)})  # Ajusta la posición del mouse

        sceneManager.handleEvent(event)  # Envía los eventos a la escena actual

    sceneManager.update(dt)  # Actualiza la lógica de la escena

    canvas.fill(bg)
    sceneManager.draw(canvas)
    scaled = pygame.transform.smoothscale(canvas, (win_w, win_h))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()  # Actualiza la pantalla

pygame.quit()  # Cierra Pygame
