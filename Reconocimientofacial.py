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
COLOR_FONDO = (255, 60, 60)        # Rojo claro
COLOR_BOTON = (10, 10, 10)         # Negro botones
COLOR_BOTON_HOVER = (60, 60, 60)   # Gris al pasar el mouse
COLOR_TEXTO = (255, 255, 255)      # Blanco texto general
COLOR_TEXTO_BOTON = (255, 255, 255)
COLOR_TITULO = (0, 0, 0)           # Negro para el título

USERS_DIR = "users_lbph"
if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)

# === Función auxiliar para texto ===
def draw_text(surface, text, pos, color=COLOR_TEXTO):
    text_render = FONT.render(text, True, color)
    surface.blit(text_render, pos)

# === Clase principal ===
class ReconocimientoFacialLBPH:
    def __init__(self):
        self.running = True
        self.name = ""

    def registrar_rostro(self):
        name = self.input_text("Ingrese su nombre de usuario:")
        if not name:
            self.show_message("Nombre inválido.")
            return
        self.name = name.strip().lower()

        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        count = 0
        faces_data = []

        self.show_message("Mira a la cámara. Se capturarán 10 imágenes.")

        while True:
            ret, frame = cap.read()
            if not ret:
                self.show_message("No se pudo acceder a la cámara.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face, (100, 100))
                faces_data.append(face_resized)
                count += 1

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"Captura {count}/10", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

            cv2.imshow("Registrando rostro", frame)
            if count >= 10 or cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if faces_data:
            mean_face = np.mean(faces_data, axis=0)
            filepath = os.path.join(USERS_DIR, f"{self.name}.npy")
            np.save(filepath, mean_face)
            self.show_message(f"Rostro guardado correctamente como '{filepath}'")
        else:
            self.show_message("No se capturó ningún rostro.")

    def cargar_rostros(self):
        encodings, names = [], []
        for file in os.listdir(USERS_DIR):
            if file.endswith(".npy"):
                path = os.path.join(USERS_DIR, file)
                encoding = np.load(path).flatten()
                encodings.append(encoding)
                names.append(os.path.splitext(file)[0])
        return encodings, names

    def login_con_rostro(self):
        known_encodings, known_names = self.cargar_rostros()
        if not known_encodings:
            self.show_message("No hay rostros registrados.")
            return

        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        start_time = time.time()
        recognized = False

        while True:
            ret, frame = cap.read()
            if not ret:
                self.show_message("No se pudo acceder a la cámara.")
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
                    color = (0, 0, 255)

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                if recognized:
                    cv2.imshow("Login con rostro", frame)
                    cv2.waitKey(1000)
                    cap.release()
                    cv2.destroyAllWindows()
                    self.show_message(f"Bienvenido, {name}!")
                    return

            cv2.imshow("Login con rostro", frame)
            if time.time() - start_time > 15 or cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.show_message("Login fallido. No se reconoció ningún rostro.")

    def show_message(self, text):
        running = True
        while running:
            SCREEN.fill(COLOR_FONDO)
            draw_text(SCREEN, text, (50, HEIGHT//2 - 20))
            draw_text(SCREEN, "Presiona ENTER para continuar", (50, HEIGHT//2 + 30), (100, 255, 100))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    running = False

    def input_text(self, prompt):
        text = ""
        entering = True
        while entering:
            SCREEN.fill(COLOR_FONDO)
            draw_text(SCREEN, prompt, (50, HEIGHT//3))
            draw_text(SCREEN, text + "|", (50, HEIGHT//2))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    entering = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        entering = False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        return text.strip()

    def menu(self):
        buttons = [
            ("Registrar rostro", self.registrar_rostro),
            ("Login con rostro", self.login_con_rostro),
            ("Salir", self.exit_app)
        ]

        while self.running:
            SCREEN.fill(COLOR_FONDO)
            draw_text(SCREEN, "Reconocimiento Facial LBPH", (180, 50), (0, 0, 0))

            mouse_pos = pygame.mouse.get_pos()
            for i, (text, action) in enumerate(buttons):
                rect = pygame.Rect(WIDTH//2 - 150, 150 + i*100, 300, 60)
                color = COLOR_BOTON if rect.collidepoint(mouse_pos) else (60, 60, 60)
                pygame.draw.rect(SCREEN, color, rect)
                draw_text(SCREEN, text, (rect.x + 50, rect.y + 15), COLOR_TEXTO_BOTON)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_app()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, (text, action) in enumerate(buttons):
                        rect = pygame.Rect(WIDTH//2 - 150, 150 + i*100, 300, 60)
                        if rect.collidepoint(event.pos):
                            action()

    def exit_app(self):
        self.running = False
        pygame.quit()

# === Ejecutar ===
if __name__ == "__main__":
    app = ReconocimientoFacialLBPH()
    app.menu()
