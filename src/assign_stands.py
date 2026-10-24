import csv
import requests
import random
import time
import os
from pathlib import Path

# ==========================================
# 1. CONFIGURAÇÕES
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

STANDS_FILE = DATA_DIR / "lppr_stands.csv"
FLIGHTS_FILE = DATA_DIR / "lppr_voos_ativos.csv"
AIRCRAFT_FILE = DATA_DIR / "aircraft_categories.csv"
OCCUPANCY_FILE = DATA_DIR / "lppr_stands_ocupacao.csv" 
OUTPUT_FILE = DATA_DIR / "lppr_atribuicoes.csv" 

# Tempo entre cada verificação (recomendo 15s para alinhar com os outros scripts)
REFRESH_RATE = 15 

ATC_BLOCKERS = [
    'LPPR_DEL', 'LPPR_GND', 'LPPR_TWR', 'LPPR_APP',
    'LPPC_CTR', 'LPPC_N_CTR', 'LPPC_NU_CTR', 'LPPC_E_CTR'
]

# ==========================================
# 2. FUNÇÕES
# ==========================================
def load_csv(filepath):
    if not filepath.exists(): return []
    with open(filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
        
        dados_limpos = []
        for row in reader:
            clean_row = {}
            for k, v in row.items():
                if k and v:
                    clean_row[k.strip()] = v.replace('"', '').strip()
                elif k:
                    clean_row[k.strip()] = ''
            dados_limpos.append(clean_row)
        return dados_limpos

def get_compatible_stands(plane_cat):
    if plane_cat == 'H': return ['H']
    if plane_cat == 'M': return ['H', 'M']
    if plane_cat == 'L': return ['H', 'M', 'L']
    return ['M']

def is_atc_online():
    url = "https://data.vatsim.net/v3/vatsim-data.json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return [c.get('callsign').upper() for c in data.get('controllers', []) if c.get('callsign', '').upper() in ATC_BLOCKERS]
    except Exception:
        return []

# ==========================================
# 3. LÓGICA PRINCIPAL (Apenas uma execução)
# ==========================================
def run_assignment():
    if is_atc_online():
        print("🛑 ATC online. Atribuição automática suspensa.")
        return 

    stands = load_csv(STANDS_FILE)
    flights = load_csv(FLIGHTS_FILE)
    aircraft_data = load_csv(AIRCRAFT_FILE)
    ocupacao_data = load_csv(OCCUPANCY_FILE)

    if not flights:
        print("Nenhum voo ativo no ficheiro de chegadas. O ficheiro de atribuições será limpo.")
        with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['callsign', 'icao', 'categoria', 'stand_atribuido', 'status', 'match'])
            writer.writeheader()
        return

    existing_assignments = {}
    if OUTPUT_FILE.exists():
        for row in load_csv(OUTPUT_FILE):
            if row.get('status') == 'ATRIBUIDO':
                existing_assignments[row['callsign']] = row['stand_atribuido']

    stands_fisicamente_ocupados = {row['stand'] for row in ocupacao_data if row.get('status') == 'OCUPADO'}

    categories_dict = {}
    for row in aircraft_data:
        icao = (row.get('icao_type') or '').strip().upper()
        cat = (row.get('category') or '').strip().upper()
        if icao: categories_dict[icao] = cat

    available_stands = []
    for s in stands:
        if not s.get('aircraft_category'): s['aircraft_category'] = 'M'
        s['occupied'] = False
        available_stands.append(s)

    resultados_atribuicao = []

    for flight in flights:
        callsign = (flight.get('callsign') or 'N/A').strip()
        icao = (flight.get('aircraft') or 'N/A').strip().upper()
        airline = callsign[:3].upper() 
        plane_cat = categories_dict.get(icao, 'M')
        
        if callsign in existing_assignments:
            stand_mantido = existing_assignments[callsign]
            
            if stand_mantido not in stands_fisicamente_ocupados:
                for s in available_stands:
                    if s['stand'] == stand_mantido:
                        s['occupied'] = True
                        break
                
                print(f"🔄 {callsign:<8} | {icao:<4} ({plane_cat}) | Mantém Stand: {stand_mantido:<4}")
                resultados_atribuicao.append({
                    'callsign': callsign, 'icao': icao, 'categoria': plane_cat,
                    'stand_atribuido': stand_mantido, 'status': 'ATRIBUIDO', 'match': 'Mantido'
                })
                continue
            else:
                print(f"⚠️ {callsign} tinha o stand {stand_mantido}, mas está ocupado. A procurar novo...")

        allowed_stands_cats = get_compatible_stands(plane_cat)
        candidates = [
            s for s in available_stands 
            if not s['occupied'] 
            and s.get('aircraft_category') in allowed_stands_cats
            and s['stand'] not in stands_fisicamente_ocupados
        ]

        if not candidates:
            print(f"❌ {callsign:<8} | {icao:<4} ({plane_cat}) | SEM STANDS DISPONÍVEIS!")
            resultados_atribuicao.append({
                'callsign': callsign, 'icao': icao, 'categoria': plane_cat,
                'stand_atribuido': 'N/A', 'status': 'SEM STAND', 'match': 'N/A'
            })
            continue

        preferred_candidates = []
        general_candidates = []

        for s in candidates:
            prefs = s.get('preferred_airlines', '')
            if prefs and airline in prefs.upper():
                preferred_candidates.append(s)
            else:
                general_candidates.append(s)
        
        if preferred_candidates:
            assigned = random.choice(preferred_candidates)
            match_type = "Companhia Preferida (Aleatório)"
        else:
            assigned = random.choice(general_candidates) if general_candidates else random.choice(candidates)
            match_type = "Geral (Aleatório)"

        assigned['occupied'] = True
        print(f"✅ {callsign:<8} | {icao:<4} ({plane_cat}) | Stand: {assigned['stand']:<4} ({match_type})")
        
        resultados_atribuicao.append({
            'callsign': callsign, 'icao': icao, 'categoria': plane_cat,
            'stand_atribuido': assigned['stand'], 'status': 'ATRIBUIDO', 'match': match_type
        })

    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['callsign', 'icao', 'categoria', 'stand_atribuido', 'status', 'match'])
        writer.writeheader()
        writer.writerows(resultados_atribuicao)
    
    print("-" * 80)
    print(f"💾 Atribuições guardadas em: {OUTPUT_FILE.name}")
    print(f"   Total de aviões no ficheiro: {len(resultados_atribuicao)}")

# ==========================================
# 4. CICLO INFINITO
# ==========================================
if __name__ == "__main__":
    print(f"🧠 Cérebro de Atribuição LPPR ligado (Atualiza a cada {REFRESH_RATE}s). Ctrl+C para parar.")
    try:
        while True:
            os.system('clear') # Limpa o terminal a cada ciclo
            print(f"⏱️  Verificação às {time.strftime('%H:%M:%S')}")
            print("=" * 80)
            
            run_assignment()
            
            print(f"\n⏳ A aguardar {REFRESH_RATE} segundos para a próxima atribuição...")
            time.sleep(REFRESH_RATE)
    except KeyboardInterrupt:
        print("\n\nCérebro desligado pelo utilizador.")