import subprocess
import time
import os
from pathlib import Path

def start_system():
    print("🚀 A INICIAR O SISTEMA COMPLETO LPPR (EM BACKGROUND)...")
    
    # Criar a pasta de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    scripts = [
        ("radar", "python3 src/lppr_vatsim_loop.py"),
        ("ocupacao", "python3 src/lppr_check_occupancy.py"),
        ("atribuicao", "python3 src/assign_stands.py")
    ]

    processes = []

    for name, cmd in scripts:
        log_file = open(log_dir / f"{name}.log", "w", encoding="utf-8")
        print(f"A iniciar {name}...")
        
        # Inicia o processo em background e redireciona o output para o log
        p = subprocess.Popen(cmd.split(), stdout=log_file, stderr=subprocess.STDOUT)
        processes.append((name, p, log_file))
        
        # Espera 1.5 segundos entre cada um para garantir que os CSVs são criados
        time.sleep(1.5)

    print("\n✅ Sistema iniciado com sucesso!")
    print("📁 Os logs estão a ser guardados na pasta 'logs/'.")
    print("👉 Para parares o sistema, prime Ctrl+C.\n")
    
    try:
        # Mantém o script principal a correr para poderes parar com Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 A parar todos os processos...")
        for name, p, log_file in processes:
            p.terminate()
            log_file.close()
        print("Todos os processos foram parados. Até à próxima!\n\n")

if __name__ == "__main__":
    start_system()