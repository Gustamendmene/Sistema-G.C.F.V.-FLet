"""Máscaras de digitação para os campos do formulário."""


def somente_digitos(texto, limite=None):
    """Mantém só os números (e corta no limite, se houver)."""
    digitos = "".join(c for c in (texto or "") if c.isdigit())
    return digitos if limite is None else digitos[:limite]


def mascara_data(novo, anterior=""):
    """Formata dd/mm/aaaa enquanto a pessoa digita.

    A barra entra sozinha depois do dia (2 dígitos) e do mês (4 dígitos).
    Quando a pessoa está apagando (texto ficou menor que antes), a barra do
    final NÃO é recolocada; senão seria impossível apagá-la com o backspace.
    """
    digitos = somente_digitos(novo, 8)
    partes = [p for p in (digitos[:2], digitos[2:4], digitos[4:8]) if p]
    texto = "/".join(partes)
    apagando = len(novo or "") < len(anterior or "")
    if not apagando and len(digitos) in (2, 4):
        texto += "/"
    return texto
