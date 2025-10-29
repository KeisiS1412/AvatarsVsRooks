# Enemies/LumberjackEnemy.py
import pygame

class Cannibal(pygame.sprite.Sprite):
    """
    Lumberjack
    - idle: 12 s en frame (row=0, col=0)
    - move_up: sube 1 celda, animando fila 1 (cols 0..3)
    States: "idle", "move_up"
    """
    def __init__(self, spritesheet_path, cell_size, image_pos,
                 rows, cols, row, col,
                 frames_rows=3, frames_cols=4,
                 wait_time=14.0, move_time=0.50,
                 move_anim_fps=8, scale_fit=-0.3,
                 crop_left=15, crop_right=1, crop_top=5, crop_bottom=0):
        super().__init__()
        self.cell_w, self.cell_h = cell_size
        self.image_pos = image_pos
        self.grid_rows = rows
        self.grid_cols = cols
        self.row = row
        self.col = col

        self.frames_rows = frames_rows
        self.frames_cols = frames_cols

        self.wait_time = wait_time       # tiempo quieto
        self.move_time = move_time       # duración del paso de 1 celda
        self.move_anim_fps = move_anim_fps

        self.state = "idle"              # "idle" | "move_up"
        self.timer = 0.0
        self.anim_timer = 0.0
        self.anim_index = 0

        self.crop_left  = crop_left
        self.crop_right = crop_right
        self.crop_top   = crop_top
        self.crop_bottom= crop_bottom

        sheet = pygame.image.load(spritesheet_path).convert_alpha()
        sw, sh = sheet.get_width(), sheet.get_height()
        fw, fh = sw // frames_cols, sh // frames_rows

        # cargar spritesheet y recortar
        sheet = pygame.image.load(spritesheet_path).convert_alpha()
        sw, sh = sheet.get_width(), sheet.get_height()
        fw, fh = sw // frames_cols, sh // frames_rows

        raw_idle = sheet.subsurface(pygame.Rect(0 * fw, 0 * fh, fw, fh))
        raw_move = [sheet.subsurface(pygame.Rect(c * fw, 1 * fh, fw, fh))
                    for c in range(frames_cols)]

        tgt_w = int(self.cell_w * scale_fit)
        tgt_h = int(self.cell_h * scale_fit)
        self.frames_idle = [pygame.transform.smoothscale(raw_idle, (tgt_w, tgt_h))]
        self.frames_move = [pygame.transform.smoothscale(img, (tgt_w, tgt_h))
                            for img in raw_move]

        self.image = self.frames_idle[0]
        self.rect = self.image.get_rect()
        self._sync_rect_to_cell()

        self.alive = True

        def cut(r, c):
            # recorte interno (quita un borde para evitar bleeding del frame vecino)
            x = c * fw + self.crop_left
            y = r * fh + self.crop_top
            w = fw - (self.crop_left + self.crop_right)
            h = fh - (self.crop_top  + self.crop_bottom)
            return sheet.subsurface(pygame.Rect(x, y, w, h))

        raw_idle = cut(0, 0)
        raw_move = [cut(1, c) for c in range(frames_cols)]

        tgt_w = int(self.cell_w * scale_fit)
        tgt_h = int(self.cell_h * scale_fit)

            
        self.frames_idle = [pygame.transform.scale(raw_idle, (tgt_w, tgt_h))]
        self.frames_move = [pygame.transform.scale(img, (tgt_w, tgt_h)) for img in raw_move]
    
    def _cell_to_pixel(self, row, col):
        x = self.image_pos[0] + col * self.cell_w
        y = self.image_pos[1] + row * self.cell_h
        return x, y

    def _sync_rect_to_cell(self):
        px, py = self._cell_to_pixel(self.row, self.col)
        self.rect.centerx = px + self.cell_w // 2
        self.rect.bottom  = py + self.cell_h

    # loop
    def update(self, dt):
        # dt en segundos
        self.timer += dt

        if self.state == "idle":
            self.image = self.frames_idle[0]
            if self.timer >= self.wait_time:
                self.state = "move_up"
                self.timer = 0.0
                self.anim_timer = 0.0
                self.anim_index = 0

        elif self.state == "move_up":
            self.anim_timer += dt
            if self.anim_timer >= 1.0 / self.move_anim_fps:
                self.anim_timer = 0.0
                self.anim_index = (self.anim_index + 1) % len(self.frames_move)
            self.image = self.frames_move[self.anim_index]

            if self.timer >= self.move_time:
                self.row = max(0, self.row - 1)  # sube una celda
                self._sync_rect_to_cell()
                self.state = "idle"
                self.timer = 0.0
