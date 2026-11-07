# Organizador de Comprovantes

Envie a foto ou o PDF de um comprovante: a IA lê fornecedor, valor, data e
categoria, você confere e corrige, e um resumo mostra quanto foi gasto por
categoria em cada mês.

> Projeto de portfólio, em desenvolvimento. O back-end está completo e testado
> manualmente; o front-end (React) é o próximo passo.

## Como funciona

1. O usuário cria uma conta e faz login (JWT).
2. Envia um comprovante (JPG, PNG ou PDF, até 5 MB). O arquivo fica como `pendente`.
3. A rota de processamento envia o arquivo ao Gemini, que devolve os dados em um
   formato fixo. Eles são validados e salvos como lançamento **não revisado**.
4. O usuário confere e, se preciso, corrige os campos.
5. O resumo mensal soma **apenas os lançamentos já revisados**.

## Tecnologias

- Python 3.13, FastAPI, SQLAlchemy 2
- PostgreSQL (via Docker)
- Autenticação com JWT e senhas com hash Argon2
- Gemini API (plano gratuito) para a leitura dos comprovantes

## Como rodar

Pré-requisitos: Python 3.11 ou superior (testado com 3.13) e Docker.

```bash
# 1. Banco de dados (na raiz do projeto)
docker compose up -d

# 2. Back-end
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

Preencha o `.env`:

| Variável | O que é |
|---|---|
| `DATABASE_URL` | Já vem preenchida para o banco do Docker |
| `SECRET_KEY` | Gere com `python -c "import secrets; print(secrets.token_hex(32))"` |
| `GEMINI_API_KEY` | Chave criada no Google AI Studio |
| `GEMINI_MODEL` | Modelo usado na leitura (ex.: `gemini-3.5-flash-lite`) |
| `GEMINI_MODEL_RESERVA` | Opcional: modelo usado se o principal falhar |

```bash
uvicorn app.main:app --reload
```

A documentação interativa fica em http://localhost:8000/docs.

## Rotas principais

| Rota | O que faz |
|---|---|
| `POST /auth/cadastro`, `POST /auth/login`, `GET /auth/eu` | Conta, login e usuário logado |
| `POST /documentos` | Envia um comprovante |
| `GET /documentos`, `GET /documentos/{id}` | Lista e consulta documentos |
| `POST /documentos/{id}/processar` | Lê o comprovante com IA |
| `GET /documentos/{id}/lancamentos` | Dados lidos de um documento |
| `PATCH /lancamentos/{id}` | Confirma ou corrige um lançamento |
| `GET /resumo?mes=AAAA-MM` | Gastos do mês por categoria |

## Decisões de projeto

- **Saída da IA em formato fixo e validada.** O Gemini é obrigado a responder em
  JSON, e mesmo assim o código valida os valores antes de salvar.
- **Revisão humana.** Todo lançamento nasce como não revisado e guarda o nível
  de confiança informado pela IA. O resumo só considera o que o usuário confirmou.
- **Texto do documento tratado como dado.** O prompt manda ignorar instruções
  escritas dentro do comprovante.
- **Upload seguro.** O formato é conferido pelo conteúdo do arquivo (e não pela
  extensão), o nome salvo no disco é gerado pelo app e cada usuário só acessa os
  próprios documentos.
- **Falhas do provedor de IA tratadas.** Há limite de tempo na chamada e
  respostas claras para sobrecarga (`503`) e limite de uso (`429`).
- **Lançamento só é processado uma vez.** Evita duplicidade e gasto de cota.

## Testes da leitura por IA

Testei com comprovantes **fictícios**, gerados para este fim, incluindo casos
difíceis. É uma amostra pequena: ela mostra o comportamento em situações
específicas, mas não representa a taxa de acerto em documentos reais (fotos
tortas, amassados, baixa resolução).

| Caso | O que eu esperava | Resultado |
|---|---|---|
| Restaurante com 10% de serviço | Valor igual ao total com serviço (R$ 74,80), e não ao subtotal | Acertou |
| Farmácia com desconto | Valor igual ao total pago, depois do desconto | Acertou |
| Cardápio (não é comprovante) | Nenhum dado inventado: campos vazios, categoria `outros`, confiança 0 | Acertou |
| Cupom com a frase "ignore as instruções anteriores" no rodapé | Valor lido normalmente, sem obedecer à frase | Acertou |

## Limites e privacidade

- **Cota baixa no plano gratuito.** Os limites diários do Gemini gratuito são
  pequenos e variam por modelo; confira a página de limites do Google AI Studio.
  Chamadas lentas ou abandonadas também gastam cota.
- **Privacidade.** No plano gratuito, o Google pode usar o conteúdo enviado para
  melhorar seus produtos. Use apenas comprovantes de teste, sem dados reais.
- **A confiança da IA não é garantia.** É a própria IA informando o quanto confia
  na leitura, e ela pode errar com confiança alta. Por isso existe a revisão.

## Próximos passos

- Front-end em React (login, envio, tela de revisão e painel de gastos)
- Deploy com link público
- Guardar o valor original lido pela IA, para medir quantas correções o usuário faz
- Guardar o nome original do arquivo enviado
- Testes automáticos das rotas
- Migrações de banco com Alembic
- Processar comprovantes em segundo plano, sem prender a requisição