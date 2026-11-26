from dataclasses import dataclass

import jwt

from app.config import JWT_ALGORITMO, JWT_EMISSOR, JWT_SEGREDO


class TokenInvalido(Exception):
    pass


@dataclass(frozen=True)
class UsuarioToken:
    id: int
    perfil: str


def ler(token: str) -> UsuarioToken:
    try:
        dados = jwt.decode(
            token,
            JWT_SEGREDO,
            algorithms=[JWT_ALGORITMO],
            issuer=JWT_EMISSOR,
            options={"require": ["exp", "iat", "sub", "iss", "perfil"]},
        )
        perfil = dados["perfil"]
        if perfil not in ("solicitante", "tecnico", "admin"):
            raise TokenInvalido()
        return UsuarioToken(id=int(dados["sub"]), perfil=perfil)
    except (jwt.PyJWTError, ValueError, KeyError) as erro:
        raise TokenInvalido() from erro
