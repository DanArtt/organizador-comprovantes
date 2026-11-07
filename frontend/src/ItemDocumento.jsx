import { CATEGORIAS } from "./categorias";

const ROTULOS = {
  pendente: "Aguardando leitura",
  processado: "Para revisar",
  revisado: "Revisado",
};

// A API manda a data como "2026-11-05"; trocamos de lugar as partes
// em vez de usar Date, para o fuso horário não mudar o dia.
function formatarData(texto) {
  const [ano, mes, dia] = texto.split("-");
  return `${dia}/${mes}/${ano}`;
}

function formatarValor(valor) {
  return Number(valor).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

export default function ItemDocumento({
  documento,
  lancamentos,
  lendo,
  bloqueado,
  aoLer,
}) {
  const enviadoEm = new Date(documento.criado_em).toLocaleString("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  });

  return (
    <li className="item">
      <div className="item-topo">
        <div>
          <p className="item-titulo">Comprovante nº {documento.id}</p>
          <p className="item-data">Enviado em {enviadoEm}</p>
        </div>
        <span className={`selo selo-${documento.status}`}>
          {ROTULOS[documento.status]}
        </span>
      </div>

      {lancamentos.map((l) => (
        <dl className="dados" key={l.id}>
          <dt>Fornecedor</dt>
          <dd>{l.fornecedor ?? "Não identificado"}</dd>
          <dt>Valor</dt>
          <dd>{l.valor !== null ? formatarValor(l.valor) : "Não identificado"}</dd>
          <dt>Data</dt>
          <dd>{l.data ? formatarData(l.data) : "Não identificada"}</dd>
          <dt>Categoria</dt>
          <dd>{CATEGORIAS[l.categoria] ?? "Sem categoria"}</dd>
          <dt>Confiança da IA</dt>
          <dd>{Math.round(Number(l.confianca) * 100)}%</dd>
        </dl>
      ))}

      {documento.status === "pendente" && (
        <div className="item-acao">
          <button
            type="button"
            className="botao"
            onClick={aoLer}
            disabled={bloqueado}
          >
            {lendo ? "Lendo…" : "Ler com IA"}
          </button>
          {lendo && <p className="apoio">A leitura pode levar até 2 minutos.</p>}
        </div>
      )}
    </li>
  );
}