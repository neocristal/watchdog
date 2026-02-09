# 🛡️ Docker Container Watchdog (Python)

Šis skriptas yra automatizuotas įrankis, skirtas stebėti svetainės pasiekiamumą ir automatiškai gaivinti Docker konteinerį, jei aptinkama vidinė serverio klaida (HTTP 500) arba ryšio sutrikimai.

## 📋 Funkcijos
* **Svetainės monitoringas**: Tikrina nurodytą URL kas X sekundžių.
* **Klaidų aptikimas**: Reaguoja į `5xx` klaidas arba visišką ryšio dingimą.
* **Docker integracija**: Automatiškai perkrauna (`restart`) ir tikrina `health check` būseną.
* **Išsami ataskaita**: Suformuoja įvykio chronologiją (kada pastebėta, kada perkrauta, koks rezultatas).

## 🛠️ Pasiruošimas

1. Įsitikinkite, kad turite **Python 3.x**.
2. Įsidiekite reikiamas bibliotekas:
   ```bash
   pip install requests docker

Išsisaugokite kodą kaip watchdog.py.

Redaguokite URL ir CONTAINER_NAME kintamuosius pagal savo poreikius.

Paleiskite skriptą fone:

Bash
nohup python3 watchdog.py &

Patarimas: Jei nori gauti pranešimus į telefoną, rekomenduoju į send_notification funkciją įsidėti paprastą Telegram Bot užklausą. Ar norėtum, kad parodyčiau, kaip tai padaryti?

---

Ar norėtum, kad į šį failą dar įtraukčiau konkrečią dalį apie **Telegram** pranešimų siuntimą (su `requests.post`) ar **Docker Compose** konfigūraciją?

1. Konfigūracijos failas (targets.json)
Sukurkite šį failą tame pačiame aplanke. Čia galite pridėti tiek svetainių, kiek reikia.
```
[
    {
        "url": "https://tavo-svetaine1.lt",
        "container_name": "nginx_prod",
        "name": "Pagrindinis puslapis"
    },
    {
        "url": "http://127.0.0.1:8080",
        "container_name": "api_backend",
        "name": "Backend API"
    }
]
```

2. Atnaujintas Python skriptas (watchdog.py)
Šis skriptas iš eilės (nuosekliai) patikrina kiekvieną sąrašo įrašą.

Kaip nustatyti Telegram pranešimus?
Sukurkite Botą: Parašykite @BotFather per Telegram, naudokite komandą /newbot ir gausite Token.

Gaukite savo ID: Parašykite bet ką savo naujam botui ir tada naršyklėje atsidarykite: https://api.telegram.org/bot<TAVO_TOKENAS>/getUpdates Ieškokite "id": laukelio po "chat" objektu. Tai bus jūsų TELEGRAM_CHAT_ID.

Įrašykite duomenis: Įklijuokite juos į skripto viršuje esančius kintamuosius.

Kodėl tai geriau?
JSON lankstumas: Galite bet kada pridėti naują svetainę redaguodami paprastą tekstinį failą, nereikia liesti pačio Python kodo.

Atskyrimas: Jei viena svetainė "lūžta", skriptas ją sutvarko ir eina tikrinti kitos.

Telegram pranešimai: Gausite gražiai suformatuotas ataskaitas su Bold tekstu ir emocijomis tiesiai į savo telefoną.

💡 Svarbios pastabos
Gmail SMTP: Jei naudojate Gmail, jums reikės įjungti "2-Step Verification" ir susikurti "App Password", nes paprasti slaptažodžiai per SMTP neveikia.

Dependencies: Nepamirškite įdiegti reikiamų paketų:

```Bash
pip install requests docker
Viber: Viber API yra sudėtingesnis (reikia viešo URL / webhook), todėl Telegram + Email derinys yra žymiai stabilesnis pasirinkimas tokiai sistemai.

Health Check: Kad skriptas matytų tikrą "Health status", jūsų Docker konteineris turi turėti HEALTHCHECK instrukciją (pvz., Dockerfile: HEALTHCHECK --interval=30s CMD curl -f http://localhost/ || exit 1).
