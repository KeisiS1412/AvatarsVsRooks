import spotipy
from spotipy.oauth2 import SpotifyOAuth


CLIENT_ID = "4d1e4a4b9fde4c7bb50b846ce28cc972"
CLIENT_SECRET = "e810dbeae0034be79d91cae2f905b948"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-playback-state,user-modify-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

def get_active_device():
    devices = sp.devices()
    if not devices["devices"]:
        print("No hay ningún dispositivo activo. Abre Spotify en tu PC o celular.")
        return None
    return devices["devices"][0]["id"]

def play_track(nombre, artista):
    if artista:
        query = f"track:{nombre} artist:{artista}"
    else:
        query = f"track:{nombre}"

    results = sp.search(q=query, type="track", limit=1)
    if not results["tracks"]["items"]:
        print("No se encontró la canción con esos datos.")
        return

    track = results["tracks"]["items"][0]
    uri = track["uri"]
    name = track["name"]
    artist_names = ", ".join(a["name"] for a in track["artists"])

    device_id = get_active_device()
    if not device_id:
        return

    sp.start_playback(device_id=device_id, uris=[uri])
    print(f"Reproduciendo '{name}' de {artist_names}.")

def pause():
    sp.pause_playback()
    print("Pausado.")

def resume():
    sp.start_playback()
    print("Reproducción reanudada.")

def skip_next():
    sp.next_track()
    print("Siguiente pista.")

def skip_previous():
    sp.previous_track()
    print("Canción anterior.")

if __name__ == "__main__":
    print("Control remoto de Spotify Premium")
    print("Comandos: play, pause, resume, next, prev, salir\n")
    while True:
        comando = input(">> ").strip().lower()

        if comando == "play":
            nombre = input("Nombre de la canción: ").strip()
            artista = input("Artista (opcional, para afinar la búsqueda): ").strip()
            if nombre:
                play_track(nombre, artista)
            else:
                print("Debes escribir al menos el nombre de la canción.")
        elif comando == "pause":
            pause()
        elif comando == "resume":
            resume()
        elif comando == "next":
            skip_next()
        elif comando == "prev":
            skip_previous()
        elif comando in ("salir", "exit"):
            break
        else:
            print("Comando no reconocido.")
