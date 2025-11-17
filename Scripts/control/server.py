import network
import socket
import time
import json 
from machine import Pin
from Hardware import Hardware

class Server:
    def __init__(self):
        self.SSID = "FLR (Primer Piso) 2.4G"
        self.PASSWORD = "Ansrole1504"
        self.port = 1710
        self.hardwareManager = Hardware()

    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.SSID, self.PASSWORD)
        
        print("Conectando a WiFi...", end="")
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(0.5)
        print("\nConectado:", wlan.ifconfig())
        return wlan.ifconfig()[0]

    def start_server(self, ip):
        s = socket.socket()
        s.bind((ip, self.port))
        s.listen(1)
        print("Esperando conexión del cliente...")
        conn, addr = s.accept()
        print("Conectado desde:", addr)
        try:
            while True:
                self.hardwareManager.DetectButtons()
                self.hardwareManager.DetectJoystick()
                stateJson = json.dumps(self.hardwareManager.state)
                conn.send(stateJson.encode())
                print(stateJson)
                time.sleep(1)
        except Exception as e:
            print("Error en conexión:", e)
        
        finally:
            conn.close()
            s.close()
            print("Conexión finalizada.")
    
server = Server()
ip = server.connect_wifi()
server.start_server(ip)