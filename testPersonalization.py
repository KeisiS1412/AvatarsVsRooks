import pygame
from PersonalizationScene import PersonalizationScene

pygame.init()
pygame.font.init()

# Resolución de la ventana
BASE_W, BASE_H = 1920, 1080
res = (BASE_W, BASE_H)

screen = pygame.display.set_mode(res)
pygame.display.set_caption("Test PersonalizationScene")
clock = pygame.time.Clock()

font = pygame.font.Font("Avenir.ttf", 32)

def dummy_switch(name, shared=None):
    print(f"➡ Cambio de escena a: {name} | shared={shared}")

scene = PersonalizationScene(font, res, dummy_switch)

running = True
while running:
    dt = clock.tick(60)  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        scene.handleEvent(event)


    scene.update(dt)


    screen.fill((0, 0, 0))      # o deja que la escena pinte su fondo
    scene.draw(screen)
    pygame.display.flip()


pygame.quit()
