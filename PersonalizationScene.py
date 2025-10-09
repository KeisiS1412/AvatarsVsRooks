# PersonalizationScene.py
import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from Dropdown import Dropdown
from InfoField import InfoField
from ColorWheel import ColorWheel

# =========================
#  L A Y O U T  C O N F I G
# =========================
BASE_W, BASE_H = 1920, 1080

# ---- Columna IZQUIERDA (Personalización)
LEFT_X      = 450
LEFT_Y0     = 300
LEFT_YSTEP  = 200

# Tamaños izquierda
MUSIC_W, MUSIC_H   = 560, 100
SEARCH_W, SEARCH_H = 100,  100
THEME_W, THEME_H   = 300, 100
HEX_W,   HEX_H     = 300, 100
WHEEL_RADIUS       = 80
WHEEL_Y_OFFSET     = 100

# ---- Columna DERECHA (Perfil)
RIGHT_CX   = 1360
RIGHT_Y0   = 450
RIGHT_DY   = 130
RIGHT_GAPX = 200

# Tamaños derecha
FIELD_W, FIELD_H   = 360, 100
EMAIL_EXTRA_WIDTH  = 40
AVATAR_R           = 68
AVATAR_POS         = (RIGHT_CX, 220)
BTN_PHOTO_W, BTN_PHOTO_H = 340, 46

# ---- Tipografías
TITLE_FONT_SIZE = 24   # títulos de los campos (más pequeño)
def make_title_font():
    return pygame.font.Font("Avenir.ttf", TITLE_FONT_SIZE)

# ===== Mock de “BD” =====
def get_current_user():
    return {
        "foto": None,
        "nombre": "Jorge",
        "apellido1": "Jorge",
        "apellido2": "Jorge",
        "usuario": "jorgito13",
        "email": "jorgito13@gmail.com",
        "telefono": "8983 3272",
        "hobbie": "Deportes",
    }

