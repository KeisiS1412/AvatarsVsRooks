import pygame
from Scene import Scene
from Buttons import Button
from control.Cliente import Client

class GameModeScene(Scene):
    def __init__(self, font, res, switchSceneCallback, manager):
        self.switchScene = switchSceneCallback
        self.font = font
        self.res = res
        self.manager = manager
        self._auto_music_started = False
        screenW, screenH = res
        self.bg_color = (218, 41, 28)  # Rojo fondo

        # ================================
        # Cargar imagen del logo
        # ================================
        self.logo = pygame.image.load("Assets/AvatarsVsRooks.png").convert_alpha()
        new_width = 1350
        new_height = 550
        self.logo = pygame.transform.smoothscale(self.logo, (new_width, new_height))
        self.logo_rect = self.logo.get_rect(center=(screenW // 2, screenH // 2 - 150))

        # ================================
        # Cargar botón de Settings como imagen
        # ================================
        self.settings_img = pygame.image.load("Assets/settings (3).png").convert_alpha()
        settings_w, settings_h = 85, 85
        self.settings_img = pygame.transform.smoothscale(self.settings_img, (settings_w, settings_h))
        self.settings_rect = self.settings_img.get_rect(topright=(screenW - 20, 20))

        # ================================
        # Botones de dificultad
        # ================================
        button_w, button_h = 300, 60
        spacing = 100
        y_center = screenH // 2
        labels = ["easy", "medium", "hard"]

        self.buttons = []
        total_width = len(labels) * button_w + (len(labels) - 1) * spacing
        start_x = (screenW - total_width) // 2

        for i, label in enumerate(labels):
            x = start_x + i * (button_w + spacing)
            btn = Button(
                x,
                y_center - button_h // 2 + 310,
                button_w,
                button_h,
                label,
                font,
                (37, 32, 28),
                (255, 255, 255),
                (255, 255, 255)
            )
            self.buttons.append(btn)

        # Botón de conectar control
        medium_btn = self.buttons[1]
        connect_y = y_center + 200
        self.connectButton = Button(
            medium_btn.rect.centerx - button_w // 2,
            connect_y,
            button_w,
            button_h,
            "Conectar control",
            font,
            (37, 32, 28),
            (255, 255, 255),
            (255, 255, 255)
        )

        # Cliente
        self.client = Client()
        self.connection_status = "Desconectado"

        # Fuente para estado de conexión
        self.status_font = pygame.font.Font(None, 36)

    def handleEvent(self, event):
        # Botones de dificultad
        for button in self.buttons:
            if button.wasClicked(event):
                if button.text == "easy":
                    self.manager.scenes["game"].setDifficulty("easy")
                    self.switchScene("game")
                elif button.text == "medium":
                    self.manager.scenes["game"].setDifficulty("medium")
                    self.switchScene("game")
                elif button.text == "hard":
                    self.manager.scenes["game"].setDifficulty("hard")
                    self.switchScene("game")

        # Botón de settings
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.settings_rect.collidepoint(event.pos):
                self.switchScene("personalization")

        # Botón de conectar control
        if self.connectButton.wasClicked(event):
            if not self.client.connected:
                success = self.client.Connect()
                self.connection_status = "Conectado" if success else "Falló conexión"
            else:
                self.client.CloseConnection()
                self.connection_status = "Desconectado"

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mousePos)
        self.connectButton.update(mousePos)

        # Recibir datos del cliente sin bloquear
        if self.client.connected:
            data = self.client.ManageMessages()
            if data:
                print("Datos recibidos:", data)

    def draw(self, screen):
        screen.fill(self.bg_color)

        # Logo
        screen.blit(self.logo, self.logo_rect)

        # Botones de dificultad
        for button in self.buttons:
            button.draw(screen)

        # Botón de settings
        screen.blit(self.settings_img, self.settings_rect)

        # Botón de conectar
        self.connectButton.draw(screen)

        # Estado de conexión
        status_surface = self.status_font.render(f"Estado: {self.connection_status}", True, (255, 255, 255))
        screen.blit(status_surface, (self.connectButton.rect.left, self.connectButton.rect.top - 40))

    def on_scene_enter(self):
        if self._auto_music_started:
            return
        try:
            from session import get_current_user
            user = get_current_user()
        except Exception as e:
            print(f"[GameModeScene] No se pudo obtener el usuario actual: {e}")
            return

        if not isinstance(user, dict):
            return

        perfil = user.get("perfil") or {}
        saved_song = (perfil.get("cancion_preferida") or "").strip()
        if not saved_song:
            return

        try:
            scenes = getattr(self.manager, "scenes", {})
            pscene = scenes.get("personalization")
        except Exception:
            pscene = None

        if pscene is None or not hasattr(pscene, "PlayMusicFromTextbox"):
            print("[GameModeScene] No se encuentra PersonalizationScene o no tiene PlayMusicFromTextbox")
            return

        try:
            pscene.musicBox.text = saved_song
            print(f"[GameModeScene] Iniciando música automática: '{saved_song}'")
            pscene.PlayMusicFromTextbox()
            self._auto_music_started = True
        except Exception as e:
            print(f"[GameModeScene] Error al iniciar música automática: {e}")
