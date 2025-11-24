import pygame

class TextBox:
    """Campo de texto interactivo con soporte para contraseñas, placeholder y validación visual."""

    def __init__(self, x, y, width, height, font, inactiveColor, activeColor, placeholder="",
                 content_offset_y=10, border_radius=8, clearsOnClick=True,
                 is_password=False,          # << NUEVO
                 right_padding=40            # << NUEVO (espacio para el icono de ojo)
                 ):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.inactiveColor = inactiveColor
        self.activeColor = activeColor
        self.currentColor = self.inactiveColor

        self.text = placeholder
        self.placeholder = placeholder
        self.font = font
        self.isActive = False

        self.cursorVisible = True
        self.cursorTimer = 0
        self.cursorInterval = 500

        self.content_offset_y = content_offset_y
        self.border_radius = border_radius
        self.clearsOnClick = clearsOnClick

        self.isInvalid = False
        self.errorBorderColor = (180, 180, 180)  # Color del borde en caso de error

        # ---- NUEVO: modo contraseña ----
        self.isPassword = bool(is_password)
        self.showPassword = False
        self.right_padding = right_padding

    # ====== NUEVOS MÉTODOS PARA CONTRASEÑA ======
    def set_password_mode(self, enabled: bool):
        """Activa/desactiva el modo contraseña (•)."""
        self.isPassword = bool(enabled)

    def set_show_password(self, show: bool):
        """Muestra/oculta el texto real de la contraseña."""
        self.showPassword = bool(show)

    def toggle_password_visibility(self):
        """Alterna visibilidad (ojo)."""
        self.showPassword = not self.showPassword

    # =============================================

    def draw(self, screen, deltaTime=0, scrollOffset=0):  # Dibuja la caja y el texto
        adjRect = self.rect.move(0, -scrollOffset)
        pygame.draw.rect(screen, self.currentColor, adjRect, border_radius=self.border_radius)
        borderColor = self.errorBorderColor if self.isInvalid else (180, 180, 180)
        pygame.draw.rect(screen, borderColor, adjRect, width=2, border_radius=self.border_radius)

        padding = 10
        # deja espacio a la derecha para el icono "ojo"
        maxTextWidth = adjRect.width - padding * 2 - self.right_padding

        # texto visible (puntitos si es password y está oculto)
        if self.isPassword and not self.showPassword and self.text != self.placeholder:
            displayText = "•" * len(self.text)
        else:
            displayText = self.text

        # color gris cuando es placeholder
        textColor = (180, 180, 180) if self.text == self.placeholder else (180, 180, 180)

        # recorta por la izquierda si se pasa del ancho disponible
        textToRender = displayText
        while self.font.size(textToRender)[0] > maxTextWidth and len(textToRender) > 0:
            textToRender = textToRender[1:]

        visibleSurface = self.font.render(textToRender, True, textColor)
        screen.blit(visibleSurface, (adjRect.x + 20, adjRect.y + padding + 5 ))

        # cursor parpadeante
        if self.isActive:
            self.cursorTimer += deltaTime
            if self.cursorTimer >= self.cursorInterval:
                self.cursorVisible = not self.cursorVisible
                self.cursorTimer = 0
            if self.cursorVisible:
                cursorX = adjRect.x + 20 + visibleSurface.get_width()
                cursorY = adjRect.y + padding + 5
                cursorHeight = visibleSurface.get_height()
                pygame.draw.line(screen, (180, 180, 180), (cursorX, cursorY), (cursorX, cursorY + cursorHeight), 2)

    def handleEvent(self, event, scrollOffset=0):  # Maneja clics y escritura del usuario
        adjRect = self.rect.move(0, -scrollOffset)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if adjRect.collidepoint(event.pos):
                self.isActive = True
                self.currentColor = self.activeColor
                self.isInvalid = False
                if self.clearsOnClick and self.text == self.placeholder:
                    self.text = ""  # Borra el placeholder al hacer clic
            else:
                self.isActive = False
                self.currentColor = self.inactiveColor
                if self.text == "":  # Si quedó vacía, vuelve a mostrar placeholder
                    self.text = self.placeholder

        if event.type == pygame.KEYDOWN and self.isActive:
            if event.key == pygame.K_BACKSPACE:
                if self.text != self.placeholder:
                    self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.isActive = False
                self.currentColor = self.inactiveColor
                if self.text == "":
                    self.text = self.placeholder
            else:
                # evita escribir sobre el placeholder literal
                if self.text == self.placeholder and self.clearsOnClick:
                    self.text = ""
                # agrega el carácter
                self.text += event.unicode

    def update(self, deltaTime=0, scrollOffset=0):  # Controla el parpadeo del cursor
        if self.isActive:
            self.cursorTimer += deltaTime
            if self.cursorTimer >= self.cursorInterval:
                self.cursorVisible = not self.cursorVisible
                self.cursorTimer = 0

    def getText(self):  # Devuelve el texto actual
        return "" if self.text == self.placeholder else self.text

    def markInvalid(self):  # Marca el campo como inválido (error visual)
        self.isInvalid = True
