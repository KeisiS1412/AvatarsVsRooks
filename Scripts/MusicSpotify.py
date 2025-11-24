import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ================================
# CONFIGURACIÓN
# ================================
CLIENT_ID = "29ff3bf551d64df3b5ec7903feddaa6e"
CLIENT_SECRET = "77f418e192484324b4564067a1707d22"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-playback-state user-modify-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# ================================================
# BPM PROMEDIO POR GÉNERO (FALLBACK)
# ================================================
BPM_POR_GENERO = {
    "pop": 115,
    "rock": 125,
    "alternative": 120,
    "indie": 118,
    "latin": 100,
    "reggaeton": 95,
    "trap": 140,
    "hip hop": 90,
    "metal": 165,
    "dance": 128,
    "house": 124,
    "edm": 128,
    "electronic": 127,
    "salsa": 150,
    "bachata": 125,
}


def bpm_por_genero(nombre_cancion, artista):
    """
    Obtiene el género principal del artista desde Spotify
    y devuelve un BPM promedio basado en un diccionario.
    """
    try:
        query = f"track:{nombre_cancion} artist:{artista}" if artista else nombre_cancion
        res = sp.search(q=query, type="track", limit=1)

        if not res["tracks"]["items"]:
            return 115  # fallback universal

        track = res["tracks"]["items"][0]
        artista_id = track["artists"][0]["id"]

        info = sp.artist(artista_id)
        generos = info.get("genres", [])

        print("Géneros detectados:", generos)

        for g in generos:
            for base in BPM_POR_GENERO:
                if base.lower() in g.lower():
                    return BPM_POR_GENERO[base]

    except Exception:
        pass

    return 115  # fallback universal


# Obtener BPM + popularidad de la canción que suena ahora
def obtener_datos_cancion_actual():
    """
    Retorna:
        bpm_estimado (por género)
        popularidad (0-100)

    Siempre funciona:
    - Si hay errores => devuelve (None, None)
    - Usa bpm_por_genero(nombre, artista)
    """

    try:
        current = sp.current_playback()

        if not current or not current.get("item"):
            print("[MusicSpotify] No hay canción reproduciéndose.")
            return None, None

        track = current["item"]

        nombre = track["name"]
        artistas = ", ".join(a["name"] for a in track["artists"])

        # Popularidad real desde Spotify
        popularidad = track.get("popularity", 0)

        bpm = bpm_por_genero(nombre, artistas)

        print(f"[MusicSpotify] Actual → {nombre} — {artistas}")
        print(f"[MusicSpotify] Popularidad = {popularidad}")
        print(f"[MusicSpotify] BPM estimado según género = {bpm}")

        return bpm, popularidad

    except Exception as e:
        print(f"[MusicSpotify] Error obteniendo BPM/Popularidad: {e}")
        return None, None


# ================================================
# Obtener dispositivo activo
# ================================================
def get_active_device():
    try:
        devices = sp.devices()

        if not devices.get("devices"):
            print("No hay dispositivos activos. Abre Spotify en tu PC/celular.")
            return None

        return devices["devices"][0]["id"]

    except Exception as e:
        print("Error obteniendo dispositivos:", e)
        return None


# ================================================
# Reproducir canción (solo BPM por género)
# ================================================
def play_track(nombre, artista):
    if artista:
        query = f"track:{nombre} artist:{artista}"
    else:
        query = f"track:{nombre}"

    try:
        results = sp.search(q=query, type="track", limit=1)

        if not results["tracks"]["items"]:
            print("No se encontró la canción.")
            return

        track = results["tracks"]["items"][0]
        uri = track["uri"]
        name = track["name"]
        artist_names = ", ".join(a["name"] for a in track["artists"])

        print(f"Reproduciendo: {name} — {artist_names}")

        # Popularidad
        popularidad = track["popularity"]
        print(f"Popularidad: {popularidad}/100")

        # =============================
        # BPM por género (ÚNICO MÉTODO)
        # =============================
        bpm = bpm_por_genero(name, artist_names)
        print(f"Tempo estimado por género: {bpm} BPM")

        # Reproducir
        device_id = get_active_device()
        if device_id:
            sp.start_playback(device_id=device_id, uris=[uri])

    except Exception as e:
        print("Error al intentar reproducir:", e)


# ================================================
# Controles básicos
# ================================================
def pause():
    try:
        sp.pause_playback()
        print("Pausado.")
    except:
        print("No se pudo pausar.")

def resume():
    try:
        sp.start_playback()
        print("Reanudado.")
    except:
        print("No se pudo reanudar.")

def next_track():
    try:
        sp.next_track()
        print("Siguiente canción.")
    except:
        print("No se pudo cambiar a la siguiente.")

def prev_track():
    try:
        sp.previous_track()
        print("Canción anterior.")
    except:
        print("No se pudo retroceder.")


# ================================================
# Información de la canción actual
# ================================================
def info():
    try:
        current = sp.current_playback()

        if not current or not current.get("item"):
            print("No hay nada reproduciéndose.")
            return

        track = current["item"]
        name = track["name"]
        artistas = ", ".join(a["name"] for a in track["artists"])
        popularidad = track["popularity"]

        print(f"\nCanción actual: {name} — {artistas}")
        print(f"Popularidad: {popularidad}/100")

        bpm = bpm_por_genero(name, artistas)
        print(f"Tempo estimado por género: {bpm} BPM\n")

    except:
        print("Error obteniendo información.")


if __name__ == "__main__":

    print("Spotify Remote + BPM (solo género)")
    print("Comandos: play, pause, resume, next, prev, info, salir\n")

    while True:
        cmd = input(">> ").strip().lower()

        if cmd == "play":
            nombre = input("Nombre de canción: ")
            artista = input("Artista (opcional): ")
            play_track(nombre, artista)

        elif cmd == "pause":
            pause()

        elif cmd == "resume":
            resume()

        elif cmd == "next":
            next_track()

        elif cmd == "prev":
            prev_track()

        elif cmd == "info":
            info()

        elif cmd in ("salir", "exit"):
            break
        else:
            print("Comando no reconocido.")
