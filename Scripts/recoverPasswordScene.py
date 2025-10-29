import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton
from MailSender import MailSender
from api_client import request_password_reset, confirm_password_reset

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
                                      "Send Code", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))
        self.codeBox = TextBox(center, yStart + ySpacing * 0, self.buttonLength, self.buttonHeigth, font,
                                   (110, 100, 100), (180, 170, 170), "Code", (229, 235, 59))
        self.recoverButton = Button(center, yStart + ySpacing * 1, self.buttonLength, self.buttonHeigth,
                                      "Recover", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))
        self.passwordBox = TextBox(center, yStart + ySpacing * 0, self.buttonLength, self.buttonHeigth, font,
                                   (110, 100, 100), (180, 170, 170), "New password", (229, 235, 59))
        self.setPasswordButton = Button(center, yStart + ySpacing * 1, self.buttonLength, self.buttonHeigth,
                                      "Set Password", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))
        self.loginButton = Button(center, yStart + ySpacing * 2, self.buttonLength, self.buttonHeigth,
                                      "Login", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))

        self.helpButton = ImageButton(50, 40, "Assets/helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "Assets/aboutButton.png", 0.15)

        self.buttonsList = [
            self.sendCodeButton,
            self.helpButton,
            self.aboutButton,
            self.recoverButton,
            self.loginButton,
            self.setPasswordButton
        ]

        self.reciveCode = False
        self.changePassword = False
        self.enterEmail = True
        self.generatedCode = None
        self.emailEntered = ""
        self.email = ""
        self.serverToken = None

    def handleEvent(self, event):
        if self.enterEmail:
            self.emailBox.handleEvent(event)
            if self.sendCodeButton.wasClicked(event):
                self.email = self.emailBox.getText()
                token = request_password_reset(self.email)  
                if token: 
                    self.serverToken = token           
                    mailer = MailSender(self.email)
                    self.code = mailer.sendEmail()          
                    print(f"Código enviado a {self.email}: {self.code}")
                    self.enterEmail = False
                    self.reciveCode = True
                else:
                    print("El servidor no reconoce este correo.")

        elif self.reciveCode:
            self.codeBox.handleEvent(event)
            if self.recoverButton.wasClicked(event):
                enteredCode = self.codeBox.getText()
                if enteredCode == str(self.code):
                    print("Código correcto. Puede cambiar su contraseña.")
                    self.reciveCode = False
                    self.changePassword = True
                else:
                    print("Código incorrecto.")
        elif self.changePassword:
            self.passwordBox.handleEvent(event)
            if self.setPasswordButton.wasClicked(event):
                newPassword = self.passwordBox.getText()
                if newPassword and len(newPassword) == 8 and newPassword.isalnum():
                    success = confirm_password_reset(self.email, self.serverToken, newPassword)
                    if success:
                        print("Contraseña actualizada correctamente.")
                        self.changePassword = False
                        self.enterEmail = True
                        self.switchScene("login")
                    else:
                        print("Error al actualizar contraseña.")
                else:
                    print("Ingrese una nueva contraseña.")

        if self.loginButton.wasClicked(event):
            self.enterEmail = True
            self.switchScene("login")
        if self.helpButton.wasClicked(event):
            print("Help clicked")
        if self.aboutButton.wasClicked(event):
            print("About clicked")

    def update(self, deltaTime):  # Actualiza los botones según la posición del mouse
        mousePos = pygame.mouse.get_pos()
        for button in self.buttonsList:
            button.update(mousePos)

    def draw(self, screen):  # Dibuja todos los elementos en la pantalla
        self.aboutButton.draw(screen)
        self.helpButton.draw(screen)
        self.loginButton.draw(screen)
        if self.enterEmail == True:
            self.emailBox.draw(screen)
            self.sendCodeButton.draw(screen)
        if self.reciveCode:
            self.codeBox.draw(screen)
            self.recoverButton.draw(screen)
        if self.changePassword:
            self.setPasswordButton.draw(screen)
            self.passwordBox.draw(screen)
