import requests
import docker
import time
from datetime import datetime

# --- KONFIGŪRACIJA ---
URL = "[http://tavo-svetaine.lt](http://tavo-svetaine.lt)"         # Tikrinamas adresas
CONTAINER_NAME = "mano_konteineris"     # Tikslus Docker konteinerio pavadinimas
CHECK_INTERVAL = 60                     # Tikrinimo dažnumas sekundėmis

def log_event(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")
    return now

def send_notification(report):
    """Čia galima integruoti Telegram/Slack pranešimų siuntimą"""
    print("\n" + "="*30)
    print("🚨 INCIDENTO ATASKAITA 🚨")
    print("="*30)
    print(report)
    print("="*30 + "\n")

def check_system():
    client = docker.from_env()
    
    try:
        response = requests.get(URL, timeout=15)
        status_code = response.status_code
    except Exception:
        status_code = "CONNECTION_FAILED"

    # Jei statusas yra 500+ arba ryšio klaida
    if status_code == "CONNECTION_FAILED" or (isinstance(status_code, int) and status_code >= 500):
        start_time = log_event(f"⚠️ Aptikta klaida: {status_code}. Pradedamas atkūrimas...")
        
        try:
            container = client.containers.get(CONTAINER_NAME)
            
            # 1. Konteinerio perkrovimas
            log_event(f"🔄 Perkraunamas konteineris '{CONTAINER_NAME}'...")
            container.restart()
            restart_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 2. Laukiam, kol atsigaus ir tikrinam Health
            time.sleep(15) 
            container.reload()
            health = container.attrs.get('State', {}).get('Health', {}).get('Status', 'N/A')
            
            # 3. Jei nepasileido - bandom force start
            if container.status != "running":
                log_event("❌ Konteineris nepasileido automatiškai. Bandoma priverstinai...")
                container.start()

            # 4. Galutinis patikrinimas
            time.sleep(5)
            try:
                final_res = requests.get(URL, timeout=10)
                final_status = f"Sėkmingas (HTTP {final_res.status_code})" if final_res.status_code == 200 else f"Klaida išlieka ({final_res.status_code})"
            except:
                final_status = "Svetainė vis dar nepasiekiama"

            finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Ataskaitos generavimas
            report = (
                f"📅 Įvykio laikas: {start_time}\n"
                f"❌ Pradinė klaida: {status_code}\n"
                f"🔄 Perkrovimo laikas: {restart_time}\n"
                f"🏥 Konteinerio Health: {health}\n"
                f"✅ Galutinė būsena: {final_status}\n"
                f"🏁 Procesas baigtas: {finish_time}"
            )
            send_notification(report)

        except docker.errors.NotFound:
            log_event(f"🛑 KLAIDA: Konteineris pavadinimu '{CONTAINER_NAME}' nerastas!")
    else:
        # Viskas gerai
        pass

if __name__ == "__main__":
    log_event(f"Sargas aktyvuotas. Stebima: {URL}")
    while True:
        check_system()
        time.sleep(CHECK_INTERVAL)