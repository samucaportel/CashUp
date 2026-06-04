import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import settings
import oracledb

def test_connection():
    print("Testando conexão DIRETA com o Oracle (sem pool)...")
    
    dsn = oracledb.makedsn(
        settings.DB_HOST,
        settings.DB_PORT,
        sid=settings.DB_SID,
    )
    
    print(f"DSN: {dsn}")
    print(f"User: {settings.DB_USER}")
    
    try:
        oracledb.init_oracle_client()
        print("Modo Thick (Instant Client) ativado com sucesso.")
    except Exception as e:
        print(f"Aviso: Não foi possível ativar o modo Thick. Você precisa do Oracle Instant Client instalado. Erro: {e}")

    try:
        conn = oracledb.connect(
            user=settings.DB_USER,
            password=settings.DB_PASS,
            dsn=dsn
        )
        print("\n✅ Conexão direta estabelecida com sucesso!")
        
        with conn.cursor() as cursor:
            # Pegar a data atual do banco como teste infalível (sem depender de v$version)
            cursor.execute("SELECT SYSDATE FROM DUAL")
            row = cursor.fetchone()
            print(f"Data no servidor Oracle: {row[0]}")
            
        conn.close()
                
    except Exception as e:
        print(f"\n❌ Erro ao conectar no Oracle:\n{e}")

if __name__ == "__main__":
    test_connection()
