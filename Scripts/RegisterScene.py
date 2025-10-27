import pygame
import threading
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton
from DropdownButton import DropdownButton
from SimpleTexts import SimpleText
import subprocess
import platform
import os
import re
from api_client import register_user


class RegisterScene(Scene):
    """Layout en dos columnas con márgenes espejados:
    - Izquierda: Datos Personales (pares) + Cuenta (pares)
    - Derecha: Pago (pares) + FaceID + TyC + Register/Login
    """

    def __init__(self, font, res, switchSceneCallback):
        self.switchScene = switchSceneCallback
        self.register_message = ""


        screenW, screenH = res

        # === Medidas base ===
        self.fieldHeight = 75
        colGap = 35            # separación entre campos en una fila (pares)
        colWidth = 420         # ancho de cada campo
        self.fieldWidth = colWidth
        totalRowWidth = colWidth * 2 + colGap  # ancho de una sección en pares
        ySpacing = 110
        sectionSpacing = 30    # separación entre secciones en la misma columna
        topY_left  = 400       # Y inicial de la columna izquierda
        topY_right = 400       # Y inicial de la columna derecha

                # === Márgenes ajustados para mejor alineación visual ===
        sideMargin = 60                  # margen general
        shiftRightLeftCol = 195          # mueve la columna izquierda hacia el centro
        shiftRightRightCol = 227      # mueve la derecha más hacia el borde derecho

        leftBlockX = sideMargin + shiftRightLeftCol
        rightBlockX = screenW - sideMargin - totalRowWidth + shiftRightRightCol

        # Fuente para mensajes de error
        self.errorFont = pygame.font.Font(None, 24)
        self.errorColor = (218, 41, 28)  # gris (puedes cambiar a DA291C si lo prefieres)

        # === Lista de países ===
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

        # Helper para crear TextBox / Dropdown
        def make_box(label, x, y):
            if label == "Hobbie":
                return DropdownButton(
                    x, y, colWidth, self.fieldHeight, font,
                    ["Deportes", "Películas", "Artes"],
                    (180, 180, 180), (255, 255, 255), (255, 255, 255),
                    placeholder="Selecciona tu hobbie"
                )
            if label == "País":
                return DropdownButton(
                    x, y, colWidth, self.fieldHeight, font,
                    countryList, (180, 180, 180), (255, 255, 255), (255, 255, 255),
                    maxVisible=6, placeholder="Selecciona tu país"
                )
            placeholder_color = (180, 180, 180)
            return TextBox(
                x, y, colWidth, self.fieldHeight, font,
                (255, 255, 255), (255, 255, 255), label, placeholder_color
            )

        self.fields = []

        # =========================
        # COLUMNA IZQUIERDA (Datos personales + Cuenta)
        # =========================
        yL = topY_left

        # --- DATOS PERSONALES (pares por fila) ---
        # Fila 1: Nombre | Apellidos
        self.fields.append(make_box("Nombre",    leftBlockX + 0,               yL))
        self.fields.append(make_box("Apellidos", leftBlockX + colWidth + colGap, yL))
        yL += ySpacing
        # Fila 2: Teléfono | Fecha de nacimiento
        self.fields.append(make_box("Teléfono",           leftBlockX + 0,               yL))
        self.fields.append(make_box("Fecha de nacimiento", leftBlockX + colWidth + colGap, yL))
        yL += ySpacing
        # Fila 3: País | Hobbie
        self.fields.append(make_box("País",   leftBlockX + 0,               yL))
        self.fields.append(make_box("Hobbie", leftBlockX + colWidth + colGap, yL))
        yL += ySpacing + sectionSpacing

        # --- CUENTA (pares por fila) ---
        # Fila 1: Usuario | Correo
        self.fields.append(make_box("Usuario", leftBlockX + 0,               yL))
        self.fields.append(make_box("Correo",  leftBlockX + colWidth + colGap, yL))
        yL += ySpacing
        # Fila 2: Contraseña | Confirmar contraseña
        passwordBox = make_box("Contraseña",           leftBlockX + 0,               yL)
        confirmBox  = make_box("Confirmar contraseña", leftBlockX + colWidth + colGap, yL)
        self.fields.append(passwordBox)
        self.fields.append(confirmBox)
        yL += ySpacing

        # Referencias para validación
        self.passwordBox = passwordBox
        self.confirmBox = confirmBox
        self.passwordError = ""
        self.confirmError = ""

        # =========================
        # COLUMNA DERECHA (Pago + FaceID + TyC + Botones)
        # =========================
        yR = topY_right

        # --- PAGO (pares por fila) ---
        # Fila 1: Titular | Número de tarjeta
        self.fields.append(make_box("Titular",           rightBlockX + 0,               yR))
        self.fields.append(make_box("Número de tarjeta", rightBlockX + colWidth + colGap, yR))
        yR += ySpacing
        # Fila 2: Expiración (MM/AA) | CVV
        self.fields.append(make_box("Expiración (MM/AA)", rightBlockX + 0,               yR))
        self.fields.append(make_box("CVV",                rightBlockX + colWidth + colGap, yR))
        yR += ySpacing + sectionSpacing

        # --- Face Recognition (centrado en la pantalla) ---
        centerX = screenW // 2

        face_gap = 0.2
        offset_face_x = 495  # cantidad de desplazamiento horizontal
        self.faceRecognitionButton = ImageButton(
            centerX + offset_face_x, yR + face_gap,
            "Assets/id-facial.png", 0.15
)

        # --- TyC (checkbox + texto) centrados respecto al centro de la pantalla ---
        tyc_gap = 5
        tyc_y = yR + tyc_gap + 80

        # Para centrar el bloque, medimos el ancho del texto
        tyc_text = "He leído y acepto los términos y condiciones"
        text_w, _ = font.size(tyc_text)

        # Anchura visual aproximada del checkbox (ajústalo si tu icono se ve más grande/pequeño)
        checkbox_visual_w = 22     # <-- si lo ves más grande/pequeño, cambia este número
        gap_cb_text = 50           # espacio entre checkbox y texto

        # Posicionamos de modo que [checkbox][gap][texto] quede centrado alrededor de centerX
        # Centro del grupo:
        group_half = (checkbox_visual_w + gap_cb_text + text_w) // 2

        offset_right = 495  # cuanto más grande, más se mueve todo a la derecha

        checkbox_center_x = centerX - group_half + (checkbox_visual_w // 2) + offset_right
        text_center_x     = centerX - group_half + checkbox_visual_w + gap_cb_text + (text_w // 2) + offset_right


        # Creamos el checkbox y el texto usando esos centros
        self.checkBox = ImageButton(
            checkbox_center_x, tyc_y,
            "Assets/checkboxBlank.png", 0.05, "Assets/checkboxFull.png"
        )
        self.termsAndConditions = SimpleText(
            tyc_text,
            text_center_x, tyc_y,
            font, (218, 41, 28), (32, 32, 32)
        )

        # --- Botones Register/Login (par, dentro del bloque derecho) ---
        buttons_gap_y = 135
        buttons_y = tyc_y + buttons_gap_y
        btnGapInside = 16
        btnWidth = (totalRowWidth - btnGapInside) // 2

        self.registerButton = Button(
            rightBlockX, buttons_y, btnWidth, self.fieldHeight,
            "Register", font, (218, 41, 28), (255, 255, 255), (255, 255, 255)
        )
        self.loginButton = Button(
            rightBlockX + btnWidth + btnGapInside, buttons_y, btnWidth, self.fieldHeight,
            "Login", font, (218, 41, 28), (255, 255, 255), (255, 255, 255)
        )

        # === Botones e imágenes base (ayuda/acerca) ===
        self.helpButton = ImageButton(50, 40, "Assets/helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "Assets/aboutButton.png", 0.15)

        self.buttonsList = [
            self.registerButton, self.loginButton, self.faceRecognitionButton,
            self.helpButton, self.aboutButton, self.checkBox
        ]

        # Scroll deshabilitado
        # self.scrollY = 0
        # self.maxScroll = 0

        # Panel: puedes cambiar estos valores como quieras
        self.panel_width = 1890      # ancho del panel
        self.panel_height = 810     # alto del panel
        self.panel_y = 200         # posición Y del panel (ajusta este valor)

    def _read_value(self, box):
        # Intenta métodos típicos de tus widgets
        for attr in ("getValue", "getText"):
            if hasattr(box, attr):
                try:
                    return getattr(box, attr)()
                except Exception:
                    pass
        # A falta de métodos, usa atributos conocidos
        if hasattr(box, "value"):
            return getattr(box, "value")
        if hasattr(box, "text"):
            return getattr(box, "text")
        return ""

    # ---------- VALIDACIÓN DE CONTRASEÑAS ----------
    def _validate_passwords(self):
        pw = getattr(self.passwordBox, "text", "")
        cf = getattr(self.confirmBox, "text", "")

        self.passwordError = ""
        self.confirmError = ""

        if not re.fullmatch(r"[A-Za-z0-9]{0,8}", pw or ""):
            if len(pw) > 8:
                self.passwordError = "Máximo 8 caracteres."
            elif any(not c.isalnum() for c in pw):
                self.passwordError = "Solo caracteres alfanuméricos."

        if not re.fullmatch(r"[A-Za-z0-9]{0,8}", cf or ""):
            if len(cf) > 8:
                self.confirmError = "Máximo 8 caracteres."
            elif any(not c.isalnum() for c in cf):
                self.confirmError = "Solo caracteres alfanuméricos."

        if self.confirmError == "" and cf and pw and (cf != pw):
            self.confirmError = "Debe coincidir con la contraseña."

    def handleEvent(self, event):
        # Entrega los eventos a todos los campos
        for box in self.fields:
            box.handleEvent(event)

        # Validación de contraseñas tras entrada
        self._validate_passwords()

        # Clicks en los botones/checkbox
        for button in self.buttonsList:
            if button.wasClicked(event):
                if button == self.registerButton:
                    # Re-valida contraseñas (usando tu propia lógica actual):
                    self._validate_passwords()
                    if self.passwordError or self.confirmError:
                        self.register_message = (self.passwordError or self.confirmError)
                        continue

                    # Arma el payload exacto para tu backend
                    perfil = {
                        "nombre":              self._read_value(self.fields[0]),
                        "apellidos":           self._read_value(self.fields[1]),
                        "telefono":            self._read_value(self.fields[2]),
                        "fecha_nacimiento":    self._read_value(self.fields[3]),
                        "pais":                self._read_value(self.fields[4]),
                        "hobbie":              self._read_value(self.fields[5]),
                    }
                    cuenta = {
                        "username":            self._read_value(self.fields[6]),
                        "email":               self._read_value(self.fields[7]),
                        "password":            getattr(self.passwordBox, "text", ""),
                        "password_confirm":    getattr(self.confirmBox, "text", "")
                    }
                    pago = {
                        "titular":             self._read_value(self.fields[10]),
                        "numero_tarjeta":      self._read_value(self.fields[11]),
                        "expiracion":          self._read_value(self.fields[12]),
                        # CVV (fields[13]) intencionalmente NO se envía
                    }
                    acepto = bool(getattr(self.checkBox, "clicked", False))

                    payload = {
                        "perfil": perfil,
                        "cuenta": cuenta,
                        "pago":   pago,
                        "acepto_tyc": False if self.checkBox.clicked else True
                    }

                    self.register_message = "Guardando..."

                    def _do_register():
                        try:
                            resp = register_user(payload, timeout=5.0)
                            if resp.get("ok"):
                                self.register_message = "Registro exitoso. Ahora inicia sesión."
                                # Si quieres cambiar de escena automáticamente:
                                # self.switchScene("login")
                            else:
                                # El backend devuelve "field" y "error" cuando hay validación
                                field = resp.get("field", "general")
                                err   = resp.get("error", "error")
                                # También puedes reflejar algunos en tus labels existentes:
                                if field == "password" and err == "invalid_format":
                                    self.passwordError = "Solo alfanumérica, máximo 8."
                                    self.register_message = self.passwordError
                                elif field == "password" and err == "mismatch":
                                    self.confirmError = "Debe coincidir con la contraseña."
                                    self.register_message = self.confirmError
                                else:
                                    self.register_message = f"Error en {field}: {err}"
                        except Exception as e:
                            self.register_message = f"Error de red: {e}"

                    threading.Thread(target=_do_register, daemon=True).start()

                elif button == self.loginButton:
                    self.switchScene("login")
                elif button == self.checkBox and self.checkBox.clicked:
                    self.openPdf("TerminosCondicionesTecnolators.pdf")

                if self.termsAndConditions.wasClicked(event):
                    self.openPdf("TerminosCondicionesTecnolators.pdf")

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for box in self.fields:
            if hasattr(box, "update"):
                box.update(deltaTime)
        for button in self.buttonsList:
            button.update(mousePos)

    def draw(self, screen):
        # Panel centrado, color gris oscuro, bordes redondeados
        screen_width, screen_height = screen.get_size()
        panel_x = (screen_width - self.panel_width) // 2
        panel_y = self.panel_y
        pygame.draw.rect(
            screen,
            (32, 32, 32),
            (panel_x, panel_y, self.panel_width, self.panel_height),
            border_radius=40
        )

        # --- Imagen centrada horizontalmente y más arriba en Y ---
        photo_img = pygame.image.load("Assets/photo.png").convert_alpha()
        # Escala la imagen al tamaño deseado
        scaled_width, scaled_height = 200, 200  # Cambia estos valores para la escala que quieras
        photo_img = pygame.transform.smoothscale(photo_img, (scaled_width, scaled_height))
        photo_rect = photo_img.get_rect()
        photo_rect.centerx = screen_width // 2
        photo_y = panel_y - 85  # Ajusta este valor para mover la imagen más arriba o abajo
        photo_rect.y = photo_y
        screen.blit(photo_img, photo_rect)

        # Primero TextBox (incluye dropdowns cerrados)
        for box in self.fields:
            if not isinstance(box, DropdownButton):
                box.draw(screen, deltaTime=0)

        # Botones, FaceID, TyC
        for button in self.buttonsList:
            button.draw(screen)
        self.termsAndConditions.draw(screen)

        # Luego Dropdowns para que sus menús se superpongan
        for box in self.fields:
            if isinstance(box, DropdownButton):
                box.draw(screen, deltaTime=0)

        # Errores bajo los campos de contraseña (en la columna izquierda)
        if self.passwordError:
            txt = self.errorFont.render(self.passwordError, True, self.errorColor)
            screen.blit(txt, (self.passwordBox.rect.x, self.passwordBox.rect.bottom + 5))
        if self.confirmError:
            txt = self.errorFont.render(self.confirmError, True, self.errorColor)
            screen.blit(txt, (self.confirmBox.rect.x, self.confirmBox.rect.bottom + 5))

        if self.register_message:
            # Usa tu fuente de errores para mantener estilo
            msg_surf = self.errorFont.render(self.register_message, True, self.errorColor)
            screen.blit(msg_surf, (self.registerButton.rect.x, self.registerButton.rect.bottom + 12))


    def openPdf(self, path):
        systemType = platform.system()
        if systemType == "Windows":
            os.startfile(path)
        elif systemType == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
