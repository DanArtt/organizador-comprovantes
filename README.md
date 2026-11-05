# Organizador de Comprovantes

Envie a foto ou o PDF de um comprovante: a IA extrai fornecedor, valor, data e
categoria, e você confere antes de salvar. Um painel mostra seus gastos.

> Em construção. Estrutura inicial do back-end e do banco de dados.

## Como rodar (back-end)

Pré-requisitos: Python 3.11+ e Docker.

```bash
# 1. Banco de dados
docker compose up -d

# 2. Back-end
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

- Documentação interativa da API: http://localhost:8000/docs
- Teste de saúde: http://localhost:8000/saude

## Modelo de dados

- `usuarios`: quem usa o app
- `documentos`: cada arquivo enviado, com status (pendente, processado, revisado)
- `lancamentos`: dados extraídos pela IA, com nível de confiança e marcação de revisão