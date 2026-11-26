import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import consumidor
from app.config import CONSUMIDOR_ATIVO, DOCS_ATIVA
from app.database import Base, engine
from app.rotas import router as notificacoes_router
from app.seguranca_http import CabecalhosDeSeguranca


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    Base.metadata.create_all(engine)
    parar = threading.Event()
    ativo = os.getenv("CONSUMIDOR_ATIVO", "1" if CONSUMIDOR_ATIVO else "0") == "1"
    if ativo:
        consumidor.iniciar(parar)
    yield
    parar.set()


app = FastAPI(
    title="HelpDesk TI · Serviço de Notificações",
    version="1.0.0",
    lifespan=ciclo_de_vida,
    docs_url="/docs" if DOCS_ATIVA else None,
    redoc_url=None,
    openapi_url="/openapi.json" if DOCS_ATIVA else None,
)
app.add_middleware(CabecalhosDeSeguranca)
app.include_router(notificacoes_router)


@app.get("/saude", tags=["Saúde"])
def saude():
    return {"status": "ok", "servico": "notificacoes"}
