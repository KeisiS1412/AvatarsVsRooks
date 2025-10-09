import pygame
from Buttons import Button

class ImageButton(Button):
    def __init__(self, x, y, imagePath, scale=1.0, clickedImagePath=None):
        originalImage = pygame.image.load(imagePath).convert_alpha()
        originalSize = originalImage.get_size()
        scaledSize = (int(originalSize[0] * scale), int(originalSize[1] * scale))
        super().__init__(x, y, scaledSize[0], scaledSize[1], "", None, None, None)

        self.image = pygame.transform.scale(originalImage, scaledSize)
        if clickedImagePath:
            clickedRaw = pygame.image.load(clickedImagePath).convert_alpha()
            self.clickedImage = pygame.transform.scale(clickedRaw, scaledSize)
        else:
            self.clickedImage = self.image

        self.currentImage = self.image
        self.clicked = False

    def draw(self, screen, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        screen.blit(self.currentImage, adjRect)

    def update(self, mousePos=None, scrollOffset=0):
        pass  # No necesitamos hover

    def handleClick(self):
        self.clicked = not self.clicked
        self.currentImage = self.clickedImage if self.clicked else self.image

    def wasClicked(self, event, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        if event.type == pygame.MOUSEBUTTONDOWN and adjRect.collidepoint(event.pos):
            self.handleClick()
            return True
        return False


