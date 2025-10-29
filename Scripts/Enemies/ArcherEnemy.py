# enemies/Flechero.py
import pygame

class Archer(pygame.sprite.Sprite):
    """
    Reglas:
      - Idle: 12 s con frame (0,0) (fila 0, col 0)
      - Mover: sube 1 celda; anima fila 1 completa (cols 0..3) durante move_time
      - Disparo: usa frame (0,2) por un pulso corto al llamar trigger_shot()
    """
    def __init__(self, spritesheet_path, cell_size, image_pos, rows, cols,
                 row, col, frames_rows=3, frames_cols=4,
                 wait_time=12.0, move_time=0.35, move_anim_fps=10, scale_fit=0.9):
        super().__init__()
        self.cell_w, self.cell_h = cell_size
        self.img_x, self.img_y = image_pos  # topleft de la matriz
        self.rows = rows
        self.cols = cols
        self.row = row
        self.col = col

        # Timers/estado
        self.state = "idle"      # "idle" | "moving" | "shot"
        self.wait_time = wait_time
        self.wait_timer = 0.0

        self.move_time = move_time
        self.move_timer = 0.0
        self.move_anim_fps = move_anim_fps
        self.move_anim_time = 0.0
        self.move_anim_index = 0

        self.shot_pulse = 0.18
        self.shot_timer = 0.0

        # Cargar y recortar sprites
        sheet = pygame.image.load(spritesheet_path).convert_alpha()
        sw, sh = sheet.get_size()
        fw = sw // frames_cols
        fh = sh // frames_rows

        tw = int(self.cell_w * scale_fit)
        th = int(self.cell_h * scale_fit)

        self.frames_cols = frames_cols
        self.frames = []
        for r in range(frames_rows):
            for c in range(frames_cols):
                f = sheet.subsurface(pygame.Rect(c*fw, r*fh, fw, fh))
                f = pygame.transform.smoothscale(f, (tw, th))
                self.frames.append(f)
        self.idx = lambda r, c: r * self.frames_cols + c

        # Imagen/rect inicial (idle)
        self.image = self.frames[self.idx(0, 0)]
        cx, cy = self.cell_center_px(self.row, self.col)
        self.rect = self.image.get_rect(center=(cx, cy))

        # Para interpolar desplazamiento
        self.move_start = (cx, cy)
        self.move_target = (cx, cy)

        self.alive = True

    # --- utilidades ---
    def cell_center_px(self, row, col):
        x = self.img_x + col * self.cell_w + self.cell_w // 2
        y = self.img_y + row * self.cell_h + self.cell_h // 2
        return x, y

    def set_center(self, cx, cy):
        self.rect = self.image.get_rect(center=(cx, cy))

    @staticmethod
    def lerp(a, b, t): return a + (b - a) * t

    # --- API ---
    def trigger_shot(self):
        self.state = "shot"
        self.shot_timer = self.shot_pulse
        self.image = self.frames[self.idx(0, 2)]  # disparo: (0,2)

    # --- ciclo ---
    def update(self, dt):
        if not self.alive:
            return

        if self.state == "idle":
            self.image = self.frames[self.idx(0, 0)]
            self.wait_timer += dt
            if self.wait_timer >= self.wait_time:
                self.wait_timer -= self.wait_time
                self._start_move_up()

        elif self.state == "moving":
            # anim fila 1 (row=1), columnas 0..3
            step = 1.0 / max(self.move_anim_fps, 1)
            self.move_anim_time += dt
            while self.move_anim_time >= step:
                self.move_anim_time -= step
                self.move_anim_index = (self.move_anim_index + 1) % self.frames_cols
                self.image = self.frames[self.idx(1, self.move_anim_index)]

            # interpolación de posición
            self.move_timer += dt
            t = min(self.move_timer / self.move_time, 1.0)
            nx = self.lerp(self.move_start[0], self.move_target[0], t)
            ny = self.lerp(self.move_start[1], self.move_target[1], t)
            self.set_center(nx, ny)

            if t >= 1.0:
                self.state = "idle"
                self.move_timer = 0.0
                self.move_anim_time = 0.0
                self.move_anim_index = 0

        elif self.state == "shot":
            self.shot_timer -= dt
            if self.shot_timer <= 0:
                self.state = "idle"

    # --- helpers ---
    def _start_move_up(self):
        if self.row <= 0:
            # Aquí podrías aplicar daño a base o desaparecer
            self.alive = False
            return
        self.state = "moving"
        self.move_timer = 0.0
        self.move_anim_time = 0.0
        self.move_anim_index = 0
        self.move_start = (self.rect.centerx, self.rect.centery)
        self.row -= 1
        self.move_target = self.cell_center_px(self.row, self.col)
