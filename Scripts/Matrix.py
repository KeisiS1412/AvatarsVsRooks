import pygame
from Coins import Coin
import random
from projectiles.FireBall import Fireball
from towers.FireTower import FireTower
from projectiles.WaterDrop import WaterDrop
from towers.WaterTower import WaterTower
from projectiles.SandShard import SandShard
from towers.SandTower import SandTower
from projectiles.Rock import Rock
from towers.RockTower import RockTower
from Enemies.ArcherEnemy import Archer
from projectiles.Arrow import Arrow
from Enemies.SquireEnemy import Squire
from projectiles.Sword import Sword
from Enemies.LumberjackEnemy import Lumberjack
from Enemies.CannibalEnemy import Cannibal

class Matrix:
    """Manejo visual y lógico de la matriz de juego, maneja instancias de Avatars, Rooks, monedas y torres."""
    def __init__(self, rows, cols, cellSize, imagePos, difficulty="normal"):
        self.rows = rows
        self.cols = cols
        self.cellSize = cellSize
        self.imagePos = imagePos
        self.matrix = [[0 for _ in range(cols)] for _ in range(rows)]
        self.towers = []
        self.enemies = []
        self.coins = []
        self.totalDamage = 0
        self.coinThreshold = 20  # Cada 20 puntos de daño global
        self.baseSpawnCooldowns = {
            "archer": 8.0,
            "lumberjack": 10.0,
            "wizard": 12.0
        }

        difficulty = difficulty.lower()
        baseMultiplier = 1.0

        # 🔹 Reducción acumulativa del 15 %
        if difficulty == "easy":
            self.difficultyMultiplier = baseMultiplier
        elif difficulty == "normal":
            self.difficultyMultiplier = baseMultiplier * 0.85
        elif difficulty == "hard":
            self.difficultyMultiplier = baseMultiplier * 0.85 * 0.85
        else:
            self.difficultyMultiplier = baseMultiplier

        # 🔹 Aplicar reducción al tiempo de regeneración
        self.spawnCooldowns = {
            enemyType: baseTime * self.difficultyMultiplier
            for enemyType, baseTime in self.baseSpawnCooldowns.items()
        }

        self.spawnTimers = {enemyType: 0.0 for enemyType in self.baseSpawnCooldowns}
        self.enemyAccumulators = {k: 0 for k in self.enemySpawnTimers}

        self.towers = {}
        self.coins = []

        # contador de daño global (acumulado entre todos los enemigos)
        self.globalDamageAccumulator = 0
        # cuántas monedas ya se han creado por el daño global (cada 20 puntos)
        self.globalCoinsDropped = 0

        # configuración de spawns por tipo (tiempo random entre min/max, y máximo simultáneo)
        self.enemyConfigs = {
            "archer": {"timer": random.uniform(18, 22), "min": 18, "max": 22, "maxSim": 1},
            "squire": {"timer": random.uniform(8, 12), "min": 8, "max": 12, "maxSim": 1},
            "lumberjack": {"timer": random.uniform(10, 14), "min": 10, "max": 14, "maxSim": 1},
            "cannibal": {"timer": random.uniform(11, 16), "min": 11, "max": 16, "maxSim": 2},
        }

    def createMatrix(self):
        self.matrix = [[0 for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def draw(self, screen):
        screen.blit(self.matrixImage, self.imagePos)
        for (row, col), tower in sorted(self.towers.items(), key=lambda item: item[0][0]):
            tower.draw(screen)
        for p in self.projectiles:
            p.draw(screen)
        for e in self.enemies:
            screen.blit(e.image, e.rect.topleft)
            if hasattr(e, "draw_hp_bar"):
                e.draw_hp_bar(screen)
        for a in self.enemy_projectiles:
            a.draw(screen)
        for tower in self.towers.values():
            tower.draw(screen)
            if hasattr(tower, "draw_hp_bar"):
                tower.draw_hp_bar(screen)

    def _spawn_fireball_below(self, tower):
        x_center = self.imagePos[0] + tower.col * self.cellSize[0] + self.cellSize[0] // 2
        y_bottom_tower_cell = self.imagePos[1] + (tower.row + 1) * self.cellSize[1]
        fb = Fireball(self.cellSize)
        fb.set_top_center(x_center, y_bottom_tower_cell - fb.rect.height)
        self.projectiles.append(fb)
    
    def _spawn_waterdrop_below(self, tower):
        row_below = tower.row + 1
        if row_below >= self.ROWS:
            return
        x_center = self.imagePos[0] + tower.col * self.cellSize[0] + self.cellSize[0] // 2
        y_bottom = self.imagePos[1] + (tower.row + 1) * self.cellSize[1]
        wd = WaterDrop(self.cellSize)
        wd.set_top_center(x_center, y_bottom - wd.rect.height)
        self.projectiles.append(wd)

    def _spawn_sandshard_below(self, tower):
        row_below = tower.row + 1
        if row_below >= self.ROWS:
            return
        x_center = self.imagePos[0] + tower.col * self.cellSize[0] + self.cellSize[0] // 2
        y_bottom = self.imagePos[1] + (tower.row + 1) * self.cellSize[1]
        ss = SandShard(self.cellSize)
        ss.set_top_center(x_center, y_bottom - ss.rect.height)
        self.projectiles.append(ss)
    
    def _spawn_rock_below(self, tower):
        row_below = tower.row + 1
        if row_below >= self.ROWS:
            return
        x_center = self.imagePos[0] + tower.col * self.cellSize[0] + self.cellSize[0] // 2
        y_bottom = self.imagePos[1] + (tower.row + 1) * self.cellSize[1]
        ss = Rock(self.cellSize)
        ss.set_top_center(x_center, y_bottom - ss.rect.height)
        self.projectiles.append(ss)

    def cell_to_pixel(self, row, col):
        px = self.imagePos[0] + col * self.cellSize[0]
        py = self.imagePos[1] + row * self.cellSize[1]
        return (px, py)

    def addAvatar(self, instance, pos):
        self.matrix[pos[0]][pos[1]] = instance
        self.avatarsList.append(instance)
    
    def addRook(self, event, instance):
        x, y = event.pos
        if self.rect.collidepoint(x, y):
            pos = self.calculateCell((x, y))
            if pos is not None and 1 <= pos[0] <= 5 and 1 <= pos[1] <= 9 and self.matrix[pos[0]][pos[1]] == 0:
                self.matrix[pos[0]][pos[1]] = instance
                self.rooksList.append(instance)

    def calculateCell(self, clickPos):
        x = clickPos[0] - self.rect.x
        y = clickPos[1] - self.rect.y
        col = x // self.cellSize[0]
        row = y // self.cellSize[1]
        if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
            return (row, col)
        else:
            return None
        
    def updateAvatars(self):
        for avatar in self.avatarsList:
            avatar.update()
    
    def updateRooks(self):
        for rook in self.rooksList:
            rook.update()

    def updateCoins(self, dt):
        for coin in self.coins:
            coin.update(dt)
    
    def drawCoins(self, screen):
        for coin in self.coins:
            coin.draw(screen, coin.position)

    def update(self, dt):
        # Spawneo por temporizadores globales (ms)
        for enemyType, interval in self.enemySpawnTimers.items():
            self.enemyAccumulators[enemyType] += dt
            if self.enemyAccumulators[enemyType] >= interval:
                self.enemyAccumulators[enemyType] = 0
                self.spawnEnemy(enemyType)

        self.updateCoins(dt)
        dt_enemies = dt / 1000.0 if dt > 5 else dt

        # Spawneo por config unificada (controla maxSim y timers independientes)
        for enemyType in list(self.enemyConfigs.keys()):
            self._maybe_spawn_enemy(dt_enemies, enemyType)

        self.updateEnemies(dt_enemies)
        self._update_enemy_projectiles(dt_enemies)
        self._melee_damage_step(dt_enemies)
         
        for tower in list(self.towers.values()):
            tower.update(dt)
            if isinstance(tower, FireTower) and tower.tick_shoot(dt):
                self._spawn_fireball_below(tower)
            elif isinstance(tower, WaterTower) and hasattr(tower, "tick_shoot") and tower.tick_shoot(dt):
                self._spawn_waterdrop_below(tower)
            elif isinstance(tower, SandTower) and hasattr(tower, "tick_shoot") and tower.tick_shoot(dt):
                self._spawn_sandshard_below(tower)
            elif isinstance(tower, RockTower) and hasattr(tower, "tick_shoot") and tower.tick_shoot(dt):
                self._spawn_rock_below(tower)

        bottom_limit = self.imagePos[1] + self.ROWS * self.cellSize[1]
        alive = []

        for p in self.projectiles:
            p.update(dt)

            hit = False

            if isinstance(p, SandShard):
                for e in self.enemies:
                    if not getattr(e, "alive", True):
                        continue
                    if p.rect.colliderect(e.rect) and isinstance(e, (Archer, Squire, Lumberjack, Cannibal)):
                        self._applyDamageAndSpawnCoins(e, 3)
                        hit = True
                        break

            elif isinstance(p, Rock):
                for e in self.enemies:
                    if not getattr(e, "alive", True):
                        continue
                    if p.rect.colliderect(e.rect) and isinstance(e, (Archer, Squire, Lumberjack, Cannibal)):
                        self._applyDamageAndSpawnCoins(e, 4)
                        hit = True
                        break

            elif isinstance(p, Fireball):
                for e in self.enemies:
                    if not getattr(e, "alive", True):
                        continue
                    if p.rect.colliderect(e.rect) and isinstance(e, (Archer, Squire, Lumberjack, Cannibal)):
                        self._applyDamageAndSpawnCoins(e, 10)
                        hit = True
                        break

            elif isinstance(p, WaterDrop):
                for e in self.enemies:
                    if not getattr(e, "alive", True):
                        continue
                    if p.rect.colliderect(e.rect) and isinstance(e, (Archer, Squire, Lumberjack, Cannibal)):
                        self._applyDamageAndSpawnCoins(e, 13)
                        hit = True
                        break
            if (not hit) and (p.rect.top < bottom_limit):
                alive.append(p)

        self.projectiles = alive
        dead_cells = []
        for pos, tower in list(self.towers.items()):
            hp = getattr(tower, "hp", None)
            is_alive = getattr(tower, "is_alive", True)
            if (hp is not None and hp <= 0) or not is_alive:
                dead_cells.append(pos)
        for pos in dead_cells:
            self._kill_tower(pos[0], pos[1], self.towers.get(pos))

    def detectCoinClick(self, event):
        for coin in self.coins:
            if coin.detectClick(event):
                self.coins.remove(coin)
                return coin.value
        return 0
    
    def addCoin(self, val=None):
        """
        Crea una moneda en una celda aleatoria.
        Si val es None, escoge aleatoriamente entre 25, 50 y 100.
        """
        if val is None:
            val = random.choice([25, 50, 100])

        while True:
            x = random.randint(1, self.COLUMNS - 1)
            y = random.randint(1, self.ROWS - 1)
            if (x, y) not in self.coinCells:
                self.coinCells.add((x, y))
                break

        pos = (
            self.imagePos[0] + x * self.cellSize[0] + random.randint(0, 1) * self.cellSize[0] // 2,
            self.imagePos[1] + y * self.cellSize[1] + random.randint(0, 1) * self.cellSize[1] // 2
        )
        newCoin = Coin(val, pos)
        self.coins.append(newCoin)

    def can_place_tower(self, row, col):
        if col == 0 or row == 0 or row == self.ROWS - 1:
            return False
        if (row, col) in self.towers or self.matrix[row][col] != 0:
            return False
        return True

    def add_tower_instance(self, row, col, tower):
        self.towers[(row, col)] = tower
        self.matrix[row][col] = tower
        tower.row = row
        tower.col = col
        tower.cell_size = self.cellSize
        tower.image_pos = self.imagePos
        if hasattr(tower, "bind_grid"):
            tower.bind_grid(row, col, self.cellSize, self.imagePos)

    def _maybe_spawn_enemy(self, dt, enemyType):
        config = self.enemyConfigs.get(enemyType)
        if not config:
            return
        cls_map = {"archer": Archer, "squire": Squire, "lumberjack": Lumberjack, "cannibal": Cannibal}
        maxSim = config["maxSim"]
        cls = cls_map.get(enemyType)
        alive_count = sum(1 for e in self.enemies if isinstance(e, cls) and getattr(e, "alive", True))
        if alive_count >= maxSim:
            return
        config["timer"] -= dt
        if config["timer"] > 0:
            return
        config["timer"] = random.uniform(config["min"], config["max"])
        self.spawnEnemy(enemyType)

    def _spawn_enemy_arrow_from_xy(self, cx, cy):
        arrow_w = max(18, int(self.cellSize[0] * 0.35))
        arrow_h = int(arrow_w * 2.2)
        arr = Arrow("Assets/enemies/flecha.png", speed_px_s=380, scale_px=(arrow_w, arrow_h))
        arr.set_center(cx, cy)
        self.enemy_projectiles.append(arr)
        
    def _spawn_enemy_sword_from_xy(self, cx, cy):
        sw = max(20, int(self.cellSize[0] * 0.40))
        sh = int(sw * 1.8)
        sword = Sword("Assets/enemies/sword.png", speed_px_s=320, scale_px=(sw, sh))
        sword.set_center(cx, cy)
        self.enemy_projectiles.append(sword)
        
    def updateEnemies(self, dt):
        topLimitY = self.imagePos[1]
        alive = []
        for e in self.enemies:
            e.update(dt)
            if not getattr(e, "alive", True):
                continue
            enemyRow = getattr(e, "row", None)
            enemyCol = getattr(e, "col", None)
            if enemyRow is None or enemyCol is None:
                cell = self.calculateCell((e.rect.centerx, e.rect.centery))
                if cell is not None:
                    enemyRow, enemyCol = cell
            if enemyRow is not None:
                if enemyRow <= 0:
                    self.onEnemyReachedTop(e)
                    continue 
            else:
                if e.rect.top <= topLimitY + 5:
                    self.onEnemyReachedTop(e)
                    continue
            alive.append(e)

        self.enemies = alive

    def _update_enemy_projectiles(self, dt):
        alive = []
        top_y = self.imagePos[1]
        bottom_y = self.imagePos[1] + self.ROWS * self.cellSize[1]
        for a in self.enemy_projectiles:
            a.update(dt)
            if a.rect.bottom < top_y or a.rect.top > bottom_y:
                continue
            hit = False
            cell = self.calculateCell((a.rect.centerx, a.rect.top))
            if cell and cell in self.towers:
                self.damage_tower(cell[0], cell[1], getattr(a, "damage", 2))
                hit = True
            if not hit:
                alive.append(a)
        self.enemy_projectiles = alive
    
    def _melee_damage_step(self, dt_sec: float):
        for e in self.enemies:
            if isinstance(e, Lumberjack):
                base_dmg, base_cd = 9, 0.60
            elif isinstance(e, Cannibal):
                base_dmg, base_cd = 12, 0.70
            else:
                continue
            e._melee_accum = getattr(e, "_melee_accum", 0.0) + dt_sec
            e._melee_cd = getattr(e, "_melee_cd", base_cd)
            e._melee_dmg = getattr(e, "_melee_dmg", base_dmg)
            if e._melee_accum < e._melee_cd:
                continue
            e._melee_accum = 0.0
            r, c = getattr(e, "row", None), getattr(e, "col", None)
            if r is None or c is None:
                continue
            OFFSETS = [(-1, 0), (0, -1), (0, 1)]
            for dr, dc in OFFSETS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.ROWS and 0 <= nc < self.COLUMNS:
                    t = self.towers.get((nr, nc))
                    if t:
                        self.damage_tower(nr, nc, e._melee_dmg)

    def damage_tower(self, row, col, dmg):
        t = self.towers.get((row, col))
        if not t:
            return
        before = getattr(t, "hp", None)
        if hasattr(t, "take_damage"):
            t.take_damage(int(dmg))
        elif before is not None:
            t.hp = max(0, before - int(dmg))
        after = getattr(t, "hp", None)
        # log opcional
        print(f"[HIT] tower {(row, col)} hp {before} -> {after} (dmg={dmg})")
        if (after is not None and after <= 0) or not getattr(t, "is_alive", True):
            self._kill_tower(row, col, t)

    def _kill_tower(self, row, col, tower):
        try:
            tower.is_alive = False
        except Exception:
            pass
        try:
            tower.kill()
        except Exception:
            pass
        self.towers.pop((row, col), None)
        self.matrix[row][col] = 0

    def onEnemyReachedTop(self, enemy):
        if hasattr(self, "onGameOver"):
            self.onGameOver()

    def spawnEnemy(self, enemyType):
        last_row = self.ROWS - 1
        valid_cols = [1, 2, 3, 4, 5]
        col = random.choice(valid_cols)

        if enemyType.lower() == "archer":
            enemy = Archer(
                spritesheet_path="Assets/enemies/flechero.png",
                cell_size=self.cellSize,
                image_pos=self.imagePos,
                rows=self.ROWS, cols=self.COLUMNS,
                row=last_row, col=col,
                frames_rows=3, frames_cols=4,
                wait_time=12.0, move_time=0.50, move_anim_fps=6, scale_fit=0.9,
                on_shoot=self._spawn_enemy_arrow_from_xy
            )
        elif enemyType.lower() == "squire":
            enemy = Squire(
                spritesheet_path="Assets/enemies/escudero.png",
                cell_size=self.cellSize,
                image_pos=self.imagePos,
                rows=self.ROWS, cols=self.COLUMNS,
                row=last_row, col=col,
                frames_rows=3, frames_cols=4,
                wait_time=12.0, move_time=0.50, move_anim_fps=8, scale_fit=0.9,
                on_attack=self._spawn_enemy_sword_from_xy
            )
        elif enemyType.lower() == "lumberjack":
            enemy = Lumberjack(
                spritesheet_path="Assets/enemies/leñador.png",
                cell_size=self.cellSize,
                image_pos=self.imagePos,
                rows=self.ROWS, cols=self.COLUMNS,
                row=last_row, col=col,
                frames_rows=3, frames_cols=4,
                wait_time=12.0, move_time=0.50, move_anim_fps=8, scale_fit=0.9
            )
        elif enemyType.lower() == "cannibal":
            enemy = Cannibal(
                spritesheet_path="Assets/enemies/canibal.png",
                cell_size=self.cellSize,
                image_pos=self.imagePos,
                rows=self.ROWS, cols=self.COLUMNS,
                row=last_row, col=col,
                frames_rows=3, frames_cols=4,
                wait_time=14.0, move_time=0.55, move_anim_fps=8, scale_fit=0.92,
                crop_left=1, crop_right=1, crop_top=1, crop_bottom=1
            )
        else:
            return

        # Inicializaciones útiles
        enemy.maxHp = getattr(enemy, "hp", None)
        enemy.coinsDropped = 0
        self.enemies.append(enemy)
        print(f"[Spawn {enemyType}] row={last_row}, col={col}, maxHp={enemy.maxHp}")

    def setDifficulty(self, difficulty):
        self.difficulty = difficulty.lower()
        self.enemySpawnTimers = self._applyDifficulty(self.enemySpawnTimersBase)

    def _applyDifficulty(self, baseTimers):
        difficultyMultipliers = {
            "easy": 1.3,     # +30% más lentos
            "normal": 1.0,   # sin cambio
            "hard": 0.7      # -30% más rápidos
        }
        multiplier = difficultyMultipliers.get(self.difficulty, 1.0)
        adjusted = {k: int(v * multiplier) for k, v in baseTimers.items()}
        return adjusted
    
    def _applyDamageAndSpawnCoins(self, enemy, damage):
        """
        Aplica 'damage' al enemigo y suma al acumulador global.
        Por cada 20 puntos de daño global acumulado genera 1 moneda
        llamando a self.addCoin() (que escogerá valor aleatorio).
        """
        if enemy is None:
            return

        # HP antes
        beforeHp = getattr(enemy, "hp", None)

        # Aplica daño usando la API del enemigo si existe
        if hasattr(enemy, "take_damage") and callable(enemy.take_damage):
            enemy.take_damage(int(damage))
        else:
            if beforeHp is not None:
                enemy.hp = max(0, int(beforeHp) - int(damage))

        # HP después
        afterHp = getattr(enemy, "hp", None)

        # Calcular daño real aplicado en este golpe (por si hubo diferencias)
        if beforeHp is None or afterHp is None:
            delta = int(damage)  # si no conocemos hp, asumimos el damage pedido
        else:
            delta = max(0, int(beforeHp) - int(afterHp))

        # sumar al acumulador global
        self.globalDamageAccumulator += delta

        # calcular cuántas monedas en total deberían haberse generado por daño global
        coinsShouldHave = self.globalDamageAccumulator // 20

        # cuántas monedas faltan por generar (nuevas)
        newCoins = coinsShouldHave - int(self.globalCoinsDropped)

        # generar las monedas nuevas (cada llamada a addCoin() elegirá valor aleatorio)
        for _ in range(max(0, newCoins)):
            self.addCoin()

        # actualizar contador de monedas globales ya creadas
        self.globalCoinsDropped += max(0, newCoins)

        # si el enemigo murió, marcarlo y disparar callback on_death si existe
        if afterHp is not None and afterHp <= 0:
            enemy.alive = False
            if callable(getattr(enemy, "on_death", None)):
                try:
                    enemy.on_death(enemy)
                except Exception:
                    pass
