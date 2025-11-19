import os
import feedparser
import smtplib
from email.mime.text import MIMEText

# Verificar variables de entorno
sender_email = os.getenv("GMAIL_SENDER_EMAIL")
sender_password = os.getenv("GMAIL_SENDER_PASSWORD")
receiver_email = os.getenv("GMAIL_RECEIVER_EMAIL")

if not sender_email or not sender_password or not receiver_email:
    print("ERROR: faltan variables de entorno. Asegúrate de tener GMAIL_SENDER_EMAIL, GMAIL_SENDER_PASSWORD, GMAIL_RECEIVER_EMAIL.")
    exit(1)

# CIK de la Republica del Peru
CIK_PERU = "0000053111"

# Feed RSS SOLO de ese CIK
RSS_FEED = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={CIK_PERU}&type=&dateb=&owner=exclude&count=40&output=atom"

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Correo enviado.")
    except Exception as e:
        print("Error al enviar correo:", e)

def check_filings():
    feed = feedparser.parse(RSS_FEED)

    if not feed.entries:
        print("No hay filings de Republic of Peru.")
        return

    latest = feed.entries[0]
    title = latest.get("title", "Sin título")
    link = latest.get("link", "Sin enlace")

    message = f"Nuevo filing de REPUBLIC OF PERU:\n\n{title}\n{link}"
    print(message)
    send_email("Nuevo Filing de Republic of Peru", message)

if __name__ == "__main__":
    check_filings()
