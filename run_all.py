import subprocess
import time
import os
import sys
from pathlib import Path

# ==========================================
# TRUQUE MÁGICO: AUTO-ATIVAR O VENV
# ==========================================
if sys.prefix == sys.base_prefix:
    venv_python = Path(__file__).parent / "venv" / "bin" / "python"
    
    if venv_python.exists():
        print("🔄 Ambiente virtual não detetado. A reiniciar o script dentro do venv...\n")
        try:
            # Adicionamos o try/except aqui para apanhar o Ctrl+C de forma limpa
            subprocess.run([str(venv_python)] + sys.argv)
        except KeyboardInterrupt:
            pass # Ignora o erro feio quando fazes Ctrl+C
        
        sys.exit(0) 
    else:
        print("❌ ERRO: A pasta 'venv' não foi encontrada!")
        print("👉 Cria o ambiente com: python3 -m venv venv")
        sys.exit(1)



# ==========================================
# SISTEMA PRINCIPAL
# ==========================================
def start_system():
    print("🚀 A INICIAR O SISTEMA COMPLETO LPPR...")
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    scripts = [
        ("radar", "python3 src/lppr_vatsim_loop.py"),
        ("ocupacao", "python3 src/lppr_check_occupancy.py"),
        ("atribuicao", "python3 src/assign_stands.py")
    ]

    processes = []

    # 1. Iniciar os motores em background
    for name, cmd in scripts:
        log_file = open(log_dir / f"{name}.log", "w", encoding="utf-8")
        print(f"A iniciar {name}...")
        
        p = subprocess.Popen(cmd.split(), stdout=log_file, stderr=subprocess.STDOUT)
        processes.append((name, p, log_file))
        
        time.sleep(1.5)

    print("\n✅ Motor iniciado! Os logs estão a ser guardados na pasta 'logs/'.")
    print("📊 A abrir o Dashboard no browser...\n")
    print("⚠️  NOTA: Para parar tudo, prime Ctrl+C neste terminal.\n")
    
    try:
        # 2. Abrir o Streamlit no primeiro plano
        # Como já estamos dentro do venv (graças ao truque lá em cima), 
        # o sys.executable já aponta para o Python correto.
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
        
    except KeyboardInterrupt:
        print("\n🛑 A parar todos os processos e a fechar o Dashboard...")
        for name, p, log_file in processes:
            p.terminate()
            log_file.close()
        print("Todos os processos foram parados. Até à próxima!\n\n")

if __name__ == "__main__":
    start_system()