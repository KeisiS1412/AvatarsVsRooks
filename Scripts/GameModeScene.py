import pygame
from Scene import Scene
from Buttons import Button

class GameModeScene(Scene):
    def __init__(self, font, res, switchSceneCallback, mananger):
        self.switchScene = switchSceneCallback
        self.font = font
        self.res = res
        self.manager = mananger
        self._auto_music_started = False 
        screenW, screenH = res
        self.bg_color = (218, 41, 28)  # Rojo fondo

        # Botones
        button_w, button_h = 300, 60
        spacing = 100  # espacio entre botones
        y_center = screenH // 2

        labels = ["easy", "medium", "hard"]
        self.buttons = []

        # Ancho total ocupado por todos los botones + espacios
        total_width = len(labels) * button_w + (len(labels) - 1) * spacing
        start_x = (screenW - total_width) // 1.4

        for i, label in enumerate(labels):
            x = start_x + i * (button_w + spacing)
            btn = Button(
                x, y_center - button_h // 2,
                button_w, button_h,
                label, font,
                (37, 32, 28),      # fondo oscuro
                (255, 255, 255),   # texto blanco
                (255, 255, 255)    # borde blanco
            )
            self.buttons.append(btn)
        
        self.settingsBtn = Button(
            screenW - 200, 30,
            180, 50,
            "Settings", font,
            (37, 32, 28),
            (255, 255, 255),
            (255, 255, 255)
        )

    def handleEvent(self, event):
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
        if self.settingsBtn.wasClicked(event):
            self.switchScene("personalization")

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mousePos)
        self.settingsBtn.update(mousePos)

    def draw(self, screen):
        screen.fill(self.bg_color)
        for button in self.buttons:
            button.draw(screen)
        self.settingsBtn.draw(screen)

    def on_scene_enter(self):  #NUEVA
        """Al entrar al menú de juego, iniciar la música si el usuario ya eligió canción."""  #NUEVA
        if self._auto_music_started:  #NUEVA
            return  #NUEVA
 #NUEVA
        # 1. Obtener usuario actual desde la sesión  #NUEVA
        try:  #NUEVA
            from session import get_current_user  #NUEVA
            user = get_current_user()  #NUEVA
        except Exception as e:  #NUEVA
            print(f"[GameModeScene] No se pudo obtener el usuario actual para música: {e}")  #NUEVA
            return  #NUEVA
 #NUEVA
        if not isinstance(user, dict):  #NUEVA
            return  #NUEVA
 #NUEVA
        perfil = user.get("perfil") or {}  #NUEVA
        saved_song = (perfil.get("cancion_preferida") or "").strip()  #NUEVA
        if not saved_song:  #NUEVA
            return  #NUEVA
 #NUEVA
        # 2. Buscar la escena de Personalization para reutilizar su cliente de Spotify  #NUEVA
        pscene = None  #NUEVA
        try:  #NUEVA
            scenes = getattr(self.manager, "scenes", {})  #NUEVA
            pscene = scenes.get("personalization")  #NUEVA
        except Exception:  #NUEVA
            pscene = None  #NUEVA
 #NUEVA
        if pscene is None or not hasattr(pscene, "PlayMusicFromTextbox"):  #NUEVA
            print("[GameModeScene] No se encuentra PersonalizationScene o no tiene PlayMusicFromTextbox")  #NUEVA
            return  #NUEVA
 #NUEVA
        # 3. Actualizar la caja de música de Personalization con la canción guardada  #NUEVA
        try:  #NUEVA
            pscene.musicBox.text = saved_song  #NUEVA
            print(f"[GameModeScene] Iniciando música automática: '{saved_song}'")  #NUEVA
            pscene.PlayMusicFromTextbox()  #NUEVA
            self._auto_music_started = True  #NUEVA
        except Exception as e:  #NUEVA
            print(f"[GameModeScene] Error al iniciar música automática: {e}")  #NUEVA
