import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton
import threading
from api_client import login_user
LOGIN_SUCCESS = pygame.USEREVENT + 2


class LoginScene(Scene):
    """Escena de inicio de sesión: permite ingresar usuario, contraseña y acceder a opciones de autenticación."""

    def __init__(self, font, res, switchSceneCallback): 
        self.login_message = "" # Inicializa los elementos de la escena
        self.switchScene = switchSceneCallback
        self.buttonHeigth = 75
        self.buttonLength = 450
        center = res[0] // 2
        yStart = 400
        ySpacing = 90

        # === TextBoxes ===
        self.usernameBox = TextBox(
            center, yStart + ySpacing * 0, self.buttonLength, self.buttonHeigth, font,
            (255, 255, 255), (255, 255, 255), "Usuario, email o número", (180, 180, 180)
        )
        self.passwordBox = TextBox(
            center, yStart + ySpacing * 1, self.buttonLength, self.buttonHeigth, font,
            (255, 255, 255), (255, 255, 255), "Contraseña", (180, 180, 180)
        )

        # === Botones ===
        self.loginButton = Button(
            center, yStart + ySpacing * 2.6, self.buttonLength, self.buttonHeigth,
            "Continuar", font, (218, 41, 28), (255, 255, 255), (255, 255, 255)
        )
        self.registerButton = Button(
            center, yStart + ySpacing * 3.6, self.buttonLength, self.buttonHeigth,
            "Registrarse", font, (218, 41, 28), (255, 255, 255), (255, 255, 255)
        )

        # === Botones con imagen ===
        self.googleButton = ImageButton(
            center + self.buttonLength // 2 - 120, yStart + ySpacing * 4.2 + 100,
            "Assets/googleLogin2.png", 0.99
        )
        self.faceRecognitionButton = ImageButton(
            center - self.buttonLength // 2 + 120, yStart + ySpacing * 4.2 + 100,
            "Assets/id-facial.png", 0.17
        )
        self.helpButton = ImageButton(50, 40, "Assets/helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "Assets/aboutButton.png", 0.15)

        self.buttonsList = [
            self.loginButton,
            self.googleButton,
            self.faceRecognitionButton,
            self.helpButton,
            self.aboutButton,
            self.registerButton
        ]

        # === "Botón" de texto: ¿Olvidaste tu contraseña? ===
        self.forgot_text = "¿Olvidaste tu contraseña?"
        self.forgot_color_normal = (218, 41, 28)
        self.forgot_color_hover = (255, 255, 255)
        self.forgot_hover = False
        self.forgot_rect = None
        # Fuente más pequeña solo para este link
        self.forgot_font = pygame.font.Font(None, 30)

        # === Texto divisorio “o continúa con” ===
        self.divider_text = "———————— o continúa con ————————"
        self.divider_color = (218, 41, 28)

        # === Fuente del TÍTULO (más grande) ===
        self.title_font = pygame.font.Font(None, 65)  # ajusta 70/90 según prefieras

    def handleEvent(self, event):
        if event.type == LOGIN_SUCCESS:
            # Si tu switchScene acepta datos, podrías pasar el usuario con event.user
            self.switchScene("game_mode")
            return

        self.usernameBox.handleEvent(event)
        self.passwordBox.handleEvent(event)

        if self.loginButton.wasClicked(event):
            user = self.usernameBox.getText()
            pwd = self.passwordBox.getText()
            self.login_message = ""

            def _do_login():
                try:
                    resp = login_user(user, pwd, timeout=5.0)
                    if resp.get("ok"):
                        u = resp["user"]["username"]
                        self.login_message = f"Bienvenido {u}"
                        # Postea al hilo principal para cambiar de escena
                        pygame.event.post(pygame.event.Event(LOGIN_SUCCESS, user=resp["user"]))
                        return
                    else:
                        self.login_message = "Usuario o contraseña incorrectos."
                except Exception as e:
                    self.login_message = f"Error de red"

            threading.Thread(target=_do_login, daemon=True).start()


        if self.googleButton.wasClicked(event):
            pass

        if self.faceRecognitionButton.wasClicked(event):
            pass

        if self.registerButton.wasClicked(event):
            self.switchScene("register")
        
        if self.recoverPassword.wasClicked(event):
            self.switchScene("recoverPassword")

        # Click en el "botón" de texto
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.forgot_rect and self.forgot_rect.collidepoint(event.pos):
                print("[ForgotPasswordLink] clicked")  # luego puedes conectarlo a tu escena

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for button in self.buttonsList:
            button.update(mousePos)

        # Hover para el link
        if self.forgot_rect and self.forgot_rect.collidepoint(mousePos):
            if not self.forgot_hover:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.forgot_hover = True
        else:
            if self.forgot_hover:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.forgot_hover = False

    def draw(self, screen):
        screen_width, screen_height = screen.get_size()
        rect_width, rect_height = 700, 850
        rect_x = (screen_width - rect_width) // 2
        rect_y = (screen_height - rect_height) // 2

        # Fondo del panel
        color_rgb = pygame.Color("#25201C")
        pygame.draw.rect(
            screen,
            color_rgb,
            (rect_x, rect_y, rect_width, rect_height),
            border_radius=30
        )

        # === Título (fuente más grande) ===
        title_text = "Iniciar Sesión"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        title_x = screen_width // 2 - title_surface.get_width() // 2
        title_y = rect_y + 110  # ajusta si necesitas más/menos espacio
        screen.blit(title_surface, (title_x, title_y))

        # TextBoxes
        self.usernameBox.draw(screen, deltaTime=0)
        self.passwordBox.draw(screen, deltaTime=0)

        # === "Botón" de texto interactivo ===
        link_color = self.forgot_color_hover if self.forgot_hover else self.forgot_color_normal
        forgot_surface = self.forgot_font.render(self.forgot_text, True, link_color)
        padding_right = 12
        padding_top = 10
        link_x = self.passwordBox.rect.right - forgot_surface.get_width() - padding_right
        link_y = self.passwordBox.rect.bottom + padding_top

        screen.blit(forgot_surface, (link_x, link_y))
        self.forgot_rect = pygame.Rect(link_x, link_y, forgot_surface.get_width(), forgot_surface.get_height())

        # Subrayado al pasar el mouse
        if self.forgot_hover:
            underline_y = link_y + forgot_surface.get_height() - 1
            pygame.draw.line(
                screen,
                link_color,
                (link_x, underline_y),
                (link_x + forgot_surface.get_width(), underline_y),
                1
            )

        # Botones
        for button in self.buttonsList:
            button.draw(screen)

        # === Texto “o continúa con” debajo del botón Registrarse ===
        divider_font = pygame.font.Font(None, 28)
        divider_surface = divider_font.render(self.divider_text, True, self.divider_color)
        divider_x = screen_width // 2 - divider_surface.get_width() // 2
        divider_y = self.registerButton.rect.bottom + 35  # un poco de espacio debajo
        screen.blit(divider_surface, (divider_x, divider_y))

        if self.login_message:
            mfont = pygame.font.Font(None, 28)
            msurf = mfont.render(self.login_message, True, (255, 255, 255))
            mx = self.loginButton.rect.x
            my = self.loginButton.rect.bottom - 100
            screen.blit(msurf, (mx, my))

