export default function Painel({ usuario, aoSair }) {
  return (
    <div className="painel">
      <header className="painel-topo">
        <p className="painel-nome">{usuario.nome}</p>
        <button type="button" className="botao botao-claro" onClick={aoSair}>
          Sair
        </button>
      </header>

      <main className="painel-vazio">
        <h1>Nenhum comprovante por aqui ainda</h1>
        <p>
          O envio de comprovantes chega no próximo passo. Por enquanto, sua
          conta já está conectada à API.
        </p>
      </main>
    </div>
  );
}