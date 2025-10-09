# PersonalizationScene.py
import os
import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from Dropdown import Dropdown
from InfoField import InfoField
from ColorWheel import ColorWheel

# >>> SPOTIFY: imports y .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except Exception:
    spotipy = None
    SpotifyOAuth = None

# Pantalla
BASE_W, BASE_H = 1920, 1080

# Columna izquierda
LEFT_X      = 450
LEFT_Y0     = 300
LEFT_YSTEP  = 175

MUSIC_W, MUSIC_H   = 560, 100
SEARCH_W, SEARCH_H = 100,  100
THEME_W, THEME_H   = 300, 100
HEX_W,   HEX_H     = 300, 100
WHEEL_RADIUS       = 80
WHEEL_Y_OFFSET     = 100

# Columna derecha
RIGHT_CX   = 1360
RIGHT_Y0   = 450
RIGHT_DY   = 130
RIGHT_GAPX = 200

FIELD_W, FIELD_H   = 360, 100
EMAIL_EXTRA_WIDTH  = 40
AVATAR_R           = 68
AVATAR_POS         = (RIGHT_CX, 220)
BTN_PHOTO_W, BTN_PHOTO_H = 340, 46

# Índices de tema 
THEME_NAMES = ["Dark", "Default", "Bright"]
THEME_MULTS = [0.45,   1.00,      1.35]  
DEFAULT_THEME_INDEX = 1                   


def mul(c, f):  # oscurece/aclara multiplicando
    r,g,b=c; return (max(0,min(255,int(r*f))),
                     max(0,min(255,int(g*f))),
                     max(0,min(255,int(b*f))))

def lum(c):
    r,g,b=c; return 0.2126*r + 0.7152*g + 0.0722*b

# Fuente
TITLE_FONT_SIZE = 24
def make_title_font():
    return pygame.font.Font("Avenir.ttf", TITLE_FONT_SIZE)

def darker(c, factor=0.82):
    r,g,b = c; return (max(0,int(r*factor)), max(0,int(g*factor)), max(0,int(b*factor)))

def lighten(c, factor=0.9):
    r,g,b=c; return (min(255,int(r+(255-r)*factor)),
                     min(255,int(g+(255-g)*factor)),
                     min(255,int(b+(255-b)*factor)))

def lum(c):
    r,g,b=c; return 0.2126*r+0.7152*g+0.0722*b

def is_dark(c):
    r,g,b = c
    L = 0.2126*r + 0.7152*g + 0.0722*b
    return L < 140  # umbral práctico

