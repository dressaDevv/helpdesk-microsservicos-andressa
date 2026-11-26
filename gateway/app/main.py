"""API Gateway do HelpDesk TI.

Ponto unico de entrada (porta 8000): serve a interface web e encaminha
as requisicoes para cada microsservico na rede interna do Docker.
"""
import asyncio
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response

from app.config import (
    CHAMADOS_URL,
    DOCS_ATIVA,
    HTTP_TIMEOUT,
    INVENTARIO_URL,
    NOTIFICACOES_URL,
    USUARIOS_URL,
)
from app.seguranca_http import CabecalhosDeSeguranca

WEB = Path(__file__).parent / "web"
METODOS = ["GET", "POST", "PUT", "PATCH", "DELETE"]

app = FastAPI(
    title="HelpDesk TI · API Gateway",
    version="2.0.0",
    docs_url="/docs" if DOCS_ATIVA else None,
    redoc_url=None,
    openapi_url="/openapi.json" if DOCS_ATIVA else None,
)
app.add_middleware(CabecalhosDeSeguranca)


async def _repassar(request: Request, base_url: str, nome_servico: str) -> Response:
    destino = f"{base_url}{request.url.path}"
    if request.url.query:
        destino = f"{destino}?{request.url.query}"

    cabecalhos = {}
    for chave in ("authorization", "content-type", "accept"):
        valor = request.headers.get(chave)
        if valor:
            cabecalhos[chave] = valor
    if request.client:
        cabecalhos["x-forwarded-for"] = request.client.host

    corpo = await request.body()

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as cliente:
            resposta = await cliente.request(
                method=request.method,
                url=destino,
                content=corpo,
                headers=cabecalhos,
            )
    except httpx.RequestError:
        return JSONResponse(
            status_code=503,
            content={"detail": f"Serviço de {nome_servico} indisponível no momento."},
        )

    headers_saida = {}
    if "cache-control" in resposta.headers:
        headers_saida["Cache-Control"] = resposta.headers["cache-control"]

    return Response(
        content=resposta.content,
        status_code=resposta.status_code,
        headers=headers_saida,
        media_type=resposta.headers.get("content-type"),
    )


async def _checar_servico(cliente: httpx.AsyncClient, nome: str, url: str) -> tuple[str, str]:
    try:
        r = await cliente.get(f"{url}/saude")
        return nome, "online" if r.status_code == 200 else f"erro ({r.status_code})"
    except httpx.RequestError:
        return nome, "indisponivel"


@app.get("/saude", tags=["Saúde"])
async def saude():
    servicos = {
        "usuarios": USUARIOS_URL,
        "inventario": INVENTARIO_URL,
        "chamados": CHAMADOS_URL,
        "notificacoes": NOTIFICACOES_URL,
    }
    async with httpx.AsyncClient(timeout=2.0) as cliente:
        pares = await asyncio.gather(*[_checar_servico(cliente, nome, url) for nome, url in servicos.items()])
    status_servicos = dict(pares)
    todos_ok = all(st == "online" for st in status_servicos.values())
    return {
        "status": "ok" if todos_ok else "degradado",
        "gateway": "online",
        "servicos": status_servicos,
    }


@app.api_route("/auth", methods=METODOS, include_in_schema=False)
@app.api_route("/auth/{caminho:path}", methods=METODOS, include_in_schema=False)
async def rota_auth(request: Request, caminho: str = ""):
    return await _repassar(request, USUARIOS_URL, "usuários")


@app.api_route("/usuarios", methods=METODOS, include_in_schema=False)
@app.api_route("/usuarios/{caminho:path}", methods=METODOS, include_in_schema=False)
async def rota_usuarios(request: Request, caminho: str = ""):
    return await _repassar(request, USUARIOS_URL, "usuários")


@app.api_route("/ativos", methods=METODOS, include_in_schema=False)
@app.api_route("/ativos/{caminho:path}", methods=METODOS, include_in_schema=False)
async def rota_ativos(request: Request, caminho: str = ""):
    return await _repassar(request, INVENTARIO_URL, "inventário")


@app.api_route("/chamados", methods=METODOS, include_in_schema=False)
@app.api_route("/chamados/{caminho:path}", methods=METODOS, include_in_schema=False)
async def rota_chamados(request: Request, caminho: str = ""):
    return await _repassar(request, CHAMADOS_URL, "chamados")


@app.api_route("/notificacoes", methods=METODOS, include_in_schema=False)
@app.api_route("/notificacoes/{caminho:path}", methods=METODOS, include_in_schema=False)
async def rota_notificacoes(request: Request, caminho: str = ""):
    return await _repassar(request, NOTIFICACOES_URL, "notificações")


@app.get("/", include_in_schema=False)
def tela_inicial():
    return FileResponse(WEB / "index.html")


@app.get("/app.js", include_in_schema=False)
def script():
    return FileResponse(WEB / "app.js", media_type="text/javascript")


@app.get("/estilo.css", include_in_schema=False)
def estilo():
    return FileResponse(WEB / "estilo.css", media_type="text/css")
