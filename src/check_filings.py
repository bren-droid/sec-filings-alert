
#!/usr/bin/env python3
"""
Script: check_filings.py
Tarea: Consultar los filings del SEC EDGAR y mandar email si aparece un nuevo filing para "REPUBLIC OF PERU".
Requiere estas variables de entorno (están en GitHub Secrets):
- GMAIL_SENDER_EMAIL
- GMAIL_SENDER_PASSWORD
- GMAIL_RECEIVER_EMAIL
- SEC_USER_AGENT (opcional)
"""

import os
import json
import requests
import smtplib
from email.mime.text import MIMEText
import sys

SEARCH_QUERY = "REPUBLIC OF PERU"
SEARCH_URL = "https://data.sec.gov/api/search"
STATE_FILE = "last_filing.json"

# ======== Cargar secrets ========
GMAIL_SENDER = os.getenv("GMAIL_SENDER_EMAIL")
GMAIL_PASS = os.getenv("GMAIL_SENDER_PASSWORD")
GMAIL_RECEIVER = os.getenv("GMAIL_RECEIVER_EMAIL")
USER_AGENT = os.getenv("SEC_USER_AGENT") or GMAIL_SENDER

if not GMAIL_SENDER or not GMAIL_PASS or not GMAIL_RECEIVER:
    print("ERROR: faltan variables de entorno. Verifica que todos los secrets estén configurados.")
    sys.exit(1)


# ======== Función: enviar email ========
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_SENDER
    msg["To"] = GMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER, GMAIL_PASS)
            server.sendmail(GMAIL_SENDER, [GMAIL_RECEIVER], msg.as_string())
        print("✔ Email enviado correctamente.")
    except Exception as e:
        print("✖ Error enviando el email:", e)


# ======== Funciones para guardar/cargar estado ========
def load_state():
    """Lee el último filing guardado."""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return None


def save_state(entry):
    """Guarda el último filing visto."""
    with open(STATE_FILE, "w") as f:
        json.dump(entry, f, indent=2)


# ======== Consultar SEC ========
def get_latest_filing():
    headers = {"User-Agent": USER_AGENT}
    params = {"q": SEARCH_QUERY, "count": 10}

    try:
        r = requests.get(SEARCH_URL, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("✖ Error consultando SEC:", e)
        return None

    hits = data.get("hits", [])
    if not hits:
        return None

    h = hits[0]  # el filing más reciente

    return {
        "title": h.get("title"),
        "date": h.get("filingDate"),
        "id": h.get("id") or h.get("accessionNumber"),
        "url": "https://www.sec.gov" + h.get("filingDetailUrl", "")
    }


def main():
    print("Ejecutando check_filings.py...")

    latest = get_latest_filing()
    if not latest:
        print("No se pudo obtener un filing.")
        return

    saved = load_state()

    # si no hay guardado, o cambió el ID, es filing nuevo
    if not saved or latest["id"] != saved["id"]:
        print("¡Nuevo filing detectado!", latest)

        subject = f"Nuevo Filing REPUBLIC OF PERU ({latest['date']})"
        body = f"""Nuevo filing detectado:

Título: {latest['title']}
Fecha: {latest['date']}
URL: {latest['url']}
"""

        send_email(subject, body)
        save_state(latest)
    else:
        print("No hay filings nuevos.")


if __name__ == "__main__":
    main()
