import { useEffect, useState } from "react";
import { lerToken, limparToken, usuarioAtual } from "./api";
import Entrada from "./Entrada";
import Painel from "./Painel";

export default function App() {
  const [usuario, setUsuario] = useState(null);
  // Se há token guardado, primeiro confirmamos com a API que ele ainda vale.
  const [carregando, setCarregando] = useState(Boolean(lerToken()));

  useEffect(() => {
    if (!lerToken()) return;
    usuarioAtual()
      .then(setUsuario)
      .catch(() => limparToken()) // token vencido ou inválido: volta ao login
      .finally(() => setCarregando(false));
  }, []);

  function sair() {
    limparToken();
    setUsuario(null);
  }

  if (carregando) return <p className="carregando">Carregando…</p>;

  return usuario ? (
    <Painel usuario={usuario} aoSair={sair} />
  ) : (
    <Entrada aoEntrar={setUsuario} />
  );
}