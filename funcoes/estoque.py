"""Consultas de estoque e alertas (somente leitura)."""
from banco.conexao import transacao


def _consultar(sql):
    with transacao() as cur:
        cur.execute(sql)
        return cur.fetchall()


def listar_alertas():
    """Vencidos, perto de vencer (7 dias) ou com estoque baixo (view alerta_estoque)."""
    return _consultar("SELECT * FROM alerta_estoque")


def resumo_estoque():
    """Devolve (produtos cadastrados, próximos do vencimento, vencidos)."""
    return _consultar("""
        SELECT
            (SELECT COUNT(*) FROM produto),
            (SELECT COUNT(*) FROM produto
              WHERE data_validade >= CURDATE()
                AND DATEDIFF(data_validade, CURDATE()) <= 7),
            (SELECT COUNT(*) FROM produto WHERE data_validade < CURDATE())
    """)[0]


def listar_estoque():
    """Devolve (produto, lote, validade, quantidade, mínimo, local, atualizado em)."""
    return _consultar("""
        SELECT p.nome, e.lote, p.data_validade, e.quantidade_atual,
               e.quantidade_minima, e.localizacao, e.data_atualizacao
        FROM estoque e
        JOIN produto p ON p.id_produto = e.id_produto
        ORDER BY p.nome
    """)
