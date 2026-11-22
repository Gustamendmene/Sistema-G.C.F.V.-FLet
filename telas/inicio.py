"""Tela inicial: alertas em destaque e resumo do estoque."""
import flet as ft

from componentes.alertas_ui import Sino, linha_alerta
from componentes.ui import cabecalho, criar_cartao
from funcoes.alertas import VENCIDO, carregar_alertas
from funcoes.estoque import resumo_estoque
from tema import AMARELO, BRANCO, LINHA, PRETO, VERMELHO
from utils.erros import mensagem_amigavel, registrar_erro


def _destaque_alertas(resultado, navegar):
    """Caixa com os 5 alertas mais graves (some se não houver nenhum)."""
    if not resultado.alertas:
        return ft.Container(visible=False)
    primeiros = resultado.alertas[:5]
    restante = len(resultado.alertas) - len(primeiros)
    texto_botao = ("Ver todos os alertas" if restante <= 0
                   else f"Ver todos os alertas (+{restante})")
    cor_icone = VERMELHO if resultado.por_tipo(VENCIDO) else AMARELO
    return ft.Container(
        bgcolor=BRANCO, padding=18, border_radius=12,
        content=ft.Column(
            controls=[
                ft.Row(controls=[
                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED,
                            color=cor_icone),
                    ft.Text("Alertas em destaque", size=16,
                            weight=ft.FontWeight.BOLD, color=PRETO),
                ]),
                *[linha_alerta(a) for a in primeiros],
                ft.TextButton(texto_botao,
                              on_click=lambda e: navegar("validade")),
            ],
            spacing=10,
        ),
    )


def criar_tela(page, navegar):
    sino = Sino(navegar)
    resultado = carregar_alertas(forcar=True)
    sino.atualizar()

    aviso = ""
    try:
        produtos, proximos, vencidos = resumo_estoque()
    except Exception as erro:
        registrar_erro(erro, "carregar tela inicial")
        produtos = proximos = vencidos = 0
        aviso = mensagem_amigavel(erro)

    return ft.Column(
        controls=[
            cabecalho("Visão geral",
                      "Bem-vindo ao sistema do Mercadinho São José!", sino),
            ft.Divider(color=LINHA),
            ft.Text(aviso, color=VERMELHO, size=13, visible=bool(aviso)),
            _destaque_alertas(resultado, navegar),
            ft.Text("Resumo do estoque", size=18,
                    weight=ft.FontWeight.BOLD, color=PRETO),
            ft.Row(
                controls=[
                    criar_cartao("Produtos cadastrados", produtos,
                                 ft.Icons.INVENTORY_2_OUTLINED, PRETO),
                    criar_cartao("Próximos do vencimento", proximos,
                                 ft.Icons.ACCESS_TIME, AMARELO),
                    criar_cartao("Produtos vencidos", vencidos,
                                 ft.Icons.WARNING_AMBER_OUTLINED, VERMELHO),
                ],
                spacing=14,
            ),
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
