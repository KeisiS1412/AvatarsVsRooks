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
    def __init__(self, res):
        self.ROWS = 10
        self.COLUMNS = 6
        self.createMatrix()
        self.rooksList = []
        self.avatarsList = []
        self.res = res
        self.projectiles = []

        self.enemies = []
        self.enemy_projectiles = []

        # Spawn controlado (uno cada ~20 s)
        self.flech_spawn_min = 18.0
        self.flech_spawn_max = 22.0
        self.flech_spawn_timer = random.uniform(self.flech_spawn_min, self.flech_spawn_max)
        self.max_flecheros = 1
        self.flech_spawn_min = 18.0
        self.flech_spawn_max = 22.0
        self.flech_spawn_timer = random.uniform(self.flech_spawn_min, self.flech_spawn_max)
        self.max_flecheros = 1

        self.squire_spawn_min = 8.0
        self.squire_spawn_max = 12.0
        self.squire_spawn_timer = random.uniform(self.squire_spawn_min, self.squire_spawn_max)
        self.max_squires = 1 

        self.lumber_spawn_min = 10.0
        self.lumber_spawn_max = 14.0
        self.lumber_spawn_timer = random.uniform(self.lumber_spawn_min, self.lumber_spawn_max)
        self.max_lumberjacks = 1

        self.cannibal_spawn_min = 11.0
        self.cannibal_spawn_max = 16.0
        self.cannibal_spawn_timer = random.uniform(self.cannibal_spawn_min, self.cannibal_spawn_max)
        self.max_cannibals = 2

        self.matrixImage = pygame.transform.rotate(pygame.image.load("Assets/matrix.png"), -90)
        self.matrixImage = pygame.transform.rotozoom(self.matrixImage, 0, 0.61)
        self.cellSize = (self.matrixImage.get_width() // 7, self.matrixImage.get_height() // 11)
        self.imagePos = (self.res[0] // 2 - self.matrixImage.get_width() // 2, 0)

        self.coinCells = set()
        self.rect = pygame.Rect(
            self.imagePos[0],
            self.imagePos[1],
            self.matrixImage.get_width(),
            self.matrixImage.get_height()
        )

        self.towers = {} 

        self.coins = []
        for i in range(5):
            self.addCoin(25)
            self.addCoin(50)
            self.addCoin(100)

    def createMatrix(self):  # Crea una matriz con listas anidadas del tamaño ya establecido
        self.matrix = [[0 for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def draw(self, screen):  # Dibuja primero la matriz, luego torres; las monedas se dibujan aparte
        screen.blit(self.matrixImage, self.imagePos)

        
        for tower in self.towers.values():
            tower.draw(screen)

        for p in self.projectiles:
            p.draw(screen)
        for e in self.enemies:
            screen.blit(e.image, e.rect.topleft)
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
        ss.set_top_center(x_center, y_bottom - ss.rect.height)  # nace pegado al borde inferior de la celda de la torre
        self.projectiles.append(ss)
    
    def _spawn_rock_below(self, tower):
        row_below = tower.row + 1
        if row_below >= self.ROWS:
            return
        x_center = self.imagePos[0] + tower.col * self.cellSize[0] + self.cellSize[0] // 2
        y_bottom = self.imagePos[1] + (tower.row + 1) * self.cellSize[1]

        ss = Rock(self.cellSize)
        ss.set_top_center(x_center, y_bottom - ss.rect.height)  # nace pegado al borde inferior de la celda de la torre
        self.projectiles.append(ss)


    def cell_to_pixel(self, row, col):
        px = self.imagePos[0] + col * self.cellSize[0]
        py = self.imagePos[1] + row * self.cellSize[1]
        return (px, py)

    def addAvatar(self, instance, pos):  # Añade un avatar en la posición dada
        self.matrix[pos[0]][pos[1]] = instance
        self.avatarsList.append(instance)
    
    def addRook(self, event, instance):  # Si se clickea una casilla dentro de la matriz, añade el rook en esa posición
        x, y = event.pos
        if self.rect.collidepoint(x, y):
            pos = self.calculateCell((x, y))
            if pos is not None and 1 <= pos[0] <= 5 and 1 <= pos[1] <= 9 and self.matrix[pos[0]][pos[1]] == 0:
                self.matrix[pos[0]][pos[1]] = instance
                self.rooksList.append(instance)
                print(f"Rook added at {pos}")

    def calculateCell(self, clickPos):  # Calcula en qué casilla cayó el clic
        x = clickPos[0] - self.rect.x
        y = clickPos[1] - self.rect.y
        col = x // self.cellSize[0]
        row = y // self.cellSize[1]
        if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
            return (row, col)
        else:
            return None
        
    def updateAvatars(self):  # Actualiza todos los avatars en la matriz
        for avatar in self.avatarsList:
            avatar.update()
    
    def updateRooks(self):  # Actualiza todos los rooks en la matriz
        for rook in self.rooksList:
            rook.update()

    def updateCoins(self, dt):
        for coin in self.coins:
            coin.update(dt)
    
    def drawCoins(self, screen):
        for coin in self.coins:
            coin.draw(screen, coin.position)

    def update(self, dt):  # Actualiza la lógica de la matriz
        self.updateCoins(dt)
        dt_enemies = dt / 1000.0 if dt > 5 else dt  # heurística segura
        self._maybe_spawn_flechero(dt_enemies)
        self._update_enemies(dt_enemies)
        self._update_enemy_projectiles(dt_enemies)
        self._maybe_spawn_squire(dt_enemies)
        self._maybe_spawn_lumberjack(dt_enemies)
        self._maybe_spawn_cannibal(dt_enemies)
         
        for tower in self.towers.values():
            tower.update(dt)
        
        if hasattr(self, "towers"):
            for tower in self.towers.values():
                tower.update(dt)

                # disparo solo para torres de fuego
                if isinstance(tower, FireTower):
                    if tower.tick_shoot(dt):
                        self._spawn_fireball_below(tower)

                if isinstance(tower, WaterTower) and hasattr(tower, "tick_shoot"):
                    if tower.tick_shoot(dt):
                        self._spawn_waterdrop_below(tower)
                
                if isinstance(tower, SandTower) and hasattr(tower, "tick_shoot"):
                    if tower.tick_shoot(dt):
                        self._spawn_sandshard_below(tower)
                if isinstance(tower, RockTower) and hasattr(tower, "tick_shoot"):
                    if tower.tick_shoot(dt):
                        self._spawn_rock_below(tower)

        # actualizar proyectiles y limpiar los que salen
        bottom_limit = self.imagePos[1] + self.ROWS * self.cellSize[1]
        alive = []
        for p in self.projectiles:
            p.update(dt)
            if p.rect.top < bottom_limit:
                alive.append(p)
        self.projectiles = alive

        dead_cells = []
        for pos, tower in list(self.towers.items()):
            hp = getattr(tower, "hp", None)
            is_alive = getattr(tower, "is_alive", True)
            if (hp is not None and hp <= 0) or not is_alive:
                dead_cells.append(pos)
                continue
            if hasattr(tower, "update"):
                tower.update(dt)

        for pos in dead_cells:
            self._kill_tower(pos[0], pos[1], self.towers.get(pos))

    def detectCoinClick(self, event):
        for coin in self.coins:
            if coin.detectClick(event):
                self.coins.remove(coin)
                return coin.value
        return 0
    
    def addCoin(self, val):
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
        # No permitir en última fila ni sobre otra entidad/torre
        if row == self.ROWS - 1:
            return False
        if (row, col) in self.towers:
            return False
        if self.matrix[row][col] != 0:
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
    
    def _maybe_spawn_flechero(self, dt):
        # Respeta el máximo simultáneo
        if sum(1 for e in self.enemies if isinstance(e, Archer) and getattr(e, "alive", True)) >= self.max_flecheros:
            return

        self.flech_spawn_timer -= dt
        if self.flech_spawn_timer > 0:
            return

        self.flech_spawn_timer = random.uniform(self.flech_spawn_min, self.flech_spawn_max)

        last_row = self.ROWS - 1
        valid_cols = [1, 2, 3, 4, 5]  # solo esas tres columnas
        col = random.choice(valid_cols)
        e = Archer(
            spritesheet_path="Assets/enemies/flechero.png",
            cell_size=self.cellSize,
            image_pos=self.imagePos,
            rows=self.ROWS, cols=self.COLUMNS,
            row=last_row, col=col,
            frames_rows=3, frames_cols=4,
            wait_time=12.0, move_time=0.50, move_anim_fps=6, scale_fit=0.9,
            on_shoot=self._spawn_enemy_arrow_from_xy  # << callback
        )
        self.enemies.append(e)
        print(f"[Spawn flechero] fila={last_row}, col={col}")
    def _maybe_spawn_squire(self, dt):
        # Respeta el máximo simultáneo
        if sum(1 for e in self.enemies if isinstance(e, Squire) and getattr(e, "alive", True)) >= self.max_squires:
            return

        self.squire_spawn_timer -= dt
        if self.squire_spawn_timer > 0:
            return

        self.squire_spawn_timer = random.uniform(self.squire_spawn_min, self.squire_spawn_max)

        last_row = self.ROWS - 1
        # columnas válidas (tú usas 1..5 para flechero; repetimos para consistencia visual)
        valid_cols = [1, 2, 3, 4, 5]
        col = random.choice(valid_cols)

        e = Squire(
            spritesheet_path="Assets/enemies/escudero.png",
            cell_size=self.cellSize,
            image_pos=self.imagePos,
            rows=self.ROWS, cols=self.COLUMNS,
            row=last_row, col=col,
            frames_rows=3, frames_cols=4,
            wait_time=12.0, move_time=0.50, move_anim_fps=8, scale_fit=0.9,
            on_attack=self._spawn_enemy_sword_from_xy
        )
        self.enemies.append(e)
        print(f"[Spawn squire] row={last_row}, col={col}")
    
    def _maybe_spawn_lumberjack(self, dt):
        # limitar por tipo
        if sum(1 for e in self.enemies if isinstance(e, Lumberjack) and getattr(e, "alive", True)) >= self.max_lumberjacks:
            return

        self.lumber_spawn_timer -= dt
        if self.lumber_spawn_timer > 0:
            return

        self.lumber_spawn_timer = random.uniform(self.lumber_spawn_min, self.lumber_spawn_max)

        last_row = self.ROWS - 1
        valid_cols = [1, 2, 3, 4, 5]  # consistente con tus otros spawns
        col = random.choice(valid_cols)

        e = Lumberjack(
            spritesheet_path="Assets/enemies/leñador.png",  # pon tu ruta real
            cell_size=self.cellSize,
            image_pos=self.imagePos,
            rows=self.ROWS, cols=self.COLUMNS,
            row=last_row, col=col,
            frames_rows=3, frames_cols=4,
            wait_time=12.0, move_time=0.50, move_anim_fps=8, scale_fit=0.9
        )
        self.enemies.append(e)
        print(f"[Spawn lumberjack] row={last_row}, col={col}")
    
    def _maybe_spawn_cannibal(self, dt):
        if sum(1 for e in self.enemies if isinstance(e, Cannibal) and getattr(e, "alive", True)) >= self.max_cannibals:
            return

        self.cannibal_spawn_timer -= dt
        if self.cannibal_spawn_timer > 0:
            return

        self.cannibal_spawn_timer = random.uniform(self.cannibal_spawn_min, self.cannibal_spawn_max)

        last_row = self.ROWS - 1
        valid_cols = [1, 2, 3, 4, 5]
        col = random.choice(valid_cols)

        e = Cannibal(
            spritesheet_path="Assets/enemies/canibal.png",   # usa tu ruta real
            cell_size=self.cellSize,
            image_pos=self.imagePos,
            rows=self.ROWS, cols=self.COLUMNS,
            row=last_row, col=col,
            frames_rows=3, frames_cols=4,
            wait_time=14.0, move_time=0.55, move_anim_fps=8, scale_fit=0.92,
            crop_left=1, crop_right=1, crop_top=1, crop_bottom=1
        )
        self.enemies.append(e)
        print(f"[Spawn cannibal] row={last_row}, col={col}")




    def _spawn_enemy_arrow_from_xy(self, cx, cy):
        # Escalamos la flecha a un ancho cómodo (p.ej., 30–35 px) proporcional a tu celda
        arrow_w = max(18, int(self.cellSize[0] * 0.35))
        arrow_h = int(arrow_w * 2.2)  # alargada
        arr = Arrow("Assets/enemies/flecha.png", speed_px_s=380, scale_px=(arrow_w, arrow_h))
        arr.set_center(cx, cy)
        self.enemy_projectiles.append(arr)
        
    def _spawn_enemy_sword_from_xy(self, cx, cy):
        # Tamaño relativo cómodo a tu celda (similar a la flecha)
        sw = max(20, int(self.cellSize[0] * 0.40))
        sh = int(sw * 1.8)
        sword = Sword("Assets/enemies/sword.png", speed_px_s=320, scale_px=(sw, sh))
        sword.set_center(cx, cy)
        self.enemy_projectiles.append(sword)
        
    def _update_enemies(self, dt):
            top_limit_y = self.imagePos[1]
            alive = []
            for e in self.enemies:
                e.update(dt)
                # Si salió por arriba o marcó not alive, lo quitamos
                if getattr(e, "alive", True) and e.rect.centery >= top_limit_y - 8:
                    alive.append(e)
            self.enemies = alive

    def _update_enemy_projectiles(self, dt):
        alive = []
        top_y = self.imagePos[1]
        bottom_y = self.imagePos[1] + self.ROWS * self.cellSize[1]

        for a in self.enemy_projectiles:
            a.update(dt)

            # 1) fuera de la matriz por arriba => descartar
            if a.rect.bottom < top_y:
                continue
            # 2) fuera (por si acaso) por abajo => mantener no aplica aquí, pero lo dejamos claro
            if a.rect.top > bottom_y:
                continue

            # 3) detectar celda golpeada en el frente de la flecha (punta)
            hit = False
            # tomamos el punto líder: el borde superior centrado
            cx = a.rect.centerx
            cy = a.rect.top

            cell = self.calculateCell((cx, cy))
            if cell is not None:
                row, col = cell
                if (row, col) in self.towers:
                    print(f"[ARROW] impact at cell {(row, col)}")
                    dmg = getattr(a, "damage", 2)
                    self.damage_tower(row, col, dmg)
                    hit = True

            # 4) si no pegó, la mantenemos viva
            if not hit:
                alive.append(a)
            # si pegó, NO la reinsertamos (desaparece en el impacto)

        self.enemy_projectiles = alive
    
    def damage_tower(self, row, col, dmg):
        t = self.towers.get((row, col))
        if not t:
            return

        before = getattr(t, "hp", None)

        if hasattr(t, "take_damage"):
            t.take_damage(int(dmg))
        else:
            # fallback por si alguna torre vieja no tiene take_damage
            if before is not None:
                t.hp = max(0, before - int(dmg))

        after = getattr(t, "hp", None)
        print(f"[HIT] tower {(row, col)} hp {before} -> {after} (dmg={dmg})")

        # Elimina inmediatamente si ya no tiene vida
        if (after is not None and after <= 0) or not getattr(t, "is_alive", True):
            self._kill_tower(row, col, t)

    def _kill_tower(self, row, col, tower):
        print(f"[KILL] removing tower at {(row, col)}")
        try:
            tower.is_alive = False
        except Exception:
            pass
        try:
            tower.kill()  # por si está en grupos de pygame
        except Exception:
            pass
        self.towers.pop((row, col), None)
        self.matrix[row][col] = 0
