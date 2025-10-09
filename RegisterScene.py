import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton
from DropdownButton import DropdownButton
from SimpleTexts import SimpleText

class RegisterScene(Scene):
    def __init__(self, font, res, switchSceneCallback):
        self.switchScene = switchSceneCallback
        self.fieldHeight = 75
        self.fieldWidth = 400
        screenW = res[0]
        yStart = 100
        ySpacing = 90

        leftX = screenW // 2 - self.fieldWidth // 2 - 25
        rightX = screenW // 2 + self.fieldWidth // 2 + 25

        countryList = [  # Lista completa de países
            "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia", "Australia",
            "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium",
            "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei",
            "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Chile", "China",
            "Colombia", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Dominican Republic",
            "Ecuador", "Egypt", "El Salvador", "Estonia", "Ethiopia", "Finland", "France", "Germany", "Greece",
            "Guatemala", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel",
            "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kuwait", "Latvia", "Lebanon", "Liberia",
            "Lithuania", "Luxembourg", "Madagascar", "Malaysia", "Maldives", "Mali", "Malta", "Mexico", "Moldova",
            "Monaco", "Mongolia", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nepal", "Netherlands", "New Zealand",
            "Nicaragua", "Niger", "Nigeria", "North Korea", "Norway", "Oman", "Pakistan", "Panama", "Paraguay",
            "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saudi Arabia",
            "Senegal", "Serbia", "Singapore", "Slovakia", "Slovenia", "South Africa", "South Korea", "Spain",
            "Sri Lanka", "Sudan", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand",
            "Tunisia", "Turkey", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States",
            "Uruguay", "Uzbekistan", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
        ]

        fieldPairs = [
            ("Nombre", "Apellidos"),
            ("Usuario", "Teléfono"),
            ("Correo", "Fecha de nacimiento"),
            ("País", "Contraseña"),
            ("Confirmar contraseña", "Hobbie"),
            ("Titular", "Número de tarjeta"),
            ("Expiración (MM/AA)", "CVV")
        ]

        self.fields = []
        for rowIndex, (leftLabel, rightLabel) in enumerate(fieldPairs):
            rowY = yStart + rowIndex * ySpacing

            for colIndex, label in enumerate([leftLabel, rightLabel]):
                colX = leftX if colIndex == 0 else rightX

                if label == "Hobbie":
                    box = DropdownButton(
                        colX, rowY, self.fieldWidth, self.fieldHeight,
                        font,
                        ["Deportes", "Películas", "Artes"],
                        (0, 0, 0), (110, 100, 100), (180, 170, 170),
                        placeholder="Selecciona tu hobbie"
                    )
                elif label == "País":
                    box = DropdownButton(
                        colX, rowY, self.fieldWidth, self.fieldHeight,
                        font,
                        countryList,
                        (0, 0, 0), (110, 100, 100), (180, 170, 170),
                        maxVisible=6,
                        placeholder="Selecciona tu país"
                    )
                else:
                    box = TextBox(
                        colX, rowY, self.fieldWidth, self.fieldHeight,
                        font,
                        (110, 100, 100),
                        (180, 170, 170),
                        label,
                        (229, 235, 59)
                    )

                self.fields.append(box)

        totalRows = len(fieldPairs)
        self.registerButton = Button(
            leftX,
            yStart + (totalRows + 2) * ySpacing + 40,
            self.fieldWidth,
            self.fieldHeight,
            "Register",
            font,
            (0, 0, 0),
            (91, 81, 81),
            (192, 58, 48)
        )
        self.loginButton = Button(
            rightX,
            yStart + (totalRows + 2) * ySpacing + 40,
            self.fieldWidth,
            self.fieldHeight,
            "Login",
            font,
            (0, 0, 0),
            (91, 81, 81),
            (192, 58, 48)
        )
        self.faceRecognitionButton = ImageButton(screenW//2, yStart + ySpacing * (totalRows) + 40, "faceRecognition.png", 0.15)
        self.helpButton = ImageButton(50, 40, "helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "aboutButton.png", 0.15)
        self.buttonsList = [self.registerButton, self.loginButton, self.faceRecognitionButton, self.helpButton, self.aboutButton]
        self.termsAndConditions = SimpleText("I have read and accept the terms and conditions", screenW // 2, yStart + ySpacing * (totalRows + 1), font, (0, 0, 0))

    def handleEvent(self, event):
        for box in self.fields:
            box.handleEvent(event)

        if self.registerButton.wasClicked(event):
            data = {box.text: box.getText() for box in self.fields}
            print("Datos registrados:", data)
        if self.loginButton.wasClicked(event):
            self.switchScene("login")
        if self.termsAndConditions.wasClicked(event):
            pass

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for button in self.buttonsList:
            button.update(mousePos)

    def draw(self, screen):
        for box in self.fields:
            box.draw(screen, deltaTime=0)
        for button in self.buttonsList:
            button.draw(screen)

        self.termsAndConditions.draw(screen)

        for box in self.fields:
            if isinstance(box, DropdownButton) and box.expanded:
                box.draw(screen, deltaTime=0)

        
