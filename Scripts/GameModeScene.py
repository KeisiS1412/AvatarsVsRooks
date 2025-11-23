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

    def on_scene_enter(self):  
        """Al entrar al menú de juego, iniciar la música si el usuario ya eligió canción."""  
        if self._auto_music_started:  
            return  
 
        # 1. Obtener usuario actual desde la sesión  
        try:  
            from session import get_current_user  
            user = get_current_user()  
        except Exception as e:  
            print(f"[GameModeScene] No se pudo obtener el usuario actual para música: {e}")  
            return  
 
        if not isinstance(user, dict):  
            return  
 
        perfil = user.get("perfil") or {}  
        saved_song = (perfil.get("cancion_preferida") or "").strip()  
        if not saved_song:  
            return  
 
        # 2. Buscar la escena de Personalization para reutilizar su cliente de Spotify  
        pscene = None  
        try:  
            scenes = getattr(self.manager, "scenes", {})  
            pscene = scenes.get("personalization")  
        except Exception:  
            pscene = None  
 
        if pscene is None or not hasattr(pscene, "PlayMusicFromTextbox"):  
            print("[GameModeScene] No se encuentra PersonalizationScene o no tiene PlayMusicFromTextbox")  
            return  
 
        # 3. Actualizar la caja de música de Personalization con la canción guardada  
        try:  
            pscene.musicBox.text = saved_song  
            print(f"[GameModeScene] Iniciando música automática: '{saved_song}'")  
            pscene.PlayMusicFromTextbox()  
            self._auto_music_started = True  
        except Exception as e:  
            print(f"[GameModeScene] Error al iniciar música automática: {e}")  
