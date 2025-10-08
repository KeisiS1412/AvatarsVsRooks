import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox

class LoginScene(Scene):
    def __init__(self, font):
        self.buttonHeigth = 75
        self.buttonLength = 400
        self.usernameBox = TextBox(960, 500, self.buttonLength, self.buttonHeigth, font, (180,180,180), (0,120,255))
        self.passwordBox = TextBox(960, 750, self.buttonLength, self.buttonHeigth, font, (180,180,180), (0,120,255))
        self.loginButton = Button(960, 900, self.buttonLength, self.buttonHeigth, "Login", font, (0,100,200), (0,150,255))

    def handleEvent(self, event): #Se encarga de detectar si el usuario hace una accion como clickear, teclear, etc...
        self.usernameBox.handleEvent(event)
        self.passwordBox.handleEvent(event)
        if self.loginButton.wasClicked(event):
            print("Username:", self.usernameBox.getText())
            print("Password:", self.passwordBox.getText())

    def update(self, deltaTime): #Actualizacion de la posicion del mouse
        mousePos = pygame.mouse.get_pos()
        self.loginButton.update(mousePos)

    def draw(self, screen): #Dibujar los elementos en pantalla.
        self.usernameBox.draw(screen, deltaTime=0)
        self.passwordBox.draw(screen, deltaTime=0)
        self.loginButton.draw(screen)