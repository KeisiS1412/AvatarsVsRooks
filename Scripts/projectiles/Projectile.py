# Scripts/projectiles/Projectile.py
import pygame

class Projectile:
    """
    Proyectil animado:
    - Carga spritesheet, recorta por alfa, normaliza a un lienzo común bottom-center y escala.
    - Se anima por FPS y se mueve con velocidad (vx, vy) en píxeles/seg.
    """

    def __init__(
        self,
        spritesheet_path: str,
        frames_cols: int,
        frames_rows: int,
        fps: int,
        cell_size: tuple[int, int],
        scale_fit: float = 0.55,
        crop_top: int = 0, crop_bottom: int = 0, crop_left: int = 0, crop_right: int = 0,
        pixel_art: bool = False,
        use_rows: tuple[int, ...] = (0,),
        use_cols: tuple[int, ...] | None = None,
        speed_px_s: float = 320.0,
        vx: float = 0.0,
        vy: float = 320.0
    ):
        self.cell_w, self.cell_h = cell_size
        self.frames = []
        self._accum = 0
        self._index = 0
        self.fps = max(1, fps)
        self.ms_per_frame = int(1000 / self.fps)
        self.speed_px_s = speed_px_s
        self.vx = vx
        self.vy = vy

        sheet = pygame.image.load(spritesheet_path).convert_alpha()
        sw, sh = sheet.get_width(), sheet.get_height()
        src_w = sw // max(1, frames_cols)
        src_h = sh // max(1, frames_rows)

        trim_w = max(1, src_w - crop_left - crop_right)
        trim_h = max(1, src_h - crop_top  - crop_bottom)

        # Extraer frames filtrando filas/columnas
        raw_frames = []
        for r in range(frames_rows):
            if r not in use_rows:
                continue
            for c in range(frames_cols):
                if use_cols is not None and c not in use_cols:
                    continue
                sx = c * src_w + crop_left
                sy = r * src_h + crop_top
                rect = pygame.Rect(sx, sy, trim_w, trim_h)
                f = pygame.Surface((trim_w, trim_h), pygame.SRCALPHA)
                f.blit(sheet, (0, 0), rect)
                raw_frames.append(f)

        if not raw_frames:
            rect = pygame.Rect(0, 0, src_w, src_h)
            f = pygame.Surface((src_w, src_h), pygame.SRCALPHA)
            f.blit(sheet, (0, 0), rect)
            raw_frames.append(f)

        # Recorte por alfa y normalización
        tight = []
        max_w = 1
        max_h = 1
        for f in raw_frames:
            bbox = f.get_bounding_rect(min_alpha=1)
            if bbox.w <= 0 or bbox.h <= 0:
                t = pygame.Surface((1, 1), pygame.SRCALPHA)
            else:
                t = pygame.Surface((bbox.w, bbox.h), pygame.SRCALPHA)
                t.blit(f, (0, 0), bbox)
            tight.append(t)
            if t.get_width() > max_w:  max_w = t.get_width()
            if t.get_height() > max_h: max_h = t.get_height()

        canvases = []
        for t in tight:
            canvas = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
            ox = (max_w - t.get_width()) // 2
            oy =  max_h - t.get_height()
            canvas.blit(t, (ox, oy))
            canvases.append(canvas)

        scaler = pygame.transform.scale if pixel_art else pygame.transform.smoothscale
        target_w = max(1, int(self.cell_w * scale_fit))
        scale = target_w / max(1, max_w)
        target_h = max(1, int(max_h * scale))
        self.frames = [scaler(f, (target_w, target_h)) for f in canvases]

        self.rect = self.frames[0].get_rect(topleft=(0, 0))  # se posiciona luego

    # Helpers de posicionamiento
    def set_top_center(self, x_center: int, y_top: int):
        self.rect.topleft = (x_center - self.rect.w // 2, y_top)

    def update(self, dt_ms: int):
        # animación
        self._accum += dt_ms
        while self._accum >= self.ms_per_frame:
            self._accum -= self.ms_per_frame
            self._index = (self._index + 1) % len(self.frames)

        # movimiento
        dt = dt_ms / 1000.0
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.frames[self._index], self.rect.topleft)
