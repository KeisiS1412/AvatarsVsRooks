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
import threading
import traceback

# Importa tu backend real
from auth import register_user  # def register_user(username, password, email=None, extra=None) -> (bool, str)


from Registrofacial import RegistroFacial


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

        # ===== Lista de países =====
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

        # ===== Campos del formulario =====
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
                    # initialText se usa como placeholder en tu TextBox
                    box = TextBox(colX, rowY, self.fieldWidth, self.fieldHeight, font,
                                  (110, 100, 100), (180, 170, 170), label, (229, 235, 59))
                self.fields.append(box)

        totalRows = len(fieldPairs)
        bottomY = yStart + (totalRows + 2) * ySpacing + 40
        self.maxScroll = max(0, bottomY - (screenH - 200))

        # ===== Botones =====
        self.registerButton = Button(leftX, bottomY, self.fieldWidth, self.fieldHeight,
                                     "Register", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))
        self.loginButton = Button(rightX, bottomY, self.fieldWidth, self.fieldHeight,
                                  "Login", font, (0, 0, 0), (91, 81, 81), (192, 58, 48))
        self.faceRecognitionButton = ImageButton(screenW//2, yStart + ySpacing * totalRows + 40, "faceRecognition.png", 0.15)
        self.helpButton = ImageButton(50, 40, "helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "aboutButton.png", 0.15)
        self.checkBox = ImageButton(screenW//2 - 375, yStart + ySpacing * (totalRows + 1), "checkboxBlank.png", 0.05, "checkboxFull.png")

        self.subscribeButton = Button(screenW // 2, 
                                      bottomY + 100, 
                                      self.fieldWidth, self.fieldHeight,
                                      "Suscribirse", font, (0, 0, 0), (91, 81, 81), (58, 192, 48))

        self.buttonsList = [self.registerButton, self.loginButton, self.faceRecognitionButton,
                            self.helpButton, self.aboutButton, self.checkBox, self.subscribeButton]


        self.termsAndConditions = SimpleText("He leído y acepto los términos y condiciones",
                                             screenW // 2, yStart + ySpacing * (totalRows + 1),
                                             font, (0, 0, 0))

    # ====== EVENTOS ======
        # Status para mensajes
        self.statusText = SimpleText("", screenW // 2, bottomY + 60, font, (255, 255, 255))
        self._is_loading = False

    # ==== helpers ====
    def _get_field_by_label(self, label):
        for box in self.fields:
            if isinstance(box, TextBox) and getattr(box, "placeholder", None) == label:
                return box
            if getattr(box, "text", None) == label:
                return box
        return None

    def _get_value(self, label):
        box = self._get_field_by_label(label)
        if box is None:
            return ""
        if isinstance(box, TextBox):
            return box.getText().strip() if hasattr(box, "getText") else ""
        return box.getText().strip() if hasattr(box, "getText") else ""

    def _set_status(self, msg, color=(255, 255, 255)):
        if self.statusText:
            self.statusText.text = msg
            self.statusText.color = color
        else:
            print(msg)

    # ==== validación de contraseña (>=8 y alfanumérica) ====
    def _password_valid(self, pwd: str) -> bool:
        return len(pwd) >= 8 and pwd.isalnum()

    # ==== acción principal de registro en hilo ====
    def on_register_click(self):
        if self._is_loading:
            return

        username = self._get_value("Usuario")
        email    = self._get_value("Correo")
        pwd      = self._get_value("Contraseña")
        pwd2     = self._get_value("Confirmar contraseña")

        if not username or not pwd:
            self._set_status("Complete usuario y contraseña.", (255, 200, 0)); return
        if not self._password_valid(pwd):
            self._set_status("La contraseña debe tener ≥8 caracteres y ser alfanumérica.", (255, 200, 0)); return
        if pwd != pwd2:
            self._set_status("Las contraseñas no coinciden.", (255, 120, 120)); return

        extra = {
            "nombre": self._get_value("Nombre"),
            "apellidos": self._get_value("Apellidos"),
            "telefono": self._get_value("Teléfono"),
            "fecha_nacimiento": self._get_value("Fecha de nacimiento"),
            "pais": self._get_value("País"),
            "hobbie": self._get_value("Hobbie"),
            "titular": self._get_value("Titular"),
            "num_tarjeta": self._get_value("Número de tarjeta"),
            "exp": self._get_value("Expiración (MM/AA)"),
            "cvv": self._get_value("CVV"),
        }

        self._is_loading = True
        self._set_status("Creando usuario...", (200, 200, 200))

        def _worker():
            try:
                ok, msg = register_user(username, pwd, email=email or None, extra=extra)
            except Exception as e:
                traceback.print_exc()
                ok, msg = False, f"Error: {e}"
            self._register_result = (ok, msg)
            self._is_loading = False

        threading.Thread(target=_worker, daemon=True).start()

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
                    data = {box.text: box.getText() for box in self.fields}
                    print("Datos registrados:", data)
                elif button == self.loginButton:
                    self.switchScene("login")

                # 🔹 Integración del reconocimiento facial, sin cambiar tu código
                elif button == self.faceRecognitionButton:
                    try:
                        usuario = self._get_value("Usuario")
                        if not usuario:
                            self._set_status("Ingrese un nombre de usuario antes de registrar el rostro.", (255, 200, 0))
                        else:
                            self._set_status("Abriendo cámara para registrar rostro...", (200, 200, 200))
                            facial = RegistroFacial(usuario)
                            facial.menu()  # menú facial con "Registrar rostro" y "Salir"
                            self._set_status("Registro facial completado ✅", (0, 255, 0))
                    except Exception as e:
                        self._set_status(f"Error en reconocimiento facial: {e}", (255, 0, 0))

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for box in self.fields:
            if hasattr(box, "update"):
                box.update(deltaTime)
        for button in self.buttonsList:
            button.update(mousePos, scrollOffset=-self.scrollY)

        # recoger resultado del hilo (si existe)
        if hasattr(self, "_register_result"):
            ok, msg = self._register_result
            del self._register_result
            if ok:
                self._set_status("Usuario creado ", (0, 220, 120))
                self.switchScene("login")   # ir a iniciar sesión inmediatamente
            else:
                self._set_status(msg or "No se pudo registrar.", (255, 120, 120))

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

    def mostrar_info(self, titulo, texto):
        """Ventana informativa a pantalla completa con botón 'Cerrar' colocado dinámicamente."""
        screen = pygame.display.get_surface()
        screen_w, screen_h = screen.get_size()

        # Crear superficie base
        info_surface = pygame.Surface((screen_w, screen_h))
        info_surface.fill((240, 240, 240))  # Fondo gris claro
        pygame.draw.rect(info_surface, (0, 0, 0), info_surface.get_rect(), 4)

        # Fuentes
        titulo_font = pygame.font.Font("Avenir.ttf", 60)
        texto_font = pygame.font.Font("Avenir.ttf", 32)
        boton_font = pygame.font.Font("Avenir.ttf", 36)

        # --- Título ---
        titulo_surf = titulo_font.render(titulo, True, (30, 30, 30))
        titulo_rect = titulo_surf.get_rect(center=(screen_w // 2, 100))
        info_surface.blit(titulo_surf, titulo_rect)

        # --- Texto ---
        x_margin = 150
        y_start = 200
        max_width = screen_w - 2 * x_margin
        line_height = texto_font.get_height() + 10
        y = y_start

        parrafos = texto.split("\n\n")

        for p in parrafos:
            palabras = p.split()
            linea = ""
            for palabra in palabras:
                test = f"{linea} {palabra}".strip()
                if texto_font.size(test)[0] < max_width:
                    linea = test
                else:
                    surf = texto_font.render(linea, True, (50, 50, 50))
                    info_surface.blit(surf, (x_margin, y))
                    y += line_height
                    linea = palabra
            if linea:
                surf = texto_font.render(linea, True, (50, 50, 50))
                info_surface.blit(surf, (x_margin, y))
                y += line_height
            y += 20  # espacio entre párrafos

        # --- Botón CERRAR dinámico ---
        boton_ancho, boton_alto = 240, 80
        espacio_inferior = 120  # margen con el borde inferior
        boton_y = min(y + 60, screen_h - espacio_inferior)  # si hay espacio, baja; si no, se queda arriba

        boton_rect = pygame.Rect(screen_w // 2 - boton_ancho // 2, boton_y, boton_ancho, boton_alto)
        texto_boton = boton_font.render("Cerrar", True, (0, 0, 0))
        texto_rect = texto_boton.get_rect(center=boton_rect.center)

        clock = pygame.time.Clock()
        esperando = True

        while esperando:
            screen.fill((0, 0, 0))  # fondo negro por si hay bordes
            screen.blit(info_surface, (0, 0))

            # Hover visual
            mouse_pos = pygame.mouse.get_pos()
            hover = boton_rect.collidepoint(mouse_pos)
            color_boton = (180, 180, 180) if hover else (200, 200, 200)
            pygame.draw.rect(screen, color_boton, boton_rect, border_radius=12)
            pygame.draw.rect(screen, (0, 0, 0), boton_rect, 2, border_radius=12)
            screen.blit(texto_boton, texto_rect)

            pygame.display.flip()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    esperando = False
                elif e.type == pygame.KEYDOWN:
                    esperando = False
                elif e.type == pygame.MOUSEBUTTONDOWN and hover:
                    esperando = False

            clock.tick(60)





        if self.statusText:
            self.statusText.draw(screen, scrollOffset=0)

    def openPdf(self, path):
        sistema = platform.system()
        if sistema == "Windows":
            os.startfile(path)
        elif sistema == "Darwin": 
            subprocess.run(["open", path])
        else:  
            subprocess.run(["xdg-open", path])