def fg_for(bg_rgb):
    return (255,255,255) if is_dark(bg_rgb) else (0,0,0)

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
    def __init__(self, font, res, switchSceneCallback):  
        self.font = font
        self.res = res                     
        self.switchScene = switchSceneCallback

        self.title_font_big = pygame.font.Font("Avenir.ttf", 56)  # títulos de secciones

        # >>> SPOTIFY: estado/cliente
        self._sp = None
        self._spotify_available = (spotipy is not None and SpotifyOAuth is not None)
        self._last_play_query = None
        self.music_muted = False  # también se usa para pause/resume

        # Columna izquierda
        # Música
        self.musicBox = TextBox(LEFT_X +10, LEFT_Y0 + 0*LEFT_YSTEP, MUSIC_W, MUSIC_H,
                                self.font, (235,235,235), (210,210,210), "Torero - Chayanne",
                                content_offset_y=16, border_radius=8)
        search_x = LEFT_X + MUSIC_W//2 + SEARCH_W//2 + 12
        self.searchBtn = Button(search_x - 20, LEFT_Y0 + 0*LEFT_YSTEP, SEARCH_W, SEARCH_H, "🔍",
                                self.font, (220,220,220), (200,200,200))
        
        # Mute/Unmute Music 
        self.muteBtn = Button(
            LEFT_X-120, LEFT_Y0 + 1*LEFT_YSTEP,  
            300, MUSIC_H,
            "Mute Music",
            self.font,
            (235,235,235),
            (210,210,210),
        )

        # Return
        self.returnBtn = Button(
            120, 70,
            150, 60,
            "Return",
            self.font,
            (235,235,235),
            (210,210,210),
        )

        def _go_main():
            if self.switchScene:
                self.switchScene("main")
        self.returnBtn.on_click = _go_main


        
        def _go_to_main():
            if self.switchScene:
                self.switchScene("main")
        self.returnBtn.on_click = _go_to_main

        # Tema
        self.themeDrop = Dropdown(
            LEFT_X-120, LEFT_Y0 + 3*LEFT_YSTEP, THEME_W, THEME_H,
            self.font, THEME_NAMES, initial_index=DEFAULT_THEME_INDEX,
            content_offset_y=16,
            title="Theme",
            title_font=make_title_font(),  
            title_color=(120,120,120))

        # Color de fondo
        self.colorHexField = InfoField(LEFT_X - 120, LEFT_Y0 +2*LEFT_YSTEP, HEX_W, HEX_H,
                                       self.font, "Background Color", "#FFFFFF",
                                       title_font=make_title_font(), content_offset_y=16)
        hex_rect = self.colorHexField.rect
        self.colorWheel = ColorWheel(
            center=(hex_rect.centerx + 340, hex_rect.centery),
            radius=WHEEL_RADIUS
        )

        # Columna derecha
        self.user = get_current_user()
        self.avatar_pos = AVATAR_POS
        self.avatar_r   = AVATAR_R
        self.changePhotoBtn = Button(RIGHT_CX, self.avatar_pos[1] + self.avatar_r + 45,
                                     BTN_PHOTO_W, BTN_PHOTO_H, "Change Profile Picture",
                                     make_title_font(), (220,220,220), (200,200,200))

        w, h = FIELD_W, FIELD_H
        xL = RIGHT_CX - RIGHT_GAPX
        xR = RIGHT_CX + RIGHT_GAPX
        y0 = RIGHT_Y0
        dy = RIGHT_DY
        tf = make_title_font()

        small_title_font = pygame.font.Font("Avenir.ttf", TITLE_FONT_SIZE)

        self.f_nombre   = InfoField(xL, y0 + 0*dy, w, h, self.font, "First Name",     self.user["nombre"],   title_font=small_title_font, content_offset_y=16)
        self.f_ap1      = InfoField(xR, y0 + 0*dy, w, h, self.font, "Last Name 1", self.user["apellido1"],title_font=small_title_font, content_offset_y=16)

        self.f_ap2      = InfoField(xL, y0 + 1*dy, w, h, self.font, "Last Name 1", self.user["apellido2"],title_font=small_title_font, content_offset_y=16)
        self.f_usuario  = InfoField(xR, y0 + 1*dy, w, h, self.font, "Username",    self.user["usuario"],  title_font=small_title_font, content_offset_y=16)

        self.f_email    = InfoField(RIGHT_CX, y0 + 2*dy, 2*w + EMAIL_EXTRA_WIDTH, h,
                        self.font, "Email", self.user["email"], title_font=small_title_font, content_offset_y=16)

        self.f_tel      = InfoField(xL, y0 + 3*dy, w, h, self.font, "Phone Number", self.user["telefono"], title_font=small_title_font, content_offset_y=16)
        self.hobbyDrop  = Dropdown(
            xR, y0 + 3*dy, w, h, self.font,
            ["Sports","Music","Art"],
            initial_index=(["Sports","Music","Art"].index(self.user["hobbie"])
                if self.user["hobbie"] in ["Sports","Music","Art"] else 0),
            content_offset_y=16,
            title="Hobbie",
            title_font=make_title_font(),
            title_color=(120,120,120)
        )
        self.theme_bg = (245,245,245)   # color de fondo de la pantalla
        self.theme_ui = (220,220,220)   # color de elementos (más oscuro que fondo)
        self.theme_fg = (0,0,0)         # color de texto

        self._apply_theme()

    def _ensure_spotify(self):
        """Inicializa el cliente de Spotify si hace falta."""
        if not self._spotify_available:
            print("[Spotify] Spotipy no disponible. Instala 'spotipy' y 'python-dotenv'.")
            return False
        if self._sp is None:
            cid = os.getenv("SPOTIPY_CLIENT_ID")
            csc = os.getenv("SPOTIPY_CLIENT_SECRET")
            red = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
            scope = os.getenv("SPOTIPY_SCOPE", "user-read-playback-state,user-modify-playback-state")

            if not cid or not csc:
                print("[Spotify] Falta SPOTIPY_CLIENT_ID/SECRET en .env")
                return False

            self._sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=cid, client_secret=csc, redirect_uri=red, scope=scope
                )
            )
        return True

    def _get_active_device_id(self):
        try:
            devices = self._sp.devices()
            devs = devices.get("devices", [])
            if not devs:
                print("[Spotify] No hay dispositivo activo. Abre Spotify en tu PC o celular.")
                return None
            return devs[0].get("id")
        except Exception as e:
            print(f"[Spotify] Error al obtener dispositivos: {e}")
            return None

    def _parse_song_artist(self, text):
        """Acepta: 'Canción - Artista', 'Canción / Artista', 'Canción, Artista' o solo 'Canción'."""
        if not text:
            return ("", "")
        seps = [" - ", " / ", ", "]
        for sep in seps:
            if sep in text:
                name, artist = text.split(sep, 1)
                return (name.strip(), artist.strip())
        # si no contiene separador, todo es 'canción'
        return (text.strip(), "")

    def _play_from_textbox(self):
        if not self._ensure_spotify():
            return
        # Usa el texto que el usuario escribió
        query = getattr(self.musicBox, "text", "").strip()
        if not query:
            print("[Spotify] Escribe una canción (y opcionalmente el artista).")
            return

        name, artist = self._parse_song_artist(query)
        try:
            q = f"track:{name}" + (f" artist:{artist}" if artist else "")
            results = self._sp.search(q=q, type="track", limit=1)
            items = results.get("tracks", {}).get("items", [])
            if not items:
                print("[Spotify] No se encontró la canción con esos datos.")
                return
            track = items[0]
            uri = track["uri"]
            device_id = self._get_active_device_id()
            if not device_id:
                return
            self._sp.start_playback(device_id=device_id, uris=[uri])
            self._last_play_query = query
            self.music_muted = False
            print(f"[Spotify] Reproduciendo '{track['name']}' - {', '.join(a['name'] for a in track['artists'])}")
        except Exception as e:
            print(f"[Spotify] Error al reproducir: {e}")

    def _spotify_pause(self):
        if not self._ensure_spotify():
            return
        try:
            self._sp.pause_playback()
            print("[Spotify] Pausado.")
        except Exception as e:
            print(f"[Spotify] Error al pausar: {e}")

    def _spotify_resume(self):
        if not self._ensure_spotify():
            return
        try:
            self._sp.start_playback()
            print("[Spotify] Reproducción reanudada.")
        except Exception as e:
            print(f"[Spotify] Error al reanudar: {e}")

    def handleEvent(self, event):
        self.musicBox.handleEvent(event)
        self.themeDrop.handleEvent(event)
        self.hobbyDrop.handleEvent(event)
        self.colorWheel.handleEvent(event)

        if self.searchBtn.wasClicked(event):
            self._play_from_textbox()

        if self.changePhotoBtn.wasClicked(event):
            pass

        if self.muteBtn.wasClicked(event):
         # toggle pause/resume en Spotify
            if not self.music_muted:
                self._spotify_pause()
                self.music_muted = True
                self.muteBtn.text = "Unmute Music"
            else:
                self._spotify_resume()
                self.music_muted = False
                self.muteBtn.text = "Mute Music"

        if hasattr(self.returnBtn, "handle"):

            self.returnBtn.handle(event)
        else:
            if hasattr(self.returnBtn, "wasClicked") and self.returnBtn.wasClicked(event):
                if getattr(self, "switchScene", None):
                    self.switchScene("main")

    def update(self, dt):
        # Color base elegido en la rueda
        base = self.colorWheel.selected  

        # Índice de tema 
        t_index = self.themeDrop.index if hasattr(self, "themeDrop") else DEFAULT_THEME_INDEX
        k = THEME_MULTS[t_index]

        bg = mul(base, k)  # respeta el matiz base

        
        ui = mul(bg, 0.75)  # cajas más oscuras que el fondo
        L = 0.2126*ui[0] + 0.7152*ui[1] + 0.0722*ui[2]
        fg = (255,255,255) if L < 140 else (0,0,0)

        self.theme_bg, self.theme_ui, self.theme_fg = bg, ui, fg
        self._apply_theme()


    def _theme_factors(self):
        # valor del dropdown; si no existe, usa "Light"
        name = self.themeDrop.value if hasattr(self, "themeDrop") else "Light"
        return THEME_PRESETS.get(name, THEME_PRESETS["Light"])


    def draw(self, s):
        s.fill(self.theme_bg)

        s.blit(self.title_font_big.render("Personalization", True, self.theme_fg), (350, 80))
        s.blit(self.title_font_big.render("Profile", True, self.theme_fg), (BASE_W//2 + 350, 80))

        self.returnBtn.draw(s)

        self.f_nombre.draw(s);  self.f_ap1.draw(s)
        self.f_ap2.draw(s);     self.f_usuario.draw(s)
        self.f_email.draw(s)
        self.f_tel.draw(s);     self.hobbyDrop.draw(s)

        
        t = self.font.render("Music", True, self.theme_fg)
        s.blit(t, (self.musicBox.rect.x, self.musicBox.rect.y - 30 - t.get_height() + 10))

        self.musicBox.draw(s, deltaTime=0)
        self.muteBtn.draw(s)
        self.searchBtn.draw(s)

        self.themeDrop.draw(s)

        self.colorHexField.draw(s)
        self.colorWheel.draw(s)

        self._draw_avatar(s, self.avatar_pos, self.avatar_r, self.user["foto"] if hasattr(self, "user") else None)
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

    def _apply_theme(self):
        # InfoFields
        info_fields = [self.f_nombre, self.f_ap1, self.f_ap2,
               self.f_usuario, self.f_email, self.f_tel,
               self.colorHexField]

        for f in info_fields:
            f.bg = self.theme_ui                      # fondo más oscuro
            f.text_color = self.theme_fg              # texto auto (blanco si oscuro)
            f.title_color = self.theme_fg
            f.border_color = (max(0,int(self.theme_ui[0]*0.65)),
                            max(0,int(self.theme_ui[1]*0.65)),
                            max(0,int(self.theme_ui[2]*0.65)))

        # Dropdowns (Theme y Hobbie si usas ambo

        def paint_dd(dd):
            dd.color_bg    = self.theme_ui
            dd.color_hover = (max(0,int(self.theme_ui[0]*0.95)),
                            max(0,int(self.theme_ui[1]*0.95)),
                            max(0,int(self.theme_ui[2]*0.95)))
            dd.color_text  = self.theme_fg
            dd.title_color = self.theme_fg
            dd.border_color= (max(0,int(self.theme_ui[0]*0.75)),
                            max(0,int(self.theme_ui[1]*0.75)),
                            max(0,int(self.theme_ui[2]*0.75)))
            dd.arrow_color = self.theme_fg

            # ⬇️ botón del dropdown (flecha) con el mismo “oscuro” que usas en botones
            btn_base = (max(0,int(self.theme_ui[0]*0.92)),
                        max(0,int(self.theme_ui[1]*0.92)),
                        max(0,int(self.theme_ui[2]*0.92)))
            btn_hover= (max(0,int(self.theme_ui[0]*0.88)),
                        max(0,int(self.theme_ui[1]*0.88)),
                        max(0,int(self.theme_ui[2]*0.88)))
            dd.button_bg    = btn_base
            dd.button_hover = btn_hover


        paint_dd(self.hobbyDrop)
        if hasattr(self, "themeDrop"):
            paint_dd(self.themeDrop)

        # TextBox de Música (si está en esta escena)
        if hasattr(self, "musicBox"):
            self.musicBox.inactiveColor = self.theme_ui
            self.musicBox.activeColor   = (max(0,int(self.theme_ui[0]*0.92)),
                                        max(0,int(self.theme_ui[1]*0.92)),
                                        max(0,int(self.theme_ui[2]*0.92)))
            self.musicBox.textColor     = self.theme_fg
            
            self.musicBox.currentColor  = self.musicBox.activeColor if self.musicBox.isActive else self.musicBox.inactiveColor

        # Botones de esta escena
        def paint_btn(b):
            btn_base  = (max(0, int(self.theme_ui[0]*0.88)),
                        max(0, int(self.theme_ui[1]*0.88)),
                        max(0, int(self.theme_ui[2]*0.88)))
            btn_hover = (max(0, int(self.theme_ui[0]*0.82)),
                        max(0, int(self.theme_ui[1]*0.82)),
                        max(0, int(self.theme_ui[2]*0.82)))

            if hasattr(b, "normalColor"): b.normalColor = btn_base
            if hasattr(b, "overColor"):   b.overColor   = btn_hover
            if hasattr(b, "idleColor"):   b.idleColor   = btn_base
            if hasattr(b, "hoverColor"):  b.hoverColor  = btn_hover

            # Texto según tono
            if hasattr(b, "textColor"): b.textColor = self.theme_fg
            if hasattr(b, "fontColor"): b.fontColor = self.theme_fg

            b.currentColor = b.overColor if getattr(b, "isHover", False) else b.normalColor

        for b in [self.searchBtn, self.muteBtn, self.changePhotoBtn, self.returnBtn]:
            paint_btn(b)


        