class PersonalizationScene(Scene):
    def __init__(self, font):
        self.font = font
        self.title_font_big = pygame.font.Font("Avenir.ttf", 56)  # títulos de secciones

        # ========= IZQUIERDA: Personalización =========
        # Música
        self.musicBox = TextBox(LEFT_X +10, LEFT_Y0 + 0*LEFT_YSTEP, MUSIC_W, MUSIC_H,
                                self.font, (235,235,235), (210,210,210), "Torero - Chayanne",
                                content_offset_y=16, border_radius=8)
        search_x = LEFT_X + MUSIC_W//2 + SEARCH_W//2 + 12
        self.searchBtn = Button(search_x - 20, LEFT_Y0 + 0*LEFT_YSTEP, SEARCH_W, SEARCH_H, "🔍",
                                self.font, (220,220,220), (200,200,200))

        # Tema
        self.themeDrop = Dropdown(
            LEFT_X-120, LEFT_Y0 + 2*LEFT_YSTEP, THEME_W, THEME_H,
            self.font, ["Claro", "Medio", "Oscuro"], initial_index=0,
            content_offset_y=16,
            title="Tema",
            title_font=make_title_font(),  # igual que InfoField
            title_color=(120,120,120))

        # Color de fondo
        self.colorHexField = InfoField(LEFT_X - 120, LEFT_Y0 +1*LEFT_YSTEP, HEX_W, HEX_H,
                                       self.font, "Color de fondo", "#FFFFFF",
                                       title_font=make_title_font(), content_offset_y=16)
        hex_rect = self.colorHexField.rect
        self.colorWheel = ColorWheel(
            center=(hex_rect.centerx + 340, hex_rect.centery),  # 340 es ejemplo, ajusta horizontalmente
            radius=WHEEL_RADIUS
)

        # ========= DERECHA: Perfil =========
        self.user = get_current_user()
        self.avatar_pos = AVATAR_POS
        self.avatar_r   = AVATAR_R
        self.changePhotoBtn = Button(RIGHT_CX, self.avatar_pos[1] + self.avatar_r + 45,
                                     BTN_PHOTO_W, BTN_PHOTO_H, "Cambiar foto de perfil",
                                     make_title_font(), (220,220,220), (200,200,200))

        w, h = FIELD_W, FIELD_H
        xL = RIGHT_CX - RIGHT_GAPX
        xR = RIGHT_CX + RIGHT_GAPX
        y0 = RIGHT_Y0
        dy = RIGHT_DY
        tf = make_title_font()

        # Usa la misma fuente que el resto, pero tamaño más pequeño para los títulos
        small_title_font = pygame.font.Font("Avenir.ttf", TITLE_FONT_SIZE)

        self.f_nombre   = InfoField(xL, y0 + 0*dy, w, h, self.font, "Nombre",     self.user["nombre"],   title_font=small_title_font, content_offset_y=16)
        self.f_ap1      = InfoField(xR, y0 + 0*dy, w, h, self.font, "Apellido 1", self.user["apellido1"],title_font=small_title_font, content_offset_y=16)

        self.f_ap2      = InfoField(xL, y0 + 1*dy, w, h, self.font, "Apellido 2", self.user["apellido2"],title_font=small_title_font, content_offset_y=16)
        self.f_usuario  = InfoField(xR, y0 + 1*dy, w, h, self.font, "Usuario",    self.user["usuario"],  title_font=small_title_font, content_offset_y=16)

        self.f_email    = InfoField(RIGHT_CX, y0 + 2*dy, 2*w + EMAIL_EXTRA_WIDTH, h,
                        self.font, "Email", self.user["email"], title_font=small_title_font, content_offset_y=16)

        self.f_tel      = InfoField(xL, y0 + 3*dy, w, h, self.font, "Teléfono", self.user["telefono"], title_font=small_title_font, content_offset_y=16)
        self.hobbyDrop  = Dropdown(
            xR, y0 + 3*dy, w, h, self.font,
            ["Deportes","Música","Lectura"],
            initial_index=(["Deportes","Música","Lectura"].index(self.user["hobbie"])
                if self.user["hobbie"] in ["Deportes","Música","Lectura"] else 0),
            content_offset_y=16,
            title="Hobbie",
            title_font=make_title_font(),
            title_color=(120,120,120)
        )

    def handleEvent(self, event):
        self.musicBox.handleEvent(event)
        self.themeDrop.handleEvent(event)
        self.hobbyDrop.handleEvent(event)
        self.colorWheel.handleEvent(event)

        if self.searchBtn.wasClicked(event):
            pass

        if self.changePhotoBtn.wasClicked(event):
            pass

    def update(self, dt):
        self.colorHexField.set_value(self.colorWheel.hex())

    def draw(self, s):
        s.fill((245,245,245))

        s.blit(self.title_font_big.render("Personalización", True, (0,0,0)), (350, 80))
        s.blit(self.title_font_big.render("Perfil", True, (0,0,0)), (BASE_W//2 + 350, 80))

        self.f_nombre.draw(s);  self.f_ap1.draw(s)
        self.f_ap2.draw(s);     self.f_usuario.draw(s)
        self.f_email.draw(s)
        self.f_tel.draw(s);     self.hobbyDrop.draw(s)

        # IZQUIERDA (títulos encima de las cajas)
        # Usa la fuente principal para el título "Música"
        t = self.font.render("Música", True, (120,120,120))
        s.blit(t, (self.musicBox.rect.x, self.musicBox.rect.y - t.get_height() + 10))
        self.musicBox.draw(s, deltaTime=0)
        self.searchBtn.draw(s)

        # Tema (usa la fuente principal como "Música", pero tamaño pequeño)
        #t = self.font.render("Tema", True, (120,120,120))
        #s.blit(t, (self.themeDrop.rect.x, self.themeDrop.rect.y - t.get_height() + 10))
        self.themeDrop.draw(s)

        # Color de fondo (InfoField ya dibuja su propio título encima)
        self.colorHexField.draw(s)
        self.colorWheel.draw(s)

        # DERECHA
        self._draw_avatar(s, self.avatar_pos, self.avatar_r, self.user["foto"])
        self.changePhotoBtn.draw(s)

        

    # helpers
    def _draw_small_title(self, s, text, target_rect, color=(120,120,120)):
        title_font = make_title_font()
        t = title_font.render(text, True, color)
        s.blit(t, (target_rect.x, target_rect.y - t.get_height() + 4))

    def _draw_avatar(self, s, center, r, image_path):
        pygame.draw.circle(s, (210,230,255), center, r)
        pygame.draw.circle(s, (180,200,230), center, r, width=2)
        if image_path:
            try:
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.smoothscale(img, (2*r, 2*r))
                rect = img.get_rect(center=center)
                s.blit(img, rect)
            except Exception:
                pass
