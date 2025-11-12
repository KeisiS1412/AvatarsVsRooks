import pygame
import cv2
import numpy as np
import os
import time
import json
import requests

pygame.init()

# === Configuración general ===
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = SCREEN.get_size()

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
        """Captura 10 imágenes del rostro actual y las guarda como .npy y JSON"""
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
                face = gray[y:y + h, x:x + w]
                face_resized = cv2.resize(face, (100, 100))
                faces_data.append(face_resized)
                count += 1
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Mostrar cámara en ventana Pygame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.flipud(np.rot90(frame_rgb)))
            SCREEN.fill(COLOR_FONDO)
            SCREEN.blit(frame_surface, (100, 50))
            draw_text(SCREEN, f"Captura {count}/10", (WIDTH // 2 - 80, HEIGHT - 60), (255, 255, 255))
            draw_text(SCREEN, "Presiona Q para cancelar", (WIDTH // 2 - 120, HEIGHT - 30), (0, 0, 0))
            pygame.display.flip()
            clock.tick(30)

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

            # === NUEVO: Enviar al servidor en formato JSON ===
            try:
                face_array = mean_face.flatten().tolist()
                r = requests.post(
                    "http://localhost:3007/faces/upload",
                    json={"username": self.name or "anonimo", "face_data": face_array},
                    timeout=10
                )
                if r.status_code == 200 and r.json().get("ok"):
                    print(" Rostro enviado correctamente al servidor.")
                else:
                    print(" No se pudo enviar el rostro al servidor:", r.text)
            except Exception as e:
                print(" Error al enviar el rostro al servidor:", e)

    def verificar_en_servidor(self, frame_gray):
        """Verifica el rostro capturado contra el servidor remoto"""
        try:
            face_resized = cv2.resize(frame_gray, (100, 100))
            arr_list = face_resized.flatten().tolist()

            r = requests.post(
                "http://localhost:3007/faces/verify",
                json={"face_data": arr_list},
                timeout=10
            )

            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(" Error al verificar en servidor:", e)
        return {"ok": False, "match": False}

    def login_con_rostro(self):
        """Compara el rostro actual con los registrados"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("No se pudo acceder a la cámara.")
            return

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        clock = pygame.time.Clock()
        start_time = time.time()
        recognized = False
        name = "Desconocido"

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            print("[DEBUG] Detectadas:", len(faces))

            for (x, y, w, h) in faces:
                face_crop = gray[y:y + h, x:x + w]
                result = self.verificar_en_servidor(face_crop)

                if result.get("match"):
                    name = result.get("username") or "Desconocido"
                    label = f"Reconocido: {name}"
                    color = (0, 255, 0)
                    recognized = True
                else:
                    label = "Desconocido"
                    color = (255, 0, 0)

                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.flipud(np.rot90(frame_rgb)))
            SCREEN.fill(COLOR_FONDO)
            SCREEN.blit(frame_surface, (100, 50))
            draw_text(SCREEN, "Presiona Q para cancelar", (WIDTH // 2 - 120, HEIGHT - 30), (0, 0, 0))
            pygame.display.flip()
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    cap.release()
                    return

            if recognized:
                print(f" Bienvenido, {name}!")
                with open("last_face_login.txt", "w") as f:
                    f.write(name)
                time.sleep(1)
                cap.release()
                return

            if time.time() - start_time > 15:
                break

        cap.release()
        print(" Login fallido: rostro no reconocido.")

    def exit_app(self):
        """Salir del programa limpiamente"""
        self.running = False
        pygame.quit()


if __name__ == "__main__":
    app = ReconocimientoFacialLBPH(usuario_actual="lll")  # cambia el nombre según el usuario actual
    app.login_con_rostro()  # o app.registrar_rostro() si quieres registrar
