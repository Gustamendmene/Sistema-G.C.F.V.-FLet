"""Validação dos campos do formulário de produto, antes de ir ao banco.

Os limites de tamanho seguem as colunas do banco (CREATE TABLE do mercado).
"""
import re
from decimal import Decimal, InvalidOperation

from utils.datas import converter_data
from utils.erros import ErroValidacao
from utils.textos import normalizar_espacos

QUANTIDADE_MINIMA_PADRAO = 5

# Código de barras
TAMANHOS_GTIN = (8, 12, 13, 14)        # EAN-8, UPC-A, EAN-13, GTIN-14
VALIDAR_DIGITO_VERIFICADOR = True      # False = aceita qualquer número do tamanho certo

# Datas
ANO_MINIMO, ANO_MAXIMO = 2000, 2100

# Limites do banco
PRECO_MAXIMO = Decimal("99999999.99")  # DECIMAL(10,2)
INTEIRO_MAXIMO = 2_147_483_647         # INT
LIMITE_NOME = 100
LIMITE_CATEGORIA = 50
LIMITE_MARCA = 50
LIMITE_FORNECEDOR = 100
LIMITE_LOTE = 30
LIMITE_LOCALIZACAO = 50

# Além de letras, números e espaço, lote/localização aceitam estes símbolos
SIMBOLOS_PERMITIDOS = "-/.,#()ºª°"


# ---------- textos ----------

def _longo(sujeito):
    """'muito longo' ou 'muito longa', conforme o sujeito ('A marca', 'O nome')."""
    return "longa" if sujeito.startswith("A ") else "longo"


def _texto_com_letra(texto, sujeito, maximo, informe=None, minimo=1):
    """Texto cujo principal são letras (números só junto com elas).

    `informe`: se dado, o campo é obrigatório e esta é a mensagem quando vazio.
    """
    texto = normalizar_espacos(texto)
    if not texto:
        if informe:
            raise ErroValidacao(informe)
        return None
    if not any(c.isalpha() for c in texto):
        raise ErroValidacao(
            f"{sujeito} precisa ter pelo menos uma letra "
            "(números sozinhos não valem).")
    if len(texto) < minimo:
        raise ErroValidacao(
            f"{sujeito} precisa ter pelo menos {minimo} caracteres.")
    if len(texto) > maximo:
        raise ErroValidacao(
            f"{sujeito} está muito {_longo(sujeito)} "
            f"(máximo {maximo} caracteres).")
    return texto


def _texto_alfanumerico(texto, sujeito, maximo):
    """Lote/localização: letras e números livres, mais alguns símbolos."""
    texto = normalizar_espacos(texto)
    if not texto:
        return None
    for c in texto:
        if not (c.isalnum() or c == " " or c in SIMBOLOS_PERMITIDOS):
            raise ErroValidacao(
                f"{sujeito} tem um caractere não permitido: '{c}'. "
                "Use letras, números e - / . , # ( ).")
    if not any(c.isalnum() for c in texto):
        raise ErroValidacao(f"{sujeito} precisa ter letras ou números.")
    if len(texto) > maximo:
        raise ErroValidacao(
            f"{sujeito} está muito {_longo(sujeito)} "
            f"(máximo {maximo} caracteres).")
    return texto


def validar_nome_categoria(texto):
    """Nome de uma categoria nova: precisa de letra; 1ª letra maiúscula."""
    texto = _texto_com_letra(
        texto, "O nome da categoria", LIMITE_CATEGORIA,
        informe="Digite o nome da categoria.", minimo=2)
    return texto[0].upper() + texto[1:]


# ---------- código de barras ----------

def _digito_verificador(corpo):
    """Dígito verificador GTIN (EAN/UPC) a partir dos dígitos sem o último."""
    soma = 0
    for posicao, c in enumerate(reversed(corpo), start=1):
        soma += int(c) * (3 if posicao % 2 == 1 else 1)
    return (10 - soma % 10) % 10


def _codigo_barras(texto):
    bruto = (texto or "").strip()
    if not bruto:
        return None  # opcional (vazio vira NULL; o banco permite vários NULL)
    if re.search(r"[^\d\s.\-]", bruto):
        raise ErroValidacao("O código de barras deve ter apenas números.")
    digitos = re.sub(r"\D", "", bruto)
    if len(digitos) not in TAMANHOS_GTIN:
        raise ErroValidacao(
            f"Código de barras com {len(digitos)} dígitos. Use 8 (EAN-8), "
            "12 (UPC), 13 (EAN-13) ou 14 (GTIN-14).")
    if VALIDAR_DIGITO_VERIFICADOR:
        esperado = _digito_verificador(digitos[:-1])
        if int(digitos[-1]) != esperado:
            raise ErroValidacao(
                "Código de barras inválido: o último dígito deveria ser "
                f"{esperado}. Confira a digitação.")
    return digitos


