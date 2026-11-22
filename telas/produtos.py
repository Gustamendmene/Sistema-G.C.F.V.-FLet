"""Tela de produtos: cadastrar, editar, listar e excluir."""
import flet as ft

from componentes.alertas_ui import Sino
from componentes.seletor_categoria import SeletorCategoria
from componentes.ui import (abrir_dialogo, botao, cabecalho, celula,
                            fechar_dialogo, painel, titulo_coluna)
from funcoes.alertas import invalidar_cache
from funcoes.produto import (atualizar_produto, buscar_produto,
                             deletar_produto, inserir_produto,
                             listar_produtos)
from tema import BRANCO, LINHA, PRETO, TEXTO_SUAVE, VERDE, VERMELHO
from utils.datas import data_para_campo, formatar_data
from utils.erros import ErroValidacao, mensagem_amigavel, registrar_erro
from utils.mascaras import mascara_data, somente_digitos
from utils.validacao import validar_produto

# (chave, rótulo, largura). A chave é a mesma usada no banco e na validação.
CAMPOS = [
    ("nome", "Nome *", 260),
    ("categoria", "Categoria", 200),
    ("marca", "Marca", 200),
    ("codigo_barras", "Código de barras", 200),
    ("fornecedor", "Fornecedor", 240),
    ("preco_custo", "Preço de custo", 160),
    ("preco_venda", "Preço de venda *", 160),
    ("data_entrega", "Entrega * (dd/mm/aaaa)", 200),
    ("data_validade", "Validade * (dd/mm/aaaa)", 200),
    ("quantidade", "Quantidade *", 140),
    ("quantidade_minima", "Qtd. mínima", 140),
    ("lote", "Lote", 160),
    ("localizacao", "Localização", 200),
]
CAMPOS_DE_DATA = ("data_entrega", "data_validade")


def _textos_do_produto(produto):
    """Registro vindo do banco -> textos para preencher o formulário."""
    textos = {chave: "" if valor is None else str(valor)
              for chave, valor in produto.items()}
    textos["quantidade"] = textos["quantidade_atual"]
    for chave in ("preco_custo", "preco_venda"):
        if produto[chave] is not None:
            textos[chave] = f"{produto[chave]:.2f}".replace(".", ",")
    for chave in CAMPOS_DE_DATA:
        textos[chave] = data_para_campo(produto[chave])
    return textos


