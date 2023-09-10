from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError

from typing import Annotated
import uvicorn
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas as pd
from pathlib import Path
from datetime import datetime
import sqlite3

from modelos import Usuario, Registro
import db_sync

# SETUP DO JINJA2
env = Environment(
  loader=FileSystemLoader("templates"),
  autoescape=select_autoescape()
)
# INSTANCIANDO OS TEMPLATES
index_template = env.get_template("upload.html")
calculos_template = env.get_template("calculos.html")

# cria um path
BASE_DIR = Path(__file__).resolve().parent

# INSTANCIA A FASTAPI
app = FastAPI()

@app.exception_handler(RequestValidationError)
def trata_erro_validacao(request, exc):
    return HTMLResponse(index_template.render(erro={
      "principal": "Erro de validação.",
      "excecao": str(exc.errors())
    }))

@app.get("/")
def index():
  return HTMLResponse(index_template.render())

@app.post("/processa_registro")
def processa_registro(
  senha: Annotated[str, Form()],
  data_hora: Annotated[datetime, Form()],
  peso: Annotated[int, Form()],
  modo: Annotated[str, Form()]
):
  # verifica a senha
  usuario = db_sync.verifica_senha(senha)
  if usuario.id == 0:
     return HTMLResponse(index_template.render(erro={
      "principal": "Erro na autenticação.",
      "excecao": "Senha incorreta ou inexistente, BURRO!"
    }))
  
  registro = db_sync.insere_registro(data_hora, peso, usuario)

  return HTMLResponse(index_template.render(sucesso={
    "header": "Registro inserido com sucesso.",
    "msg": f"DH: {registro.data_hora}, PESO: {registro.peso}g"
  }))

@app.post("/calculo")
def calculos(
  senha: Annotated[str, Form()], 
  planilha: Annotated[UploadFile, File()]
):
  # verifica a senha
  usuario = db_sync.verifica_senha(senha)
  if usuario.id == 0:
     return HTMLResponse(index_template.render(erro={
      "principal": "Erro na autenticação.",
      "excecao": "Senha incorreta ou inexistente, BURRO!"
    }))

  # recebe a planilha
  try:
    conteudo = planilha.file.read()
    planilha.close()
    nome = BASE_DIR / "planilhas" / f"{datetime.now().timestamp()}_{planilha.filename}"
    with open(nome, "wb") as f:
      f.write(conteudo)
  except Exception as e:
    return HTMLResponse(index_template.render(erro={
      "principal": "Erro ao receber planilha.",
      "excecao": str(e)
    }))

  # carrega no pandas
  try:
    df = pd.read_excel(nome)
    nome.unlink()
  except Exception as e:
    return HTMLResponse(index_template.render(erro={
      "principal": "Erro ao carregar o conteúdo da planilha.",
      "excecao": str(e)
    }))
  
  # se a planilha estiver diferente do esperado, devolve
  colunas = df.columns.to_list()
  if colunas.sort() != ["TIMESTAMP", "NU_PESO_G"].sort():
    return HTMLResponse(index_template.render(erro={
        "principal": "Erro ao carregar o conteúdo da planilha.",
        "excecao": "Planilha fora de padrão, usa a que eu mandei no grupo, jumento!"
      }))
  
  try:
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], errors="coerce")
  except Exception as e:
    return HTMLResponse(index_template.render(erro={
      "principal": "Erro ao converter o campo TIMESTAMP.",
      "excecao": str(e)
    }))

  # faz os calculos
  df_calculado = db_sync.faz_calculos(df)
  
    # pensar se vou subir pra um sqlite e pegar com sql ou se vou fazer com o pandas
  return HTMLResponse(df_calculado.to_html(index=False))
  
  # renderiza o template
  # return HTMLResponse(calculos_template.render())

if __name__ == "__main__":
    porta = 0
    # opção de receber a porta como parâmetro
    if len(sys.argv) > 1:
        if len(sys.argv) < 3:
            try:
                porta = int(sys.argv[1])
            except ValueError as e:
                print(f"A porta informada não é um número inteiro: {sys.argv[1]}")
                sys.exit(1)
        else:
            print("A API recebe apenas a porta como parâmetro.")
            sys.exit(1)
    
    # caso não receba a porta como parâmetro, roda na porta 3003
    if porta == 0:
        porta=3003

    # roda o servidor da aplicação
    # BASE_DIR = Path(__file__).resolve().parent
    uvicorn.run(
        app, 
        host="localhost",
        port=porta,
        # USEI O mkcert PRA GERAR OS CERTIFICADOS
        # DA PRA BAIXAR NO GITHUB DELE OS RELEASES PRÉ-COMPILADOS PRA CADA PLATAFORMA
        # mkcert sp7172sr009.sp.caixa E ELE GERA AMBAS AS CHAVES, PÚBLICA E PRIVADA
        # ssl_keyfile=BASE_DIR / "cert/sp7172sr009.sp.caixa-key.pem",
        # ssl_certfile=BASE_DIR / "cert/sp7172sr009.sp.caixa.pem"
    )