# ---------- números e datas ----------

def _preco(texto, rotulo, obrigatorio):
    """`rotulo` é masculino: 'preço de venda', 'preço de custo'."""
    if not texto:
        if obrigatorio:
            raise ErroValidacao(f"Informe o {rotulo}.")
        return Decimal("0")
    texto = texto.replace(" ", "")
    if "," in texto:  # 1.234,56 -> 1234.56
        texto = texto.replace(".", "").replace(",", ".")
    try:
        valor = Decimal(texto)
    except InvalidOperation:
        raise ErroValidacao(f"Valor inválido no {rotulo}. Exemplo: 25,90.")
    if not valor.is_finite():
        raise ErroValidacao(f"Valor inválido no {rotulo}. Exemplo: 25,90.")
    if valor < 0:
        raise ErroValidacao(f"O {rotulo} não pode ser negativo.")
    if valor.as_tuple().exponent < -2:
        raise ErroValidacao(
            f"Use no máximo 2 casas decimais no {rotulo}. Exemplo: 25,90.")
    if valor > PRECO_MAXIMO:
        raise ErroValidacao(f"O {rotulo} está muito alto.")
    return valor


def _inteiro(texto, rotulo, obrigatorio, padrao=None):
    """`rotulo` é feminino: 'quantidade', 'quantidade mínima'."""
    if not texto:
        if obrigatorio:
            raise ErroValidacao(f"Informe a {rotulo}.")
        return padrao
    try:
        valor = int(texto)
    except ValueError:
        raise ErroValidacao(f"A {rotulo} deve ser um número inteiro.")
    if valor < 0:
        raise ErroValidacao(f"A {rotulo} não pode ser negativa.")
    if valor > INTEIRO_MAXIMO:
        raise ErroValidacao(f"A {rotulo} está muito alta.")
    return valor


def _data(texto, rotulo):
    if not texto:
        raise ErroValidacao(f"Informe a data de {rotulo}.")
    try:
        data = converter_data(texto)
    except ValueError:
        raise ErroValidacao(
            f"Data de {rotulo} inválida. Use o formato dd/mm/aaaa.")
    if not ANO_MINIMO <= data.year <= ANO_MAXIMO:
        raise ErroValidacao(
            f"O ano da data de {rotulo} deve estar entre "
            f"{ANO_MINIMO} e {ANO_MAXIMO}.")
    return data


# ---------- formulário completo ----------

def validar_produto(valores):
    """Recebe os textos dos campos (dict) e devolve os dados prontos para o banco.

    As chaves do dicionário devolvido têm o mesmo nome dos parâmetros de
    inserir_produto() / atualizar_produto(), então dá para usar `**dados`.
    Levanta ErroValidacao com uma mensagem clara se algo estiver errado.
    """
    nome = _texto_com_letra(
        valores["nome"], "O nome", LIMITE_NOME,
        informe="Informe o nome do produto.", minimo=2)
    categoria = _texto_com_letra(
        valores["categoria"], "A categoria", LIMITE_CATEGORIA)
    marca = _texto_com_letra(valores["marca"], "A marca", LIMITE_MARCA)
    codigo_barras = _codigo_barras(valores["codigo_barras"])
    fornecedor = _texto_com_letra(
        valores["fornecedor"], "O fornecedor", LIMITE_FORNECEDOR)

    preco_custo = _preco(valores["preco_custo"], "preço de custo", False)
    preco_venda = _preco(valores["preco_venda"], "preço de venda", True)

    entrega = _data(valores["data_entrega"], "entrega")
    validade = _data(valores["data_validade"], "validade")
    if validade < entrega:
        raise ErroValidacao(
            "A validade não pode ser anterior à data de entrega.")

    quantidade = _inteiro(valores["quantidade"], "quantidade", True)
    quantidade_minima = _inteiro(
        valores["quantidade_minima"], "quantidade mínima", False,
        QUANTIDADE_MINIMA_PADRAO)

    lote = _texto_alfanumerico(valores["lote"], "O lote", LIMITE_LOTE)
    localizacao = _texto_alfanumerico(
        valores["localizacao"], "A localização", LIMITE_LOCALIZACAO)

    return {
        "nome": nome,
        "categoria": categoria,
        "marca": marca,
        "codigo_barras": codigo_barras,
        "fornecedor": fornecedor,
        "preco_custo": preco_custo,
        "preco_venda": preco_venda,
        "data_entrega": entrega,
        "data_validade": validade,
        "quantidade": quantidade,
        "quantidade_minima": quantidade_minima,
        "lote": lote,
        "localizacao": localizacao,
    }
