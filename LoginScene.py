import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton
from SimpleTexts import SimpleText
import threading
import traceback

from auth import verify_login  # def verify_login(username_or_email, password) -> (bool, str)

NEXT_SCENE_AFTER_LOGIN = "home"  # cámbialo si tu escena destino tiene otro nombre

class LoginScene(Scene):
    def __init__(self, font, res, switchSceneCallback):
        self.switchScene = switchSceneCallback
        self.buttonHeigth = 75
        self.buttonLength = 450
        center = res[0]//2
        yStart = 400
        ySpacing = 90
        
        self.usernameBox = TextBox(center, yStart + ySpacing * 0, self.buttonLength, self.buttonHeigth, font, (110,100,100), (180,170,170), "Username, email or number", (229, 235, 59))
        self.passwordBox = TextBox(center,  yStart + ySpacing * 1, self.buttonLength, self.buttonHeigth, font, (110,100,100), (180,170,170), "Password", (229, 235, 59))
        self.loginButton = Button(center, yStart + ySpacing * 2, self.buttonLength, self.buttonHeigth, "Login", font, (0,0,0), (91,81,81), (192, 58, 48))
        self.registerButton = Button(center, yStart + ySpacing * 3, self.buttonLength, self.buttonHeigth, "Register", font, (0,0,0), (91,81,81), (192, 58, 48))
        self.recoverPassword = Button(center, yStart + ySpacing * 4, self.buttonLength, self.buttonHeigth, "Recover Password", font, (0,0,0), (91,81,81), (192, 58, 48))
        self.googleButton = ImageButton(center + self.buttonLength//2, yStart + ySpacing * 5 + 100, "googleLogin.png", 1)
        self.faceRecognitionButton = ImageButton(center - self.buttonLength//2 + 75, yStart + ySpacing * 5 + 100, "faceRecognition.png", 0.20)
        self.helpButton = ImageButton(50, 40, "helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "aboutButton.png", 0.15)
        
        self.buttonsList = [
            self.loginButton,
            self.googleButton,
            self.faceRecognitionButton,
            self.helpButton,
            self.aboutButton,
            self.registerButton,
            self.recoverPassword
        ]

        # Status para mensajes
        self.statusText = SimpleText("", center, yStart + ySpacing * 2 - 40, font, (255, 255, 255))

        # Flag de carga para evitar bloqueos/doble click
        self._is_loading = False

    def _set_status(self, msg, color=(255, 255, 255)):
        if self.statusText:
            self.statusText.text = msg
            self.statusText.color = color
        else:
            print(msg)

    def on_login_click(self):
        if self._is_loading:
            return

        username_or_email = self.usernameBox.getText().strip() if hasattr(self.usernameBox, "getText") else ""
        password = self.passwordBox.getText().strip() if hasattr(self.passwordBox, "getText") else ""

        if not username_or_email or not password:
            self._set_status("Ingrese usuario/correo y contraseña.", (255, 200, 0))
            return

        self._is_loading = True
        self._set_status("Verificando...", (200, 200, 200))

        def _worker():
            try:
                ok, msg = verify_login(username_or_email, password)
            except Exception as e:
                traceback.print_exc()
                ok, msg = False, f"Error: {e}"
            self._login_result = (ok, msg)
            self._is_loading = False

        threading.Thread(target=_worker, daemon=True).start()

    def handleEvent(self, event):
        self.usernameBox.handleEvent(event)
        self.passwordBox.handleEvent(event)

        if self.loginButton.wasClicked(event):
            self.on_login_click()
        if self.googleButton.wasClicked(event):
            pass
        if self.faceRecognitionButton.wasClicked(event):
            pass
        if self.registerButton.wasClicked(event):
            self.switchScene("register")
        if self.aboutButton.wasClicked(event):
            self.mostrar_info("About", 
                        "Avatars vs Rooks es una aplicación diseñada para ofrecer una experiencia de usuario segura y personalizada.\n\n"
                        "Además, Avatars vs Rooks permite a los usuarios personalizar su experiencia eligiendo colores y música que se adapten a sus preferencias, creando así un entorno más agradable y único para cada individuo.\n\n"
                        "La aplicación está diseñada para ser intuitiva y fácil de usar, asegurando que tanto usuarios nuevos como experimentados puedan navegar por sus funciones sin dificultad.\n\n"
                        )
        if self.helpButton.wasClicked(event):
            self.mostrar_info("Help", 
                        "Bienvenido. En caso de necesitar ayuda con el registro o el login, por favor lea las siguientes instrucciones:\n\n"
                        "Si es la primera vez que usa la aplicación: Debe registrarse llenando todos los campos del formulario y luego presionando el botón 'Register'.\n\n"
                        "Una vez registrado, irá al apartado de Personalización, donde podrá elegir su color favorito y la música de su agrado.\n\n"
                        "Si ya está registrado: Puede ir al apartado de Login, donde podrá iniciar sesión con su usuario y contraseña.\n\n"
                        "Si el problema persiste, por favor contacte con soporte técnico."
                        )
        if self.recoverPassword.wasClicked(event):
            self._set_status("Función no implementada aún.", (0, 200, 255))

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for button in self.buttonsList:
            button.update(mousePos)

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

        # recoger resultado del hilo (si existe)
        if hasattr(self, "_login_result"):
            ok, msg = self._login_result
            del self._login_result
            if ok:
                self._set_status("Login correcto ✅", (0, 220, 120))
                self.switchScene(NEXT_SCENE_AFTER_LOGIN)
            else:
                self._set_status(msg or "Credenciales inválidas.", (255, 120, 120))

    def draw(self, screen):
        self.usernameBox.draw(screen, deltaTime=0)
        self.passwordBox.draw(screen, deltaTime=0)
        for button in self.buttonsList:
            button.draw(screen)
        if self.statusText:
            self.statusText.draw(screen)
