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
        self.matrix.onGameOver = self.handleGameOver
        self.matrix.onNextScene = lambda: self.switchScene("next")
        self.coins = 0
        self.selectedRook = None

        self.shop = ShopPanel(self.res)

    def draw(self, screen):
        self.matrix.draw(screen)
        self.matrix.drawCoins(screen)
        self.shop.draw(screen)

        remaining = self.matrix.get_remaining_time()
        time_text = f"Tiempo: {remaining}s"
        text_surf = self.font.render(time_text, True, (255, 255, 255))
        
        # Posición: esquina superior derecha
        x = self.res[0] - text_surf.get_width() - 10
        y = 10
        screen.blit(text_surf, (x, y))

    def handleEvent(self, event):
        # 0) Tecla ESC para cancelar selección desde cualquier escena
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.shop.clear_selection()
            return

        # 0bis) Click derecho en cualquier parte: cancelar selección
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.shop.clear_selection()
            return

        # 1) Primero deja que el panel consuma el click si fue allí
        consumed, changed = self.shop.handle_event(event)
        if consumed:
            return

        # 2) Clicks sobre la matriz
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.matrix.rect.collidepoint(event.pos):

                # ★ PRIORIDAD MONEDAS: trata de recoger primero
                earned = self.matrix.detectCoinClick(event)
                if earned > 0:
                    self.coins += earned
                    # print(f"Coins: {self.coins}")
                    return  # ya usamos el click para moneda

                # Si no había moneda, entonces veamos si hay torre seleccionada
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
                    return  # click procesado

                # Sin torre seleccionada: tu flujo original de rook / otras acciones
                if self.selectedRook:
                    if self.selectedRook.cost < self.coins:
                        self.coins = self.coins - self.selectedRook.cost
                        self.matrix.addRook(event, self.selectedRook)


    def update(self, dt):
        self.matrix.update(dt)

    def handleGameOver(self):
        self.switchScene("login")
