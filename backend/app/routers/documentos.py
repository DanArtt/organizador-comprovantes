import uuid
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import ia
from ..database import get_db
from ..models import Documento, Lancamento, StatusDocumento, Usuario
from ..schemas import DocumentoSaida, LancamentoSaida
from .auth import usuario_atual

router = APIRouter(prefix="/documentos", tags=["documentos"])

PASTA_UPLOADS = Path("uploads")
TAMANHO_MAXIMO = 5 * 1024 * 1024  # 5 MB

# Primeiros bytes de cada formato aceito -> extensão que usamos ao salvar.
# Conferir o conteúdo é mais seguro do que confiar no nome ou no tipo
# informado pelo cliente, que podem ser forjados.
ASSINATURAS = [
    (b"\xff\xd8\xff", ".jpg"),
    (b"\x89PNG\r\n\x1a\n", ".png"),
    (b"%PDF-", ".pdf"),
]

MIME_POR_EXTENSAO = {
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".pdf": "application/pdf",
}


def detectar_extensao(inicio: bytes) -> str | None:
    for assinatura, extensao in ASSINATURAS:
        if inicio.startswith(assinatura):
            return extensao
    return None


def buscar_documento(
    documento_id: int, usuario: Usuario, db: Session
) -> Documento:
    documento = db.get(Documento, documento_id)
    # Mesma resposta para "não existe" e "é de outro usuário",
    # para não revelar quais ids existem.
    if documento is None or documento.usuario_id != usuario.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento não encontrado")
    return documento


@router.post("", response_model=DocumentoSaida, status_code=status.HTTP_201_CREATED)
def enviar(
    arquivo: UploadFile,
    usuario: Usuario = Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    """Recebe um comprovante (JPG, PNG ou PDF) e registra como pendente."""
    # Lê no máximo 1 byte além do limite, só para saber se estourou.
    conteudo = arquivo.file.read(TAMANHO_MAXIMO + 1)

    if not conteudo:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Arquivo vazio")
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Arquivo maior que 5 MB"
        )

    extensao = detectar_extensao(conteudo[:16])
    if extensao is None:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Formato não aceito. Envie JPG, PNG ou PDF",
        )

    # Nome gerado por nós: evita colisões e ignora o nome enviado pelo cliente.
    pasta = PASTA_UPLOADS / str(usuario.id)
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{uuid.uuid4().hex}{extensao}"
    caminho = pasta / nome
    caminho.write_bytes(conteudo)

    documento = Documento(
        usuario_id=usuario.id,
        arquivo=f"{usuario.id}/{nome}",
        status=StatusDocumento.pendente,
    )
    db.add(documento)
    try:
        db.commit()
    except Exception:
        # Se o banco falhar, não deixa um arquivo órfão no disco.
        db.rollback()
        caminho.unlink(missing_ok=True)
        raise
    db.refresh(documento)
    return documento


@router.get("", response_model=list[DocumentoSaida])
def listar(
    usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)
):
    """Lista os documentos do usuário logado, do mais novo para o mais antigo."""
    consulta = (
        select(Documento)
        .where(Documento.usuario_id == usuario.id)
        .order_by(Documento.criado_em.desc())
    )
    return list(db.scalars(consulta))


@router.get("/{documento_id}", response_model=DocumentoSaida)
def obter(
    documento_id: int,
    usuario: Usuario = Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    return buscar_documento(documento_id, usuario, db)


@router.post("/{documento_id}/processar", response_model=LancamentoSaida)
def processar(
    documento_id: int,
    usuario: Usuario = Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    """Lê o comprovante com IA e salva os dados extraídos para revisão."""
    documento = buscar_documento(documento_id, usuario, db)

    if documento.status != StatusDocumento.pendente:
        raise HTTPException(status.HTTP_409_CONFLICT, "Este documento já foi processado")

    caminho = PASTA_UPLOADS / documento.arquivo
    if not caminho.is_file():
        raise HTTPException(status.HTTP_410_GONE, "Arquivo não encontrado no servidor")

    try:
        dados = ia.extrair_dados(
            caminho.read_bytes(), MIME_POR_EXTENSAO[caminho.suffix.lower()]
        )
    except ia.ErroIA as erro:
        if erro.limite_excedido:
            codigo = status.HTTP_429_TOO_MANY_REQUESTS
        elif erro.indisponivel:
            codigo = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            codigo = status.HTTP_502_BAD_GATEWAY
        raise HTTPException(codigo, str(erro))

    # A IA pode errar: garantimos que a confiança fique entre 0 e 1.
    confianca = min(max(dados.confianca, 0.0), 1.0)

    lancamento = Lancamento(
        documento_id=documento.id,
        fornecedor=dados.fornecedor,
        valor=Decimal(str(round(dados.valor, 2))) if dados.valor is not None else None,
        data=dados.data,
        categoria=dados.categoria,
        confianca=Decimal(str(round(confianca, 3))),
        revisado=False,
    )
    documento.status = StatusDocumento.processado
    db.add(lancamento)
    db.commit()
    db.refresh(lancamento)
    return lancamento


@router.get("/{documento_id}/lancamentos", response_model=list[LancamentoSaida])
def listar_lancamentos(
    documento_id: int,
    usuario: Usuario = Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    return buscar_documento(documento_id, usuario, db).lancamentos