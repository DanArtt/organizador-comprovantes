from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .ia import Categoria
from .models import StatusDocumento


class UsuarioCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)


class UsuarioSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusDocumento
    criado_em: datetime


class LancamentoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    documento_id: int
    fornecedor: str | None
    valor: Decimal | None
    data: date | None
    categoria: str | None
    confianca: Decimal | None
    revisado: bool


class LancamentoRevisao(BaseModel):
    """Correções enviadas pelo usuário. Todos os campos são opcionais."""

    model_config = ConfigDict(extra="forbid")

    fornecedor: str | None = Field(default=None, min_length=1, max_length=200)
    valor: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2
    )
    data: date | None = None
    categoria: Categoria | None = None


class ItemCategoria(BaseModel):
    categoria: str | None
    total: Decimal
    quantidade: int
    percentual: float


class ResumoSaida(BaseModel):
    mes: str
    total: Decimal
    quantidade: int
    por_categoria: list[ItemCategoria]
    a_revisar: int