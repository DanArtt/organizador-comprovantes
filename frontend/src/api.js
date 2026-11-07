// Tudo o que fala com o back-end fica neste arquivo.

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const CHAVE_TOKEN = "token";

export const guardarToken = (token) => localStorage.setItem(CHAVE_TOKEN, token);
export const lerToken = () => localStorage.getItem(CHAVE_TOKEN);
export const limparToken = () => localStorage.removeItem(CHAVE_TOKEN);

export class ErroApi extends Error {
  constructor(mensagem, status) {
    super(mensagem);
    this.status = status;
  }
}

async function requisicao(caminho, opcoes = {}) {
  const headers = { ...opcoes.headers };
  const token = lerToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let resposta;
  try {
    resposta = await fetch(`${BASE}${caminho}`, { ...opcoes, headers });
  } catch {
    throw new ErroApi(
      "Não foi possível falar com o servidor. Confira se a API está rodando.",
      0,
    );
  }

  if (!resposta.ok) {
    let detalhe = "Algo deu errado. Tente de novo.";
    try {
      const corpo = await resposta.json();
      if (typeof corpo.detail === "string") detalhe = corpo.detail;
      else if (Array.isArray(corpo.detail)) detalhe = "Confira os campos preenchidos.";
    } catch {
      // resposta sem JSON: fica a mensagem padrão
    }
    throw new ErroApi(detalhe, resposta.status);
  }
  return resposta.json();
}

export function cadastrar({ nome, email, senha }) {
  return requisicao("/auth/cadastro", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome, email, senha }),
  });
}

// A rota de login segue o padrão OAuth2: recebe formulário, e o e-mail vai no
// campo "username".
export async function entrar(email, senha) {
  const corpo = new URLSearchParams({ username: email, password: senha });
  const { access_token } = await requisicao("/auth/login", {
    method: "POST",
    body: corpo,
  });
  guardarToken(access_token);
}

export const usuarioAtual = () => requisicao("/auth/eu");