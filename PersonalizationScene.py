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

# Fuente
TITLE_FONT_SIZE = 24
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

        # Tema
        self.themeDrop = Dropdown(
            LEFT_X-120, LEFT_Y0 + 3*LEFT_YSTEP, THEME_W, THEME_H,
            self.font, ["Light", "Medium", "Dark"], initial_index=0,
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

    # >>> SPOTIFY: helpers
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

        if self.returnBtn.wasClicked(event):
            # Aquí va la lógica para volver o salir
            pass

    def update(self, dt):
        self.colorHexField.set_value(self.colorWheel.hex())

    def draw(self, s):
        s.fill((245,245,245))

        s.blit(self.title_font_big.render("Personalización", True, (0,0,0)), (350, 80))
        s.blit(self.title_font_big.render("Perfil", True, (0,0,0)), (BASE_W//2 + 350, 80))

        self.returnBtn.draw(s)

        self.f_nombre.draw(s);  self.f_ap1.draw(s)
        self.f_ap2.draw(s);     self.f_usuario.draw(s)
        self.f_email.draw(s)
        self.f_tel.draw(s);     self.hobbyDrop.draw(s)

        t = self.font.render("Música", True, (120,120,120))
        s.blit(t, (self.musicBox.rect.x, self.musicBox.rect.y - t.get_height() + 10))
        self.musicBox.draw(s, deltaTime=0)
        self.muteBtn.draw(s) 
        self.searchBtn.draw(s)

        self.themeDrop.draw(s)

        self.colorHexField.draw(s)
        self.colorWheel.draw(s)

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
