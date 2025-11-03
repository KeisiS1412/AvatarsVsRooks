import pygame
import threading
from Scene import Scene
from CalendarTextBox import CalendarTextBox
from Buttons import Button
from TextBoxes import TextBox
import base64, mimetypes
from ImageButtons import ImageButton
from DropdownButton import DropdownButton
from SimpleTexts import SimpleText
import subprocess
import platform
import os
import re
from api_client import register_user

# === NUEVO: para abrir el diálogo de archivos ===
try:
    import tkinter as _tk
    from tkinter import filedialog as _fd
    _TK_OK = True
except Exception:
    _TK_OK = False

REGISTER_SUCCESS = pygame.USEREVENT + 1


class RegisterScene(Scene):
    """Layout en dos columnas con márgenes espejados:
    - Izquierda: Datos Personales (pares) + Cuenta (pares)
    - Derecha: Pago (pares) + FaceID + TyC + Register/Login
    """

    def __init__(self, font, res, switchSceneCallback):
        screenW, screenH = res

        # === Medidas base ===
        self.fieldHeight = 75
        colGap = 35
        colWidth = 420
        self.fieldWidth = colWidth
        totalRowWidth = colWidth * 2 + colGap
        ySpacing = 110
        sectionSpacing = 30
        topY_left  = 400
        topY_right = 400

        # === Márgenes ajustados para mejor alineación visual ===
        sideMargin = 60
        shiftRightLeftCol = 195
        shiftRightRightCol = 227

        leftBlockX = sideMargin + shiftRightLeftCol
        rightBlockX = screenW - sideMargin - totalRowWidth + shiftRightRightCol

        self.buttonsList = []

        self.switchScene = switchSceneCallback
        self.register_message = ""
        self.errorFont = pygame.font.Font(None, 24)
        self.errorColor = (218, 41, 28)

        # =========================
        # AVATAR / FOTO (CIRCULAR)
        # =========================
        # Tamaño del avatar en pantalla (cuadrado -> se recorta a círculo)
        self.AVATAR_SIZE = 200
        # Colores de aro
        self.COLOR_RED = (218, 41, 28)
        self.COLOR_DARK = (32, 32, 32)

        # Carga por defecto: PRO.png -> photo.png (fallback)
        default_avatar_path = "Assets/photo.png"
        if not os.path.exists(default_avatar_path):
            default_avatar_path = "Assets/photo.png"
        self.avatar_surface = self._load_circular_avatar(default_avatar_path, self.AVATAR_SIZE)
        # Se posiciona en draw(); aquí sólo guardamos rect “estándar” para colisiones
        self.photo_rect = pygame.Rect(0, 0, self.AVATAR_SIZE, self.AVATAR_SIZE)
        self.avatar_path = default_avatar_path  # por si luego quieres persistir

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
            if label == "Fecha de nacimiento":
                return CalendarTextBox(
                    x, y, colWidth, self.fieldHeight, font,
                    (255, 255, 255), (255, 255, 255), label
                )
            placeholder_color = (180, 180, 180)
            is_pwd = label in ("Contraseña", "Confirmar contraseña")
            return TextBox(
                x, y, colWidth, self.fieldHeight, font,
                (255, 255, 255), (255, 255, 255), label, placeholder_color,
                is_password=is_pwd,
                right_padding=40
            )

        self.fields = []

        # =========================
        # COLUMNA IZQUIERDA
        # =========================
        yL = topY_left
        self.fields.append(make_box("Nombre",    leftBlockX + 0,                 yL))
        self.fields.append(make_box("Apellidos", leftBlockX + colWidth + colGap, yL))
        yL += ySpacing
        self.fields.append(make_box("Teléfono",           leftBlockX + 0,                 yL))
        self.fields.append(make_box("Fecha de nacimiento", leftBlockX + colWidth + colGap, yL))
        yL += ySpacing
        self.fields.append(make_box("País",   leftBlockX + 0,                 yL))
        self.fields.append(make_box("Hobbie", leftBlockX + colWidth + colGap, yL))
        yL += ySpacing + sectionSpacing

        self.fields.append(make_box("Usuario", leftBlockX + 0,                 yL))
        self.fields.append(make_box("Correo",  leftBlockX + colWidth + colGap, yL))
        yL += ySpacing
        passwordBox = make_box("Contraseña",           leftBlockX + 0,                 yL)
        confirmBox  = make_box("Confirmar contraseña", leftBlockX + colWidth + colGap, yL)
        self.fields.append(passwordBox)
        self.fields.append(confirmBox)
        yL += ySpacing

        self.passwordBox = passwordBox
        self.confirmBox = confirmBox
        self.passwordError = ""
        self.confirmError = ""

        self.eyePwd = ImageButton(
            self.passwordBox.rect.right - 36, self.passwordBox.rect.centery + 1,
            "Assets/eye-closed.png", 0.08, "Assets/eye-open.png"
        )
        self.eyeConfirm = ImageButton(
            self.confirmBox.rect.right - 36, self.confirmBox.rect.centery + 1,
            "Assets/eye-closed.png", 0.08, "Assets/eye-open.png"
        )
        self.buttonsList.extend([self.eyePwd, self.eyeConfirm])

        # =========================
        # COLUMNA DERECHA
        # =========================
        yR = topY_right
        self.fields.append(make_box("Titular",           rightBlockX + 0,                 yR))
        self.fields.append(make_box("Número de tarjeta", rightBlockX + colWidth + colGap, yR))
        yR += ySpacing
        self.fields.append(make_box("Expiración (MM/AA)", rightBlockX + 0,                 yR))
        self.fields.append(make_box("CVV",                rightBlockX + colWidth + colGap, yR))
        yR += ySpacing + sectionSpacing

        centerX = screenW // 2
        face_gap = 0.2
        offset_face_x = 495
        self.faceRecognitionButton = ImageButton(
            centerX + offset_face_x, yR + face_gap,
            "Assets/id-facial.png", 0.15
        )

        tyc_gap = 5
        tyc_y = yR + tyc_gap + 80
        tyc_text = "He leído y acepto los términos y condiciones"
        text_w, _ = font.size(tyc_text)
        checkbox_visual_w = 22
        gap_cb_text = 50
        group_half = (checkbox_visual_w + gap_cb_text + text_w) // 2
        offset_right = 495
        checkbox_center_x = centerX - group_half + (checkbox_visual_w // 2) + offset_right
        text_center_x     = centerX - group_half + checkbox_visual_w + gap_cb_text + (text_w // 2) + offset_right

        self.checkBox = ImageButton(
            checkbox_center_x, tyc_y,
            "Assets/checkboxBlank.png", 0.05, "Assets/checkboxFull.png"
        )
        self.termsAndConditions = SimpleText(
            tyc_text, text_center_x, tyc_y, font, (218, 41, 28), (32, 32, 32)
        )

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

        self.helpButton = ImageButton(50, 40, "Assets/helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "Assets/aboutButton.png", 0.15)

        self.buttonsList.extend([
            self.registerButton, self.loginButton, self.faceRecognitionButton,
            self.helpButton, self.aboutButton, self.checkBox
        ])

        self.panel_width = 1890
        self.panel_height = 810
        self.panel_y = 200

    # ---------- Helpers Avatar ----------
    def _load_circular_avatar(self, path, size):
        """Carga imagen, la escala a size×size y la recorta a círculo (Surface RGBA)."""
        try:
            img = pygame.image.load(path).convert_alpha()
        except Exception:
            # Si falla, crea un placeholder gris
            img = pygame.Surface((size, size), pygame.SRCALPHA)
            img.fill((200, 200, 200, 255))
        img = pygame.transform.smoothscale(img, (size, size))

        # Surface final
        avatar = pygame.Surface((size, size), pygame.SRCALPHA)
        avatar.blit(img, (0, 0))

        # Máscara circular: blanco opaco dentro, transparente fuera
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
        # Multiplica RGBA por la máscara → recorte circular
        avatar.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return avatar

    def _select_new_avatar(self):
        """Abre diálogo de archivos y reemplaza el avatar si el usuario elige imagen."""
        if not _TK_OK:
            self.register_message = "No se pudo abrir el selector (tkinter no disponible)."
            return
        try:
            root = _tk.Tk()
            root.withdraw()
            filetypes = [("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("Todos", "*.*")]
            path = _fd.askopenfilename(title="Selecciona tu foto", filetypes=filetypes)
            root.destroy()
        except Exception:
            path = ""

        if path and os.path.exists(path):
            self.avatar_surface = self._load_circular_avatar(path, self.AVATAR_SIZE)
            self.avatar_path = path
            self.register_message = ""  # limpiar cualquier mensaje previo

    # ---------- Lectura/validación ----------
    def _read_value(self, box):
        for attr in ("getValue", "getText"):
            if hasattr(box, attr):
                try:
                    return getattr(box, attr)()
                except Exception:
                    pass
        if hasattr(box, "value"):
            return getattr(box, "value")
        if hasattr(box, "text"):
            return getattr(box, "text")
        return ""

    def _validate_passwords(self):
        pw = getattr(self.passwordBox, "text", "")
        cf = getattr(self.confirmBox, "text", "")

        self.passwordError = ""
        self.confirmError = ""

        if re.fullmatch(r"[A-Za-z0-9]{0,8}", pw or ""):
            if len(pw) < 8:
                self.passwordError = "Mínimo 8 caracteres."
            elif any(not c.isalnum() for c in pw):
                self.passwordError = "Solo caracteres alfanuméricos."

        if re.fullmatch(r"[A-Za-z0-9]{0,8}", cf or ""):
            if len(cf) < 8:
                self.confirmError = "Mínimo 8 caracteres."
            elif any(not c.isalnum() for c in cf):
                self.confirmError = "Solo caracteres alfanuméricos."

        if self.confirmError == "" and cf and pw and (cf != pw):
            self.confirmError = "Debe coincidir con la contraseña."

    # ---------- Eventos ----------
    def handleEvent(self, event):
        if event.type == REGISTER_SUCCESS:
            self.switchScene("login")
            return

        # Click en el avatar → abrir selector
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.photo_rect.collidepoint(event.pos):
                self._select_new_avatar()

        for box in self.fields:
            box.handleEvent(event)

        self._validate_passwords()

        for button in self.buttonsList:
            if button.wasClicked(event):
                if button == self.registerButton:
                    self._validate_passwords()
                    if self.passwordError or self.confirmError:
                        self.register_message = (self.passwordError or self.confirmError)
                        continue

                    perfil = {
                        "nombre":            self._read_value(self.fields[0]),
                        "apellidos":         self._read_value(self.fields[1]),
                        "telefono":          self._read_value(self.fields[2]),
                        "fecha_nacimiento":  self._read_value(self.fields[3]),
                        "pais":              self._read_value(self.fields[4]),
                        "hobbie":            self._read_value(self.fields[5]),
                    }
                    cuenta = {
                        "username":          self._read_value(self.fields[6]),
                        "email":             self._read_value(self.fields[7]),
                        "password":          getattr(self.passwordBox, "text", ""),
                        "password_confirm":  getattr(self.confirmBox, "text", "")
                    }
                    pago = {
                        "titular":           self._read_value(self.fields[10]),
                        "numero_tarjeta":    self._read_value(self.fields[11]),
                        "expiracion":        self._read_value(self.fields[12]),
                    }

                    avatar_b64 = None
                    avatar_mime = None
                    try:
                        if self.avatar_path and os.path.exists(self.avatar_path):
                            with open(self.avatar_path, "rb") as f:
                                raw = f.read()
                            avatar_b64 = base64.b64encode(raw).decode("ascii")
                            avatar_mime = mimetypes.guess_type(self.avatar_path)[0] or "application/octet-stream"
                    except Exception:
                        avatar_b64 = None
                        avatar_mime = None

                    payload = {
                        "perfil": perfil,
                        "cuenta": cuenta,
                        "pago":   pago,
                        "acepto_tyc": False if self.checkBox.clicked else True,
                        "avatar_b64": avatar_b64,       # <--- NUEVO
                        "avatar_mime": avatar_mime   
                    }

                    self.register_message = "Guardando..."

                    def _do_register():
                        try:
                            resp = register_user(payload, timeout=5.0)
                            if resp.get("ok"):
                                pygame.event.post(pygame.event.Event(REGISTER_SUCCESS))
                                return
                            else:
                                field = resp.get("field", "general")
                                err   = resp.get("error", "error")
                                if field == "password" and err == "invalid_format":
                                    self.passwordError = "Solo alfanumérica, máximo 8."
                                    self.register_message = self.passwordError
                                elif field == "password" and err == "mismatch":
                                    self.confirmError = "Debe coincidir con la contraseña."
                                    self.register_message = self.confirmError
                                else:
                                    self.register_message = f"Error en {field}: {err}"
                        except Exception:
                            self.register_message = f"Error de red:"
                    threading.Thread(target=_do_register, daemon=True).start()

                elif button == self.loginButton:
                    self.switchScene("login")
                elif button == self.checkBox and self.checkBox.clicked:
                    self.openPdf("Assets/TerminosCondicionesTecnolators.pdf")
                elif button == self.eyePwd:
                    self.passwordBox.set_show_password(self.eyePwd.clicked)
                elif button == self.eyeConfirm:
                    self.confirmBox.set_show_password(self.eyeConfirm.clicked)

                if self.termsAndConditions.wasClicked(event):
                    self.openPdf("Assets/TerminosCondicionesTecnolators.pdf")
                if self.helpButton.wasClicked(event):
                    self.switchScene("Help")
                if self.aboutButton.wasClicked(event):
                    self.switchScene("About")

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for box in self.fields:
            if hasattr(box, "update"):
                box.update(deltaTime)
        for button in self.buttonsList:
            button.update(mousePos)

    def draw(self, screen):
        # Panel
        screen_width, screen_height = screen.get_size()
        panel_x = (screen_width - self.panel_width) // 2
        panel_y = self.panel_y
        pygame.draw.rect(
            screen, (32, 32, 32),
            (panel_x, panel_y, self.panel_width, self.panel_height),
            border_radius=40
        )

        # ============ AVATAR CIRCULAR + ARO ============
        # Centro horizontal, un poco hacia arriba (como tenías)
        cx = screen_width // 2
        cy = panel_y - 85 + 20  # ajusta si lo quieres más arriba/abajo

        # Guardamos rect para colisiones de click
        self.photo_rect.size = (self.AVATAR_SIZE, self.AVATAR_SIZE)
        self.photo_rect.center = (cx, cy + self.AVATAR_SIZE // 2)  # acomodo fino visual

        # Aro exterior rojo y fondo oscuro intermedio para simular doble borde
        outer_r = int(self.AVATAR_SIZE * 0.60)
        inner_r = int(self.AVATAR_SIZE * 0.52)
        pygame.draw.circle(screen, self.COLOR_RED, (cx, cy + self.AVATAR_SIZE // 2), outer_r)
        pygame.draw.circle(screen, self.COLOR_DARK, (cx, cy + self.AVATAR_SIZE // 2), inner_r)

        # Blit del avatar (ya recortado en círculo)
        # Colócalo centrado exactamente donde está el aro
        av_rect = self.avatar_surface.get_rect(center=(cx, cy + self.AVATAR_SIZE // 2))
        screen.blit(self.avatar_surface, av_rect.topleft)

        # -------- Campos / botones / dropdowns --------
        for box in self.fields:
            if not isinstance(box, DropdownButton):
                box.draw(screen, deltaTime=0)

        for button in self.buttonsList:
            button.draw(screen)
        self.termsAndConditions.draw(screen)

        for box in self.fields:
            if isinstance(box, DropdownButton):
                box.draw(screen, deltaTime=0)

        for box in self.fields:
            if isinstance(box, CalendarTextBox):
                box.draw_overlay(screen, scrollOffset=0)

        if self.passwordError:
            txt = self.errorFont.render(self.passwordError, True, self.errorColor)
            screen.blit(txt, (self.passwordBox.rect.x, self.passwordBox.rect.bottom + 5))
        if self.confirmError:
            txt = self.errorFont.render(self.confirmError, True, self.errorColor)
            screen.blit(txt, (self.confirmBox.rect.x, self.confirmBox.rect.bottom + 5))

        if self.register_message:
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
