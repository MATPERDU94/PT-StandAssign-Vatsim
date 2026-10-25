import requests
import time
import csv
import math 
from datetime import datetime
from pathlib import Path

# ==========================================
# CONFIGURAÇÕES
# ==========================================
REFRESH_RATE = 15  # Tempo em segundos entre cada atualização (muda para 300 para 5 mins)

# ADICIONADO: Coordenadas do Aeroporto do Porto e limite de distância
LPPR_LAT = 41.2383
LPPR_LON = -8.6817
MAX_DISTANCE_NM = 60.0 

# Define o caminho da pasta data e do ficheiro
BASE_DIR = Path(__file__).resolve().parent.parent 
DATA_FILE = BASE_DIR / "data" / "lppr_voos_ativos.csv"

# ADICIONADO: Função para calcular a distância em Milhas Náuticas
def get_distance_nm(lat1, lon1, lat2, lon2):
    R = 3440.065 # Raio da Terra em Milhas Náuticas
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

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
                p_lat = pilot.get('latitude')
                p_lon = pilot.get('longitude')
                
                if p_lat and p_lon:
                    # Calcula a distância
                    dist_nm = get_distance_nm(p_lat, p_lon, LPPR_LAT, LPPR_LON)
                    
                    # SÓ ADICIONA SE ESTIVER A MENOS DE 60 NM
                    if dist_nm <= MAX_DISTANCE_NM:
                        arrivals.append({
                            'callsign': pilot.get('callsign', 'N/A'),
                            'departure': flight_plan.get('departure', 'N/A'),
                            'aircraft': flight_plan.get('aircraft_short', 'N/A'),
                            'altitude': altitude,
                            'groundspeed': pilot.get('groundspeed', 0),
                            'distance_nm': round(dist_nm, 1), # Adicionado ao CSV
                            'route': flight_plan.get('route', 'N/A')
                        })

    if arrivals:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Atualizado com a nova coluna 'distance_nm'
        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['callsign', 'departure', 'aircraft', 'altitude', 'groundspeed', 'distance_nm', 'route'])
            writer.writeheader()
            writer.writerows(arrivals)
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Atualizado: {len(arrivals)} voos a caminho de LPPR (<= 60NM).")
    else:
        if DATA_FILE.exists():
            open(DATA_FILE, 'w').close()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Atualizado: Nenhum voo a caminho de LPPR (<= 60NM).")

if __name__ == "__main__":
    print(f"A iniciar o radar LPPR (Atualiza a cada {REFRESH_RATE}s). A filtrar voos a 60 NM.")
    try:
        while True:
            get_lppr_arrivals()
            time.sleep(REFRESH_RATE) 
    except KeyboardInterrupt:
        print("\nRadar desligado pelo utilizador.")