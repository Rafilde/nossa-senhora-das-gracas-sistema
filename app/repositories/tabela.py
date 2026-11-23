import time
import threading
import uuid
from .sheets import get_planilha

CACHE_SEGUNDOS = 30
_cache = {}                  # nome da aba -> (momento, valores)
_trava = threading.Lock()


def gerar_id():
    return uuid.uuid4().hex[:8]


class Tabela:
    def __init__(self, nome):
        self.nome = nome

    @property
    def _ws(self):
        return get_planilha().worksheet(self.nome)

    # ---------- cache ----------
    def _valores(self, usar_cache=True):
        agora = time.time()
        if usar_cache:
            with _trava:
                item = _cache.get(self.nome)
                if item and agora - item[0] < CACHE_SEGUNDOS:
                    return item[1]
        valores = self._ws.get_all_values()
        with _trava:
            _cache[self.nome] = (agora, valores)
        return valores

    def _invalidar(self):
        with _trava:
            _cache.pop(self.nome, None)

    # ---------- leitura interna ----------
    def _ler(self, usar_cache=True):
        """Devolve (cabecalho, [(numero_da_linha, dict), ...])."""
        valores = self._valores(usar_cache)
        cabecalho = valores[0]
        linhas = []
        for numero, linha in enumerate(valores[1:], start=2):
            if not any(linha):
                continue
            linha = linha + [""] * (len(cabecalho) - len(linha))
            linhas.append((numero, dict(zip(cabecalho, linha))))
        return cabecalho, linhas

    @staticmethod
    def _confere(registro, filtros):
        return all(registro.get(c) == str(v) for c, v in filtros.items())

    # ---------- leitura (usa cache) ----------
    def listar(self):
        return [r for _, r in self._ler()[1]]

    def filtrar(self, **filtros):
        return [r for _, r in self._ler()[1] if self._confere(r, filtros)]

    def buscar(self, **filtros):
        encontrados = self.filtrar(**filtros)
        return encontrados[0] if encontrados else None

    # ---------- escrita (nunca usa cache para achar linhas) ----------
    def inserir(self, dados):
        ws = self._ws
        cabecalho = ws.row_values(1)
        dados = dict(dados)
        if "id" in cabecalho and not dados.get("id"):
            dados["id"] = gerar_id()
        linha = [str(dados.get(c, "")) for c in cabecalho]
        ws.append_row(linha, value_input_option="RAW")
        self._invalidar()
        return dados

    def atualizar(self, filtros, novos_dados):
        """Atualiza a primeira linha que bate com os filtros."""
        cabecalho, linhas = self._ler(usar_cache=False)
        for numero, registro in linhas:
            if self._confere(registro, filtros):
                registro.update({k: str(v) for k, v in novos_dados.items()})
                linha = [registro.get(c, "") for c in cabecalho]
                self._ws.update(
                    range_name=f"A{numero}",
                    values=[linha],
                    value_input_option="RAW",
                )
                self._invalidar()
                return registro
        return None

    def salvar_lote(self, campos_chave, registros):
        """Atualiza as linhas que já existem (mesma chave) e insere as novas.
        Devolve (quantos_atualizados, quantos_novos)."""
        ws = self._ws
        cabecalho, linhas = self._ler(usar_cache=False)
        indice = {tuple(r[c] for c in campos_chave): n for n, r in linhas}

        atualizacoes, novas = [], []
        for reg in registros:
            reg = {k: str(v) for k, v in reg.items()}
            chave = tuple(reg[c] for c in campos_chave)
            linha = [reg.get(c, "") for c in cabecalho]
            if chave in indice:
                atualizacoes.append({"range": f"A{indice[chave]}", "values": [linha]})
            else:
                novas.append(linha)

        if atualizacoes:
            ws.batch_update(atualizacoes, value_input_option="RAW")
        if novas:
            ws.append_rows(novas, value_input_option="RAW")
        self._invalidar()
        return len(atualizacoes), len(novas)

    def apagar(self, **filtros):
        """Apaga todas as linhas que batem. Devolve quantas apagou."""
        ws = self._ws
        numeros = [
            n for n, r in self._ler(usar_cache=False)[1]
            if self._confere(r, filtros)
        ]
        for n in sorted(numeros, reverse=True):
            ws.delete_rows(n)
        self._invalidar()
        return len(numeros)

    def apagar_tudo(self):
        """Limpa os dados e mantém o cabeçalho."""
        self._ws.batch_clear(["A2:Z"])
        self._invalidar()