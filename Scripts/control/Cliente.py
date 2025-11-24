import socket
import json

class Client:
    SERVER_IP = "192.168.18.211"
    PORT = 1711

    def __init__(self):
        self.client_socket = None
        self.connected = False

    def Connect(self):
        # Crear un nuevo socket cada vez que se intenta conectar
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(3)  # 3 segundos de espera

        try:
            self.client_socket.connect((self.SERVER_IP, self.PORT))
            self.client_socket.setblocking(False)
            self.connected = True
            print(f"Conectado al servidor {self.SERVER_IP}:{self.PORT}")
            return True
        except (ConnectionRefusedError, TimeoutError, OSError) as e:
            print(f"No se pudo conectar con el servidor: {e}")
            self.connected = False
            self.client_socket.close()  # Asegurarse de liberar el socket
            self.client_socket = None
            return False
        finally:
            # Quitar el timeout para no afectar recv()
            if self.client_socket:
                self.client_socket.settimeout(None)

    def ManageMessages(self):
        if not self.connected or not self.client_socket:
            return None

        try:
            data = self.client_socket.recv(1024).decode()
            if not data:
                return None
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        except BlockingIOError:
            # No hay datos disponibles (modo no bloqueante)
            return None
        except (ConnectionResetError, OSError) as e:
            print(f"⚠️ Conexión perdida: {e}")
            self.connected = False
            return None
        except Exception as e:
            print(f"Error en cliente: {e}")
            return None

    def CloseConnection(self):
        if self.client_socket:
            try:
                self.client_socket.close()
                print("🔌 Conexión cerrada correctamente.")
            except Exception as e:
                print(f"Error al cerrar conexión: {e}")
        self.client_socket = None
        self.connected = False
