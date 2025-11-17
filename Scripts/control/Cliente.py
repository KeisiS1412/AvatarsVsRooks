import socket
import json

class Client():
    SERVER_IP = "192.168.18.211"
    PORT = 1710

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def Connect(self):
        try:
            self.client_socket.connect((self.SERVER_IP, self.PORT))
            return True
        except:
            return False
        
    def ManageMessages(self):
        try:
            data = self.client_socket.recv(1024).decode()
            if not data:
                return None
            try:
                state = json.loads(data)
                return state
            except:
                return None

        except KeyboardInterrupt:
            return "Error"

    def CloseConnection(self):
        self.client_socket.close()


