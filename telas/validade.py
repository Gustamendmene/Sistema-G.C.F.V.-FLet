"""Controle de validade: todos os alertas, do mais grave ao menos grave."""
from componentes.listagem import tela_lista
from componentes.ui import etiqueta
from funcoes.alertas import invalidar_cache, obter_alertas
from tema import CORES_ALERTA, PRETO
from utils.datas import formatar_data


def _linhas():
    invalidar_cache()  # o contador do sino também será atualizado
    return [
        (a.id_produto, a.nome, formatar_data(a.validade), a.prazo,
         a.quantidade, a.minimo,
         etiqueta(a.tipo, CORES_ALERTA.get(a.tipo, PRETO)))
        for a in obter_alertas()
    ]


def criar_tela(page, navegar):
    return tela_lista(
        page, navegar,
        "Controle de validade",
        "Produtos vencidos, que vencem em até 7 dias ou com estoque baixo.",
        ["ID", "Produto", "Validade", "Prazo", "Quantidade", "Mínimo",
         "Alerta"],
        _linhas,
        "Nenhum alerta no momento. Tudo dentro da validade e do estoque "
        "mínimo.",
    )
