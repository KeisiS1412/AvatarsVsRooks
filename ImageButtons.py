import pygame
from Buttons import Button  # Asumiendo que Button está en Buttons.py

import pygame

class ImageButton(Button):
    def __init__(self, x, y, imagePath, scale=1.0, hoverImagePath=None):
        originalImage = pygame.image.load(imagePath).convert_alpha()
        originalSize = originalImage.get_size()
        scaledSize = (int(originalSize[0] * scale), int(originalSize[1] * scale))

        super().__init__(x, y, scaledSize[0], scaledSize[1], "", None, None, None)

        self.image = pygame.transform.scale(originalImage, scaledSize)

        if hoverImagePath:
            hoverRaw = pygame.image.load(hoverImagePath).convert_alpha()
            self.hoverImage = pygame.transform.scale(hoverRaw, scaledSize)
        else:
            self.hoverImage = self.image

        self.currentImage = self.image

    def draw(self, screen):
        screen.blit(self.currentImage, self.rect)

    def update(self, mousePos):
        self.currentImage = self.hoverImage if self.rect.collidepoint(mousePos) else self.image
