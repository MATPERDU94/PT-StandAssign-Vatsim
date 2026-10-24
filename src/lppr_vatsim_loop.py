import requests
import time
import csv
from datetime import datetime
from pathlib import Path

# ==========================================
# CONFIGURAÇÕES
# ==========================================
REFRESH_RATE = 15  # Tempo em segundos entre cada atualização (muda para 300 para 5 mins)

# Define o caminho da pasta data e do ficheiro
BASE_DIR = Path(__file__).resolve().parent.parent 
DATA_FILE = BASE_DIR / "data" / "lppr_voos_ativos.csv"

def get_lppr_arrivals():
    url = "https://data.vatsim.net/v3/vatsim-data.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro na ligação: {e}")
        return

    pilots = data.get('pilots', [])
    arrivals = []

    for pilot in pilots:
        flight_plan = pilot.get('flight_plan')
        
        if flight_plan and flight_plan.get('arrival') == 'LPPR':
            altitude = pilot.get('altitude', 0)
            
            if altitude > 0:
                arrivals.append({
                    'callsign': pilot.get('callsign', 'N/A'),
                    'departure': flight_plan.get('departure', 'N/A'),
                    'aircraft': flight_plan.get('aircraft_short', 'N/A'),
                    'altitude': altitude,
                    'groundspeed': pilot.get('groundspeed', 0),
                    'route': flight_plan.get('route', 'N/A')
                })

    if arrivals:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['callsign', 'departure', 'aircraft', 'altitude', 'groundspeed', 'route'])
            writer.writeheader()
            writer.writerows(arrivals)
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Atualizado: {len(arrivals)} voos a caminho de LPPR guardados.")
    else:
        if DATA_FILE.exists():
            open(DATA_FILE, 'w').close()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Atualizado: Nenhum voo a caminho de LPPR.")

if __name__ == "__main__":
    print(f"A iniciar o radar LPPR (Atualiza a cada {REFRESH_RATE} segundos). Pressiona Ctrl+C para parar.")
    try:
        while True:
            get_lppr_arrivals()
            time.sleep(REFRESH_RATE) # Agora usa a variável
    except KeyboardInterrupt:
        print("\nRadar desligado pelo utilizador.")