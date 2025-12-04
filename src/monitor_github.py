import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from notifier import send_email

BASE_DIR = Path(__file__).resolve().parents[1]
STATE_FILE = BASE_DIR / "last_seen.json"

USER_AGENT = os.getenv("SEC_USER_AGENT", "").strip()
CIK = os.getenv("CIK_FILTER", "").strip()
COMPANY_NAME = os.getenv("COMPANY_NAME", "").strip().lower()

HEADERS = {"User-Agent": USER_AGENT}
SEC_URL = "https://data.sec.gov/submissions/CIK{cik}.json"


def fetch_json(url):
    """GET simple para el JSON de la SEC."""
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


def load_last_seen():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            return {"last": None}
    return {"last": None}


def save_last_seen(value):
    STATE_FILE.write_text(json.dumps(value))


def find_latest(data):
    recent = data.get("filings", {}).get("recent", {})
    acc = recent.get("accessionNumber", [])
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    if not (acc and forms and dates):
        return None
    return {
        "accession": acc[0],
        "form": forms[0],
        "date": dates[0],
    }


def main():
    if not USER_AGENT or not CIK:
        print("Faltan variables: SEC_USER_AGENT, CIK_FILTER")
        return

    url = SEC_URL.format(cik=CIK.zfill(10))
    try:
        data = fetch_json(url)
    except Exception as e:
        print("Error obteniendo SEC JSON:", e)
        return

    latest = find_latest(data)
    if not latest:
        print("No filings recientes")
        return

    latest_key = f"{latest['accession']}_{latest['form']}_{latest['date']}"
    last_key = load_last_seen().get("last")

    if latest_key == last_key:
        print("No hay nuevos filings")
        return

    # Enviar email
    body = (
        f"Nuevo filing detectado:\n"
        f"Form: {latest['form']}\n"
        f"Accession: {latest['accession']}\n"
        f"Date: {latest['date']}\n"
    )
    send_email("Nuevo filing detectado", body)

    save_last_seen({"last": latest_key})
    print("Alerta enviada")


if __name__ == "__main__":
    main()
