import smtplib
import ssl
import os
import random
from email.message import EmailMessage
from dotenv import load_dotenv


class MailSender:
    """
    Clase para enviar correos de recuperación de contraseña
    usando el servicio SMTP de Gmail.
    """

    def __init__(self, clientEmail): # Cargar datos del .env
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
        self.emailEmisor = os.getenv("GMAIL_ADDRESS")
        self.emailPassword = os.getenv("GMAIL_APP_PASS")
        self.emailReceptor = clientEmail

    def generateCode(self): # Código de recuperación
        return random.randint(100000, 999999)

    def sendEmail(self): # Enviar correo
        code = self.generateCode()

        asunto = "Recuperación de contraseña - Avatars vs Rooks"
        cuerpo = f"""
Hola,

Para recuperar su contraseña, ingrese el siguiente código en la ventana de su juego:

    Código: {code}

Si no solicitó esta recuperación, ignore este mensaje.
        """

        mensaje = EmailMessage()
        mensaje["From"] = self.emailEmisor
        mensaje["To"] = self.emailReceptor
        mensaje["Subject"] = asunto
        mensaje.set_content(cuerpo)

        contexto = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as smtp:
                smtp.login(self.emailEmisor, self.emailPassword)  # Iniciar sesión
                smtp.send_message(mensaje)  # Enviar mensaje
        except Exception as e:
            return False

        return code  # Retorna el código generado
