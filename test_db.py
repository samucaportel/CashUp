import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import settings
from db.oracle import OracleConnector

def test_connection():
    print("Testando conexão com o Oracle...")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"SID: {settings.DB_SID}")
    print(f"User: {settings.DB_USER}")
    
    try:
        db = OracleConnector()
        with db:
            print("\n✅ Conexão estabelecida com sucesso!")
            
            # Tenta pegar a versão do banco para confirmar
            try:
                res = db.execute_query("SELECT * FROM v$version WHERE ROWNUM = 1")
                if res:
                    # Pode vir em estrutura de tupla ou dict dependendo do cursor
                    if isinstance(res[0], dict):
                        version = list(res[0].values())[0]
                    else:
                        version = res[0][0]
                    print(f"Versão do Banco: {version}")
            except Exception as e:
                print(f"Conectou, mas não conseguiu ler a versão (sem permissão em v$version): {e}")
                
    except Exception as e:
        print(f"\n❌ Erro ao conectar no Oracle:\n{e}")

if __name__ == "__main__":
    test_connection()
