import pygame
from Scene import Scene
from ui.ShopPanel import ShopPanel
from Matrix import Matrix
from towers.TowerFactory import TowerFactory

def _mul_color(c, f):  
    r = max(0, min(255, int(c[0] * f)))  
    g = max(0, min(255, int(c[1] * f)))  
    b = max(0, min(255, int(c[2] * f)))  
    return (r, g, b)  


def _hex_to_rgb(hex_str):  
    if not isinstance(hex_str, str):  
        return None  
    h = hex_str.strip().lstrip("#")  
    if len(h) != 6:  
        return None  
    try:  
        r = int(h[0:2], 16)  
        g = int(h[2:4], 16)  
        b = int(h[4:6], 16)  
        return (r, g, b)  
    except Exception:  
        return None  


def _pick_fg(bg):  
    """Devuelve blanco o negro según la luminosidad del fondo."""  
    r, g, b = bg  
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b  
    return (0, 0, 0) if lum > 140 else (255, 255, 255)  

THEME_NAMES = ["Dark", "Default", "Bright"]  
THEME_MULTS = [0.45, 1.00, 1.35]  

def _mul_color(c, f):  
    r = max(0, min(255, int(c[0] * f)))  
    g = max(0, min(255, int(c[1] * f)))  
    b = max(0, min(255, int(c[2] * f)))  
    return (r, g, b)  

def _hex_to_rgb(hex_str):  
    if not isinstance(hex_str, str):  
        return None  
    h = hex_str.strip().lstrip("#")  
    if len(h) != 6:  
        return None  
    try:  
        r = int(h[0:2], 16)  
        g = int(h[2:4], 16)  
        b = int(h[4:6], 16)  
        return (r, g, b)  
    except Exception:  
        return None  

def _lum(c):  
    r, g, b = c  
    return 0.2126 * r + 0.7152 * g + 0.0722 * b  

def _is_dark(c):  
    return _lum(c) < 140  


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
        self.theme_bg = (218, 41, 28)      
        self.theme_ui = _mul_color(self.theme_bg, 0.88)              
        self.theme_fg = _pick_fg(self.theme_bg)                       
        self._load_theme_from_user()        

    def _load_theme_from_user(self):
        """Carga color y tema desde el usuario en sesión."""
        try:
            from session import get_current_user
            user = get_current_user()
        except Exception as e:
            print(f"[GameScene] No se pudo leer usuario para tema: {e}")
            return

        if not isinstance(user, dict):
            return

        perfil = user.get("perfil") or {}

        # Color base guardado en Personalization 
        saved_color = perfil.get("color_preferido")
        rgb = _hex_to_rgb(saved_color) if saved_color else None
        if rgb is None:
            return

        # Tema guardado
        saved_theme = perfil.get("tema_preferido") or "Default"
        try:
            t_index = THEME_NAMES.index(saved_theme)
        except ValueError:
            t_index = 1  # Default

        k = THEME_MULTS[t_index]

        base = rgb
        bg = _mul_color(base, k)
        ui = _mul_color(bg, 0.75)
        fg = (255, 255, 255) if _is_dark(ui) else (0, 0, 0)

        self.theme_bg = bg
        self.theme_ui = ui
        self.theme_fg = fg

        print(f"[GameScene] Tema aplicado desde usuario: color={saved_color}, tema={saved_theme}, bg={bg}, ui={ui}, fg={fg}")


    def on_scene_enter(self):  
        """Al entrar de nuevo a la escena de juego, recargar el tema por si cambió."""  
        self._load_theme_from_user()  

    def draw(self, screen):
        screen.fill(self.theme_bg)       

        self.matrix.draw(screen)
        self.matrix.drawCoins(screen)
        self.shop.draw(screen)

        remaining = self.matrix.get_remaining_time()
        time_text = f"Tiempo: {remaining}s"
        text_surf = self.font.render(time_text, True, self.theme_fg)

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
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (self.res[0]//2 -150, self.res[1]//2-75))

        rect = pygame.Rect(200, 150, 200, 100)
        rect.center = (self.res[0]//2, self.res[1]//2)

        panel_color = self.theme_ui
        border_color = _mul_color(self.theme_ui, 0.85)

        pygame.draw.rect(screen, panel_color, rect, border_radius=10)
        pygame.draw.rect(screen, border_color, rect, 3, border_radius=10)

        text = self.font.render("PAUSA", True, self.theme_fg)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
