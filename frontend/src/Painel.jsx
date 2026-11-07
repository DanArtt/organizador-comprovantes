import { useCallback, useEffect, useRef, useState } from "react";
import {
  enviarDocumento,
  listarDocumentos,
  listarLancamentos,
  processarDocumento,
} from "./api";
import ItemDocumento from "./ItemDocumento";

export default function Painel({ usuario, aoSair }) {
  const [documentos, setDocumentos] = useState([]);
  const [lancamentos, setLancamentos] = useState({}); // id do documento -> lançamentos
  const [carregando, setCarregando] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [lendo, setLendo] = useState(null); // id do documento em leitura
  const [erro, setErro] = useState("");
  const campoArquivo = useRef(null);

  const carregar = useCallback(async () => {
    try {
      const docs = await listarDocumentos();
      const lidos = docs.filter((d) => d.status !== "pendente");
      const listas = await Promise.all(lidos.map((d) => listarLancamentos(d.id)));
      setDocumentos(docs);
      setLancamentos(Object.fromEntries(lidos.map((d, i) => [d.id, listas[i]])));
    } catch (e) {
      setErro(e.message);
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  async function enviar(evento) {
    evento.preventDefault();
    const arquivo = campoArquivo.current?.files[0];
    if (!arquivo) {
      setErro("Escolha um arquivo JPG, PNG ou PDF.");
      return;
    }
    setErro("");
    setEnviando(true);
    try {
      await enviarDocumento(arquivo);
      campoArquivo.current.value = "";
      await carregar();
    } catch (e) {
      setErro(e.message);
    } finally {
      setEnviando(false);
    }
  }

  async function ler(id) {
    setErro("");
    setLendo(id);
    try {
      await processarDocumento(id);
      await carregar();
    } catch (e) {
      setErro(e.message);
    } finally {
      setLendo(null);
    }
  }

  return (
    <div className="painel">
      <header className="painel-topo">
        <p className="painel-nome">{usuario.nome}</p>
        <button type="button" className="botao botao-claro" onClick={aoSair}>
          Sair
        </button>
      </header>

      <main>
        <section className="envio" aria-labelledby="titulo-envio">
          <h1 id="titulo-envio">Enviar comprovante</h1>
          <form className="envio-form" onSubmit={enviar}>
            <input
              ref={campoArquivo}
              type="file"
              accept="image/jpeg,image/png,application/pdf"
              aria-label="Arquivo do comprovante"
            />
            <button className="botao" type="submit" disabled={enviando}>
              {enviando ? "Enviando…" : "Enviar"}
            </button>
          </form>
          <p className="apoio">
            JPG, PNG ou PDF, até 5 MB. Use apenas comprovantes de teste, sem
            dados reais.
          </p>
        </section>

        {erro && (
          <p className="erro" role="alert">
            {erro}
          </p>
        )}

        <section aria-labelledby="titulo-lista">
          <h2 id="titulo-lista">Seus comprovantes</h2>
          {carregando ? (
            <p className="apoio">Carregando…</p>
          ) : documentos.length === 0 ? (
            <p className="apoio">Nenhum comprovante ainda. Envie o primeiro acima.</p>
          ) : (
            <ul className="lista">
              {documentos.map((d) => (
                <ItemDocumento
                  key={d.id}
                  documento={d}
                  lancamentos={lancamentos[d.id] ?? []}
                  lendo={lendo === d.id}
                  bloqueado={lendo !== null}
                  aoLer={() => ler(d.id)}
                />
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}