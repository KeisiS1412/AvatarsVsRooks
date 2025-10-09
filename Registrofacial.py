import pygame
import cv2
import numpy as np
import os

pygame.init()

# === Configuración general ===
WIDTH, HEIGHT = 800, 500
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Registro Facial LBPH")

FONT = pygame.font.SysFont("Arial", 28)
COLOR_FONDO = (255, 60, 60)
COLOR_BOTON = (10, 10, 10)
COLOR_BOTON_HOVER = (60, 60, 60)
COLOR_TEXTO_BOTON = (255, 255, 255)
COLOR_TITULO = (0, 0, 0)

USERS_DIR = "users_lbph"
os.makedirs(USERS_DIR, exist_ok=True)


def draw_text(surface, text, pos, color=(255, 255, 255)):
    render = FONT.render(text, True, color)
    surface.blit(render, pos)


class RegistroFacial:
    def __init__(self, usuario_actual=None):
        self.running = True
        self.name = usuario_actual.strip().lower() if usuario_actual else "usuario"
        print(f"[DEBUG] Usuario activo: {self.name}")

    def registrar_rostro(self):
        """Captura 10 imágenes del rostro actual y las guarda como .npy"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] No se pudo acceder a la cámara.")
            return

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        count = 0
        faces_data = []
        clock = pygame.time.Clock()

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                rostro = gray[y:y+h, x:x+w]
                rostro_resized = cv2.resize(rostro, (100, 100))
                faces_data.append(rostro_resized)
                count += 1
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.flipud(np.rot90(frame_rgb)))
            SCREEN.fill(COLOR_FONDO)
            SCREEN.blit(frame_surface, (100, 50))
            draw_text(SCREEN, f"Captura {count}/10", (WIDTH//2 - 80, HEIGHT - 60))
            draw_text(SCREEN, "Presiona Q para cancelar", (WIDTH//2 - 120, HEIGHT - 30))
            pygame.display.flip()
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release(); pygame.quit(); return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    cap.release(); return

            if count >= 10:
                break

        cap.release()
        if faces_data:
            mean_face = np.mean(faces_data, axis=0)
            filename = f"{self.name}.npy"
            filepath = os.path.join(USERS_DIR, filename)
            np.save(filepath, mean_face)
            print(f"[OK] Rostro guardado correctamente en '{filepath}'")
        else:
            print("[ERROR] No se capturó ningún rostro.")

    def menu(self):
        """Menú Pygame con dos botones: Registrar y Salir"""
        buttons = [
            ("Registrar rostro", self.registrar_rostro),
            ("Salir", self.exit_app)
        ]
        clock = pygame.time.Clock()

        while self.running:
            SCREEN.fill(COLOR_FONDO)
            draw_text(SCREEN, "MENÚ DE REGISTRO FACIAL", (200, 60), COLOR_TITULO)

            mouse_pos = pygame.mouse.get_pos()
            for i, (text, action) in enumerate(buttons):
                rect = pygame.Rect(WIDTH//2 - 150, 180 + i*120, 300, 70)
                color = COLOR_BOTON_HOVER if rect.collidepoint(mouse_pos) else COLOR_BOTON
                pygame.draw.rect(SCREEN, color, rect)
                draw_text(SCREEN, text, (rect.x + 40, rect.y + 20))
                if pygame.mouse.get_pressed()[0] and rect.collidepoint(mouse_pos):
                    action()

            pygame.display.flip()
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_app()

    def exit_app(self):
        self.running = False
        pygame.quit()


if __name__ == "__main__":
    app = RegistroFacial("usuario")
    app.menu()
