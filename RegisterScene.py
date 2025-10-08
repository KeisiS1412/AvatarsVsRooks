import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox

class RegisterScene(Scene):
    def __init__(self, font):
        self.fieldHeight = 60
        self.fieldWidth = 500
        centerX = 1920 // 2

        yStart = 150
        ySpacing = 90

        self.nameBox = TextBox(centerX, yStart + ySpacing * 0, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Nombre")
        self.lastNamesBox = TextBox(centerX, yStart + ySpacing * 1, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Apellidos")
        self.usernameBox = TextBox(centerX, yStart + ySpacing * 2, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Usuario")
        self.mailBox = TextBox(centerX, yStart + ySpacing * 3, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Correo")
        self.passwordBox = TextBox(centerX, yStart + ySpacing * 4, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Contraseña")
        self.birthdateBox = TextBox(centerX, yStart + ySpacing * 5, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Fecha de nacimiento")
        self.hobbieBox = TextBox(centerX, yStart + ySpacing * 6, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Hobbie")
        self.phoneBox = TextBox(centerX, yStart + ySpacing * 7, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Teléfono")
        self.faceIdBox = TextBox(centerX, yStart + ySpacing * 8, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "FaceID")

        # Campos de tarjeta
        self.cardNumberBox = TextBox(centerX, yStart + ySpacing * 9, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Número de tarjeta")
        self.expirationBox = TextBox(centerX, yStart + ySpacing * 10, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Expiración (MM/AA)")
        self.cvvBox = TextBox(centerX, yStart + ySpacing * 11, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "CVV")
        self.cvvBox = TextBox(centerX, yStart + ySpacing * 12, self.fieldWidth, self.fieldHeight, font, (180,180,180), (0,120,255), "Titular")

        self.registerButton = Button(centerX, yStart + ySpacing * 13, self.fieldWidth, self.fieldHeight, "Registrarse", font, (0,100,200), (0,150,255))

        self.allFields = [
            self.nameBox, self.lastNamesBox, self.usernameBox, self.mailBox, self.passwordBox,
            self.birthdateBox, self.hobbieBox, self.phoneBox, self.faceIdBox,
            self.cardNumberBox, self.expirationBox, self.cvvBox
        ]

    def handleEvent(self, event): #Se encarga de detectar si el usuario hace una accion como clickear, teclear, etc...
        for box in self.allFields:
            box.handleEvent(event)

        if self.registerButton.wasClicked(event):
            data = { 
                "name": self.nameBox.getText(),
                "lastNames": self.lastNamesBox.getText(),
                "username": self.usernameBox.getText(),
                "mail": self.mailBox.getText(),
                "password": self.passwordBox.getText(),
                "birthdate": self.birthdateBox.getText(),
                "hobbie": self.hobbieBox.getText(),
                "phoneNumber": self.phoneBox.getText(),
                "faceId": self.faceIdBox.getText(),
                "cardNumber": self.cardNumberBox.getText(),
                "expiration": self.expirationBox.getText(),
                "cvv": self.cvvBox.getText()
            }

    def update(self, deltaTime): #Actualizacion de la posicion del mouse
        mousePos = pygame.mouse.get_pos()
        self.registerButton.update(mousePos)

    def draw(self, screen): #Dibujar los elementos en pantalla.
        for box in self.allFields:
            box.draw(screen, deltaTime=0)
        self