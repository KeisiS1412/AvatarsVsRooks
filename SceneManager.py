
class SceneManager:
    def __init__(self, initialScene):
        self.currentScene = initialScene

    def changeScene(self, newScene):
        self.currentScene = newScene

    def handleEvent(self, event):
        self.currentScene.handleEvent(event)

    def update(self, deltaTime):
        self.currentScene.update(deltaTime)

    def draw(self, screen):
        self.currentScene.draw(screen)