import pygame

class AssetsUtils:
    """Funciones estáticas para manejo de assets y spritesheets."""
    
    @staticmethod
    def load_first_frame(path: str, frames_cols: int, frames_rows: int, icon_size: tuple[int, int] | None):
        """Carga el primer frame (0,0) de una spritesheet y lo escala a icon_size (w,h)."""
        sheet = pygame.image.load(path).convert_alpha()
        sw, sh = sheet.get_width(), sheet.get_height()
        fw, fh = sw // frames_cols, sh // frames_rows
        fh -= 30
        rect = pygame.Rect(0, 0, fw, fh)

        frame = pygame.Surface((fw, fh), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), rect)

        if icon_size is not None:
            frame = pygame.transform.smoothscale(frame, icon_size)

        return frame
