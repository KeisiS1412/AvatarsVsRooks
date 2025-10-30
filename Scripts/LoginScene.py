import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton
import threading
from api_client import login_user, get_user  
from session import set_current_user 
LOGIN_SUCCESS = pygame.USEREVENT + 2

# ARRIBA, con el resto de imports
from api_client import login_user, get_user
from session import set_current_user

# Helpers (si aún no los tienes en este archivo):
def _merge_dicts(base: dict, extra: dict) -> dict:
    if not isinstance(base, dict): base = {}
    if not isinstance(extra, dict): return base
    out = dict(base)
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            tmp = dict(out[k]); tmp.update(v); out[k] = tmp
        else:
            out[k] = v
    return out

def _try_fetch_profile(username: str) -> dict:
    if not username:
        return {}
    prof = get_user(username, timeout=3.0)
    if isinstance(prof, dict) and prof.get("ok") and isinstance(prof.get("user"), dict):
        return prof["user"]
    if isinstance(prof, dict) and ("username" in prof or "perfil" in prof):
        # por si el server devolviera el usuario directamente
        return prof
    return {}



class LoginScene(Scene):
    """Escena de inicio de sesión: permite ingresar usuario, contraseña y acceder a opciones de autenticación."""

    def __init__(self, font, res, switchSceneCallback): 
        self.login_message = "" # Inicializa los elementos de la escena
        self.switchScene = switchSceneCallback
        self.buttonHeigth = 75
        self.buttonLength = 450
        self._login_ok = False
        self._merged_user = None
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
            (255, 255, 255), (255, 255, 255), "Contraseña", (180, 180, 180),
            # ← tu TextBox ya soporta estos kwargs (los usamos en Register)
            is_password=True,
            right_padding=40
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

        self.eyePwd = ImageButton(
            self.passwordBox.rect.right - 36,   # ajusta horizontal
            self.passwordBox.rect.centery + 1, # ajusta vertical
            "Assets/eye-closed.png",
            0.08,
            "Assets/eye-open.png"
        )
        self.buttonsList.append(self.eyePwd)

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


    def _do_login_thread(self, user: str, pwd: str):
        """Corre en un hilo: hace login, mergea perfil y notifica al hilo principal."""
        try:
            resp = login_user(user, pwd, timeout=5.0)
            if resp.get("ok"):
                u = resp.get("user") or {}
                username = (u.get("username") or u.get("usuario") or "").strip()

                # Merge best-effort con perfil completo, nunca bloquea el flujo
                merged = u
                try:
                    prof_user = _try_fetch_profile(username)
                    if prof_user:
                        merged = _merge_dicts(u, prof_user)
                except Exception:
                    pass

                # Guarda en sesión (que un fallo aquí no bloquee)
                try:
                    set_current_user(merged)
                except Exception:
                    pass

                # Señal 1: evento al hilo principal
                try:
                    pygame.event.post(pygame.event.Event(LOGIN_SUCCESS, user=merged))
                except Exception:
                    pass

                # Señal 2 (respaldo): flag para cambiar en update()
                self._merged_user = merged
                self._login_ok = True

                # Mensaje opcional
                self.login_message = f"Bienvenido {merged.get('username') or merged.get('usuario', '')}"
            else:
                self.login_message = "Usuario o contraseña incorrectos."
        except Exception:
            self.login_message = "Error de red"

    def intentar_login(self, user: str, pwd: str):
        """Llama esto desde tu handler del botón/enter."""
        self.login_message = "Iniciando sesión..."
        threading.Thread(target=self._do_login_thread, args=(user, pwd), daemon=True).start()


    def handleEvent(self, event):
        # 1) Cambio de escena al recibir el evento de éxito de login
        if event.type == LOGIN_SUCCESS:
            try:
                ev_user = getattr(event, "user", None)
                if isinstance(ev_user, dict):
                    try:
                        set_current_user(ev_user)  # refuerza sesión con el usuario del evento
                    except Exception:
                        pass
                self.switchScene("personalization")  # ajusta el nombre si tu escena se llama distinto
                return
            except Exception:
                # incluso si algo falla aquí, el "Plan B" en update() hará el cambio
                pass

        # 2) Forward de eventos a los inputs
        self.usernameBox.handleEvent(event)
        self.passwordBox.handleEvent(event)

        # 3) Click en botón de login: dispara el hilo y señales de notificación
        if self.loginButton.wasClicked(event):
            user = self.usernameBox.getText()
            pwd = self.passwordBox.getText()
            self.login_message = "Iniciando sesión..."
            self._login_ok = False
            self._merged_user = None

            def _do_login():
                try:
                    resp = login_user(user, pwd, timeout=5.0)
                    if resp.get("ok"):
                        u = resp.get("user") or {}
                        username = (u.get("username") or u.get("usuario") or "").strip()

                        # Merge con perfil (tolerante a fallos; jamás bloquea)
                        merged = u
                        try:
                            prof_user = _try_fetch_profile(username)
                            if prof_user:
                                merged = _merge_dicts(u, prof_user)
                        except Exception:
                            pass

                        # Guardar en sesión (tolerante)
                        try:
                            set_current_user(merged)
                        except Exception:
                            pass

                        # Señal 1: evento al hilo principal
                        try:
                            pygame.event.post(pygame.event.Event(LOGIN_SUCCESS, user=merged))
                        except Exception:
                            pass

                        # Señal 2: flags para el Plan B en update()
                        self._merged_user = merged
                        self._login_ok = True

                        # Mensaje opcional
                        self.login_message = f"Bienvenido {merged.get('username') or merged.get('usuario', '')}"
                    else:
                        self.login_message = "Usuario o contraseña incorrectos."
                except Exception:
                    self.login_message = "Error de red"

            threading.Thread(target=_do_login, daemon=True).start()

        if self.eyePwd.wasClicked(event):
            if hasattr(self.passwordBox, "set_show_password"):
                self.passwordBox.set_show_password(self.eyePwd.clicked)
            else:
                    # fallback si no añadiste el método helper:
                self.passwordBox.showPassword = self.eyePwd.clicked
            # Flags de respaldo (Plan B) para cambiar de escena desde update()

        # 4) Otros botones
        if self.googleButton.wasClicked(event):
            pass

        if self.faceRecognitionButton.wasClicked(event):
            pass

        if self.registerButton.wasClicked(event):
            self.switchScene("register")

        # 5) Click en el "link" de texto (forgot password)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.forgot_rect and self.forgot_rect.collidepoint(event.pos):
                self.switchScene("recoverPassword")  # ajusta al nombre real de tu escena


    def update(self, deltaTime):
        # 0) Plan B: si no llegó el evento o no se reenvían eventos a la escena,
        #    cambia de escena aquí al detectar el flag
        if getattr(self, "_login_ok", False):
            self._login_ok = False
            try:
                if isinstance(getattr(self, "_merged_user", None), dict):
                    set_current_user(self._merged_user)
            except Exception:
                pass
            try:
                self.switchScene("personalization")  # ajusta el nombre si es distinto
            except Exception:
                pass
            return

        # 1) Actualización de botones (hover)
        mousePos = pygame.mouse.get_pos()
        for button in self.buttonsList:
            button.update(mousePos)

        # 2) Hover para el link (cambio de cursor)
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

