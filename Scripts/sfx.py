# sfx.py
import pygame

# Mapea eventos -> archivo de audio
# event puede ser: "avatar_sent", "avatar_hit", "tower_sent", "tower_hit"
# subtype (opcional) para diferenciar tipo de arma/torre.

_SFX_FILES = {
    # Avatars: ataque ENVIADO (distintos)
    ("avatar_sent", "arrow"):    "Sound/arrow_atack.mp3",   # (ojo al nombre del archivo)
    ("avatar_sent", "sword"):    "Sound/sword_attack.mp3",
    ("avatar_sent", "axe"):      "Sound/axe_attack.mp3",
    ("avatar_sent", "cannibal"): "Sound/cannibal_attack.m4a",

    # Avatars: impacto RECIBIDO (único)
    ("avatar_hit", None):        "Sound/avatar_grunt.mp3",

    # Torres: ataque ENVIADO (único)
    ("tower_sent", None):        "Sound/tower_attack.mp3",

    # Torres: impacto RECIBIDO (diferente por tipo)
    ("tower_hit", "fire"):       "Sound/fire_attacked.mp3",
    ("tower_hit", "water"):      "Sound/water_attacked.mp3",
    ("tower_hit", "sand"):       "Sound/sand_attacked.mp3",
    ("tower_hit", "rock"):       "Sound/rock_attacked.mp3",
}

_SOUNDS = {}
_INITIALIZED = False

def init_sfx():
    """Inicializa mixer y precarga los sonidos (idempotente)."""
    global _INITIALIZED
    if _INITIALIZED:
        return
    try:
        # Latencia pequeña y formato común
        pygame.mixer.pre_init(44100, -16, 2, 512)
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except Exception:
        # si falla el dispositivo de audio, dejamos sfx silencioso
        pass

    for key, path in _SFX_FILES.items():
        try:
            _SOUNDS[key] = pygame.mixer.Sound(path)
            _SOUNDS[key].set_volume(0.8)
        except Exception:
            _SOUNDS[key] = None  # tolerante a archivos faltantes

    _INITIALIZED = True

def sfx(event: str, subtype: str | None = None):
    """Reproduce el sonido para (event, subtype). Si no existe, no crashea."""
    snd = _SOUNDS.get((event, subtype))
    if snd is None:
        # intenta fallback sin subtype (para tower_sent/avatar_hit)
        snd = _SOUNDS.get((event, None))
    if snd is not None:
        snd.play()
