from LoginScene import LoginScene
from RegisterScene import RegisterScene
from PersonalizationScene import PersonalizationScene
from MainWindow import MainWindow

class SceneManager:
    def __init__(self, font, res):
        self.font = font
        self.currentScene = None
        self.scenes = {
            "login": LoginScene(font, res, self.changeScene),
            "register": RegisterScene(font, res, self.changeScene),
            "personalization": PersonalizationScene(font, res, self.changeScene),
            "main": MainWindow(font, res, self.changeScene)
        }
        self.changeScene("login")

    def changeScene(self, name):
        if name in self.scenes:
            self.currentScene = self.scenes[name]
        else:
            raise ValueError(f"Scene '{name}' does not exist.")

    def draw(self, screen):
        self.currentScene.draw(screen)

    def update(self, deltaTime):
        self.currentScene.update(deltaTime)


    def handleEvent(self, event):
        
        self.handle(event)
        self.btnBack.on_click = lambda: self.switchScene("personalization") if self.switchScene else None


