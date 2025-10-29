from towers.FireTower import FireTower
from towers.WaterTower import WaterTower
from towers.SandTower import SandTower
from towers.RockTower import RockTower

class TowerFactory:
    """Fábrica para crear torres según el tipo seleccionado en el panel."""

    @staticmethod
    def create_tower(tower_type: str, cell_size, cell_topleft, row, col):
        tower_type = tower_type.lower()
        if tower_type == "fire":
            return FireTower(cell_size, cell_topleft, row, col)
        elif tower_type == "water":
            return WaterTower(cell_size, cell_topleft, row, col)
        elif tower_type == "sand":
            return SandTower(cell_size, cell_topleft, row, col)
        elif tower_type == "rock":
            return RockTower(cell_size, cell_topleft, row, col)
        else:
            print(f"[TowerFactory] Tipo desconocido: {tower_type}")
            return None
