import pygame
from SceneManager import SceneManager
from LoginScene import LoginScene

pygame.init()

BASE_W, BASE_H = 1920, 1080

info = pygame.display.Info()
win_w, win_h = info.current_w, info.current_h
screen = pygame.display.set_mode((win_w, win_h), pygame.FULLSCREEN)
pygame.display.set_caption("Registro")

clock = pygame.time.Clock()
font = pygame.font.Font("Avenir.ttf", 32)
sceneManager = SceneManager(LoginScene(font))
bg = (240, 240, 240)
fps = 30
running = True

canvas = pygame.Surface((BASE_W, BASE_H))

while running:
    dt = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION) and hasattr(event, "pos"):
            x, y = event.pos
            lx = int(x * BASE_W / win_w)
            ly = int(y * BASE_H / win_h)
            event = pygame.event.Event(event.type, {**event.dict, "pos": (lx, ly)})

        sceneManager.handleEvent(event)

    sceneManager.update(dt)

    canvas.fill(bg)
    sceneManager.draw(canvas)
    scaled = pygame.transform.smoothscale(canvas, (win_w, win_h))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

pygame.quit()
