"""CRUD de produtos (acesso ao banco). Nada aqui conhece a interface.

`dados` é o dicionário devolvido por utils.validacao.validar_produto().
"""
from banco.conexao import transacao


def inserir_produto(dados):
    """Cadastra o produto e já cria a linha dele no estoque. Devolve o id novo."""
    with transacao() as cur:
        cur.execute(
            """INSERT INTO produto (nome, categoria, marca, codigo_barras,
                   fornecedor, preco_custo, preco_venda, data_entrega,
                   data_validade)
               VALUES (%(nome)s, %(categoria)s, %(marca)s, %(codigo_barras)s,
                   %(fornecedor)s, %(preco_custo)s, %(preco_venda)s,
                   %(data_entrega)s, %(data_validade)s)""",
            dados,
        )
        id_produto = cur.lastrowid
        cur.execute(
            """INSERT INTO estoque (id_produto, quantidade_atual,
                   quantidade_minima, lote, localizacao)
               VALUES (%(id_produto)s, %(quantidade)s, %(quantidade_minima)s,
                   %(lote)s, %(localizacao)s)""",
            {**dados, "id_produto": id_produto},
        )
        return id_produto


def buscar_produto(id_produto):
    """Dados completos de um produto (dict) ou None se não existir."""
    with transacao(dicionario=True) as cur:
        cur.execute(
            """SELECT p.id_produto, p.nome, p.categoria, p.marca,
                      p.codigo_barras, p.fornecedor, p.preco_custo,
                      p.preco_venda, p.data_entrega, p.data_validade,
                      e.quantidade_atual, e.quantidade_minima,
                      e.lote, e.localizacao
               FROM produto p JOIN estoque e ON e.id_produto = p.id_produto
               WHERE p.id_produto = %s""",
            (id_produto,),
        )
        return cur.fetchone()


def atualizar_produto(id_produto, dados):
    """Atualiza produto e estoque na mesma transação."""
    parametros = {**dados, "id_produto": id_produto}
    with transacao() as cur:
        cur.execute(
            """UPDATE produto SET nome=%(nome)s, categoria=%(categoria)s,
                   marca=%(marca)s, codigo_barras=%(codigo_barras)s,
                   fornecedor=%(fornecedor)s, preco_custo=%(preco_custo)s,
                   preco_venda=%(preco_venda)s, data_entrega=%(data_entrega)s,
                   data_validade=%(data_validade)s
               WHERE id_produto=%(id_produto)s""",
            parametros,
        )
        cur.execute(
            """UPDATE estoque SET quantidade_atual=%(quantidade)s,
                   quantidade_minima=%(quantidade_minima)s, lote=%(lote)s,
                   localizacao=%(localizacao)s
               WHERE id_produto=%(id_produto)s""",
            parametros,
        )


def deletar_produto(id_produto):
    """Apaga o produto (o estoque some junto, por ON DELETE CASCADE).

    Devolve quantas linhas foram apagadas (0 = o produto já não existia).
    """
    with transacao() as cur:
        cur.execute("DELETE FROM produto WHERE id_produto = %s", (id_produto,))
        return cur.rowcount


def listar_produtos():
    """Lista para a tabela da tela (cada linha é um dict)."""
    with transacao(dicionario=True) as cur:
        cur.execute(
            """SELECT p.id_produto, p.nome, p.categoria, p.data_validade,
                      e.quantidade_atual, e.localizacao
               FROM produto p JOIN estoque e ON e.id_produto = p.id_produto
               ORDER BY p.nome"""
        )
        return cur.fetchall()