def criar_tela(page, navegar):
    sino = Sino(navegar)
    estado = {"id_em_edicao": None}  # None = cadastrando; número = editando
    ultimo_valor = {}                # último texto de cada campo (máscara de data)

    # ---------- campos do formulário ----------
    campos = {}
    controles_form = []
    for chave, rotulo, largura in CAMPOS:
        if chave == "categoria":
            seletor = SeletorCategoria(
                page, lambda t: (avisar(t, erro=True), page.update()),
                largura=largura)
            campos[chave] = seletor.campo
            controles_form.append(seletor.controle)
        else:
            campos[chave] = ft.TextField(label=rotulo, width=largura)
            controles_form.append(campos[chave])

    mensagem = ft.Text("", size=13)
    titulo_form = ft.Text("Novo produto", size=16,
                          weight=ft.FontWeight.BOLD, color=PRETO)
    vazio = ft.Text("Nenhum produto cadastrado ainda. Preencha o formulário "
                    "e clique em Salvar produto.",
                    color=TEXTO_SUAVE, size=13, visible=False)
    tabela = ft.DataTable(
        columns=[titulo_coluna(t) for t in
                 ["ID", "Produto", "Categoria", "Validade", "Quantidade",
                  "Local", "Ações"]],
        rows=[],
        column_spacing=28,
    )

    # ---------- mensagens e formulário ----------
    def avisar(texto, erro=False):
        mensagem.value = texto
        mensagem.color = VERMELHO if erro else VERDE

    def tratar_erro(erro, contexto):
        """Mostra a mensagem amigável; erros inesperados vão para o log."""
        if not isinstance(erro, ErroValidacao):
            registrar_erro(erro, contexto)
        avisar(mensagem_amigavel(erro), erro=True)
        page.update()

    def definir(chave, texto):
        campos[chave].value = texto
        ultimo_valor[chave] = texto

    def voltar_ao_cadastro():
        """Limpa o formulário e volta ao modo 'Novo produto'."""
        for chave in campos:
            definir(chave, "")
        estado["id_em_edicao"] = None
        titulo_form.value = "Novo produto"

    def atualizar_alertas():
        """Os dados mudaram: refaz a contagem do sino do cabeçalho."""
        invalidar_cache()
        sino.atualizar()

    def ao_digitar_data(chave):
        def tratar(e):
            definir(chave, mascara_data(campos[chave].value,
                                        ultimo_valor.get(chave, "")))
            page.update()
        return tratar

    def ao_digitar_codigo(e):
        definir("codigo_barras", somente_digitos(campos["codigo_barras"].value, 14))
        page.update()

    for chave in CAMPOS_DE_DATA:
        campos[chave].on_change = ao_digitar_data(chave)
    campos["codigo_barras"].on_change = ao_digitar_codigo

    # ---------- tabela ----------
    def carregar_tabela():
        try:
            produtos = listar_produtos()
        except Exception as erro:
            registrar_erro(erro, "listar produtos")
            tabela.rows = []
            vazio.visible = False
            avisar(mensagem_amigavel(erro), erro=True)
            return

        def acoes(p):
            return ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED, icon_color=PRETO,
                        tooltip="Editar produto",
                        on_click=lambda e, i=p["id_produto"]: editar(i)),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE, icon_color=VERMELHO,
                        tooltip="Excluir produto",
                        on_click=lambda e, i=p["id_produto"], n=p["nome"]:
                            pedir_exclusao(i, n)),
                ],
                spacing=0,
            )

        tabela.rows = [
            ft.DataRow(cells=[
                celula(p["id_produto"]),
                celula(p["nome"]),
                celula(p["categoria"] or "-"),
                celula(formatar_data(p["data_validade"])),
                celula(p["quantidade_atual"]),
                celula(p["localizacao"] or "-"),
                celula(acoes(p)),
            ])
            for p in produtos
        ]
        vazio.visible = not produtos

    # ---------- ações ----------
    def salvar(e):
        """Cadastra um produto novo ou atualiza o que está em edição."""
        id_produto = estado["id_em_edicao"]
        try:
            dados = validar_produto({chave: (campo.value or "").strip()
                                     for chave, campo in campos.items()})
            if id_produto:
                atualizar_produto(id_produto, dados)
            else:
                inserir_produto(dados)
        except Exception as erro:
            tratar_erro(erro, "salvar produto")
            return
        voltar_ao_cadastro()
        avisar(f"Produto '{dados['nome']}' "
               f"{'atualizado' if id_produto else 'salvo'} com sucesso.")
        atualizar_alertas()
        carregar_tabela()
        page.update()

    def editar(id_produto):
        try:
            produto = buscar_produto(id_produto)
        except Exception as erro:
            tratar_erro(erro, f"buscar produto {id_produto}")
            return
        if produto is None:
            avisar("Esse produto não existe mais (talvez já tenha sido "
                   "excluído).", erro=True)
            carregar_tabela()
            page.update()
            return
        textos = _textos_do_produto(produto)
        for chave in campos:
            definir(chave, textos.get(chave, ""))
        estado["id_em_edicao"] = id_produto
        titulo_form.value = f"Editar produto (ID {id_produto})"
        avisar("")
        page.update()

    def limpar(e):
        """Limpa os campos (se estava editando, cancela a edição)."""
        voltar_ao_cadastro()
        avisar("")
        page.update()

    def pedir_exclusao(id_produto, nome):
        def confirmar(e):
            fechar_dialogo(page, dialogo)
            try:
                apagados = deletar_produto(id_produto)
            except Exception as erro:
                tratar_erro(erro, f"excluir produto {id_produto}")
                return
            if estado["id_em_edicao"] == id_produto:
                voltar_ao_cadastro()
            if apagados:
                avisar(f"Produto '{nome}' excluído.")
            else:
                avisar("Esse produto já havia sido excluído.", erro=True)
            atualizar_alertas()
            carregar_tabela()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Excluir produto"),
            content=ft.Text(f"Deseja excluir '{nome}'? O estoque desse "
                            "produto também será apagado."),
            actions=[
                ft.TextButton("Cancelar",
                              on_click=lambda e: fechar_dialogo(page, dialogo)),
                botao("Excluir produto", confirmar, cor=VERMELHO),
            ],
        )
        abrir_dialogo(page, dialogo)

    # ---------- montagem da tela ----------
    carregar_tabela()

    return ft.Column(
        controls=[
            cabecalho("Produtos",
                      "Cadastre, consulte, edite e exclua os produtos do "
                      "mercado.", sino),
            ft.Divider(color=LINHA),
            ft.Container(
                bgcolor=BRANCO, padding=18, border_radius=12,
                content=ft.Column(
                    controls=[
                        titulo_form,
                        ft.Row(controls=controles_form, wrap=True,
                               spacing=12, run_spacing=12),
                        ft.Row(controls=[
                            botao("Salvar produto", salvar,
                                  icon=ft.Icons.SAVE_OUTLINED),
                            ft.OutlinedButton("Limpar campos", on_click=limpar),
                        ], spacing=10),
                        mensagem,
                    ],
                    spacing=14,
                ),
            ),
            ft.Text("Produtos cadastrados", size=18,
                    weight=ft.FontWeight.BOLD, color=PRETO),
            painel(tabela),
            vazio,
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
