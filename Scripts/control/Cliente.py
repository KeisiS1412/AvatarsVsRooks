import socket
import json

class Client():
    SERVER_IP = "192.168.18.211"
    PORT = 1711

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def Connect(self):
        try:
            self.client_socket.connect((self.SERVER_IP, self.PORT))
            print(f"Conectado al servidor {self.SERVER_IP}:{self.PORT}")
            self.client_socket.setblocking(False)
            return True
        except Exception as e:
            print(f"No se pudo conectar: {e}")
            return False
        
    def ManageMessages(self):
        try:
            data = self.client_socket.recv(1024).decode()
            if not data:
                return None
            try:
                state = json.loads(data)
                return state
            except json.JSONDecodeError:
                return None
        except BlockingIOError:
            return None
        except Exception as e:
            print("Error en cliente:", e)
            return None

    def CloseConnection(self):
        self.client_socket.close()


