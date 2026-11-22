"""Campo 'Categoria': escolhe numa lista pesquisável (ordem alfabética).

A janela tem um botão "Nova categoria" para criar categorias na hora.
"""
import flet as ft

from componentes.ui import abrir_dialogo, botao, fechar_dialogo
from funcoes.categoria import criar_categoria, listar_categorias
from tema import PRETO, VERMELHO
from utils.erros import ErroValidacao, mensagem_amigavel, registrar_erro
from utils.textos import chave_de_busca, normalizar_espacos


class SeletorCategoria:
    """`.controle` vai no formulário; `.campo.value` guarda a categoria."""

    def __init__(self, page, avisar_erro, largura=240):
        self.page = page
        self._avisar_erro = avisar_erro  # função(texto) para erros fora da janela
        self.campo = ft.TextField(label="Categoria", read_only=True,
                                  width=largura - 44)
        self.controle = ft.Row(
            controls=[
                self.campo,
                ft.IconButton(icon=ft.Icons.ARROW_DROP_DOWN,
                              icon_color=PRETO,
                              tooltip="Escolher categoria",
                              on_click=self.abrir),
            ],
            spacing=0, width=largura,
        )

    def abrir(self, e=None):
        try:
            todas = listar_categorias()
        except Exception as erro:
            registrar_erro(erro, "listar categorias")
            self._avisar_erro(mensagem_amigavel(erro))
            return

        page = self.page
        busca = ft.TextField(label="Pesquisar categoria", autofocus=True)
        lista = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        aviso = ft.Text("", size=12, color=VERMELHO)
        nova = ft.TextField(label="Nome da nova categoria", autofocus=True)

        def fechar_e_atualizar():
            fechar_dialogo(page, dialogo)
            page.update()

        def escolher(nome):
            self.campo.value = nome
            fechar_e_atualizar()

        def desenhar():
            termo = chave_de_busca(busca.value)
            visiveis = [c for c in todas if termo in chave_de_busca(c)]
            if visiveis:
                lista.controls = [
                    ft.ListTile(
                        title=ft.Text(nome),
                        selected=(nome == self.campo.value),
                        on_click=lambda e, n=nome: escolher(n),
                        dense=True,
                    )
                    for nome in visiveis
                ]
            else:
                lista.controls = [ft.Text(
                    "Nenhuma categoria encontrada. "
                    "Use “Nova categoria” para criar.", size=13)]

        def ao_digitar(e):
            desenhar()
            page.update()

        def mostrar_nova(visivel):
            painel_nova.visible = visivel
            botao_nova.visible = not visivel
            aviso.value = ""
            page.update()

        def abrir_nova(e):
            nova.value = normalizar_espacos(busca.value)  # aproveita o que já digitou
            mostrar_nova(True)

        def cancelar_nova(e):
            nova.value = ""
            mostrar_nova(False)

        def criar(e):
            try:
                nome = criar_categoria(nova.value or "")
            except Exception as erro:
                if not isinstance(erro, ErroValidacao):
                    registrar_erro(erro, "criar categoria")
                aviso.value = mensagem_amigavel(erro)
                page.update()
                return
            escolher(nome)

        def sem_categoria(e):
            self.campo.value = ""
            fechar_e_atualizar()

        busca.on_change = ao_digitar
        nova.on_submit = criar
        botao_nova = ft.TextButton("Nova categoria", icon=ft.Icons.ADD,
                                   on_click=abrir_nova)
        painel_nova = ft.Column(
            controls=[nova,
                      ft.Row(controls=[botao("Criar", criar),
                                       ft.TextButton("Cancelar",
                                                     on_click=cancelar_nova)])],
            spacing=8, visible=False,
        )
        desenhar()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Categoria"),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    controls=[busca, botao_nova, painel_nova, aviso,
                              ft.Container(height=260, content=lista)],
                    spacing=10, tight=True,
                ),
            ),
            actions=[
                ft.TextButton("Sem categoria", on_click=sem_categoria),
                botao("Fechar", lambda e: fechar_e_atualizar()),
            ],
        )
        abrir_dialogo(page, dialogo)
