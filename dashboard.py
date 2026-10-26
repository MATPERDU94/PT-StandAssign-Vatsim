import streamlit as st
import pandas as pd
import time
from pathlib import Path

# ==========================================
# CONFIGURAÇÕES DA PÁGINA
# ==========================================
st.set_page_config(page_title="LPPR Stand Manager", page_icon="🛬", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ATTR_FILE = DATA_DIR / "lppr_atribuicoes.csv"
OCCUPANCY_FILE = DATA_DIR / "lppr_stands_ocupacao.csv"

# Função para ler CSV com segurança
def load_data(filepath):
    if not filepath.exists():
        return pd.DataFrame()
    try:
        # O pandas lê o CSV e limpa os espaços
        df = pd.read_csv(filepath, skipinitialspace=True)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return pd.DataFrame()

# ==========================================
# INTERFACE VISUAL
# ==========================================
st.title("🛬 LPPR - Sistema de Gestão de Stands")
st.markdown("Dashboard em tempo real do Aeroporto do Porto (VATSIM)")

# Criar duas colunas lado a lado
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Atribuições de Chegadas")
    df_attr = load_data(ATTR_FILE)
    if not df_attr.empty:
        # Mostrar a tabela de atribuições
        st.dataframe(
            df_attr[['callsign', 'icao', 'stand_atribuido', 'status']], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma atribuição ativa no momento.")

with col2:
    st.subheader("🅿️ Estado dos Stands (Físico)")
    df_occ = load_data(OCCUPANCY_FILE)
    if not df_occ.empty:
        # Filtrar apenas os ocupados para mostrar na lista principal
        df_ocupados = df_occ[df_occ['status'] == 'OCUPADO']
        
        if not df_ocupados.empty:
            st.dataframe(
                df_ocupados[['stand', 'callsign', 'distancia_metros']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("Todos os stands estão livres no simulador!")
            
        # Mostrar a contagem total
        total_ocupados = len(df_ocupados)
        total_stands = len(df_occ)
        st.metric(label="Ocupação do Aeroporto", value=f"{total_ocupados} / {total_stands} stands")
    else:
        st.info("A aguardar dados do sensor de ocupação...")

# ==========================================
# AUTO-REFRESH (Atualiza a cada 10 segundos)
# ==========================================
time.sleep(10)
st.rerun()