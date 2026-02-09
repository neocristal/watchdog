# watchdog
watchdog of the service in docker and website
Reikalavimai
Pirmiausia, įsidiekite reikiamas bibliotekas:

Bash
pip install requests docker
Python automatizacijos skriptas
Šis skriptas veikia kaip "sargas" (watchdog): tikrina svetainę, o radęs klaidą – imasi veiksmų.

Python
import requests
import docker
import time
from datetime import datetime

# --- KONFIGŪRACIJA ---
URL = "http://tavo-svetaine.lt"
CONTAINER_NAME = "mano_konteineris"
CHECK_INTERVAL = 60  # sekundės tarp patikrinimų

def log_event(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")
    return now

def send_notification(report):
    # Čia galite įdėti Telegram/Discord webhook ar el. pašto siuntimą
    print("\n--- ATASKAITA ---")
    print(report)
    print("-----------------\n")

def check_and_fix():
    client = docker.from_env()
    
    try:
        response = requests.get(URL, timeout=10)
        status_code = response.status_code
    except Exception as e:
        status_code = "Connection Failed"

    # Tikriname, ar klaida (5xx serija) arba nepasiekiama
    if isinstance(status_code, int) and status_code < 500:
        return # Viskas gerai, išeiname

    # JEI RASTA KLAIDA:
    start_time = log_event(f"Klaida aptikta! Statusas: {status_code}. Pradedama gaivinimo procedūra.")
    
    try:
        container = client.containers.get(CONTAINER_NAME)
        
        # 1. Perkrovimas
        log_event(f"Perkraunamas konteineris: {CONTAINER_NAME}...")
        container.restart()
        restart_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. Health check laukimas
        time.sleep(10) # Leidžiame šiek tiek laiko startuoti
        container.reload() # Atnaujiname informaciją apie konteinerį
        
        health_status = container.attrs.get('State', {}).get('Health', {}).get('Status', 'Nėra health check')
        
        # 3. Jei nepasileido ar "unhealthy", bandom startuoti dar kartą
        if container.status != "running":
            log_event("Konteineris vis dar nebeveikia. Bandoma paleisti priverstinai...")
            container.start()

        # 4. Galutinis patikrinimas
        time.sleep(5)
        try:
            final_res = requests.get(URL, timeout=10)
            final_status = "Veikia (200 OK)" if final_res.status_code == 200 else f"Klaida išlieka: {final_res.status_code}"
        except:
            final_status = "Svetainė vis dar nepasiekiama"

        finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Ataskaitos formavimas
        report = (
            f"Sistemos ataskaita:\n"
            f"- Pastebėta: {start_time}\n"
            f"- Pradinis statusas: {status_code}\n"
            f"- Perkrauta: {restart_time}\n"
            f"- Konteinerio būsena: {container.status} (Health: {health_status})\n"
            f"- Galutinis statusas: {final_status}\n"
            f"- Pabaigta: {finish_time}"
        )
        send_notification(report)

    except docker.errors.NotFound:
        log_event(f"KLAIDA: Konteineris {CONTAINER_NAME} nerastas!")

if __name__ == "__main__":
    log_event("Sargas paleistas...")
    while True:
        check_and_fix()
        time.sleep(CHECK_INTERVAL)
Kaip tai veikia:
Svetainės stebėjimas: Skriptas naudoja requests.get(). Jei gaunamas kodas 500, 502, 503 arba ryšys nutrūksta, suveikia logika.

Docker valdymas: Naudojama oficiali Docker SDK biblioteka. Skriptas bendrauja tiesiogiai su tavo sistemos Docker demonu.

Health Check:

Svarbu: Kad health_status veiktų, tavo docker-compose.yml arba Dockerfile turi būti aprašyta HEALTHCHECK instrukcija.

Jei konteineris tiesiog "running", bet svetainė neveikia, skriptas vis tiek bandys perkrauti.

Ataskaita: Skriptas surenka laiko žymas (timestamp) kiekviename žingsnyje ir gale išveda pilną suvestinę.

Patarimas:
Kad šis skriptas pats neužgestų, geriausia jį paleisti kaip atskirą Docker konteinerį arba naudoti Systemd servisą Linux sistemoje. Taip pat, rekomenduoju send_notification funkcijoje prijungti Telegram Bot API, kad gautumėte pranešimus tiesiai į telefoną.
