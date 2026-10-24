import csv
import requests
import math
import time
import os 
from pathlib import Path

# ==========================================
# CONFIGURAÇÕES DE CAMINHOS E TEMPO
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

STANDS_FILE = DATA_DIR / "lppr_stands.csv"
OCCUPANCY_FILE = DATA_DIR / "lppr_stands_ocupacao.csv" 
ATTR_FILE = DATA_DIR / "lppr_atribuicoes.csv" 

REFRESH_RATE = 15 

def load_csv(filepath):
    if not filepath.exists(): return []
    with open(filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
        return [row for row in reader]

def dms_to_decimal(dms_str):
    try:
        dms_str = dms_str.strip()
        direction = dms_str[0] 
        parts = dms_str[1:].split()
        decimal = float(parts[0]) + (float(parts[1]) / 60.0) + (float(parts[2]) / 3600.0)
        if direction in ['S', 'W']: decimal = -decimal
        return decimal
    except Exception: return 0.0

def get_distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def clean_disconnected_flights(online_callsigns):
    """Limpa as atribuições de aviões que já desligaram do VATSIM."""
    if not ATTR_FILE.exists(): return
    
    atribuicoes = load_csv(ATTR_FILE)
    if not atribuicoes: return

    updated_attr = []
    changed = False

    for row in atribuicoes:
        callsign = row.get('callsign', '').strip()
        # Se o avião já não está online e o status era ATRIBUIDO
        if callsign and callsign not in online_callsigns and row.get('status') == 'ATRIBUIDO':
            row['status'] = 'DESCONECTADO'
            row['stand_atribuido'] = 'LIVRE'
            changed = True
        updated_attr.append(row)

    if changed:
        with open(ATTR_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['callsign', 'icao', 'categoria', 'stand_atribuido', 'status', 'match'])
            writer.writeheader()
            writer.writerows(updated_attr)
        print("🧹 Limpeza: Voos que desligaram foram removidos e stands libertados.")

def run_check():
    stands = load_csv(STANDS_FILE)
    for s in stands:
        s['lat'] = dms_to_decimal(s.get('latitude', ''))
        s['lon'] = dms_to_decimal(s.get('longitude', ''))
        s['occupied_by'] = None
        s['distance'] = 0.0

    url = "https://data.vatsim.net/v3/vatsim-data.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"⚠️ Erro ao ligar ao VATSIM: {e}")
        return

    pilots = data.get('pilots', [])
    online_callsigns = {p.get('callsign') for p in pilots}
    
    # CHAMAR A FUNÇÃO DE LIMPEZA AQUI
    clean_disconnected_flights(online_callsigns)

    ground_pilots = [p for p in pilots if p.get('groundspeed', 0) < 5 and p.get('altitude', 0) < 500]
    MATCH_DISTANCE = 80.0 

    for pilot in ground_pilots:
        p_lat, p_lon = pilot.get('latitude'), pilot.get('longitude')
        callsign = pilot.get('callsign', 'Unknown')
        closest_stand = None
        min_dist = float('inf')

        for stand in stands:
            dist = get_distance_meters(p_lat, p_lon, stand['lat'], stand['lon'])
            if dist < min_dist:
                min_dist = dist
                closest_stand = stand

        if closest_stand and min_dist <= MATCH_DISTANCE:
            closest_stand['occupied_by'] = callsign
            closest_stand['distance'] = round(min_dist, 1)

    print("\n" + "="*60)
    print(f" 🅿️  ESTADO DOS STANDS (LPPR) - {time.strftime('%H:%M:%S')} 🅿️")
    print("="*60)

    resultados_ocupacao = []
    occupied_count = 0

    for s in stands:
        if s['occupied_by']:
            occupied_count += 1
            status = "OCUPADO"
            print(f"🔴 {s['stand']:<4} | OCUPADO por {s['occupied_by']} (a {s['distance']}m)")
        else:
            status = "LIVRE"
            
        resultados_ocupacao.append({
            'stand': s['stand'], 'status': status,
            'callsign': s['occupied_by'] if s['occupied_by'] else '',
            'distancia_metros': s['distance']
        })

    print("-" * 60)
    print(f"Total de stands ocupados: {occupied_count} / {len(stands)}")
    print("="*60)

    with open(OCCUPANCY_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['stand', 'status', 'callsign', 'distancia_metros'])
        writer.writeheader()
        writer.writerows(resultados_ocupacao)
    print(f"💾 Ocupação guardada em: {OCCUPANCY_FILE.name}")

if __name__ == "__main__":
    print(f"📡 Monitor de Ocupação LPPR ligado (Atualiza a cada {REFRESH_RATE}s). Ctrl+C para parar.")
    try:
        while True:
            os.system('clear') 
            run_check()
            print(f"\n⏳ A aguardar {REFRESH_RATE} segundos...")
            time.sleep(REFRESH_RATE)
    except KeyboardInterrupt:
        print("\n\nMonitor desligado.")