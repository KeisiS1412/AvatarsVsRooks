import pygame
from ShopPanel import ShopPanel

def main():
    pygame.init()
    res = (1280, 720)
    screen = pygame.display.set_mode(res)
    pygame.display.set_caption("Demo Selector de Torres (UI)")
    clock = pygame.time.Clock()

    shop = ShopPanel(res)
    running = True

    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            consumed, changed = shop.handle_event(event)
            if changed:
                print("Torre seleccionada:", shop.get_selected_type())

        screen.fill((18, 18, 22))
        shop.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
