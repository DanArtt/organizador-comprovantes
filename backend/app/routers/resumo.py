from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Documento, Lancamento, Usuario
from ..schemas import ItemCategoria, ResumoSaida
from .auth import usuario_atual

router = APIRouter(prefix="/resumo", tags=["resumo"])


def intervalo_do_mes(mes: str | None) -> tuple[str, date, date]:
    """Devolve (rótulo "AAAA-MM", primeiro dia do mês, primeiro dia do mês seguinte).

    Sem `mes`, usa o mês atual.
    """
    if mes is None:
        hoje = date.today()
        ano, numero = hoje.year, hoje.month
    else:
        ano, numero = int(mes[:4]), int(mes[5:7])

    inicio = date(ano, numero, 1)
    # Usar "até o início do mês seguinte" evita calcular o último dia do mês.
    fim = date(ano + 1, 1, 1) if numero == 12 else date(ano, numero + 1, 1)
    return f"{ano:04d}-{numero:02d}", inicio, fim


@router.get("", response_model=ResumoSaida)
def resumo_do_mes(
    mes: str | None = Query(
        default=None,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        description="Mês no formato AAAA-MM. Se omitido, usa o mês atual.",
    ),
    usuario: Usuario = Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    """Total de gastos do mês por categoria.

    Só entram lançamentos já revisados: os números mostrados são os que o
    usuário confirmou, e não o palpite bruto da IA.
    """
    rotulo, inicio, fim = intervalo_do_mes(mes)

    soma = func.sum(Lancamento.valor)
    consulta = (
        select(Lancamento.categoria, soma, func.count(Lancamento.id))
        .join(Documento, Lancamento.documento_id == Documento.id)
        .where(
            Documento.usuario_id == usuario.id,
            Lancamento.revisado.is_(True),
            Lancamento.valor.is_not(None),
            Lancamento.data >= inicio,
            Lancamento.data < fim,
        )
        .group_by(Lancamento.categoria)
        .order_by(soma.desc())
    )
    linhas = db.execute(consulta).all()

    total = sum((linha[1] for linha in linhas), Decimal("0"))
    por_categoria = [
        ItemCategoria(
            categoria=categoria,
            total=subtotal,
            quantidade=quantidade,
            percentual=round(float(subtotal / total * 100), 1) if total > 0 else 0.0,
        )
        for categoria, subtotal, quantidade in linhas
    ]

    # Quantos lançamentos ainda esperam conferência (de qualquer mês): serve
    # para a tela avisar "você tem N itens para revisar".
    a_revisar = db.scalar(
        select(func.count(Lancamento.id))
        .join(Documento, Lancamento.documento_id == Documento.id)
        .where(
            Documento.usuario_id == usuario.id,
            Lancamento.revisado.is_(False),
        )
    )

    return ResumoSaida(
        mes=rotulo,
        total=total,
        quantidade=sum(item.quantidade for item in por_categoria),
        por_categoria=por_categoria,
        a_revisar=a_revisar or 0,
    )