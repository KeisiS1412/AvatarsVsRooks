from towers.Tower import Tower
from BaseTower import BaseTower

class WaterTower(Tower):
    """Torre de fuego animada desde columnas 0, 1 y 3 de la fila 0, con recorte lateral izquierdo."""

    def __init__(self, cell_size, cell_topleft, row, col):
        super().__init__(
            spritesheet_path="Assets/towers/water2.png",
            frames_cols=4,          # total de columnas del spritesheet
            frames_rows=2,          # total de filas del spritesheet
            fps=5,
            cell_size=cell_size,
            cell_topleft=cell_topleft,
            row=row,
            col=col,
            scale_fit=0.85,
            # Recorte manual para eliminar borde izquierdo de la torre vecina
            crop_left=15,           # recorte extra a la izquierda
            crop_right=0,
            crop_top=0,
            crop_bottom=25,
            anchor_bottom_center=True,
            pixel_art=False,
            use_rows=(0,),          # usa SOLO la fila 0
            use_cols=(0, 1, 2),     # usa solo las columnas 0, 1 y 3
        )

        BaseTower.__init__(self, hp=12)

        # Ajuste visual fino
        self.offset_fix_x = -5     # mueve ligeramente a la izquierda
        self.offset_fix_y = 0      # no mover verticalmente

        self.shoot_cooldown_ms = 1800
        self._shoot_accum = 0

    def tick_shoot(self, dt_ms: int) -> bool:
        self._shoot_accum += dt_ms
        if self._shoot_accum >= self.shoot_cooldown_ms:
            self._shoot_accum = 0
            return True
        return False