import sys
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

# Configura log básico para ver o que acontece por baixo dos panos na API
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from db.oracle import OracleConnector
from api.client import CashUpClient
from sync.clientes import SyncClientes

def test_sync():
    print("Iniciando teste de sincronizacao de Clientes...")
    try:
        db = OracleConnector()
        api = CashUpClient()
        
        with db:
            service = SyncClientes(db, api)
            print("\nExecutando extracao e envio...")
            result = service.execute()
            
            print("\n" + "="*40)
            print("RESULTADO DA SINCRONIZACAO")
            print("="*40)
            print(f"Status Final   : {result.status.upper()}")
            print(f"Lidos da View  : {result.total_records}")
            print(f"Enviados (OK)  : {result.sent_records}")
            print(f"Erros no envio : {result.error_records}")
            print(f"Duracao        : {result.duration_seconds:.2f} segundos")
            
            if result.errors:
                print("\nDETALHES DOS ERROS:")
                for i, err in enumerate(result.errors, 1):
                    print(f"{i}. {err}")
            print("="*40)
            
    except Exception as e:
        print(f"\n❌ Erro crítico durante o teste: {e}")

if __name__ == "__main__":
    test_sync()
