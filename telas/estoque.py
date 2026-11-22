"""Tela de estoque (somente consulta): quantidade, lote, validade e local."""
from componentes.listagem import tela_lista
from componentes.ui import etiqueta
from funcoes.estoque import listar_estoque
from tema import LARANJA, VERDE
from utils.datas import formatar_data


def _linhas():
    linhas = []
    for nome, lote, validade, qtd, minimo, local, atualizado in listar_estoque():
        situacao = (etiqueta("ESTOQUE BAIXO", LARANJA) if qtd <= minimo
                    else etiqueta("OK", VERDE))
        linhas.append((nome, lote or "-", formatar_data(validade), qtd,
                       minimo, situacao, local or "-",
                       formatar_data(atualizado)))
    return linhas


def criar_tela(page, navegar):
    return tela_lista(
        page, navegar,
        "Estoque",
        "Quantidade, lote, validade e local de cada produto.",
        ["Produto", "Lote", "Validade", "Quantidade", "Mínimo", "Situação",
         "Local", "Atualizado em"],
        _linhas,
        "O estoque está vazio. Cadastre um produto na tela Produtos.",
    )
