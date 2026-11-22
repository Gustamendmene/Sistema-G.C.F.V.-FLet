"""Pequenas funções para tratar textos digitados."""
import unicodedata


def normalizar_espacos(texto):
    """Tira espaços das pontas e troca sequências de espaços por um só."""
    return " ".join((texto or "").split())


def chave_de_busca(texto):
    """Texto sem acento e sem diferença de maiúsculas, para pesquisar e ordenar.

    'Água' e 'agua' viram a mesma chave.
    """
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", texto or "")
        if not unicodedata.combining(c))
    return normalizar_espacos(sem_acento).casefold()
