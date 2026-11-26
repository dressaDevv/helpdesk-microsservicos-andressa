"""Clientes HTTP para outros microsservicos (com timeout e tratamento de falha)."""
import httpx

from app.config import HTTP_TIMEOUT, INVENTARIO_URL, USUARIOS_URL
from app.erros import NaoEncontrado, RegraDeNegocio, ServicoIndisponivel


def conferir_ativo(ativo_id: int, token: str) -> dict:
    try:
        r = httpx.get(
            f"{INVENTARIO_URL}/ativos/{ativo_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=HTTP_TIMEOUT,
        )
    except httpx.RequestError as erro:
        raise ServicoIndisponivel("Serviço de inventário indisponível no momento.") from erro

    if r.status_code == 404:
        raise NaoEncontrado(f"Ativo {ativo_id} não encontrado.")
    if r.status_code >= 500:
        raise ServicoIndisponivel("Serviço de inventário indisponível no momento.")
    if r.status_code != 200:
        raise RegraDeNegocio("Não foi possível validar o equipamento no inventário.")
    return r.json()


def conferir_tecnico(tecnico_id: int, token: str) -> dict:
    try:
        r = httpx.get(
            f"{USUARIOS_URL}/usuarios/{tecnico_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=HTTP_TIMEOUT,
        )
    except httpx.RequestError as erro:
        raise ServicoIndisponivel("Serviço de usuários indisponível no momento.") from erro

    if r.status_code == 404:
        raise NaoEncontrado(f"Usuário {tecnico_id} não encontrado.")
    if r.status_code >= 500:
        raise ServicoIndisponivel("Serviço de usuários indisponível no momento.")
    if r.status_code != 200:
        raise RegraDeNegocio("Não foi possível validar o técnico no serviço de usuários.")

    usuario = r.json()
    if usuario.get("perfil") != "tecnico":
        raise RegraDeNegocio(f"Usuário {tecnico_id} não é técnico.")
    return usuario
