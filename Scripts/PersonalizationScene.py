# PersonalizationScene.py
import os
import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from Dropdown import Dropdown
from InfoField import InfoField
from ColorWheel import ColorWheel


try:
    from dotenv import load_dotenv
    load_dotenv()
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except Exception:
    spotipy = None
    SpotifyOAuth = None

BASE_W, BASE_H = 1920, 1080

# Columna izquierda
LEFT_X      = 450
LEFT_Y0     = 300
LEFT_YSTEP  = 175

MUSIC_W, MUSIC_H   = 560, 100
SEARCH_W, SEARCH_H = 100, 100
THEME_W, THEME_H   = 300, 100
HEX_W, HEX_H       = 300, 100
WHEEL_RADIUS       = 80

# Columna derecha
RIGHT_CX   = 1360
RIGHT_Y0   = 450
RIGHT_DY   = 130
RIGHT_GAPX = 200

FIELD_W, FIELD_H      = 360, 100
EMAIL_EXTRA_WIDTH     = 40
AVATAR_R              = 68
AVATAR_POS            = (RIGHT_CX, 220)
BTN_PHOTO_W, BTN_PHOTO_H = 340, 46

# Índices de tema 
THEME_NAMES = ["Dark", "Default", "Bright"]
THEME_MULTS = [0.45, 1.00, 1.35]  
DEFAULT_THEME_INDEX = 1

TITLE_FONT_SIZE = 24

def mul(c, f): # Multiplica un color por un factor
    r, g, b = c
    return (max(0, min(255, int(r*f))),
            max(0, min(255, int(g*f))),
            max(0, min(255, int(b*f))))

def lum(c): # Calcula la luminancia de un color
    r, g, b = c
    return 0.2126*r + 0.7152*g + 0.0722*b

def is_dark(c):
    return lum(c) < 140

def MakeTitleFont():
    return pygame.font.Font("Assets/Avenir.ttf", TITLE_FONT_SIZE)


# Obtiene los datos del usuario actual desde la sesión
def GetCurrentUser():
    try:
        from session import get_current_user
        raw = get_current_user()
    except Exception:
        raw = None

    if not isinstance(raw, dict):
        raw = {}

    perfil = raw.get("perfil") if isinstance(raw.get("perfil"), dict) else {}

    # Tomar apellido1/2 si ya vienen separados
    ap1 = perfil.get("apellido1", "")
    ap2 = perfil.get("apellido2", "")

    # dividir 'apellidos'
    if not ap1 and not ap2:
        ap_combo = perfil.get("apellidos")
        if isinstance(ap_combo, str):
            parts = ap_combo.strip().split()
            ap1 = parts[0] if parts else ""
            ap2 = " ".join(parts[1:]) if len(parts) > 1 else ""

    return {
        "usuario":   raw.get("username") or raw.get("usuario") or "",
        "nombre":    perfil.get("nombre", "Nombre"),
        "apellido1": ap1,
        "apellido2": ap2,
        "email":     raw.get("email") or perfil.get("email", ""),
        "telefono":  perfil.get("telefono", ""),
        "hobbie":    perfil.get("hobbie", ""),
        "cumple":    perfil.get("cumple") or perfil.get("fecha_nacimiento") or perfil.get("birthday") or "",
        "foto":      perfil.get("foto") or raw.get("avatar"),
        "_raw":      raw
    }




