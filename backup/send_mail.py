#!/usr/bin/env python3
"""
Script de envío de correos para notificaciones de backup
Integrado con el sistema de backup de Moodle Docker
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import sys
import os

def enviar_correo(destinatarios, asunto, mensaje, archivo=None):
    """
    Envía un correo electrónico con opción de adjuntar archivo

    Args:
        destinatarios: String con emails separados por comas
        asunto: Asunto del correo
        mensaje: Cuerpo del mensaje
        archivo: Ruta del archivo a adjuntar (opcional)

    Returns:
        True si el envío fue exitoso, False en caso contrario
    """
    # Obtener configuración desde variables de entorno
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    port = int(os.getenv('SMTP_PORT', '465'))  # Puerto para SSL
    sender_email = os.getenv('SMTP_USER', 'CORREO')
    password = os.getenv('SMTP_PASSWORD', 'CONTRASEÑA')
    from_name = os.getenv('SMTP_FROM_NAME', 'Moodle Backup System')

    # Validar configuración
    if sender_email == 'CORREO' or password == 'CONTRASEÑA':
        print("ERROR: Las credenciales SMTP no están configuradas correctamente")
        print("Configure las variables de entorno SMTP_USER y SMTP_PASSWORD")
        return False

    # Procesar lista de destinatarios
    lista_destinatarios = [dest.strip() for dest in destinatarios.split(',')]

    # Crear mensaje
    msg = MIMEMultipart()
    msg['From'] = f"{from_name} <{sender_email}>"
    msg['To'] = ', '.join(lista_destinatarios)
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    # Adjuntar archivo si se proporciona
    if archivo and os.path.exists(archivo):
        try:
            part = MIMEBase('application', "octet-stream")
            with open(archivo, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(archivo)}"')
            msg.attach(part)
            print(f"Archivo adjunto: {os.path.basename(archivo)}")
        except Exception as e:
            print(f"Advertencia: No se pudo adjuntar el archivo {archivo}: {e}")

    try:
        # Iniciar servidor usando SSL
        server = smtplib.SMTP_SSL(smtp_server, port)

        # Login
        server.login(sender_email, password)

        # Enviar correo
        text = msg.as_string()
        server.sendmail(sender_email, lista_destinatarios, text)
        print(f"Correo enviado correctamente a {', '.join(lista_destinatarios)}")
        print(f"Asunto: {asunto}")
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError:
        print("ERROR: Falló la autenticación SMTP. Verifique las credenciales.")
        return False
    except smtplib.SMTPException as e:
        print(f"ERROR SMTP: {e}")
        return False
    except Exception as e:
        print(f"ERROR al enviar correo: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        destinatarios = sys.argv[1]
        asunto = sys.argv[2]
        mensaje = sys.argv[3]
        archivo = sys.argv[4] if len(sys.argv) > 4 else None

        # Ejecutar envío
        exito = enviar_correo(destinatarios, asunto, mensaje, archivo)

        # Retornar código de salida apropiado
        sys.exit(0 if exito else 1)
    else:
        print("Uso: python3 send_mail.py destinatarios asunto mensaje [archivo]")
        print("")
        print("Argumentos:")
        print("  destinatarios  - Lista de correos separados por comas")
        print("  asunto        - Asunto del correo")
        print("  mensaje       - Cuerpo del mensaje")
        print("  archivo       - Ruta del archivo a adjuntar (opcional)")
        print("")
        print("Variables de entorno requeridas:")
        print("  SMTP_SERVER      - Servidor SMTP (default: smtp.gmail.com)")
        print("  SMTP_PORT        - Puerto SMTP (default: 465)")
        print("  SMTP_USER        - Usuario SMTP")
        print("  SMTP_PASSWORD    - Contraseña SMTP")
        print("  SMTP_FROM_NAME   - Nombre del remitente (default: Moodle Backup System)")
        sys.exit(1)