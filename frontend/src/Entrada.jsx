import { useState } from "react";
import { cadastrar, entrar, usuarioAtual } from "./api";

export default function Entrada({ aoEntrar }) {
  const [modo, setModo] = useState("entrar"); // "entrar" ou "criar"
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  const criando = modo === "criar";

  function trocarModo() {
    setModo(criando ? "entrar" : "criar");
    setErro("");
  }

  async function enviar(evento) {
    evento.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      if (criando) await cadastrar({ nome, email, senha });
      await entrar(email, senha);
      aoEntrar(await usuarioAtual());
    } catch (e) {
      setErro(e.message);
      setEnviando(false);
    }
  }

  return (
    <div className="entrada">
      <main className="formulario">
        <h1>{criando ? "Criar conta" : "Entrar"}</h1>
        <p className="apoio">
          Envie comprovantes, confira os dados lidos pela IA e veja quanto você
          gastou em cada mês.
        </p>

        <form className="campos" onSubmit={enviar}>
          {criando && (
            <div className="campo">
              <label htmlFor="nome">Nome</label>
              <input
                id="nome"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                autoComplete="name"
                minLength={2}
                required
              />
            </div>
          )}

          <div className="campo">
            <label htmlFor="email">E-mail</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </div>

          <div className="campo">
            <label htmlFor="senha">
              {criando ? "Senha (mínimo de 8 caracteres)" : "Senha"}
            </label>
            <input
              id="senha"
              type="password"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              autoComplete={criando ? "new-password" : "current-password"}
              minLength={criando ? 8 : undefined}
              required
            />
          </div>

          {erro && (
            <p className="erro" role="alert">
              {erro}
            </p>
          )}

          <button className="botao" type="submit" disabled={enviando}>
            {enviando ? "Aguarde…" : criando ? "Criar conta" : "Entrar"}
          </button>
        </form>

        <p className="trocar">
          {criando ? "Já tem conta? " : "Ainda não tem conta? "}
          <button type="button" className="link" onClick={trocarModo}>
            {criando ? "Entrar" : "Criar conta"}
          </button>
        </p>
      </main>

      <aside className="comprovante" aria-hidden="true">
        <h2>Padaria Esquina Doce</h2>
        <p className="exemplo">Exemplo de leitura</p>
        <dl>
          <dt>Valor</dt>
          <dd>R$ 18,90</dd>
          <dt>Data</dt>
          <dd>05/11/2026</dd>
          <dt>Categoria</dt>
          <dd>Alimentação</dd>
        </dl>
        <span className="selo">Para revisar</span>
      </aside>
    </div>
  );
}