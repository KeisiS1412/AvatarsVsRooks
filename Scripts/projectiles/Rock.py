# Scripts/projectiles/SandShard.py
from projectiles.Projectile import Projectile

class Rock(Projectile):
    """Fragmento de arena/polvo que cae verticalmente por la misma columna."""
    def __init__(self, cell_size):
        super().__init__(
            spritesheet_path="Assets/towersprojectiles/rock.png",  # <-- pon tu ruta real
            frames_cols=4,         # ajusta si tu sheet difiere
            frames_rows=1,
            fps=6,                # animación fluida
            cell_size=cell_size,
            scale_fit=0.42,        # un poco más pequeño que el agua/fuego
            crop_left=0, crop_right=0, crop_top=0, crop_bottom=0,
            pixel_art=False,
            use_rows=(0,),
            use_cols=None,        # usa todos los cuadros de esa fila
            speed_px_s=300.0,
            vx=0.0,
            vy=300.0               # hacia abajo
        )
