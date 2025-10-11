import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton

class LoginScene(Scene):
    """Escena de inicio de sesión: permite ingresar usuario, contraseña y acceder a opciones de autenticación."""

    def __init__(self, font, res, switchSceneCallback):  # Inicializa los elementos de la escena
        self.switchScene = switchSceneCallback
        self.buttonHeigth = 75
        self.buttonLength = 450
        center = res[0] // 2
        yStart = 400
        ySpacing = 90

        self.usernameBox = TextBox(center, yStart + ySpacing * 0, self.buttonLength, self.buttonHeigth, font,
                                   (110, 100, 100), (180, 170, 170), "Username, email or number", (229, 235, 59))
        self.passwordBox = TextBox(center, yStart + ySpacing * 1, self.buttonLength, self.buttonHeigth, font,
                                   (110, 100, 100), (180, 170, 170), "Password", (229, 235, 59))
        self.loginButton = Button(center, yStart + ySpacing * 2, self.buttonLength, self.buttonHeigth,
                                  "Login", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))
        self.registerButton = Button(center, yStart + ySpacing * 3, self.buttonLength, self.buttonHeigth,
                                     "Register", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))
        self.recoverPassword = Button(center, yStart + ySpacing * 4, self.buttonLength, self.buttonHeigth,
                                      "Recover Password", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))

        self.googleButton = ImageButton(center + self.buttonLength // 2, yStart + ySpacing * 5 + 100,
                                        "Assets/googleLogin.png", 1)
        self.faceRecognitionButton = ImageButton(center - self.buttonLength // 2 + 75, yStart + ySpacing * 5 + 100,
                                                 "Assets/faceRecognition.png", 0.20)
        self.helpButton = ImageButton(50, 40, "Assets/helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "Assets/aboutButton.png", 0.15)

        self.buttonsList = [
            self.loginButton,
            self.googleButton,
            self.faceRecognitionButton,
            self.helpButton,
            self.aboutButton,
            self.registerButton,
            self.recoverPassword
        ]

    def handleEvent(self, event):  # Maneja los eventos de entrada del usuario
        self.usernameBox.handleEvent(event)
        self.passwordBox.handleEvent(event)

        if self.loginButton.wasClicked(event):
            print("Username:", self.usernameBox.getText())
            print("Password:", self.passwordBox.getText())

        if self.googleButton.wasClicked(event):
            pass

        if self.faceRecognitionButton.wasClicked(event):
            pass

        if self.registerButton.wasClicked(event):
            self.switchScene("register")

    def update(self, deltaTime):  # Actualiza los botones según la posición del mouse
        mousePos = pygame.mouse.get_pos()
        for button in self.buttonsList:
            button.update(mousePos)

    def draw(self, screen):  # Dibuja todos los elementos en la pantalla
        self.usernameBox.draw(screen, deltaTime=0)
        self.passwordBox.draw(screen, deltaTime=0)
        for button in self.buttonsList:
            button.draw(screen)
