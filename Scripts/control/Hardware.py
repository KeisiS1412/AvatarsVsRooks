from machine import Pin, ADC
import time
import math

class Hardware:
    CENTER = 33000
    DEADZONE = 9000
    def __init__(self):
        btnPins = [0, 1, 2, 3, 4, 5]
        labels = ["Arriba", "Abajo", "Izquierda", "Derecha", "Aceptar", "Cancelar"]
        self.buttons = [(p, Pin(p, Pin.IN, Pin.PULL_UP)) for p in btnPins]
        self.buttonNames = dict(zip(btnPins, labels))
        self.state = {"x": 0, "y": 0, "Arriba": 0, "Abajo":0, "Izquierda":0, "Derecha":0, "Aceptar":0, "Cancelar":0, "JoystickButton":0}
        self.vx = ADC(26)   #cable 6
        self.vy = ADC(27)   # cable 7
        self.sw = Pin(8, Pin.IN, Pin.PULL_UP)  #Boton
        
    def DetectButtons(self):
        for pinNumber, b in self.buttons:
            name = self.buttonNames[pinNumber]
            self.state[name] = 1 if b.value() == 0 else 0
                    

    def DetectJoystick(self):
        xRaw = self.vx.read_u16() - self.CENTER
        yRaw = self.vy.read_u16() - self.CENTER

        angleDeg = -25
        angleRad = math.radians(angleDeg)
        
        xRot = xRaw * math.cos(angleRad) - yRaw * math.sin(angleRad)
        yRot = xRaw * math.sin(angleRad) + yRaw * math.cos(angleRad)

        self.state["x"] = self.Moved(int(xRot + self.CENTER))
        self.state["y"] = -self.Moved(int(yRot + self.CENTER))
        self.state["joystickButton"] = int(self.sw.value() == 0)
            
    def Moved(self, value):
        if value < self.CENTER - self.DEADZONE:
            return -1
        elif value > self.CENTER + self.DEADZONE:
            return 1
        else:
            return 0
        
    def UpdateState(self):
        self.DetectButtons()
        self.DetectJoystick()


    
