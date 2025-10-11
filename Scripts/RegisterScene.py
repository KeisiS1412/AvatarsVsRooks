import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton
from DropdownButton import DropdownButton
from SimpleTexts import SimpleText
import subprocess
import platform
import os

class RegisterScene(Scene):
    def __init__(self, font, res, switchSceneCallback):
        self.switchScene = switchSceneCallback
        self.fieldHeight = 75
        self.fieldWidth = 450
        screenW, screenH = res
        yStart = 300
        ySpacing = 90

        leftX = screenW // 2 - self.fieldWidth // 2 - 25
        rightX = screenW // 2 + self.fieldWidth // 2 + 25

        self.scrollY = 0
        self.maxScroll = 0

        countryList = [
            "Afghanistan","Albania","Algeria","Andorra","Angola","Argentina","Armenia","Australia",
            "Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium",
            "Belize","Benin","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei",
            "Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Chile","China",
            "Colombia","Costa Rica","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Dominican Republic",
            "Ecuador","Egypt","El Salvador","Estonia","Ethiopia","Finland","France","Germany","Greece",
            "Guatemala","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel",
            "Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kuwait","Latvia","Lebanon","Liberia",
            "Lithuania","Luxembourg","Madagascar","Malaysia","Maldives","Mali","Malta","Mexico","Moldova",
            "Monaco","Mongolia","Morocco","Mozambique","Myanmar","Namibia","Nepal","Netherlands","New Zealand",
            "Nicaragua","Niger","Nigeria","North Korea","Norway","Oman","Pakistan","Panama","Paraguay",
            "Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia","Rwanda","Saudi Arabia",
            "Senegal","Serbia","Singapore","Slovakia","Slovenia","South Africa","South Korea","Spain",
            "Sri Lanka","Sudan","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand",
            "Tunisia","Turkey","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States",
            "Uruguay","Uzbekistan","Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"
        ]

        fieldPairs = [
            ("Nombre", "Apellidos"),
            ("Usuario", "Teléfono"),
            ("Correo", "Fecha de nacimiento"),
            ("País", "Hobbie"),
            ("Contraseña", "Confirmar contraseña"),
            ("Titular", "Número de tarjeta"),
            ("Expiración (MM/AA)", "CVV")
        ]

        self.fields = []
        for rowIndex, (leftLabel, rightLabel) in enumerate(fieldPairs):
            rowY = yStart + rowIndex * ySpacing
            for colIndex, label in enumerate([leftLabel, rightLabel]):
                colX = leftX if colIndex == 0 else rightX
                if label == "Hobbie":
                    box = DropdownButton(colX, rowY, self.fieldWidth, self.fieldHeight, font,
                                         ["Deportes", "Películas", "Artes"], (0, 0, 0),
                                         (110, 100, 100), (180, 170, 170),
                                         placeholder="Selecciona tu hobbie")
                elif label == "País":
                    box = DropdownButton(colX, rowY, self.fieldWidth, self.fieldHeight, font,
                                         countryList, (0, 0, 0), (110, 100, 100), (180, 170, 170),
                                         maxVisible=6, placeholder="Selecciona tu país")
                else:
                    box = TextBox(colX, rowY, self.fieldWidth, self.fieldHeight, font,
                                  (110, 100, 100), (180, 170, 170), label, (229, 235, 59))
                self.fields.append(box)

        totalRows = len(fieldPairs)
        bottomY = yStart + (totalRows + 2) * ySpacing + 40
        self.maxScroll = max(0, bottomY - (screenH - 200))

        self.registerButton = Button(leftX, bottomY, self.fieldWidth, self.fieldHeight,
                                     "Register", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))
        self.loginButton = Button(rightX, bottomY, self.fieldWidth, self.fieldHeight,
                                  "Login", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))
        self.faceRecognitionButton = ImageButton(screenW//2, yStart + ySpacing * totalRows + 40, "Assets/faceRecognition.png", 0.15)
        self.helpButton = ImageButton(50, 40, "Assets/helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "Assets/aboutButton.png", 0.15)
        self.checkBox = ImageButton(screenW//2 - 375, yStart + ySpacing * (totalRows + 1), "Assets/checkboxBlank.png", 0.05, "Assets/checkboxFull.png")

        self.subscribeButton = Button(screenW // 2, 
                                      bottomY + 100, 
                                      self.fieldWidth, self.fieldHeight,
                                      "Suscribirse", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))

        self.buttonsList = [self.registerButton, self.loginButton, self.faceRecognitionButton,
                            self.helpButton, self.aboutButton, self.checkBox, self.subscribeButton]

        self.termsAndConditions = SimpleText("He leído y acepto los términos y condiciones",
                                             screenW // 2, yStart + ySpacing * (totalRows + 1),
                                             font, (0, 0, 0), (218, 41, 28))

    def handleEvent(self, event):
        dropdownHovered = False
        mousePos = pygame.mouse.get_pos()

        for box in self.fields:
            if isinstance(box, DropdownButton) and box.expanded:
                adjRect = box.rect.move(0, -self.scrollY)
                menuHeight = box.optionHeight * min(len(box.options), box.maxVisible)
                menuRect = pygame.Rect(adjRect.x, adjRect.bottom, adjRect.width, menuHeight)
                if menuRect.collidepoint(mousePos) or adjRect.collidepoint(mousePos):
                    dropdownHovered = True
                    break

        if event.type == pygame.MOUSEWHEEL:
            if dropdownHovered:
                for box in self.fields:
                    if isinstance(box, DropdownButton):
                        box.handleEvent(event, scrollOffset=-self.scrollY)
            else:
                self.scrollY += event.y * 40
                self.scrollY = max(-self.maxScroll, min(0, self.scrollY))

        for box in self.fields:
            box.handleEvent(event, scrollOffset=-self.scrollY)
        for button in self.buttonsList:
            if button.wasClicked(event, scrollOffset=-self.scrollY):
                if button == self.registerButton:
                    pass
                elif button == self.loginButton:
                    self.switchScene("login")
                elif button == self.subscribeButton:
                    pass
                elif button == self.checkBox:
                    if self.checkBox.clicked == True:
                        self.openPdf("TerminosCondicionesTecnolators.pdf")

        if self.termsAndConditions.wasClicked(event, scrollOffset=-self.scrollY):
           self.openPdf("TerminosCondicionesTecnolators.pdf")

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for box in self.fields:  
            if hasattr(box, "update"):
                box.update(deltaTime)
        for button in self.buttonsList:
            button.update(mousePos, scrollOffset=-self.scrollY)

    def draw(self, screen):
        offset = -self.scrollY
        for box in self.fields:
            if not isinstance(box, DropdownButton):
                box.draw(screen, deltaTime=0, scrollOffset=offset)
        for button in self.buttonsList:
            button.draw(screen, scrollOffset=offset)
        self.termsAndConditions.draw(screen, scrollOffset=offset)
        for box in self.fields:
            if isinstance(box, DropdownButton):
                box.draw(screen, deltaTime=0, scrollOffset=offset)

    def openPdf(self, path):
        sistema = platform.system()
        if sistema == "Windows":
            os.startfile(path)
        elif sistema == "Darwin": 
            subprocess.run(["open", path])
        else:  
            subprocess.run(["xdg-open", path])
