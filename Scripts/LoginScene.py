import pygame
import threading

from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from ImageButtons import ImageButton

from api_client import login_user, get_user
from session import set_current_user

LOGIN_SUCCESS = pygame.USEREVENT + 2


# =============================
# HELPERS
# =============================

def _merge_dicts(base: dict, extra: dict) -> dict:
    """Une dicts sin tirar errores si algo falta."""
    if not isinstance(base, dict):
        base = {}
    if not isinstance(extra, dict):
        return base

    out = dict(base)
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            tmp = dict(out[k])
            tmp.update(v)
            out[k] = tmp
        else:
            out[k] = v
    return out


def _try_fetch_profile(username: str) -> dict:
    """Pide perfil completo si existe. Falla sin romper login."""
    if not username:
        return {}

    print(f"[DEBUG LoginScene] get_user({username})")
    prof = get_user(username, timeout=3.0)
    print(f"[DEBUG LoginScene] Respuesta perfil: {prof}")

    if isinstance(prof, dict) and prof.get("ok") and isinstance(prof.get("user"), dict):
        return prof["user"]

    if isinstance(prof, dict) and ("username" in prof or "perfil" in prof):
        return prof

    return {}


# ===============================================================
# ========================== LOGIN SCENE =========================
# ===============================================================

class LoginScene(Scene):

    def __init__(self, font, res, switchSceneCallback):
        self.switchScene = switchSceneCallback
        self.login_message = ""

        self.buttonHeigth = 75
        self.buttonLength = 450

        self._login_ok = False
        self._merged_user = None
        self._target_scene = None

        center = res[0] // 2
        yStart = 400
        ySpacing = 90

        # ============================
        # TEXTBOXES
        # ============================
        self.usernameBox = TextBox(
            center, yStart + ySpacing * 0,
            self.buttonLength, self.buttonHeigth,
            font, (255, 255, 255), (255, 255, 255),
            "Usuario, email o número", (180, 180, 180)
        )

        self.passwordBox = TextBox(
            center, yStart + ySpacing * 1,
            self.buttonLength, self.buttonHeigth,
            font,
            (255, 255, 255), (255, 255, 255),
            "Contraseña", (180, 180, 180),
            is_password=True,
            right_padding=40
        )

        # ============================
        # BOTONES NORMALES
        # ============================
        self.loginButton = Button(
            center, yStart + ySpacing * 2.6,
            self.buttonLength, self.buttonHeigth,
            "Continuar", font,
            (218, 41, 28), (255, 255, 255), (255, 255, 255)
        )
        self.registerButton = Button(
            center, yStart + ySpacing * 3.6,
            self.buttonLength, self.buttonHeigth,
            "Registrarse", font,
            (218, 41, 28), (255, 255, 255), (255, 255, 255)
        )

        # ============================
        # BOTONES CON IMAGEN
        # ============================
        self.googleButton = ImageButton(
            center + self.buttonLength // 2 - 120,
            yStart + ySpacing * 4.2 + 100,
            "Assets/googleLogin2.png", 0.99
        )
        self.faceRecognitionButton = ImageButton(
            center - self.buttonLength // 2 + 120,
            yStart + ySpacing * 4.2 + 100,
            "Assets/id-facial.png", 0.17
        )
        self.helpButton = ImageButton(50, 40, "Assets/helpButton.png", 0.15)
        self.aboutButton = ImageButton(140, 40, "Assets/aboutButton.png", 0.15)

        # ============================
        # EYE PASSWORD BUTTON
        # ============================
        self.eyePwd = ImageButton(
            self.passwordBox.rect.right - 36,
            self.passwordBox.rect.centery + 1,
            "Assets/eye-closed.png",
            0.08,
            "Assets/eye-open.png"
        )

        # Lista total de botones
        self.buttonsList = [
            self.loginButton,
            self.registerButton,
            self.googleButton,
            self.faceRecognitionButton,
            self.helpButton,
            self.aboutButton,
            self.eyePwd
        ]

        # ============================
        # FORGOT PASSWORD TEXT
        # ============================
        self.forgot_text = "¿Olvidaste tu contraseña?"
        self.forgot_font = pygame.font.Font(None, 30)
        self.forgot_color_normal = (218, 41, 28)
        self.forgot_color_hover = (255, 255, 255)
        self.forgot_rect = None
        self.forgot_hover = False

        # ============================
        # DECORATIVO
        # ============================
        self.divider_text = "———————— o continúa con ————————"
        self.divider_color = (218, 41, 28)
        self.title_font = pygame.font.Font(None, 65)

        # ============================
        # ANTI BRUTE FORCE
        # ============================
        self.fail_count = 0
        self.lock_until_ms = 0

    # ===========================================================
    # ANTI-BRUTE-FORCE
    # ===========================================================

    def _is_locked(self):
        return pygame.time.get_ticks() < self.lock_until_ms

    def _lock_for(self, ms):
        self.lock_until_ms = pygame.time.get_ticks() + ms

    def _remaining_lock_seconds(self):
        rem = self.lock_until_ms - pygame.time.get_ticks()
        return max(0, (rem + 999) // 1000)

    def _register_failed_attempt(self):
        self.fail_count += 1
        if self.fail_count >= 3:
            self.fail_count = 0
            self._lock_for(15_000)
            self.login_message = "Demasiados intentos. Bloqueado 15 s."
        else:
            self.login_message = "Usuario o contraseña incorrectos."

    def _reset_attempts(self):
        self.fail_count = 0
        self.lock_until_ms = 0


    def _do_login_thread(self, user, pwd):
        """Corre en un hilo: hace login, mergea perfil y notifica al hilo principal."""
        try:
            resp = login_user(user, pwd, timeout=5.0)
            
            if resp.get("ok"):
                u = resp.get("user") or {}
                
                username = (u.get("username") or u.get("usuario") or "").strip()

                # Merge best-effort con perfil completo
                merged = u
                try:
                    prof_user = _try_fetch_profile(username)
                    
                    if prof_user:
                        merged = _merge_dicts(u, prof_user)
                except Exception as e:
                    print(f"[LoginScene] Error en merge: {e}")

                # Guarda en sesión
                try:
                    set_current_user(merged)
                except Exception as e:
                    print(f"LoginScene] Error guardando en sesión: {e}")

                # Señales...
                try:
                    pygame.event.post(pygame.event.Event(LOGIN_SUCCESS, user=merged))
                except Exception:
                    pass

                self._merged_user = merged
                self._login_ok = True

                self.login_message = f"Bienvenido {merged.get('username') or merged.get('usuario', '')}"
            else:
                self.login_message = "Usuario o contraseña incorrectos."
        except Exception as e:
            print(f"[LoginScene] Error general: {e}")
            import traceback
            traceback.print_exc()
            self.login_message = "Error de red"

    # ===========================================================
    # HANDLE EVENT
    # ===========================================================

    def handleEvent(self, event):

        # Bloqueado → no permitir escribir ni login
        if self._is_locked():
            if self.loginButton.wasClicked(event):
                self.login_message = f"Bloqueado {self._remaining_lock_seconds()} s…"
            return

        # SI LLEGA EVENTO LOGIN_SUCCESS
        if event.type == LOGIN_SUCCESS:
            merged = getattr(event, "user", None)
            scene = getattr(event, "target_scene", "game_mode")

            if isinstance(merged, dict):
                try:
                    set_current_user(merged)
                except Exception:
                    pass

            print(f"[LoginScene] Cambiando a escena: {scene}")
            self.switchScene(scene)
            return

        # Pasar eventos a las cajas
        self.usernameBox.handleEvent(event)
        self.passwordBox.handleEvent(event)

        # CLICK LOGIN
        if self.loginButton.wasClicked(event):
            user = self.usernameBox.getText()
            pwd = self.passwordBox.getText()

            self.login_message = "Iniciando sesión..."
            threading.Thread(
                target=self._do_login_thread,
                args=(user, pwd),
                daemon=True
            ).start()

        # Mostrar contraseña
        if self.eyePwd.wasClicked(event):
            self.passwordBox.showPassword = self.eyePwd.clicked

        # GOOGLE LOGIN (placeholder)
        if self.googleButton.wasClicked(event):
            print("[LoginScene] Google login placeholder")

        # FACE LOGIN
        if self.faceRecognitionButton.wasClicked(event):
            self._start_face_recognition()

        # REGISTER
        if self.registerButton.wasClicked(event):
            self.switchScene("register")

        # HELP
        if self.helpButton.wasClicked(event):
            self.switchScene("Help")

        # ABOUT
        if self.aboutButton.wasClicked(event):
            self.switchScene("About")

        # FORGOT PASSWORD LINK
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.forgot_rect and self.forgot_rect.collidepoint(event.pos):
                self.switchScene("recoverPassword")

    # ===========================================================
    # FACE LOGIN THREAD
    # ===========================================================

    def _start_face_recognition(self):
        from Reconocimientofacial import ReconocimientoFacialLBPH

        def _face_login():
            recog = ReconocimientoFacialLBPH()
            recog.running = True
            recog.login_con_rostro()

            nombre = None
            try:
                with open("last_face_login.txt", "r") as f:
                    nombre = f.read().strip()
            except:
                pass

            if not nombre:
                self.login_message = "Rostro no reconocido."
                return

            try:
                base = get_user(nombre, timeout=3.0)
                if isinstance(base, dict) and base.get("ok"):
                    base = base.get("user", {})

                prof = _try_fetch_profile(nombre)
                merged = _merge_dicts(base, prof)

                set_current_user(merged)

                pygame.event.post(
                    pygame.event.Event(LOGIN_SUCCESS, user=merged, target_scene="game_mode")
                )

            except:
                pygame.event.post(
                    pygame.event.Event(LOGIN_SUCCESS, user={"username": nombre}, target_scene="game_mode")
                )

        threading.Thread(target=_face_login, daemon=True).start()

    # ===========================================================
    # UPDATE
    # ===========================================================

    def update(self, deltaTime):

        # Si está bloqueado → actualizar mensaje
        if self._is_locked():
            self.login_message = f"Bloqueado {self._remaining_lock_seconds()} s…"

        # PLAN B PARA CAMBIO DE ESCENA
        if self._login_ok:
            self._login_ok = False
            try:
                set_current_user(self._merged_user)
            except:
                pass

            print(f"[LoginScene] (Plan B) Cambiando a: {self._target_scene}")
            self.switchScene(self._target_scene)
            return

        # Hover de botones
        mousePos = pygame.mouse.get_pos()
        for b in self.buttonsList:
            b.update(mousePos)

        # Hover del link
        if self.forgot_rect and self.forgot_rect.collidepoint(mousePos):
            self.forgot_hover = True
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            if self.forgot_hover:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.forgot_hover = False

    # ===========================================================
    # DRAW
    # ===========================================================

    def draw(self, screen):
        screen_width, screen_height = screen.get_size()
        rect_width, rect_height = 700, 850
        rect_x = (screen_width - rect_width) // 2
        rect_y = (screen_height - rect_height) // 2

        # Panel
        color_rgb = pygame.Color("#25201C")
        pygame.draw.rect(screen, color_rgb, (rect_x, rect_y, rect_width, rect_height), border_radius=30)

        # Título
        title_surface = self.title_font.render("Iniciar Sesión", True, (255, 255, 255))
        screen.blit(title_surface, (screen_width//2 - title_surface.get_width()//2, rect_y + 110))

        # Inputs
        self.usernameBox.draw(screen, 0)
        self.passwordBox.draw(screen, 0)

        # Forgot password
        link_color = self.forgot_color_hover if self.forgot_hover else self.forgot_color_normal
        forgot_surface = self.forgot_font.render(self.forgot_text, True, link_color)
        link_x = self.passwordBox.rect.right - forgot_surface.get_width() - 12
        link_y = self.passwordBox.rect.bottom + 10
        screen.blit(forgot_surface, (link_x, link_y))
        self.forgot_rect = pygame.Rect(link_x, link_y, forgot_surface.get_width(), forgot_surface.get_height())

        # underline
        if self.forgot_hover:
            pygame.draw.line(screen, link_color,
                             (link_x, link_y + forgot_surface.get_height() - 1),
                             (link_x + forgot_surface.get_width(), link_y + forgot_surface.get_height() - 1), 1)

        # Buttons
        for b in self.buttonsList:
            b.draw(screen)

        # Divider
        div_font = pygame.font.Font(None, 28)
        div_surf = div_font.render(self.divider_text, True, self.divider_color)
        screen.blit(div_surf,
                    (screen_width//2 - div_surf.get_width()//2,
                     self.registerButton.rect.bottom + 35))

        # Mensaje (error / bienvenido)
        if self.login_message:
            mf = pygame.font.Font(None, 28)
            surf = mf.render(self.login_message, True, (255, 255, 255))
            screen.blit(surf, (self.loginButton.rect.x, self.loginButton.rect.bottom - 100))
