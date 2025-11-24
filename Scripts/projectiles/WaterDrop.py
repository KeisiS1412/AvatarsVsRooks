# Scripts/projectiles/WaterDrop.py
from projectiles.Projectile import Projectile

class WaterDrop(Projectile):
    """Gota de agua que cae verticalmente por la misma columna."""
    def __init__(self, cell_size):
        super().__init__(
            spritesheet_path="Assets/towersprojectiles/waterdrop.png",  # <-- pon tu ruta real
            frames_cols=4,     # si tu spritesheet tiene otro layout, ajusta
            frames_rows=1,
            fps=8,
            cell_size=cell_size,
            scale_fit=0.37,    # tamaño relativo a la celda
            crop_left=0, crop_right=0, crop_top=0, crop_bottom=0,
            pixel_art=False,
            use_rows=(0,),
            use_cols=None,     # usa todos los cuadros de la fila
            speed_px_s=315.0,
            vx=0.0,
            vy=315.0          # hacia abajo
        )
