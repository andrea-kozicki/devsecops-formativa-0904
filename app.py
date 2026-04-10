# =========================================================
# IMPORTAÇÕES
# =========================================================
from datetime import datetime, timezone
import json
import logging
import sqlite3
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse


# =========================================================
# CONFIGURAÇÃO DA APLICAÇÃO
# =========================================================
API = FastAPI()

metricas = {
    "requisicoes": 0,
    "erros": 0,
    "logins_falhos": 0
}

DB_NAME = "usuarios_banco.db"
LOG_FILE = "app.log"


# =========================================================
# LOGGING ESTRUTURADO
# =========================================================
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nivel": record.levelname,
            "endpoint": getattr(record, "endpoint", None),
            "ip": getattr(record, "ip", None),
            "mensagem": record.getMessage()
        }
        return json.dumps(log_record, ensure_ascii=False)


logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)
logger.propagate = False

if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(JsonFormatter())

console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())

logger.addHandler(file_handler)
logger.addHandler(console_handler)


# =========================================================
# BANCO DE DADOS
# =========================================================
def estabelecer_conexao():
    return sqlite3.connect(DB_NAME)


def iniciar_banco():
    conn = estabelecer_conexao()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute(
        "INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)",
        ("admin", "1234")
    )
    cursor.execute(
        "INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)",
        ("andrea", "senha123")
    )
    cursor.execute(
        "INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)",
        ("teste", "teste123")
    )

    conn.commit()
    conn.close()


iniciar_banco()


# =========================================================
# MIDDLEWARE
# =========================================================
@API.middleware("http")
async def contar_requisicoes_e_logar(request: Request, call_next):
    metricas["requisicoes"] += 1

    ip = request.client.host if request.client else "desconhecido"
    endpoint = request.url.path

    logger.info(
        "Acesso ao endpoint",
        extra={"endpoint": endpoint, "ip": ip}
    )

    try:
        resposta = await call_next(request)

        if resposta.status_code >= 400:
            metricas["erros"] += 1
            logger.warning(
                f"Resposta com status HTTP {resposta.status_code}",
                extra={"endpoint": endpoint, "ip": ip}
            )

        return resposta

    except Exception as exc:
        metricas["erros"] += 1
        logger.error(
            f"Erro interno não tratado: {str(exc)}",
            extra={"endpoint": endpoint, "ip": ip}
        )
        raise


# =========================================================
# TRATAMENTO GLOBAL DE ERROS
# =========================================================
@API.exception_handler(Exception)
async def tratar_erros_internos(request: Request, exc: Exception):
    ip = request.client.host if request.client else "desconhecido"
    endpoint = request.url.path

    logger.error(
        f"Erro interno do servidor: {str(exc)}",
        extra={"endpoint": endpoint, "ip": ip}
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )


# =========================================================
# ENDPOINT: CRIAR USUÁRIO
# =========================================================
@API.post("/criar")
def criar_usuario(
    request: Request,
    usuario: Optional[str] = Form(None),
    senha: Optional[str] = Form(None)
):
    ip = request.client.host if request.client else "desconhecido"
    endpoint = request.url.path

    if not usuario or not senha:
        logger.warning(
            "Tentativa de criação de usuário sem preencher usuário ou senha",
            extra={"endpoint": endpoint, "ip": ip}
        )
        raise HTTPException(status_code=400, detail="Usuário e senha são obrigatórios")

    conn = estabelecer_conexao()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            (usuario, senha)
        )
        conn.commit()

        logger.info(
            f"Usuário '{usuario}' criado com sucesso",
            extra={"endpoint": endpoint, "ip": ip}
        )

    except sqlite3.IntegrityError:
        logger.warning(
            f"Tentativa de criar usuário já existente: '{usuario}'",
            extra={"endpoint": endpoint, "ip": ip}
        )
        raise HTTPException(status_code=400, detail="Usuário já existe")

    finally:
        conn.close()

    return {"status": "usuário criado", "usuario": usuario}


# =========================================================
# ENDPOINT: LOGIN
# =========================================================
@API.post("/login")
def login(
    request: Request,
    usuario: Optional[str] = Form(None),
    senha: Optional[str] = Form(None)
):
    ip = request.client.host if request.client else "desconhecido"
    endpoint = request.url.path

    if not usuario or not senha:
        metricas["logins_falhos"] += 1
        logger.warning(
            "Tentativa de login sem usuário ou senha",
            extra={"endpoint": endpoint, "ip": ip}
        )
        raise HTTPException(status_code=400, detail="Usuário e senha são obrigatórios")

    conn = estabelecer_conexao()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username FROM usuarios WHERE username = ? AND password = ?",
        (usuario, senha)
    )

    resultado_query = cursor.fetchone()
    conn.close()

    if resultado_query:
        logger.info(
            f"Autenticação bem-sucedida para o usuário '{usuario}'",
            extra={"endpoint": endpoint, "ip": ip}
        )
        return {
            "status": "logged in",
            "usuario": resultado_query[1]
        }

    metricas["logins_falhos"] += 1
    logger.warning(
        f"Falha de autenticação para o usuário '{usuario}'",
        extra={"endpoint": endpoint, "ip": ip}
    )
    raise HTTPException(status_code=401, detail="Credenciais inválidas")


# =========================================================
# ENDPOINT: HEALTHCHECK
# =========================================================
@API.get("/health")
def health():
    return "OK"


# =========================================================
# ENDPOINT: MÉTRICAS
# =========================================================
@API.get("/metricas")
def get_metricas():
    return metricas


# =========================================================
# ENDPOINT: RAIZ
# =========================================================
@API.get("/")
def raiz():
    return {"mensagem": "API em funcionamento"}