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
from towers.TowerFactory import TowerFactory
from Selector import Selector


class Matrix:
    """Manejo visual y lógico de la matriz de juego, maneja instancias de Avatars, Rooks, monedas y torres."""
    def __init__(self, res, difficulty="easy"):
        self.ROWS = 10
        self.COLUMNS = 6
        self.createMatrix()

        # listas auxiliares
        self.rooksList = []
        self.avatarsList = []

        self.res = res
        self.projectiles = []
        self.enemy_projectiles = []
        self.onNextScene = None

        self.enemies = []
        self.enemy_projectiles = []

        self.money = 300
        self._hud_font = pygame.font.SysFont("Arial", 26, bold=True)

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

        # --- Niveles / tiempos por nivel (ms) ---
        base_ms = 60 * 1000  # 60s
        lvl1 = base_ms
        lvl2 = int(base_ms * 1.25) # +25% del anterior
        lvl3 = int(lvl2 * 1.25)        # +25% del anterior
        self.levelDurations = [lvl1, lvl2, lvl3]  # tres niveles antes de cambiar escena
        self.levelIndex = 0                 # índice actual (0 = primer nivel)
        self.levelTimeAccumulator = 0       # ms transcurridos en el nivel actual
        self.sceneChanged = False

        self.totalTime = 0  # (si lo usas en otra parte)
        self.difficulty = difficulty.lower()

        # --- Spawn timers base (ms) EXACTOS como pediste: 6s, 9s, 12s, 15s ---
        self.enemySpawnTimersBase = {
            "archer": 6_000,      # 6s
            "squire": 9_000,      # 9s
            "lumberjack": 12_000, # 12s
            "cannibal": 15_000    # 15s
        }
        # initialize timers/accumulators from base
        self.enemySpawnTimers = dict(self.enemySpawnTimersBase)
        self.enemyAccumulators = {k: 0 for k in self.enemySpawnTimers}

        # Aplica dificultad inicial (reduce spawn en 15% por nivel)
        self.setDifficulty(self.difficulty)

        self.coinCells = set()
        self.rect = pygame.Rect(
            self.imagePos[0],
            self.imagePos[1],
            self.matrixImage.get_width(),
            self.matrixImage.get_height()
        )

        self.towers = {}
        self.coins = []

        # contador de daño global (acumulado entre todos los enemigos)
        self.globalDamageAccumulator = 0
        # cuántas monedas ya se han creado por el daño global (cada 20 puntos)
        self.globalCoinsDropped = 0

        # configuración de spawns por tipo (timer en segundos, usado por lógica unificada)
        self.enemyConfigs = {
            "archer": {"timer": random.uniform(18, 22), "min": 18, "max": 22, "maxSim": 1},
            "squire": {"timer": random.uniform(8, 12), "min": 8, "max": 12, "maxSim": 1},
            "lumberjack": {"timer": random.uniform(10, 14), "min": 10, "max": 14, "maxSim": 1},
            "cannibal": {"timer": random.uniform(11, 16), "min": 11, "max": 16, "maxSim": 2},
        }

        cell_w, cell_h = self.cellSize
        img_x, img_y = self.imagePos
        img_w, img_h = self.matrixImage.get_width(), self.matrixImage.get_height()

        self.selector = Selector(
            self.cellSize,
            xlimits=(img_x + cell_w, img_x + img_w - (2 * cell_w)),   # excluye primera/última columna
            ylimits=(img_y + cell_h, img_y + img_h - (2 * cell_h))    # excluye primera/última fila
)

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
        # HUD en la parte derecha, centrado verticalmente
        self._draw_hud(screen)
        self.selector.draw(screen)

    def _draw_hud(self, screen):
        """Dibuja panel en la parte derecha (centrado vertical) con:
           - Dinero
           - Tiempo restante (MM:SS)
           - Dificultad
        """
        # Preparar textos
        money_text = f"${self.money}"
        seconds = self.get_remaining_time()
        mm = seconds // 60
        ss = seconds % 60
        time_text = f"{mm:02d}:{ss:02d}"
        diff_text = f"Difficulty: {self.difficulty.capitalize()}"

        surf_money = self._hud_font.render(money_text, True, (255, 230, 90))
        surf_time  = self._hud_font.render(time_text, True, (230, 230, 230))
        surf_diff  = self._hud_font.render(diff_text, True, (230, 230, 235))

        spacing = 8
        padding = 12

        # calcular tamaño panel
        text_widths = [surf_money.get_width(), surf_time.get_width(), surf_diff.get_width()]
        panel_w = max(text_widths) + padding * 2
        panel_h = surf_money.get_height() + surf_time.get_height() + surf_diff.get_height() + spacing * 2 + padding * 2

        # crear surface semitransparente
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((10, 10, 12, 160))  # fondo semitransparente

        # dibujar bordes ligeros
        pygame.draw.rect(panel, (80, 80, 90, 200), panel.get_rect(), width=2, border_radius=8)

        # posiciones dentro del panel
        x_text = padding
        y_text = padding
        panel.blit(surf_money, (x_text, y_text))
        y_text += surf_money.get_height() + spacing
        panel.blit(surf_time, (x_text, y_text))
        y_text += surf_time.get_height() + spacing
        panel.blit(surf_diff, (x_text, y_text))

        # posición en pantalla (derecha, centrado vertical)
        margin_right = 20
        screen_x = self.res[0] - panel_w - margin_right
        screen_y = (self.res[1] // 2) - (panel_h // 2)

        screen.blit(panel, (screen_x, screen_y))

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
    
    def add_tower_instance(self, row, col, tower):
        # Marca en estructuras
        self.towers[(row, col)] = tower
        self.matrix[row][col] = tower

        # Ayuda a la torre a conocer su grid (si lo usa)
        setattr(tower, "row", row)
        setattr(tower, "col", col)
        if hasattr(tower, "bind_grid"):
            tower.bind_grid(row, col, self.cellSize, self.imagePos)

    def addAvatar(self, instance, pos):  # Añade un avatar en la posición dada
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
        # dt en milisegundos (tal y como viene de main.py)
        # --- tiempo del nivel actual ---
        self.levelTimeAccumulator += dt
        self.totalTime += dt

        # --- Avanzar niveles si el acumulador supera la duración del nivel ---
        while self.levelIndex < len(self.levelDurations) and self.levelTimeAccumulator >= self.levelDurations[self.levelIndex]:
            # restamos la duración completada para permitir saltos múltiples si dt es grande
            self.levelTimeAccumulator -= self.levelDurations[self.levelIndex]
            self.levelIndex += 1

            if self.levelIndex < len(self.levelDurations):
                # cambiamos dificultad al nuevo nivel
                if self.levelIndex == 1:
                    self.setDifficulty("normal")
                    print("[Matrix] Dificultad cambiada a NORMAL")
                elif self.levelIndex == 2:
                    self.setDifficulty("hard")
                    print("[Matrix] Dificultad cambiada a HARD")
                # limpiar rooks/avatars/enemigos/proyectiles al entrar al nuevo nivel
                self.clear_units()
            else:
                # ya pasamos el último nivel -> cambiar de escena (una sola vez)
                if not self.sceneChanged:
                    self.sceneChanged = True
                    print("[Matrix] Todos los niveles completados -> cambiando escena")
                    self.clear_units()

                try:
                    from MusicSpotify import obtener_datos_cancion_actual
                    from Algoritmo import calcular_puntaje_ajustado
                    from session import get_current_user
                    from pantalla import pantalla_victoria     # ORIGINAL
                    from Salon_fama import guardar_en_fama

                    # Obtener datos de Spotify
                    tempo, popularidad = obtener_datos_cancion_actual()

                    if tempo and popularidad:
                        avatars_matados = len(getattr(self, "enemies", []))
                        puntos_avatar = int(self.money)
                        limite_maximo = 1000

                        puntaje = calcular_puntaje_ajustado(
                            tempo,
                            popularidad,
                            avatars_matados,
                            puntos_avatar,
                            limite_maximo
                        )
                        print(f"[Matrix] Puntaje final calculado: {puntaje:.2f}")

                    else:
                        puntaje = 0
                        print("[Matrix] No se pudieron obtener datos de Spotify, puntaje = 0")

                    # ============================
                    # GUARDAR EN JSON LOCAL
                    # ============================
                    user = get_current_user()
                    username = user.get("username", "Jugador")
                    pantalla_victoria(username, puntaje)

                    # guardar en JSON después
                    guardar_en_fama(username, puntaje)

                except Exception as e:
                    print("[Matrix] ERROR en cálculo de puntaje final:", e)

                return



        # --- Si ya cambiamos escena, evitamos spawnear enemigos nuevos ---
        if self.sceneChanged:
            # aún actualizamos objetos existentes para que se limpien correctamente
            pass

        # --- Spawneo por temporizadores globales (ms) ---
        for enemyType, interval in self.enemySpawnTimers.items():
            self.enemyAccumulators[enemyType] += dt
            if self.enemyAccumulators[enemyType] >= interval:
                self.enemyAccumulators[enemyType] = 0
                # no spawnear si ya cambiamos escena
                if not self.sceneChanged:
                    self.spawnEnemy(enemyType)

        # --- Actualiza monedas ---
        self.updateCoins(dt)

        # --- Spawneo unificado y actualización de enemigos ---
        dt_seconds = dt / 1000.0 if dt > 5 else dt
        for enemyType in list(self.enemyConfigs.keys()):
            self._maybe_spawn_enemy(dt_seconds, enemyType)

        self.updateEnemies(dt_seconds)
        self._update_enemy_projectiles(dt_seconds)
        self._melee_damage_step(dt_seconds)

        # --- Actualización de torres ---
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

        # --- Actualiza proyectiles y detección de colisiones ---
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

        # --- Elimina torres destruidas ---
        dead_cells = []
        for pos, tower in list(self.towers.items()):
            hp = getattr(tower, "hp", None)
            is_alive = getattr(tower, "is_alive", True)
            if (hp is not None and hp <= 0) or not is_alive:
                dead_cells.append(pos)
        for pos in dead_cells:
            self._kill_tower(pos[0], pos[1], self.towers.get(pos))


    def detectCoinClick(self, event):
        for coin in list(self.coins):
            if coin.detectClick(event):
                self.coins.remove(coin)
                self.add_money(coin.value)
                return coin.value
        return 0
    
    def collectCoins(self):
        for coin in list(self.coins):
            self.coins.remove(coin)
            self.add_money(coin.value)

    
    def addCoin(self, val=None):
        # elegir denominación si no se especificó
        if val is None:
            val = random.choice([25, 50, 100])

        # busca una celda libre para colocar la moneda (evita repetir)
        attempts = 0
        while True:
            x = random.randint(1, self.COLUMNS - 1)
            y = random.randint(1, self.ROWS - 1)
            if (x, y) not in self.coinCells:
                self.coinCells.add((x, y))
                break
            attempts += 1
            # por seguridad, salir si no encuentra tras muchas iteraciones
            if attempts > 50:
                # coloca en (1,1) como fallback
                x, y = 1, 1
                self.coinCells.add((x, y))
                break

        pos = (
            self.imagePos[0] + x * self.cellSize[0] + random.randint(0, 1) * (self.cellSize[0] // 2),
            self.imagePos[1] + y * self.cellSize[1] + random.randint(0, 1) * (self.cellSize[1] // 2)
        )
        newCoin = Coin(val, pos)
        self.coins.append(newCoin)

        
    def add_money(self, amount: int):
        """Suma (o resta si amount<0) y evita negativos."""
        try:
            self.money = max(0, int(self.money) + int(amount))
        except Exception:
            # fallback defensivo si amount no fue entero
            self.money = max(0, int(self.money))

    def can_afford(self, tower_type: str) -> bool:
        """¿Alcanza el dinero para comprar 'tower_type'?"""
        try:
            return self.money >= TowerFactory.get_cost(tower_type)
        except Exception:
            return False

    def try_place_tower(self, tower_type: str, row: int, col: int) -> bool:
        """
        Intenta comprar y colocar una torre en (row, col).
        - Verifica celda válida
        - Verifica dinero suficiente
        - Descuenta y coloca
        Devuelve True si se colocó.
        """
        if not self.can_place_tower(row, col):
            # celda ocupada o fila prohibida
            return False

        
        cost = TowerFactory.get_cost(tower_type)
        if self.money < cost:
            # fondos insuficientes
            return False

        # Crea torre usando tu factoría actual (mismos parámetros que ya usas)
        cell_tl = self.cell_to_pixel(row, col)  # topleft de la celda
        tower = TowerFactory.create_tower(tower_type, self.cellSize, cell_tl, row, col)
        if tower is None:
            return False

        # Descontar y colocar
        self.money -= cost
        self.add_tower_instance(row, col, tower)
        return True


    def can_place_tower(self, row, col):
        if col == 0 or row == 0 or row == self.ROWS - 1:
            return False
        if (row, col) in self.towers or self.matrix[row][col] != 0:
            return False
        return True

    def add_tower_instance(self, row, col, tower):
        # agrega torre y asegura hp/is_alive por defecto si no existen
        self.towers[(row, col)] = tower
        self.matrix[row][col] = tower
        tower.row = row
        tower.col = col
        tower.cell_size = self.cellSize
        tower.image_pos = self.imagePos
        if not hasattr(tower, "hp"):
            # valor por defecto; ajústalo si quieres otro
            tower.hp = 30
        if not hasattr(tower, "is_alive"):
            tower.is_alive = True
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
        # respeta sceneChanged (no spawn si ya cambiaste escena)
        if not self.sceneChanged:
            self.spawnEnemy(enemyType)

    def _spawn_enemy_arrow_from_xy(self, cx, cy):
        arrow_w = max(18, int(self.cellSize[0] * 0.35))
        arrow_h = int(arrow_w * 2.2)
        arr = Arrow("Assets/enemies/flecha.png", speed_px_s=380, scale_px=(arrow_w, arrow_h))
        arr.set_center(cx, cy)
        # Forzar daño de la flecha del arquero: 2
        setattr(arr, "damage", 2)
        self.enemy_projectiles.append(arr)
        
    def _spawn_enemy_sword_from_xy(self, cx, cy):
        sw = max(20, int(self.cellSize[0] * 0.40))
        sh = int(sw * 1.8)
        sword = Sword("Assets/enemies/sword.png", speed_px_s=320, scale_px=(sw, sh))
        sword.set_center(cx, cy)
        # Forzar daño del sword del escudero: 3
        setattr(sword, "damage", 3)
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
        from pantalla import pantalla_derrota   # llamada directa
        from session import get_current_user

        user = get_current_user()
        username = user.get("username", "Jugador")

        print("[Matrix] ¡Enemigo llegó arriba! -> GAME OVER")
        pantalla_derrota(username)   # ⬅ FULLSCREEN REAL, sin escalado




    def spawnEnemy(self, enemyType):
        last_row = self.ROWS - 1
        valid_cols = [1, 2, 3, 4, 5]
        col = random.choice(valid_cols)

        et = enemyType.lower()
        if et == "archer":
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
            # Forzamos HP y valores relevantes
            enemy.hp = 5
        elif et == "squire":
            enemy = Squire(
                spritesheet_path="Assets/enemies/escudero.png",
                cell_size=self.cellSize,
                image_pos=self.imagePos,
                rows=self.ROWS, cols=self.COLUMNS,
                row=last_row, col=col,
                frames_rows=3, frames_cols=4,
                wait_time=13.0, move_time=0.50, move_anim_fps=8, scale_fit=0.9,
                on_attack=self._spawn_enemy_sword_from_xy
            )
            enemy.hp = 10
        elif et == "lumberjack":
            enemy = Lumberjack(
                spritesheet_path="Assets/enemies/leñador.png",
                cell_size=self.cellSize,
                image_pos=self.imagePos,
                rows=self.ROWS, cols=self.COLUMNS,
                row=last_row, col=col,
                frames_rows=3, frames_cols=4,
                wait_time=10.0, move_time=0.50, move_anim_fps=8, scale_fit=0.9
            )
            enemy.hp = 20
        elif et == "cannibal":
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
            enemy.hp = 25
        else:
            return

        enemy.maxHp = getattr(enemy, "hp", None)
        enemy.coinsDropped = 0
        enemy.alive = True
        self.enemies.append(enemy)

    def setDifficulty(self, difficulty):
        """
        Ajusta los timers de spawn basado en la dificultad.
        Queremos reducir el tiempo de spawn en un 15% por cada paso:
          easy -> base
          normal -> base * 0.85
          hard -> base * 0.85 * 0.85 (acumulativo)
        """
        self.difficulty = difficulty.lower()
        if self.difficulty == "easy":
            mult = 1.0
        elif self.difficulty == "normal":
            mult = 0.85
        elif self.difficulty == "hard":
            mult = 0.85 * 0.85
        else:
            mult = 1.0
        # aplicar multiplicador sobre la base (en ms), evitando valores absurdos
        self.enemySpawnTimers = {k: max(200, int(v * mult)) for k, v in self.enemySpawnTimersBase.items()}
        # reiniciamos acumuladores para evitar spawn instantáneo al cambiar dificultad
        self.enemyAccumulators = {k: 0 for k in self.enemySpawnTimers}
        print(f"[Matrix] setDifficulty -> {self.difficulty}, spawn timers: {self.enemySpawnTimers}")

    def _applyDifficulty(self, baseTimers):
        """
        (Utilidad, no estrictamente usada) Mapea dificultad a multiplicadores legibles.
        """
        difficultyMultipliers = {
            "easy": 1.0,
            "normal": 0.85,
            "hard": 0.85 * 0.85
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
        beforeHp = getattr(enemy, "hp", None)
        if hasattr(enemy, "take_damage") and callable(enemy.take_damage):
            enemy.take_damage(int(damage))
        else:
            if beforeHp is not None:
                enemy.hp = max(0, int(beforeHp) - int(damage))
        afterHp = getattr(enemy, "hp", None)
        if beforeHp is None or afterHp is None:
            delta = int(damage)
        else:
            delta = max(0, int(beforeHp) - int(afterHp))
        self.globalDamageAccumulator += delta
        coinsShouldHave = self.globalDamageAccumulator // 20
        newCoins = coinsShouldHave - int(self.globalCoinsDropped)
        for _ in range(max(0, newCoins)):
            self.addCoin()
        self.globalCoinsDropped += max(0, newCoins)
        if afterHp is not None and afterHp <= 0:
            enemy.alive = False
            if callable(getattr(enemy, "on_death", None)):
                try:
                    enemy.on_death(enemy)
                except Exception:
                    pass

    def get_remaining_time(self):
        """
        Devuelve segundos restantes del nivel actual.
        """
        if self.levelIndex >= len(self.levelDurations):
            return 0
        remaining_ms = self.levelDurations[self.levelIndex] - self.levelTimeAccumulator
        if remaining_ms < 0:
            remaining_ms = 0
        return max(0, remaining_ms // 1000)
    
    def clear_units(self):
        # Limpia torres (intenta kill + quitar de grid)
        for tower in list(self.towers.values()):
            try:
                setattr(tower, "is_alive", False)
            except Exception:
                pass
            try:
                tower.kill()
            except Exception:
                pass
            r = getattr(tower, "row", None)
            c = getattr(tower, "col", None)
            if r is not None and c is not None and 0 <= r < self.ROWS and 0 <= c < self.COLUMNS:
                try:
                    if self.matrix[r][c] is tower:
                        self.matrix[r][c] = 0
                except Exception:
                    pass
        self.towers.clear()

        # Limpia enemigos
        for e in list(self.enemies):
            try:
                setattr(e, "alive", False)
            except Exception:
                pass
            try:
                e.kill()
            except Exception:
                pass
            r = getattr(e, "row", None)
            c = getattr(e, "col", None)
            if r is not None and c is not None and 0 <= r < self.ROWS and 0 <= c < self.COLUMNS:
                try:
                    if self.matrix[r][c] is e:
                        self.matrix[r][c] = 0
                except Exception:
                    pass
        self.enemies.clear()

        # Limpia rooks
        for rook in list(self.rooksList):
            try:
                setattr(rook, "is_alive", False)
            except Exception:
                pass
            try:
                rook.kill()
            except Exception:
                pass
            r = getattr(rook, "row", None)
            c = getattr(rook, "col", None)
            if r is not None and c is not None and 0 <= r < self.ROWS and 0 <= c < self.COLUMNS:
                try:
                    if self.matrix[r][c] is rook:
                        self.matrix[r][c] = 0
                except Exception:
                    pass
        self.rooksList.clear()

        # Limpia avatars
        for avatar in list(self.avatarsList):
            try:
                setattr(avatar, "is_alive", False)
            except Exception:
                pass
            try:
                avatar.kill()
            except Exception:
                pass
            r = getattr(avatar, "row", None)
            c = getattr(avatar, "col", None)
            if r is not None and c is not None and 0 <= r < self.ROWS and 0 <= c < self.COLUMNS:
                try:
                    if self.matrix[r][c] is avatar:
                        self.matrix[r][c] = 0
                except Exception:
                    pass
        self.avatarsList.clear()

        # Proyectiles
        try:
            for p in list(self.projectiles):
                try:
                    p.kill()
                except Exception:
                    pass
            self.projectiles.clear()
        except Exception:
            self.projectiles = []
        try:
            for p in list(self.enemy_projectiles):
                try:
                    p.kill()
                except Exception:
                    pass
            self.enemy_projectiles.clear()
        except Exception:
            self.enemy_projectiles = []

        # Limpia la matriz de referencias no-int (si hay objetos)
        for r in range(self.ROWS):
            for c in range(self.COLUMNS):
                cell = self.matrix[r][c]
                if cell and not isinstance(cell, int):
                    self.matrix[r][c] = 0

        # Reset acumuladores y timers de spawn config
        try:
            self.enemyAccumulators = {k: 0 for k in self.enemySpawnTimers}
        except Exception:
            pass
        for k, cfg in self.enemyConfigs.items():
            try:
                cfg["timer"] = random.uniform(cfg["min"], cfg["max"])
            except Exception:
                pass
        print("[Matrix] clear_units: torres/enemigos/rooks/avatars/proyectiles limpiados")

    def shoot_from_selected_tower(self):
        """Dispara el proyectil de la torre seleccionada hacia abajo (usa los métodos existentes)."""
        pos = self.calculateCell(self.selector.position)
        if not pos:
            return

        row, col = pos
        tower = self.towers.get((row, col))
        if not tower:
            return

        # Dispara según el tipo de torre
        if isinstance(tower, FireTower):
            self._spawn_fireball_below(tower)
            print("[Matrix] Disparo manual de FireTower")
        elif isinstance(tower, WaterTower):
            self._spawn_waterdrop_below(tower)
            print("[Matrix] Disparo manual de WaterTower")
        elif isinstance(tower, SandTower):
            self._spawn_sandshard_below(tower)
            print("[Matrix] Disparo manual de SandTower")
        elif isinstance(tower, RockTower):
            self._spawn_rock_below(tower)
            print("[Matrix] Disparo manual de RockTower")
