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
