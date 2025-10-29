# Enemies/SquireEnemy.py
import pygame

class Squire(pygame.sprite.Sprite):
    """
    Squire (escudero)
    - Idle: 12 s en frame (row=0, col=0).
    - Move Up: sube 1 celda; anima toda la fila 1 (cols 0..3).
    Estados con nombres en inglés: "idle", "move_up".
    """
    def __init__(self, spritesheet_path, cell_size, image_pos,
                 rows, cols, row, col,
                 frames_rows=3, frames_cols=4,
                 wait_time=12.0, move_time=0.35,
                 move_anim_fps=10, scale_fit=0.9):
        super().__init__()
        self.cell_w, self.cell_h = cell_size
        self.image_pos = image_pos  # topleft absoluto de la matriz
        self.grid_rows = rows
        self.grid_cols = cols
        self.row = row
        self.col = col

        self.frames_rows = frames_rows
        self.frames_cols = frames_cols
        self.wait_time = wait_time
        self.move_time = move_time
        self.move_anim_fps = move_anim_fps

        self.state = "idle"      # "idle" | "move_up"
        self.timer = 0.0
        self.anim_timer = 0.0
        self.anim_index = 0

        # cargar spritesheet y fraccionar
        sheet = pygame.image.load(spritesheet_path).convert_alpha()
        sw, sh = sheet.get_width(), sheet.get_height()
        fw, fh = sw // frames_cols, sh // frames_rows

        raw_idle = sheet.subsurface(pygame.Rect(0 * fw, 0 * fh, fw, fh))
        raw_move = [sheet.subsurface(pygame.Rect(c * fw, 1 * fh, fw, fh))
                    for c in range(frames_cols)]

        # escalar a celda (scale_fit relativo)
        target_w = int(self.cell_w * scale_fit)
        target_h = int(self.cell_h * scale_fit)
        self.frames_idle = [pygame.transform.smoothscale(raw_idle, (target_w, target_h))]
        self.frames_move = [pygame.transform.smoothscale(img, (target_w, target_h))
                            for img in raw_move]

        self.image = self.frames_idle[0]
        self.rect = self.image.get_rect()
        self._sync_rect_to_cell()

        self.alive = True  # por consistencia con tu manejador

    # helpers
    def _cell_to_pixel(self, row, col):
        x = self.image_pos[0] + col * self.cell_w
        y = self.image_pos[1] + row * self.cell_h
        return x, y

    def _sync_rect_to_cell(self):
        px, py = self._cell_to_pixel(self.row, self.col)
        # centrar sprite dentro de la celda
        self.rect.centerx = px + self.cell_w // 2
        self.rect.bottom  = py + self.cell_h  # apoyado “al piso” de la celda

    # ciclo
    def update(self, dt):
        self.timer += dt

        if self.state == "idle":
            # quieto en (0,0)
            self.image = self.frames_idle[0]
            if self.timer >= self.wait_time:
                self.state = "move_up"
                self.timer = 0.0
                self.anim_timer = 0.0
                self.anim_index = 0

        elif self.state == "move_up":
            # animación de fila 1
            self.anim_timer += dt
            if self.anim_timer >= 1.0 / self.move_anim_fps:
                self.anim_timer = 0.0
                self.anim_index = (self.anim_index + 1) % len(self.frames_move)
            self.image = self.frames_move[self.anim_index]

            if self.timer >= self.move_time:
                # subir una celda
                new_row = max(0, self.row - 1)
                self.row = new_row
                self._sync_rect_to_cell()
                self.state = "idle"
                self.timer = 0.0

                # si llegó arriba del todo, puedes decidir marcarlo como muerto o futuro "attack"
                if self.row == 0:
                    # por ahora lo dejamos vivo para que luego lance espada.
                    pass
