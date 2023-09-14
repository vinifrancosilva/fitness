import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

from modelos import Usuario, Registro
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
  try: 
    conn.executescript(sql.DDL)
    conn.commit()
  except Exception as e:
     print("Não foi possível executar o DDL no sqlite: ", e)
     sys.exit(1)

def insere_registro(data_hora, peso, usuario) -> Registro:
  # VERIFICA SE EXISTE REGISTRO PARA AQUELE DIA
  cursor = conn.cursor()
  res = cursor.execute(sql.SELECIONA_REGISTRO_DATA_USUARIO_ID, (data_hora.date(), usuario.id))
  row = res.fetchone()

  # SE JÁ TEM REGISTRO PARA A DATA, FAZ O UPDATE
  if row is not None:
    cursor.execute(
      sql.ATUALIZA_REGISTRO_DATA_USUARIO_ID, 
      (data_hora, peso, data_hora.date(), usuario.id,)
    )
    id = row[0]
  else:
    # SE NÃO TEM, INSERE
    cursor.execute(sql.INSERE_REGISTRO, (usuario.id, data_hora, peso, ))
    id = cursor.lastrowid

  # COMMITA A TRANSAÇÃO
  conn.commit()

  # CRIA E RETORNA UM PYDANTIC PARA O REGISTRO RETORNADO
  res = cursor.execute(sql.SELECIONA_REGISTRO_ID, (id, ))
  row = res.fetchone()
  
  return Registro(
    id = row[0],
    usuario_id = row[1],
    data_hora=row[2],
    peso=row[3],
  )

def faz_calculos(usuario: Usuario) -> pd.DataFrame:
  df_calculo = pd.read_sql_query(sql.CALCULO, conn, params=(usuario.id,))

  return df_calculo

# conecta no banco
try:
  conn = sqlite3.connect(BASE_DIR / "db.sqlite", check_same_thread=False)
  executa_ddl()
except Exception as e:
  print("Não foi possível conectar ao db.sqlite: ", e)
  sys.exit(1)
