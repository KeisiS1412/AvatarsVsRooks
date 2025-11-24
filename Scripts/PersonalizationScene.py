# PersonalizationScene.py
import os
import pygame
from Scene import Scene
from Buttons import Button
from TextBoxes import TextBox
from Dropdown import Dropdown
from InfoField import InfoField
from ColorWheel import ColorWheel
from api_client import login_user, get_user, update_user_preferences  

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
        "perfil":    perfil,  # ← AGREGAR ESTA LÍNEA para tener acceso directo al perfil
        "_raw":      raw      # ← Mantener esto por compatibilidad
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
            120, 70, 150, 60, "Save",
            self.font, (235, 235, 235), (210, 210, 210)
        )
        self.returnBtn.on_click = self.save_preferences
        

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
        self.load_saved_preferences()
        
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

    def save_preferences(self):
        """Guarda las preferencias de color y tema del usuario"""
        username = self.user.get("usuario", "")
        if not username:
            print("No hay usuario en sesión")
            return
        
        # Obtener valores actuales
        color_hex = self.colorWheel.hex()
        theme_name = THEME_NAMES[self.themeDrop.index]
        song_query = getattr(self.musicBox, "text", "").strip()
        
        print(f"[Personalization] Guardando preferencias...")
        print(f"  Usuario: {username}")
        print(f"  Color: {color_hex}")
        print(f"  Tema: {theme_name}")
        print(f"  Canción: {song_query}")
        
        try:
            # Llamar al API para guardar
            result = update_user_preferences(username, color_hex, theme_name, song_query)
            
            if result.get("ok"):
                print("Preferencias guardadas exitosamente en el servidor")
                
                # Actualizar sesión local con las nuevas preferencias
                try:
                    from session import get_current_user, set_current_user
                    current = get_current_user()
                    
                    if isinstance(current, dict):
                        if "perfil" not in current:
                            current["perfil"] = {}
                        current["perfil"]["color_preferido"] = color_hex
                        current["perfil"]["tema_preferido"] = theme_name
                        set_current_user(current)
                        print("Sesión local actualizada")

                except Exception as e:
                    print(f"No se pudo actualizar sesión local: {e}")

                print("Cambiando a GameMode...")
                self.switchScene("game_mode")
                return

            else:
                print(f"Error del servidor: {result.get('error', 'unknown')}")

        except Exception as e:
            print(f"Error al guardar preferencias: {e}")
            import traceback
            traceback.print_exc()



    def load_saved_preferences(self):
        """Carga y aplica las preferencias de color y tema guardadas del usuario"""
        # El perfil está directamente en self.user["perfil"], no en self.user["_raw"]["perfil"]
        perfil = self.user.get("perfil", {})
        
        # Restaurar color guardado
        saved_color = perfil.get("color_preferido")
        
        if saved_color and isinstance(saved_color, str) and saved_color.startswith("#"):
            try:
                print(f"[Personalization] Cargando color guardado: {saved_color}")
                # Convertir hex a RGB para el ColorWheel
                hex_color = saved_color.lstrip("#")
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    self.colorWheel.selected = (r, g, b)
                    self.colorHexField.set_content(saved_color)
            
            except Exception as e:
                print(f"Error cargando color: {e}")
        else:
            print(f"No hay color guardado válido")
        
        # Restaurar tema guardado
        saved_theme = perfil.get("tema_preferido")
        
        if saved_theme and saved_theme in THEME_NAMES:
            try:
                theme_idx = THEME_NAMES.index(saved_theme)
                self.themeDrop.index = theme_idx
                print(f"Tema aplicado")
            except Exception as e:
                print(f"Error cargando tema: {e}")
        else:
            print(f"No hay tema guardado válido")

        saved_song = perfil.get("cancion_preferida")

        if saved_song and isinstance(saved_song, str) and saved_song.strip():
            try:
                print(f"[Personalization] Cargando canción guardada: {saved_song}")
                self.musicBox.text = saved_song
                
                # Reproducir automáticamente
                print(f"[Personalization] Reproduciendo canción guardada...")
                self.PlayMusicFromTextbox()
                print(f"✓ Canción cargada y reproduciendo")
            except Exception as e:
                print(f"✗ Error cargando/reproduciendo canción: {e}")

    def EnsureSpotify(self):
        """Inicializa el cliente de Spotify si hace falta."""
        if not self._spotify_available:
            print("[Spotify] Spotipy no disponible. Instala 'spotipy' y 'python-dotenv'.")
            return False
        
        if self._sp is None:
            
            cid = os.getenv("SPOTIPY_CLIENT_ID")
            csc = os.getenv("SPOTIPY_CLIENT_SECRET")
            red = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
            scope = os.getenv("SPOTIPY_SCOPE", "user-read-playback-state,user-modify-playback-state")

            print(f"[Spotify] Client ID: {cid[:10]}..." if cid else "[Spotify] Client ID no encontrado")
            print(f"[Spotify] Redirect URI: {red}")

            if not cid or not csc:
                print("[Spotify] ❌ Falta SPOTIPY_CLIENT_ID/SECRET en .env")
                return False

            try:
                self._sp = spotipy.Spotify(
                    auth_manager=SpotifyOAuth(
                        client_id=cid,
                        client_secret=csc,
                        redirect_uri=red,
                        scope=scope,
                        open_browser=True  # Abrirá el navegador para autorizar
                    )
                )
                print("[Spotify] ✓ Cliente inicializado correctamente")
            except Exception as e:
                print(f"[Spotify] ❌ Error al inicializar: {e}")
                return False
        
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
        self.musicBox.handleEvent(event)
        self.themeDrop.handleEvent(event)
        self.hobbyDrop.handleEvent(event)
        self.colorWheel.handleEvent(event)
        self.colorHexField.set_content(self.colorWheel.hex())

        if self.searchBtn.wasClicked(event):
            self.PlayMusicFromTextbox()

        if self.changePhotoBtn.wasClicked(event):
            pass

        if self.muteBtn.wasClicked(event):
            if not self.music_muted:
                self.SpotifyPause()
                self.music_muted = True
                self.muteBtn.text = "Unmute Music"
            else:
                self.SpotifyResume()
                self.music_muted = False
                self.muteBtn.text = "Mute Music"

        if hasattr(self.returnBtn, "wasClicked") and self.returnBtn.wasClicked(event):
            self.save_preferences() 

    # Actualizar lógica de la escena
    def update(self, dt):
        # Detectar si el usuario cambió (por ejemplo, después de login)
        current_username = self.user.get("usuario", "")
        
        try:
            from session import get_current_user
            session_user = get_current_user()
            session_username = ""
            if isinstance(session_user, dict):
                session_username = session_user.get("username") or session_user.get("usuario") or ""
        except Exception:
            session_username = ""
        
        # Si el usuario en sesión cambió, recargar
        if session_username and session_username != current_username:
            print(f"[PersonalizationScene] Usuario cambió de '{current_username}' a '{session_username}', recargando...")
            self.refresh_user()
            self.load_saved_preferences()
        
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
        s.fill(self.theme_bg)

        s.blit(self.title_font_big.render("Personalization", True, self.theme_fg), (350, 80))
        s.blit(self.title_font_big.render("Profile", True, self.theme_fg), (BASE_W//2 + 325, 80))

        self.returnBtn.draw(s)

        self.f_nombre.draw(s)
        self.f_ap1.draw(s)
        self.f_ap2.draw(s)
        self.f_usuario.draw(s)
        self.f_email.draw(s)
        self.f_tel.draw(s)
        self.hobbyDrop.draw(s)

        self.musicBox.draw(s, deltaTime=0)
        title_font = MakeTitleFont()
        t = title_font.render("Music", True, self.theme_fg)
        s.blit(t, (self.musicBox.rect.x + 20, self.musicBox.rect.y - t.get_height() + 45))
        
        self.muteBtn.draw(s)
        self.searchBtn.draw(s)

        self.themeDrop.draw(s)
        self.colorHexField.draw(s)
        self.colorWheel.draw(s)

        self.DrawAvatar(s, self.avatar_pos, self.avatar_r, self.user.get("foto"))
        self.changePhotoBtn.draw(s)

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

    





