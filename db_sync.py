import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

from modelos import Usuario
import sql

# cria um path
BASE_DIR = Path(__file__).resolve().parent

def verifica_senha(senha: str) -> Usuario:
  sql = "select * from usuario where senha=?"
  cur = conn.cursor()
  res = cur.execute(sql, (senha,))
  row = res.fetchone()
  if row is None:
     return Usuario()
  
  return Usuario(
    id = row[0],
    nome=row[1],
    senha=row[2],
  )

def executa_ddl():
  sql = """
    CREATE TABLE IF NOT EXISTS usuario (
      ID INTEGER PRIMARY KEY AUTOINCREMENT,
      NOME TEXT NOT NULL,
      SENHA TEXT NOT NULL
    );
  """
  try: 
    conn.execute(sql)
    conn.commit()
  except Exception as e:
     print("Não foi possível executar o DDL no sqlite: ", e)
     sys.exit(1)

def faz_calculos(df: pd.DataFrame) -> pd.DataFrame:
  print(df.info())
  conn_mem = sqlite3.connect(":memory:")
  conn_mem.execute(sql.SQL_DDL_CALCULO)
  conn_mem.commit()

  with conn_mem:
    for _, row in df.iterrows():
      conn_mem.execute(
        "INSERT INTO peso (TIMESTAMP, NU_PESO_G) VALUES(?, ?)", 
        (str(row["TIMESTAMP"]), row["NU_PESO_G"],)
      )

  df_calculo = pd.read_sql_query(sql.SQL_CALCULO,conn_mem)

  conn_mem.close()

  return df_calculo

# conecta no banco
try:
  conn = sqlite3.connect(BASE_DIR / "db.sqlite", check_same_thread=False)
  executa_ddl()
except Exception as e:
  print("Não foi possível conectar ao db.sqlite: ", e)
  sys.exit(1)
