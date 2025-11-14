import pygame
from Reconocimientofacial import ReconocimientoFacialLBPH

class FacialLoginScene:
    def __init__(self, font, res, changeSceneCallback):
        self.font = font
        self.res = res
        self.changeScene = changeSceneCallback
        self.finished = False
        self.result_name = None
        self.app = ReconocimientoFacialLBPH()

    def on_enter(self):
        """Se llama cuando la escena inicia"""
        print("[FacialLoginScene] Iniciando escaneo facial...")
        self.result_name = self.app.login_con_rostro()

        if self.result_name:
            print("[FacialLoginScene] Usuario reconocido:", self.result_name)
            # Guarda el usuario reconocido
            with open("last_face_login.txt", "w") as f:
                f.write(self.result_name)

            # Cambia a la escena de juego o login
            self.changeScene("login")
        else:
            print("[FacialLoginScene] No reconocido, regresando al login.")
            self.changeScene("login")

    def draw(self, screen):
        """Pantalla mientras se activa la cámara"""
        screen.fill((255, 60, 60))
        text = self.font.render("Iniciando reconocimiento facial...", True, (255,255,255))
        screen.blit(text, (self.res[0]//2 - 200, self.res[1]//2))

    def update(self, dt):
        pass

    def handleEvent(self, event):
        pass


class FacialRegisterScene:
    def __init__(self, font, res, changeSceneCallback, usuario=""):
        self.font = font
        self.res = res
        self.changeScene = changeSceneCallback
        self.usuario = usuario
        self.app = ReconocimientoFacialLBPH(usuario_actual=self.usuario)

    def on_enter(self):
        print("[FacialRegisterScene] Registrando rostro de:", self.usuario)

        self.app.registrar_rostro()

        # Una vez terminado, regresar al registro normal
        self.changeScene("register")

    def draw(self, screen):
        screen.fill((255, 60, 60))
        msg = f"Registrando rostro para {self.usuario}..."
        text = self.font.render(msg, True, (255,255,255))
        screen.blit(text, (self.res[0]//2 - 250, self.res[1]//2))

    def update(self, dt):
        pass

    def handleEvent(self, event):
        pass