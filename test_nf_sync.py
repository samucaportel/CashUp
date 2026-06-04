import sys
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

# Configura log básico
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from db.oracle import OracleConnector
from api.client import CashUpClient
from sync.notas_fiscais import SyncNotasFiscais

def test_nf_sync():
    print("Iniciando teste de sincronizacao de Notas Fiscais...")
    try:
        db = OracleConnector()
        api = CashUpClient()
        
        with db:
            service = SyncNotasFiscais(db, api)
            print("\nExecutando extracao e envio (limitado a 5 registros)...")
            # Passamos ultimo_id=0 para forçar a busca de registros se a tabela de controle estiver vazia
            # Ou deixamos o padrão.
            result = service.execute(ultimo_id=0, limit=5)
            
            print("\n" + "="*40)
            print("RESULTADO DA SINCRONIZACAO - NOTAS FISCAIS")
            print("="*40)
            print(f"Status Final   : {result.status.upper()}")
            print(f"Lidos da View  : {result.total_records}")
            print(f"Enviados (OK)  : {result.sent_records}")
            print(f"Erros no envio : {result.error_records}")
            print(f"Duracao        : {result.duration_seconds:.2f} segundos")
            
            if result.errors:
                print("\nDETALHES DOS ERROS:")
                for i, err in enumerate(result.errors, 1):
                    # Limita a exibição de erros longos
                    msg = str(err)
                    if len(msg) > 200:
                        msg = msg[:197] + "..."
                    print(f"{i}. {msg}")
            print("="*40)
            
    except Exception as e:
        import traceback
        print(f"\n❌ Erro crítico durante o teste: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_nf_sync()
