"""Regras dos alertas de validade e estoque (sem interface).

Os dados vêm da view `alerta_estoque` do MySQL (funcoes/estoque.py). Aqui viram
objetos `Alerta`, ordenados por gravidade, e ficam num cache curto para o sino
do cabeçalho não consultar o banco a cada clique.
"""
import time
from dataclasses import dataclass

from funcoes.estoque import listar_alertas
from utils.erros import mensagem_amigavel, registrar_erro

# Tipos devolvidos pela view alerta_estoque, do mais grave ao menos grave
VENCIDO = "VENCIDO"
PROXIMO = "PRÓXIMO DO VENCIMENTO"
BAIXO = "ESTOQUE BAIXO"
_GRAVIDADE = {VENCIDO: 0, PROXIMO: 1, BAIXO: 2}

SEGUNDOS_EM_CACHE = 30


@dataclass(frozen=True)
class Alerta:
    """Uma linha da view alerta_estoque (os campos seguem a ordem das colunas)."""
    id_produto: int
    nome: str
    validade: object
    dias: int          # negativo = já venceu
    quantidade: int
    minimo: int
    tipo: str

    @property
    def prazo(self):
        if self.dias < 0:
            return f"venceu há {-self.dias} dia(s)"
        if self.dias == 0:
            return "vence hoje"
        if self.dias == 1:
            return "vence amanhã"
        return f"vence em {self.dias} dias"

    @property
    def descricao(self):
        if self.tipo == BAIXO:
            return (f"{self.nome}: estoque baixo "
                    f"({self.quantidade} em estoque, mínimo {self.minimo})")
        return f"{self.nome}: {self.prazo}"


@dataclass
class ResultadoAlertas:
    alertas: list
    erro: str = ""   # mensagem amigável se o banco falhou

    def por_tipo(self, tipo):
        return [a for a in self.alertas if a.tipo == tipo]


def obter_alertas():
    """Consulta o banco; vencidos primeiro e, dentro de cada tipo, o prazo mais curto."""
    alertas = [Alerta(*linha) for linha in listar_alertas()]
    alertas.sort(key=lambda a: (_GRAVIDADE.get(a.tipo, 9), a.dias, a.nome))
    return alertas


_cache = {"quando": 0.0, "resultado": None}


def carregar_alertas(forcar=False):
    """Devolve um ResultadoAlertas (nunca levanta exceção).

    Usa o cache por 30 s, a menos que `forcar=True`. Se o banco falhar, o erro
    é gravado no log e vem em `resultado.erro` (e também fica em cache, para
    não travar cada tela esperando o MySQL desligado).
    """
    agora = time.monotonic()
    em_cache = _cache["resultado"]
    if (not forcar and em_cache is not None
            and agora - _cache["quando"] < SEGUNDOS_EM_CACHE):
        return em_cache
    try:
        resultado = ResultadoAlertas(obter_alertas())
    except Exception as erro:
        registrar_erro(erro, "carregar alertas")
        resultado = ResultadoAlertas([], mensagem_amigavel(erro))
    _cache["quando"] = time.monotonic()
    _cache["resultado"] = resultado
    return resultado


def invalidar_cache():
    """Chame depois de cadastrar, editar ou excluir produtos."""
    _cache["resultado"] = None
