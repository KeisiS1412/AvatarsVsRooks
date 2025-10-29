import pygame
from Scene import Scene
from ui.ShopPanel import ShopPanel
from Matrix import Matrix
from towers.TowerFactory import TowerFactory

"""Escena de juego con matriz, monedas y panel de torres."""
class GameScene(Scene):
    def __init__(self, font, res, switchSceneCallback):
        self.switchScene = switchSceneCallback
        self.res = res
        self.font = font

        self.matrix = Matrix(self.res)
        self.coins = 0
        self.selectedRook = None

        self.shop = ShopPanel(self.res)

    def draw(self, screen):
        self.matrix.draw(screen)
        self.matrix.drawCoins(screen)
        self.shop.draw(screen)

    def handleEvent(self, event):
        consumed, changed = self.shop.handle_event(event)
        if consumed:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.matrix.rect.collidepoint(event.pos):
                tower_type = self.shop.get_selected_type()

                if tower_type:
                    cell = self.matrix.calculateCell(event.pos)
                    if cell is not None:
                        row, col = cell
                        if self.matrix.can_place_tower(row, col):
                            cell_topleft = self.matrix.cell_to_pixel(row, col)
                            tower = TowerFactory.create_tower(
                                tower_type, self.matrix.cellSize, cell_topleft, row, col
                            )
                            if tower:
                                self.matrix.add_tower_instance(row, col, tower)
                    return

                if self.selectedRook:
                    if self.selectedRook.cost < self.coins:
                        self.coins = self.coins - self.selectedRook.cost
                        self.matrix.addRook(event, self.selectedRook)
                else:
                    earned = self.matrix.detectCoinClick(event)
                    self.coins += earned
                    if earned > 0:
                        print(f"Coins: {self.coins}")

    def update(self, dt):
        self.matrix.update(dt)
