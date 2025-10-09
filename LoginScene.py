import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton
from SimpleTexts import SimpleText
import threading
import traceback

from auth import verify_login  # def verify_login(username_or_email, password) -> (bool, str)

NEXT_SCENE_AFTER_LOGIN = "home"  # cámbialo si tu escena destino tiene otro nombre

class LoginScene(Scene):
    def __init__(self, font, res, switchSceneCallback):
        self.switchScene = switchSceneCallback
        self.buttonHeigth = 75
        self.buttonLength = 450
        center = res[0]//2
        yStart = 400
        ySpacing = 90
        
        self.usernameBox = TextBox(center, yStart + ySpacing * 0, self.buttonLength, self.buttonHeigth, font, (110,100,100), (180,170,170), "Username, email or number", (229, 235, 59))
        self.passwordBox = TextBox(center,  yStart + ySpacing * 1, self.buttonLength, self.buttonHeigth, font, (110,100,100), (180,170,170), "Password", (229, 235, 59))
        self.loginButton = Button(center, yStart + ySpacing * 2, self.buttonLength, self.buttonHeigth, "Login", font, (0,0,0), (91,81,81), (192, 58, 48))
        self.registerButton = Button(center, yStart + ySpacing * 3, self.buttonLength, self.buttonHeigth, "Register", font, (0,0,0), (91,81,81), (192, 58, 48))
        self.recoverPassword = Button(center, yStart + ySpacing * 4, self.buttonLength, self.buttonHeigth, "Recover Password", font, (0,0,0), (91,81,81), (192, 58, 48))
        self.googleButton = ImageButton(center + self.buttonLength//2, yStart + ySpacing * 5 + 100, "googleLogin.png", 1)
        self.faceRecognitionButton = ImageButton(center - self.buttonLength//2 + 75, yStart + ySpacing * 5 + 100, "faceRecognition.png", 0.20)
        self.helpButton = ImageButton(50, 40, "helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "aboutButton.png", 0.15)
        
        self.buttonsList = [
            self.loginButton,
            self.googleButton,
            self.faceRecognitionButton,
            self.helpButton,
            self.aboutButton,
            self.registerButton,
            self.recoverPassword
        ]

        # Status para mensajes
        self.statusText = SimpleText("", center, yStart + ySpacing * 2 - 40, font, (255, 255, 255))

        # Flag de carga para evitar bloqueos/doble click
        self._is_loading = False

    def _set_status(self, msg, color=(255, 255, 255)):
        if self.statusText:
            self.statusText.text = msg
            self.statusText.color = color
        else:
            print(msg)

    def on_login_click(self):
        if self._is_loading:
            return

        username_or_email = self.usernameBox.getText().strip() if hasattr(self.usernameBox, "getText") else ""
        password = self.passwordBox.getText().strip() if hasattr(self.passwordBox, "getText") else ""

        if not username_or_email or not password:
            self._set_status("Ingrese usuario/correo y contraseña.", (255, 200, 0))
            return

        self._is_loading = True
        self._set_status("Verificando...", (200, 200, 200))

        def _worker():
            try:
                ok, msg = verify_login(username_or_email, password)
            except Exception as e:
                traceback.print_exc()
                ok, msg = False, f"Error: {e}"
            self._login_result = (ok, msg)
            self._is_loading = False

        threading.Thread(target=_worker, daemon=True).start()

    def handleEvent(self, event):
        self.usernameBox.handleEvent(event)
        self.passwordBox.handleEvent(event)

        if self.loginButton.wasClicked(event):
            self.on_login_click()
        if self.googleButton.wasClicked(event):
            pass
        if self.faceRecognitionButton.wasClicked(event):
            pass
        if self.registerButton.wasClicked(event):
            self.switchScene("register")
        if self.recoverPassword.wasClicked(event):
            self._set_status("Función no implementada aún.", (0, 200, 255))

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for button in self.buttonsList:
            button.update(mousePos)

        # recoger resultado del hilo (si existe)
        if hasattr(self, "_login_result"):
            ok, msg = self._login_result
            del self._login_result
            if ok:
                self._set_status("Login correcto ✅", (0, 220, 120))
                self.switchScene(NEXT_SCENE_AFTER_LOGIN)
            else:
                self._set_status(msg or "Credenciales inválidas.", (255, 120, 120))

    def draw(self, screen):
        self.usernameBox.draw(screen, deltaTime=0)
        self.passwordBox.draw(screen, deltaTime=0)
        for button in self.buttonsList:
            button.draw(screen)
        if self.statusText:
            self.statusText.draw(screen)
