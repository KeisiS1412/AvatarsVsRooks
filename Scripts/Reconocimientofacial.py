import pygame
import cv2
import numpy as np
import os
import time

pygame.init()

# === Configuración general ===
WIDTH, HEIGHT = 800, 500
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reconocimiento Facial LBPH")

FONT = pygame.font.SysFont("Arial", 28)
COLOR_FONDO = (255, 60, 60)
COLOR_BOTON = (10, 10, 10)
COLOR_BOTON_HOVER = (60, 60, 60)
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_BOTON = (255, 255, 255)
COLOR_TITULO = (0, 0, 0)

USERS_DIR = "users_lbph"
os.makedirs(USERS_DIR, exist_ok=True)


def draw_text(surface, text, pos, color=COLOR_TEXTO):
    text_render = FONT.render(text, True, color)
    surface.blit(text_render, pos)


class ReconocimientoFacialLBPH:
    def __init__(self, usuario_actual=None):
        self.running = True
        self.name = usuario_actual.strip().lower() if usuario_actual else ""
        print(f"[DEBUG] Usuario activo: {self.name}")

    def registrar_rostro(self):
        """Captura 10 imágenes del rostro actual y las guarda como .npy sin validación previa"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("No se pudo acceder a la cámara.")
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
                face = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face, (100, 100))
                faces_data.append(face_resized)
                count += 1
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

            # Mostrar cámara en ventana Pygame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.flipud(np.rot90(frame_rgb)))
            SCREEN.fill(COLOR_FONDO)
            SCREEN.blit(frame_surface, (100, 50))
            draw_text(SCREEN, f"Captura {count}/10", (WIDTH//2 - 80, HEIGHT - 60), (255,255,255))
            draw_text(SCREEN, "Presiona Q para cancelar", (WIDTH//2 - 120, HEIGHT - 30), (0,0,0))
            pygame.display.flip()
            clock.tick(30)

            # Eventos Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    cap.release()
                    return

            if count >= 10:
                break

        cap.release()
        if faces_data:
            mean_face = np.mean(faces_data, axis=0)
            filename = f"{self.name or 'rostro_generico'}.npy"
            filepath = os.path.join(USERS_DIR, filename)
            np.save(filepath, mean_face)
            print(f" Rostro guardado correctamente en '{filepath}'")
        else:
            print(" No se capturó ningún rostro.")

    def cargar_rostros(self):
        """Carga los rostros .npy guardados en users_lbph"""
        encodings, names = [], []
        for file in os.listdir(USERS_DIR):
            if file.endswith(".npy"):
                path = os.path.join(USERS_DIR, file)
                encoding = np.load(path).flatten()
                encodings.append(encoding)
                names.append(os.path.splitext(file)[0])
        return encodings, names

    def login_con_rostro(self):
        """Compara el rostro actual con los registrados"""
        known_encodings, known_names = self.cargar_rostros()
        if not known_encodings:
            print(" No hay rostros registrados.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("No se pudo acceder a la cámara.")
            return

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        clock = pygame.time.Clock()
        start_time = time.time()
        recognized = False

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face = cv2.resize(gray[y:y+h, x:x+w], (100, 100)).flatten()
                distances = [np.linalg.norm(face - known) for known in known_encodings]
                min_distance = min(distances)
                best_match = np.argmin(distances)

                if min_distance < 10000:
                    name = known_names[best_match]
                    label = f"Reconocido: {name}"
                    color = (0, 255, 0)
                    recognized = True
                else:
                    label = "Desconocido"
                    color = (255, 0, 0)

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # Mostrar cámara dentro de Pygame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.flipud(np.rot90(frame_rgb)))
            SCREEN.fill(COLOR_FONDO)
            SCREEN.blit(frame_surface, (100, 50))
            draw_text(SCREEN, "Presiona Q para cancelar", (WIDTH//2 - 120, HEIGHT - 30), (0,0,0))
            pygame.display.flip()
            clock.tick(30)

            # Eventos Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    cap.release()
                    return

            if recognized:
                print(f"Bienvenido, {name}!")
                time.sleep(1)
                cap.release()
                return

            if time.time() - start_time > 15:
                break

        cap.release()
        print(" Login fallido: rostro no reconocido.")

    def menu(self):
        """Menú principal en Pygame"""
        buttons = [
            ("Registrar rostro", self.registrar_rostro),
            ("Login con rostro", self.login_con_rostro),
            ("Salir", self.exit_app)
        ]
        clock = pygame.time.Clock()

        while self.running:
            SCREEN.fill(COLOR_FONDO)
            draw_text(SCREEN, f"Reconocimiento Facial ({self.name or 'Invitado'})", (150, 50), COLOR_TITULO)

            mouse_pos = pygame.mouse.get_pos()
            for i, (text, action) in enumerate(buttons):
                rect = pygame.Rect(WIDTH//2 - 150, 150 + i*100, 300, 60)
                color = COLOR_BOTON_HOVER if rect.collidepoint(mouse_pos) else COLOR_BOTON
                pygame.draw.rect(SCREEN, color, rect)
                draw_text(SCREEN, text, (rect.x + 50, rect.y + 15), COLOR_TEXTO_BOTON)

                # Click del mouse
                if pygame.mouse.get_pressed()[0] and rect.collidepoint(mouse_pos):
                    action()

            pygame.display.flip()
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_app()

    def exit_app(self):
        """Salir del programa"""
        self.running = False
        pygame.quit()

if __name__ == "__main__":  # [FIX]
    app = ReconocimientoFacialLBPH(usuario_actual="el_mas_pro")  # [FIX] puedes poner aquí el usuario activo
    app.menu()