"""Escena de personalización del usuario, incluyendo música y tema visual"""
class PersonalizationScene(Scene):
    def __init__(self, font, res, switchSceneCallback):  
        self.font = font
        self.res = res
        self.switchScene = switchSceneCallback

        self.title_font_big = pygame.font.Font("Assets/Avenir.ttf", 56)

        self._sp = None
        self._spotify_available = (spotipy is not None and SpotifyOAuth is not None)
        self._last_play_query = None
        self.music_muted = False

        self.musicBox = TextBox(
            LEFT_X + 10, LEFT_Y0 + 0*LEFT_YSTEP, MUSIC_W, MUSIC_H,
            self.font, (235, 235, 235), (210, 210, 210), "Song",
            content_offset_y=30, border_radius=8
        )
        
        search_x = LEFT_X + MUSIC_W//2 + SEARCH_W//2 + 12
        self.searchBtn = Button(
            search_x - 20, LEFT_Y0 + 0*LEFT_YSTEP, SEARCH_W, SEARCH_H, "🔍",
            self.font, (220, 220, 220), (200, 200, 200)
        )
        
        self.muteBtn = Button(
            LEFT_X - 120, LEFT_Y0 + 1*LEFT_YSTEP, 300, MUSIC_H,
            "Mute Music", self.font, (235, 235, 235), (210, 210, 210)
        )

        self.returnBtn = Button(
            120, 70, 150, 60, "Return",
            self.font, (235, 235, 235), (210, 210, 210)
        )
        self.returnBtn.on_click = lambda: self.switchScene("main") if self.switchScene else None

        self.themeDrop = Dropdown(
            LEFT_X - 120, LEFT_Y0 + 3*LEFT_YSTEP, THEME_W, THEME_H,
            self.font, THEME_NAMES, initial_index=DEFAULT_THEME_INDEX,
            content_offset_y=16,
            title="Theme",
            title_font=MakeTitleFont(),  
            title_color=(120, 120, 120)
        )

        self.colorHexField = InfoField(
            LEFT_X - 120, LEFT_Y0 + 2*LEFT_YSTEP, HEX_W, HEX_H,
            self.font, "Background Color", "#FFFFFF",
            title_font=MakeTitleFont(), content_offset_y=16
        )
        
        hex_rect = self.colorHexField.rect
        self.colorWheel = ColorWheel(
            center=(hex_rect.centerx + 340, hex_rect.centery),
            radius=WHEEL_RADIUS
        )

        self.user = GetCurrentUser()
        self.avatar_pos = AVATAR_POS
        self.avatar_r = AVATAR_R
        
        self.changePhotoBtn = Button(
            RIGHT_CX, self.avatar_pos[1] + self.avatar_r + 45,
            BTN_PHOTO_W, BTN_PHOTO_H, "Change Profile Picture",
            MakeTitleFont(), (220, 220, 220), (200, 200, 200)
        )

        # Campos de información
        w, h = FIELD_W, FIELD_H
        xL = RIGHT_CX - RIGHT_GAPX
        xR = RIGHT_CX + RIGHT_GAPX
        y0 = RIGHT_Y0
        dy = RIGHT_DY
        tf = MakeTitleFont()

        self.f_nombre = InfoField(xL, y0 + 0*dy, w, h, self.font, "First Name", self.user["nombre"], title_font=tf, content_offset_y=16)
        self.f_ap1 = InfoField(xR, y0 + 0*dy, w, h, self.font, "Last Name 1", self.user["apellido1"], title_font=tf, content_offset_y=16)
        self.f_ap2 = InfoField(xL, y0 + 1*dy, w, h, self.font, "Last Name 1", self.user["apellido2"], title_font=tf, content_offset_y=16)
        self.f_usuario = InfoField(xR, y0 + 1*dy, w, h, self.font, "Username", self.user["usuario"], title_font=tf, content_offset_y=16)
        self.f_email = InfoField(RIGHT_CX, y0 + 2*dy, 2*w + EMAIL_EXTRA_WIDTH, h, self.font, "Email", self.user["email"], title_font=tf, content_offset_y=16)
        self.f_tel = InfoField(xL, y0 + 3*dy, w, h, self.font, "Phone Number", self.user["telefono"], title_font=tf, content_offset_y=16)
        
        self.hobbyDrop = Dropdown(
            xR, y0 + 3*dy, w, h, self.font,
            ["Sports", "Music", "Art"],
            initial_index=(["Sports", "Music", "Art"].index(self.user["hobbie"]) if self.user["hobbie"] in ["Sports", "Music", "Art"] else 0),
            content_offset_y=16,
            title="Hobbie",
            title_font=MakeTitleFont(),
            title_color=(120, 120, 120)
        )
        
        # Colores de tema
        self.theme_bg = (245, 245, 245)
        self.theme_ui = (220, 220, 220)
        self.theme_fg = (0, 0, 0)

        self.ApplyTheme()

    # Refresca los datos del usuario desde la sesión
    def refresh_user(self):
        self.user = GetCurrentUser()

        def put(widget, key):
            if widget is None: return
            val = self.user.get(key, "")
            try:
                widget.set_content(val)
            except Exception:
                try:
                    widget.text = val
                except Exception:
                    pass

        # Ajusta estos nombres a tus variables reales
        put(getattr(self, "f_nombre", None),   "nombre")
        put(getattr(self, "f_ap1", None),      "apellido1")
        put(getattr(self, "f_ap2", None),      "apellido2")
        put(getattr(self, "f_usuario", None),  "usuario")
        put(getattr(self, "f_email", None),    "email")
        put(getattr(self, "f_tel", None),      "telefono")

        # Dropdown de hobbie 
        try:
            dd = getattr(self, "hobbyDrop", None)
            if dd:
                raw_val = (self.user.get("hobbie") or "").strip()

                import unicodedata
                def norm(s):
                    s = s.strip().lower()
                    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
                    return s

                v = norm(raw_val)

                alias = {
                    "deportes": "Sports",
                    "sport": "Sports",
                    "sports": "Sports",
                    "musica": "Music",
                    "music": "Music",
                    "películas": "Movies",
                    "movies": "Movies",
                }
                target = alias.get(v, raw_val)  

                if hasattr(dd, "set_value"):
                    dd.set_value(target)
                else:
                    options = getattr(dd, "options", None)
                    if isinstance(options, (list, tuple)) and options:
                        def opt_value(item):
                            return item[1] if isinstance(item, (list, tuple)) and len(item) >= 2 else item
                        vals = [opt_value(o) for o in options]
                        idx = vals.index(target) if target in vals else 0
                        dd.index = idx
        except Exception:
            pass


        self.avatar_path = self.user.get("foto", None)

    
    def EnsureSpotify(self): # Setup Spotify client
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

    # Obtener el ID del dispositivo activo en Spotify
    def GetActiveDeviceID(self):
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

    # Analiza texto de la caja de música
    def ParseSongArtist(self, text):
        """Acepta: 'Canción - Artista', 'Canción / Artista', 'Canción, Artista' o solo 'Canción'."""
        if not text:
            return ("", "")
        seps = [" - ", " / ", ", "]
        for sep in seps:
            if sep in text:
                name, artist = text.split(sep, 1)
                return (name.strip(), artist.strip())
        return (text.strip(), "")

    # Reproduce canción desde la caja de texto
    def PlayMusicFromTextbox(self):
        if not self.EnsureSpotify():
            return
        query = getattr(self.musicBox, "text", "").strip()
        if not query:
            print("[Spotify] Escribe una canción (y opcionalmente el artista).")
            return

        name, artist = self.ParseSongArtist(query)
        try:
            q = f"track:{name}" + (f" artist:{artist}" if artist else "")
            results = self._sp.search(q=q, type="track", limit=1)
            items = results.get("tracks", {}).get("items", [])
            if not items:
                print("[Spotify] No se encontró la canción con esos datos.")
                return
            track = items[0]
            uri = track["uri"]
            device_id = self.GetActiveDeviceID()
            if not device_id:
                return
            self._sp.start_playback(device_id=device_id, uris=[uri])
            self._last_play_query = query
            self.music_muted = False
            print(f"[Spotify] Reproduciendo '{track['name']}' - {', '.join(a['name'] for a in track['artists'])}")
        except Exception as e:
            print(f"[Spotify] Error al reproducir: {e}")

    # Pausar música
    def SpotifyPause(self):
        if not self.EnsureSpotify():
            return
        try:
            self._sp.pause_playback()
            print("[Spotify] Pausado.")
        except Exception as e:
            print(f"[Spotify] Error al pausar: {e}")

    # Reanudar música
    def SpotifyResume(self):
        if not self.EnsureSpotify():
            return
        try:
            self._sp.start_playback()
            print("[Spotify] Reproducción reanudada.")
        except Exception as e:
            print(f"[Spotify] Error al reanudar: {e}")

    # Manejar eventos de entrada
    def handleEvent(self, event):
        screen = pygame.display.get_surface()
        if screen and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            tw, th = screen.get_size()
            scale = min(tw / BASE_W, th / BASE_H)
            offs_x = (tw - BASE_W * scale) / 2
            offs_y = (th - BASE_H * scale) / 2

            ed = event.dict.copy()
            if 'pos' in ed:
                px, py = ed['pos']
                sx = (px - offs_x) / scale
                sy = (py - offs_y) / scale
                ed['pos'] = (int(sx), int(sy))
            if event.type == pygame.MOUSEMOTION and 'rel' in ed:
                rx, ry = ed['rel']
                ed['rel'] = (rx / scale, ry / scale)

            mapped = pygame.event.Event(event.type, ed)
        else:
            mapped = event

        self.musicBox.handleEvent(mapped)
        self.themeDrop.handleEvent(mapped)
        self.hobbyDrop.handleEvent(mapped)
        self.colorWheel.handleEvent(mapped)
        self.colorHexField.set_content(self.colorWheel.hex())

        if self.searchBtn.wasClicked(mapped):
            self.PlayMusicFromTextbox()

        if self.changePhotoBtn.wasClicked(mapped):
            pass

        if self.muteBtn.wasClicked(mapped):
            if not self.music_muted:
                self.SpotifyPause()
                self.music_muted = True
                self.muteBtn.text = "Unmute Music"
            else:
                self.SpotifyResume()
                self.music_muted = False
                self.muteBtn.text = "Mute Music"

        if hasattr(self.returnBtn, "handle"):
            self.returnBtn.handle(mapped)
        elif hasattr(self.returnBtn, "wasClicked") and self.returnBtn.wasClicked(mapped):
            if self.switchScene:
                self.switchScene("main")

    # Actualizar lógica de la escena
    def update(self, dt):
        base = self.colorWheel.selected  
        t_index = self.themeDrop.index
        k = THEME_MULTS[t_index]

        bg = mul(base, k)
        ui = mul(bg, 0.75)
        fg = (255, 255, 255) if is_dark(ui) else (0, 0, 0)

        self.theme_bg, self.theme_ui, self.theme_fg = bg, ui, fg
        self.ApplyTheme()

    # Dibujar la escena
    def draw(self, s):
        virt = pygame.Surface((BASE_W, BASE_H)).convert()
        virt.fill(self.theme_bg)

        virt.blit(self.title_font_big.render("Personalization", True, self.theme_fg), (350, 80))
        virt.blit(self.title_font_big.render("Profile", True, self.theme_fg), (BASE_W//2 + 325, 80))

        self.returnBtn.draw(virt)

        self.f_nombre.draw(virt)
        self.f_ap1.draw(virt)
        self.f_ap2.draw(virt)
        self.f_usuario.draw(virt)
        self.f_email.draw(virt)
        self.f_tel.draw(virt)
        self.hobbyDrop.draw(virt)

        self.musicBox.draw(virt, deltaTime=0)
        title_font = MakeTitleFont()
        t = title_font.render("Music", True, self.theme_fg)
        virt.blit(t, (self.musicBox.rect.x + 20, self.musicBox.rect.y - t.get_height() + 45))
        
        self.muteBtn.draw(virt)
        self.searchBtn.draw(virt)

        self.themeDrop.draw(virt)
        self.colorHexField.draw(virt)
        self.colorWheel.draw(virt)

        self.DrawAvatar(virt, self.avatar_pos, self.avatar_r, self.user.get("foto"))
        self.changePhotoBtn.draw(virt)

        tw, th = s.get_size()
        scale = min(tw / BASE_W, th / BASE_H)
        new_w, new_h = int(BASE_W * scale), int(BASE_H * scale)
        scaled = pygame.transform.smoothscale(virt, (new_w, new_h))
        offs_x = (tw - new_w) // 2
        offs_y = (th - new_h) // 2

        s.fill((0, 0, 0))
        s.blit(scaled, (offs_x, offs_y))

    # Dibuja el avatar del usuario
    def DrawAvatar(self, s, center, r, image_path):
        pygame.draw.circle(s, (210, 230, 255), center, r)
        pygame.draw.circle(s, (180, 200, 230), center, r, width=2)
        if image_path:
            try:
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.smoothscale(img, (2*r, 2*r))
                rect = img.get_rect(center=center)
                s.blit(img, rect)
            except Exception:
                pass

    # Aplica los colores del tema a los elementos UI
    def ApplyTheme(self):
        info_fields = [
            self.f_nombre, self.f_ap1, self.f_ap2,
            self.f_usuario, self.f_email, self.f_tel,
            self.colorHexField
        ]

        for f in info_fields:
            f.bg = self.theme_ui
            f.text_color = self.theme_fg
            f.title_color = self.theme_fg
            f.border_color = mul(self.theme_ui, 0.65)

        # Dropdowns
        def PaintDropdowns(dd):
            dd.color_bg = self.theme_ui
            dd.color_hover = mul(self.theme_ui, 0.95)
            dd.color_text = self.theme_fg
            dd.title_color = self.theme_fg
            dd.border_color = mul(self.theme_ui, 0.75)
            dd.arrow_color = self.theme_fg
            dd.button_bg = mul(self.theme_ui, 0.92)
            dd.button_hover = mul(self.theme_ui, 0.88)

        PaintDropdowns(self.hobbyDrop)
        PaintDropdowns(self.themeDrop)
        self.refresh_user()

        # TextBox de Música
        self.musicBox.inactiveColor = self.theme_ui
        self.musicBox.activeColor = mul(self.theme_ui, 0.92)
        self.musicBox.textColor = self.theme_fg
        self.musicBox.currentColor = self.musicBox.activeColor if self.musicBox.isActive else self.musicBox.inactiveColor

        # Botones
        def PaintButton(b):
            btn_base = mul(self.theme_ui, 0.88)
            btn_hover = mul(self.theme_ui, 0.82)

            if hasattr(b, "normalColor"): b.normalColor = btn_base
            if hasattr(b, "overColor"): b.overColor = btn_hover
            if hasattr(b, "idleColor"): b.idleColor = btn_base
            if hasattr(b, "hoverColor"): b.hoverColor = btn_hover
            if hasattr(b, "textColor"): b.textColor = self.theme_fg
            if hasattr(b, "fontColor"): b.fontColor = self.theme_fg

            b.currentColor = b.overColor if getattr(b, "isHover", False) else b.normalColor

        for b in [self.searchBtn, self.muteBtn, self.changePhotoBtn, self.returnBtn]:
            PaintButton(b)

    



