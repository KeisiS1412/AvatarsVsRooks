import pygame
from PersonalizationScene import PersonalizationScene

pygame.init()
BASE_W, BASE_H = 1920, 1080
screen = pygame.display.set_mode((BASE_W, BASE_H))
clock = pygame.time.Clock()
font = pygame.font.Font("Avenir.ttf", 32)
scene = PersonalizationScene(font)

running = True
while running:
    dt = clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        scene.handleEvent(event)
    scene.update(dt)
    scene.draw(screen)
    pygame.display.flip()

pygame.quit()