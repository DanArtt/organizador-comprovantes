from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Lancamento, StatusDocumento, Usuario
from ..schemas import LancamentoRevisao, LancamentoSaida
from .auth import usuario_atual

router = APIRouter(prefix="/lancamentos", tags=["lancamentos"])


@router.patch("/{lancamento_id}", response_model=LancamentoSaida)
def revisar(
    lancamento_id: int,
    revisao: LancamentoRevisao,
    usuario: Usuario = Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    """Confirma um lançamento lido pela IA, corrigindo os campos que vierem.

    Só os campos enviados são alterados. Chamar sem corpo (`{}`) significa
    "a IA acertou tudo": o lançamento só é marcado como revisado.
    """
    lancamento = db.get(Lancamento, lancamento_id)
    # Mesma resposta para "não existe" e "é de outro usuário".
    if lancamento is None or lancamento.documento.usuario_id != usuario.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lançamento não encontrado")

    for campo, valor in revisao.model_dump(exclude_unset=True).items():
        if valor is not None:  # null enviado por engano não apaga o dado
            setattr(lancamento, campo, valor)
    lancamento.revisado = True

    # Quando todos os lançamentos do documento foram conferidos,
    # o documento inteiro passa a "revisado".
    documento = lancamento.documento
    if all(item.revisado for item in documento.lancamentos):
        documento.status = StatusDocumento.revisado

    db.commit()
    db.refresh(lancamento)
    return lancamento