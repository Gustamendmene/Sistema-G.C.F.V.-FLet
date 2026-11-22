"""Categorias de produto: lista que o usuário mantém.

A tabela `categoria` guarda as categorias criadas à mão (mesmo sem produto).
A listagem junta essa tabela com as categorias que já aparecem nos produtos,
então nada que já foi cadastrado se perde.
"""
from banco.conexao import transacao
from utils.textos import chave_de_busca
from utils.validacao import validar_nome_categoria

_tabela_pronta = False


def _garantir_tabela(cur):
    """Cria a tabela na primeira vez (não faz nada se ela já existir)."""
    global _tabela_pronta
    if _tabela_pronta:
        return
    cur.execute(
        """CREATE TABLE IF NOT EXISTS categoria (
               id_categoria INT NOT NULL AUTO_INCREMENT,
               nome VARCHAR(50) NOT NULL,
               PRIMARY KEY (id_categoria),
               UNIQUE KEY nome (nome)
           ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
             COLLATE=utf8mb4_0900_ai_ci"""
    )
    _tabela_pronta = True


def listar_categorias():
    """Nomes das categorias em ordem alfabética (sem acento nem maiúscula)."""
    with transacao() as cur:
        _garantir_tabela(cur)
        cur.execute(
            """SELECT nome FROM categoria
               UNION
               SELECT DISTINCT categoria FROM produto
               WHERE categoria IS NOT NULL AND categoria <> ''"""
        )
        return sorted((linha[0] for linha in cur.fetchall()),
                      key=chave_de_busca)


def criar_categoria(nome):
    """Cadastra a categoria e devolve o nome como ficou gravado.

    Se já existir uma igual (ignorando maiúsculas e acentos), devolve a
    existente. Levanta ErroValidacao se o nome for inválido.
    """
    nome = validar_nome_categoria(nome)
    with transacao() as cur:
        _garantir_tabela(cur)
        cur.execute("INSERT IGNORE INTO categoria (nome) VALUES (%s)", (nome,))
        cur.execute("SELECT nome FROM categoria WHERE nome = %s", (nome,))
        return cur.fetchone()[0]
