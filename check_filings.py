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

# URL RSS del feed de la SEC
RSS_FEED = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=&company=&dateb=&owner=include&start=0&count=40&output=atom"

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
        print("No hay nuevos filings en el feed.")
        return

    latest = feed.entries[0]
    title = latest.get("title", "Sin título")
    link = latest.get("link", "Sin enlace")

    message = f"Nuevo filing detectado:\n\n{title}\n{link}"
    print(message)
    send_email("Nuevo Filing detectado", message)

if __name__ == "__main__":
    check_filings()
