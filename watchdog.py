import requests
import docker
import time
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# --- KONFIGŪRACIJA ---
CONFIG_FILE = "targets.json"
CHECK_INTERVAL = 60  # Kas kiek sekundžių tikrinti visą sąrašą

# --- TELEGRAM NUSTATYMAI ---
TELEGRAM_TOKEN = "TAVO_BOT_TOKENAS"
TELEGRAM_CHAT_ID = "TAVO_CHAT_ID"

# --- EL. PAŠTO (SMTP) NUSTATYMAI ---
SMTP_SERVER = "smtp.gmail.com"  # Pvz., gmail, outlook ar tavo pašto serveris
SMTP_PORT = 587
SMTP_USER = "tavo-pastas@gmail.com"
SMTP_PASS = "tavo-programos-slaptazodis"  # Gmail atveju - "App Password"
EMAIL_RECEIVER = "kur-siusti@pastas.lt"

client = docker.from_env()

def send_notifications(report):
    """Siunčia ataskaitą per Telegram ir El. Paštą"""
    
    # 1. TELEGRAM SIUNTIMAS
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    tg_payload = {"chat_id": TELEGRAM_CHAT_ID, "text": report, "parse_mode": "Markdown"}
    try:
        requests.post(tg_url, json=tg_payload, timeout=10)
    except Exception as e:
        print(f"Telegram klaida: {e}")

    # 2. EL. PAŠTO SIUNTIMAS
    msg = MIMEText(report)
    msg['Subject'] = f"🚨 Incidento Ataskaita: Docker Monitorius"
    msg['From'] = SMTP_USER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        print(f"El. pašto klaida: {e}")

def log_event(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{now}] {message}"
    print(full_msg)
    return now

def check_target(target):
    url = target['url']
    c_name = target['container_name']
    friendly_name = target['name']

    try:
        response = requests.get(url, timeout=15)
        status_code = response.status_code
    except:
        status_code = "OFFLINE"

    # Tikriname ar klaida (5xx) arba ryšio nėra
    if status_code == "OFFLINE" or (isinstance(status_code, int) and status_code >= 500):
        start_time = log_event(f"⚠️ Klaida {friendly_name}: {status_code}")
        
        try:
            container = client.containers.get(c_name)
            
            # Veiksmas: Restart
            log_event(f"🔄 Perkraunamas {c_name}...")
            container.restart()
            restart_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Health Check
            time.sleep(20)
            container.reload()
            health = container.attrs.get('State', {}).get('Health', {}).get('Status', 'Nėra health check')
            
            # Jei vis dar nepasileido
            if container.status != "running":
                container.start()

            # Galutinis patikrinimas
            time.sleep(5)
            try:
                final_res = requests.get(url, timeout=10)
                final_status = f"✅ Atstatyta (HTTP {final_res.status_code})" if final_res.status_code == 200 else f"❌ Vis dar klaida ({final_res.status_code})"
            except:
                final_status = "❌ Svetainė neatsigavo"

            finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Formuojame ataskaitą
            report = (
                f"🚨 MONITORIAUS PRANEŠIMAS 🚨\n\n"
                f"Svetainė: {friendly_name} ({url})\n"
                f"Konteineris: {c_name}\n"
                f"----------------------------\n"
                f"🕒 Pastebėta: {start_time}\n"
                f"🛑 Klaidos kodas: {status_code}\n"
                f"🔄 Perkrovimas: {restart_time}\n"
                f"🏥 Health Status: {health}\n"
                f"🏁 Galutinis statusas: {final_status}\n"
                f"⏱️ Pabaigta: {finish_time}"
            )
            
            send_notifications(report)

        except Exception as e:
            send_notifications(f"🛑 Kritinė klaida su konteineriu {c_name}: {str(e)}")

def main():
    log_event("Monitorius paleistas...")
    while True:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                targets = json.load(f)
            
            for target in targets:
                check_target(target)
                time.sleep(3) # Pauzė tarp skirtingų svetainių
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
