from towers.FireTower import FireTower
from towers.WaterTower import WaterTower
from towers.SandTower import SandTower
from towers.RockTower import RockTower

class TowerFactory:
    """Fábrica para crear torres según el tipo seleccionado en el panel."""
    COSTS = {
        "sand": 50,    # Arena
        "rock": 100,   # Roca
        "fire": 150,   # Fuego
        "water": 150,  # Agua
    }
    @staticmethod
    def get_cost(tower_type: str) -> int:
        # Devuelve el costo de la torre según su tipo.
        return TowerFactory.COSTS.get((tower_type or "").lower(), 0)

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
