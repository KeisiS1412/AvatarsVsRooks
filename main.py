import pygame
from SceneManager import SceneManager
from LoginScene import LoginScene

pygame.init()
resolution = (1920, 1080)
screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
clock = pygame.time.Clock()
avenirFont = pygame.font.Font("Avenir.ttf", 32)
sceneManager = SceneManager(LoginScene(avenirFont))
backgroundColor = (240, 240, 240)
fps = 30
running = True

while running:
    deltaTime = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        sceneManager.handleEvent(event)

    sceneManager.update(deltaTime)
    screen.fill(backgroundColor)
    sceneManager.draw(screen)
    pygame.display.flip()

pygame.quit()