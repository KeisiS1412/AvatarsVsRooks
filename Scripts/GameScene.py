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
        self.matrix = Matrix(self.res, "easy")
        self.matrix.onGameOver = self.handleGameOver
        self.matrix.onNextScene = lambda: self.switchScene("next")
        self.coins = 0
        self.selectedRook = None
        self.shop = ShopPanel(self.res)
        self.pause = False

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
        if self.pause:
            self.drawPauseMenu(screen)
            

    def handleEvent(self, event):
        if not self.pause:
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
                    earned = self.matrix.detectCoinClick(event)  # ya suma a self.matrix.money
                    if earned > 0:
                        return  # ya usamos el click para moneda

                    # Si no había moneda, entonces veamos si hay torre seleccionada
                    tower_type = self.shop.get_selected_type()
                    if tower_type:
                        cell = self.matrix.calculateCell(event.pos)
                        if cell is not None:
                            row, col = cell
                            placed = self.matrix.try_place_tower(tower_type, row, col)
                            if placed:
                                # compra y colocación OK -> deseleccionar herramienta
                                self.shop.clear_selection()
                            # Si no se pudo (fondos/celda), puedes mostrar feedback aquí si quieres
                        return  # click procesado, no continues con otras acciones

                    # Sin torre seleccionada: tu flujo original de rook / otras acciones
                    if self.selectedRook:
                        cost = getattr(self.selectedRook, "cost", 0)
                        if self.matrix.money >= cost:
                            self.matrix.money -= cost
                            self.matrix.addRook(event, self.selectedRook)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.pause = not self.pause




    def update(self, dt):
        if self.pause:
            pass
        else:
            self.matrix.update(dt)

    def handleGameOver(self):
        self.switchScene("login")

    def setDifficulty(self, difficulty):
        self.difficulty = difficulty
        self.matrix = Matrix(self.res, difficulty)

    def drawPauseMenu(self, screen):
        overlay = pygame.Surface((300, 150), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # RGBA (negro con transparencia)
        screen.blit(overlay, (self.res[0]//2 -150, self.res[1]//2-75))
        rect = pygame.Rect(200, 150, 200, 100)
        rect.center = (self.res[0]//2, self.res[1]//2)
        pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=10)

        text = self.font.render("PAUSA", True, (0, 0, 0))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)