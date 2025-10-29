# Scripts/projectiles/Fireball.py
from projectiles.Projectile import Projectile

class Fireball(Projectile):
    """Bola de fuego que cae verticalmente (misma columna)."""
    def __init__(self, cell_size):
        super().__init__(
            spritesheet_path="Assets/towersprojectiles/fireball.png",  # pon la ruta real
            frames_cols=4,
            frames_rows=1,
            fps=10,                  # animación fluida
            cell_size=cell_size,
            scale_fit=0.45,          # tamaño relativo a la celda
            crop_left=0, crop_right=0, crop_top=0, crop_bottom=0,
            pixel_art=False,
            use_rows=(0,),
            use_cols=None,           # usa los 4 cuadros
            speed_px_s=380.0,
            vx=0.0,
            vy=380.0                 # siempre hacia abajo
        )
