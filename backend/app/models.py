import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class StatusDocumento(str, enum.Enum):
    pendente = "pendente"      # arquivo enviado, ainda sem leitura da IA
    processado = "processado"  # IA extraiu os dados, falta o usuário conferir
    revisado = "revisado"      # usuário conferiu e confirmou


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    documentos: Mapped[list["Documento"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )


class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    arquivo: Mapped[str] = mapped_column(String(500))
    status: Mapped[StatusDocumento] = mapped_column(
        Enum(StatusDocumento, name="status_documento"),
        default=StatusDocumento.pendente,
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="documentos")
    lancamentos: Mapped[list["Lancamento"]] = relationship(
        back_populates="documento", cascade="all, delete-orphan"
    )


class Lancamento(Base):
    __tablename__ = "lancamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"), index=True)
    fornecedor: Mapped[str | None] = mapped_column(String(200))
    valor: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    data: Mapped[date | None] = mapped_column(Date)
    categoria: Mapped[str | None] = mapped_column(String(80))
    # Nível de certeza da IA, de 0 a 1. Base da tela de revisão.
    confianca: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    revisado: Mapped[bool] = mapped_column(Boolean, default=False)

    documento: Mapped["Documento"] = relationship(back_populates="lancamentos")