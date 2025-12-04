import os
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from notifier import send_email

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parents[1]

# Cargar variables del archivo .env
load_dotenv(BASE_DIR / ".env")

# Variables de entorno
USER_AGENT = os.getenv("SEC_USER_AGENT")
CIK = os.getenv("CIK_FILTER")
STATE_FILE = BASE_DIR / "last_seen.json"

HEADERS = {"User-Agent": USER_AGENT}


def fetch_filings():
    """Obtiene el archivo JSON de submissions de la SEC para el CIK."""
    cik_10 = CIK.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_10}.json"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


def load_last_seen():
    """Carga el último filing visto del archivo last_seen.json."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last": None}


def save_last_seen(state):
    """Guarda el último filing visto."""
    STATE_FILE.write_text(json.dumps(state))


def check_new_filings(data, last_seen):
    """Revisa si hay un filing nuevo comparado con el último visto."""
    recent = data["filings"]["recent"]

    acc_nums = recent["accessionNumber"]
    forms = recent["form"]
    dates = recent["filingDate"]

    latest_key = f"{acc_nums[0]}_{forms[0]}_{dates[0]}"

    if last_seen != latest_key:
        return {
            "accession": acc_nums[0],
            "form": forms[0],
            "date": dates[0]
        }
    return None


def main():
    state = load_last_seen()
    last_seen = state["last"]

    try:
        data = fetch_filings()
    except Exception as e:
        print("ERROR:", e)
        return

    new = check_new_filings(data, last_seen)

    if new:
        body = (
            f"Nuevo filing detectado:\n"
            f"Form: {new['form']}\n"
            f"Accession: {new['accession']}\n"
            f"Date: {new['date']}\n"
        )

        send_email("Nuevo Filing Detectado", body)

        # Actualiza el último filing visto
        state["last"] = f"{new['accession']}_{new['form']}_{new['date']}"
        save_last_seen(state)

        print("Alerta enviada.")
    else:
        print("No hay nuevos filings.")


if __name__ == "__main__":
    main()