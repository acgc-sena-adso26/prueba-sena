from psycopg2 import connect
from dotenv import load_dotenv
import os
load_dotenv()
def conectar():
    conn = connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        sslmode=os.getenv("DB_SSLMODE")
    )
    return conn


def query(sql, params=None, fetchone=True):
    conn = conectar()
    # Usar dictionary=True si usas MySQL para acceder por nombre de columna
    cursor = conn.cursor() 
    try:
        if params and not isinstance(params, (tuple, list)):
            params = (params,)
            
        cursor.execute(sql, params or ())
        
        # 1. Verificamos si la consulta es de lectura (SELECT)
        sql_upper = sql.strip().upper()
        if sql_upper.startswith("SELECT") or sql_upper.startswith("SHOW"):
            return cursor.fetchone() if fetchone else cursor.fetchall()
        
        # 2. Si es INSERT, UPDATE o DELETE, guardamos los cambios
        conn.commit()
        return cursor.rowcount  # Retorna cuántas filas fueron afectadas
        
    except Exception as e:
        conn.rollback()
        print(f"Error en la consulta: {e}")
        return None
    finally:
        cursor.close()
        conn.close()