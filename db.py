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