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
        self.matrix.onNextScene = self.switchScene
        self.matrix.onGameOver = self.handleGameOver
        self.coins = 0
        self.selectedRook = None
        self.shop = ShopPanel(self.res)
        self.pause = False
        self.client = None
        self.connected = False
        self.state = {"x": 0, "y": 0, "sand": 0, "fire":0, "rock":0, "water":0, "collect":0, "pause":0, "joystickButton":0}
        self.prevPause = 0
        self.prevCollect = 0
        self.prevX = 0
        self.prevY = 0
        self.prevArriba = 0
        self.prevAbajo = 0
        self.prevIzquierda = 0
        self.prevDerecha = 0

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



    def update(self, dt):
        new_state = self.client.ManageMessages()
        if new_state and new_state != self.state:
            self.state = new_state
            print(self.state)
        self.handleController(dt)
        if self.pause:
            pass
        else:
            self.matrix.update(dt)
        
    
    def handleController(self, dt):
        # --- Configuración de sensibilidad ---
        initial_delay = 500   # tiempo antes de repetir (segundos)
        repeat_rate = 300    # tiempo entre repeticiones sostenidas (segundos)

        # --- Inicializar variables si no existen ---
        if not hasattr(self, "x_timer"):
            self.x_timer = 0
            self.y_timer = 0
            self.x_held = False
            self.y_held = False

        # --- Pausa (flanco 0→1) ---
        if self.state["pause"] == 1 and self.prevPause == 0:
            self.pause = not self.pause
            print("Pausa:", self.pause)

        # --- Recolectar monedas ---
        if self.state["collect"] == 1 and self.prevCollect == 0:
            self.matrix.collectCoins()

        # ===============================
        # --- Movimiento en X ---
        # ===============================
        if self.state["x"] != 0:
            if self.state["x"] != self.prevX:
                # primer movimiento inmediato
                self.matrix.selector.moveX(self.state["x"])
                self.x_timer = 0
                self.x_held = True
            else:
                self.x_timer += dt
                if self.x_held:
                    if self.x_timer >= initial_delay:
                        # después del retardo inicial, mover cada repeat_rate
                        steps = int(self.x_timer // repeat_rate)
                        if steps > 0:
                            self.matrix.selector.moveX(self.state["x"])
                            self.x_timer -= steps * repeat_rate
        else:
            self.x_timer = 0
            self.x_held = False

        # ===============================
        # --- Movimiento en Y ---
        # ===============================
        if self.state["y"] != 0:
            if self.state["y"] != self.prevY:
                self.matrix.selector.moveY(self.state["y"])
                self.y_timer = 0
                self.y_held = True
            else:
                self.y_timer += dt
                if self.y_held:
                    if self.y_timer >= initial_delay:
                        steps = int(self.y_timer // repeat_rate)
                        if steps > 0:
                            self.matrix.selector.moveY(self.state["y"])
                            self.y_timer -= steps * repeat_rate
        else:
            self.y_timer = 0
            self.y_held = False

        # --- Posición del selector ---
        pos = self.matrix.calculateCell(self.matrix.selector.position)

        # --- Colocar torres ---
        if self.state["fire"] == 1 and self.prevArriba == 0:
            self.matrix.try_place_tower("fire", pos[0], pos[1])
        if self.state["water"] == 1 and self.prevAbajo == 0:
            self.matrix.try_place_tower("water", pos[0], pos[1])
        if self.state["sand"] == 1 and self.prevIzquierda == 0:
            self.matrix.try_place_tower("sand", pos[0], pos[1])
        if self.state["rock"] == 1 and self.prevDerecha == 0:
            self.matrix.try_place_tower("rock", pos[0], pos[1])
        if self.state.get("joystickButton", 0) == 1 and getattr(self, "prevJoystickButton", 0) == 0:
            self.matrix.shoot_from_selected_tower()

        # --- Actualizar previos ---
        self.prevPause = self.state["pause"]
        self.prevCollect = self.state["collect"]
        self.prevX = self.state["x"]
        self.prevY = self.state["y"]
        self.prevArriba = self.state["fire"]
        self.prevAbajo = self.state["water"]
        self.prevIzquierda = self.state["sand"]
        self.prevDerecha = self.state["rock"]
        self.prevJoystickButton = self.state.get("joystickButton", 0)

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

    def SetClient(self, client, connected):
        self.client = client
        self.connected = connected
