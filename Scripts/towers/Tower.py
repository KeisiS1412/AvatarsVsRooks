import pygame

class Tower:
    """
    Base de torres animadas:
    - Recorta por alfa cada frame, normaliza a lienzo común (max_w x max_h) bottom-center.
    - Permite filtrar filas y columnas del spritesheet (use_rows, use_cols).
    - Blindajes: _accum/_index inicializados SIEMPRE y fallback si no hay frames.
    """

    def __init__(
        self,
        spritesheet_path: str,
        frames_cols: int,
        frames_rows: int,
        fps: int,
        cell_size: tuple[int, int],
        cell_topleft: tuple[int, int],
        row: int,
        col: int,
        scale_fit: float = 0.95,
        crop_top: int = 0, crop_bottom: int = 0, crop_left: int = 0, crop_right: int = 0,
        anchor_bottom_center: bool = True,
        pixel_art: bool = False,
        use_rows: tuple[int, ...] = (0,),
        use_cols: tuple[int, ...] | None = None
    ):
        # --- estado base / blindajes ---
        self.row = row
        self.col = col
        self.cell_w, self.cell_h = cell_size
        self.x, self.y = cell_topleft
        self.fps = max(1, fps)
        self.ms_per_frame = int(1000 / self.fps)
        self._accum = 0          # <- inicializado desde el inicio
        self._index = 0          # <- inicializado desde el inicio
        self.frames: list[pygame.Surface] = []

        # --- cargar hoja ---
        sheet = pygame.image.load(spritesheet_path).convert_alpha()
        sw, sh = sheet.get_width(), sheet.get_height()
        src_w = sw // max(1, frames_cols)
        src_h = sh // max(1, frames_rows)

        # recorte manual
        trim_w = max(1, src_w - crop_left - crop_right)
        trim_h = max(1, src_h - crop_top  - crop_bottom)

        # --- extraer frames crudos filtrando filas/columnas ---
        raw_frames: list[pygame.Surface] = []
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

        # --- Fallback si no se seleccionó ningún frame ---
        if not raw_frames:
            # intenta al menos tomar (0,0) sin recortes para no romper
            rect = pygame.Rect(0, 0, src_w, src_h)
            f = pygame.Surface((src_w, src_h), pygame.SRCALPHA)
            f.blit(sheet, (0, 0), rect)
            raw_frames.append(f)

        # --- recorte por alfa + medir max_w/max_h ---
        tight_frames: list[pygame.Surface] = []
        max_w = 1
        max_h = 1
        for f in raw_frames:
            bbox = f.get_bounding_rect(min_alpha=1)
            if bbox.w <= 0 or bbox.h <= 0:
                trimmed = pygame.Surface((1, 1), pygame.SRCALPHA)
            else:
                trimmed = pygame.Surface((bbox.w, bbox.h), pygame.SRCALPHA)
                trimmed.blit(f, (0, 0), bbox)
            tight_frames.append(trimmed)
            if trimmed.get_width()  > max_w: max_w = trimmed.get_width()
            if trimmed.get_height() > max_h: max_h = trimmed.get_height()

        # --- normalizar a lienzo común bottom-center ---
        norm_frames: list[pygame.Surface] = []
        for tf in tight_frames:
            canvas = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
            ox = (max_w - tf.get_width()) // 2
            oy =  max_h - tf.get_height()
            canvas.blit(tf, (ox, oy))
            norm_frames.append(canvas)

        # --- escalar todos igual ---
        scaler = pygame.transform.scale if pixel_art else pygame.transform.smoothscale
        target_w = max(1, int(self.cell_w * scale_fit))
        scale = target_w / max(1, max_w)
        target_h = max(1, int(max_h * scale))
        self.frames = [scaler(f, (target_w, target_h)) for f in norm_frames]

        # Si por alguna razón no hay frames (hiper raro), crea un dummy
        if not self.frames:
            dummy = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
            self.frames = [dummy]

        # --- anclaje dentro de la celda ---
        if anchor_bottom_center:
            self.offset_x = (self.cell_w - target_w) // 2
            self.offset_y = self.cell_h - target_h
        else:
            self.offset_x = (self.cell_w - target_w) // 2
            self.offset_y = (self.cell_h - target_h) // 2

        # offsets de corrección manual (por si la hoja está descentrada)
        self.offset_fix_x = 0
        self.offset_fix_y = 0

    def update(self, dt_ms: int):
        # si hubiera un caso extremo de 0 frames, evita crash
        if not self.frames:
            return
        self._accum += dt_ms
        # protección: len(self.frames) >= 1 garantizado por el dummy
        while self._accum >= self.ms_per_frame:
            self._accum -= self.ms_per_frame
            self._index = (self._index + 1) % len(self.frames)

    def draw(self, screen: pygame.Surface):
        if not self.frames:
            return
        screen.blit(
            self.frames[self._index],
            (self.x + self.offset_x + self.offset_fix_x, self.y + self.offset_y + self.offset_fix_y)
        )
