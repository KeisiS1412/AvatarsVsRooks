import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton
from MailSender import MailSender

class recoverPasswordScene(Scene):
    """Escena de recuperacion de contrasena"""

    def __init__(self, font, res, switchSceneCallback):  # Inicializa los elementos de la escena
        self.switchScene = switchSceneCallback
        self.buttonHeigth = 75
        self.buttonLength = 450
        center = res[0] // 2
        yStart = 400
        ySpacing = 90
        self.code = False
        self.emailBox = TextBox(center, yStart + ySpacing * 0, self.buttonLength, self.buttonHeigth, font,
                                   (110, 100, 100), (180, 170, 170), "Email", (229, 235, 59))
        self.sendCodeButton = Button(center, yStart + ySpacing * 1, self.buttonLength, self.buttonHeigth,
                                      "SendCode", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))
        self.codeBox = TextBox(center, yStart + ySpacing * 0, self.buttonLength, self.buttonHeigth, font,
                                   (110, 100, 100), (180, 170, 170), "Code", (229, 235, 59))
        self.recoverButton = Button(center, yStart + ySpacing * 1, self.buttonLength, self.buttonHeigth,
                                      "Recover", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))

        self.helpButton = ImageButton(50, 40, "Assets/helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "Assets/aboutButton.png", 0.15)

        self.buttonsList = [
            self.recoverButton,
            self.sendCodeButton,
            self.helpButton,
            self.aboutButton,
        ]

    def handleEvent(self, event):  # Maneja los eventos de entrada del usuario
        self.codeBox.handleEvent(event)
        self.emailBox.handleEvent(event)

        if self.sendCodeButton.wasClicked(event):
            sender = MailSender(self.emailBox.getText())
            self.code = sender.sendEmail()
        
        if self.recoverButton.wasClicked(event):
            if self.code != False 

    def update(self, deltaTime):  # Actualiza los botones según la posición del mouse
        mousePos = pygame.mouse.get_pos()
        for button in self.buttonsList:
            button.update(mousePos)

    def draw(self, screen):  # Dibuja todos los elementos en la pantalla
        self.usernameBox.draw(screen, deltaTime=0)
        self.passwordBox.draw(screen, deltaTime=0)
        for button in self.buttonsList:
            button.draw(screen)
