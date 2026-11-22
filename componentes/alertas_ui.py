"""Interface dos alertas: sino com contador, linha de alerta e aviso ao abrir."""
import flet as ft

from componentes.ui import abrir_dialogo, etiqueta
from funcoes.alertas import PROXIMO, VENCIDO, carregar_alertas
from tema import AMARELO, BRANCO, CORES_ALERTA, PRETO, VERMELHO
from utils.erros import registrar_erro


def linha_alerta(alerta):
    """Uma linha: etiqueta colorida (tipo do alerta) + descrição."""
    chip = etiqueta(alerta.tipo, CORES_ALERTA.get(alerta.tipo, PRETO))
    chip.width = 190
    chip.alignment = ft.Alignment(0, 0)
    return ft.Row(
        controls=[chip,
                  ft.Text(alerta.descricao, size=13, color=PRETO, expand=True)],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


class Sino:
    """Sino do cabeçalho com um selo mostrando quantos alertas existem.

    Clicar leva à tela Validade. O selo é vermelho se há produto vencido e
    amarelo nos demais casos. Use `atualizar()` depois de mudar produtos.
    """

    def __init__(self, navegar):
        self._numero = ft.Text("", size=10, color=BRANCO,
                               weight=ft.FontWeight.BOLD)
        self._selo = ft.Container(
            content=self._numero, width=18, height=18, border_radius=9,
            bgcolor=VERMELHO, alignment=ft.Alignment(0, 0), visible=False,
            right=2, top=2,
        )
        self._botao = ft.IconButton(
            icon=ft.Icons.NOTIFICATIONS_NONE, icon_color=PRETO,
            tooltip="Ver alertas", on_click=lambda e: navegar("validade"),
        )
        self.controle = ft.Stack(width=48, height=48,
                                 controls=[self._botao, self._selo])
        self.atualizar()

    def atualizar(self):
        resultado = carregar_alertas()
        total = len(resultado.alertas)
        self._selo.visible = total > 0
        self._numero.value = "9+" if total > 9 else str(total)
        self._selo.bgcolor = VERMELHO if resultado.por_tipo(VENCIDO) else AMARELO
        self._botao.tooltip = (f"{total} alerta(s)" if total
                               else "Nenhum alerta")


def avisar_alertas_urgentes(page, navegar):
    """Aviso ao abrir o sistema se houver produto vencido ou perto de vencer."""
    try:
        resultado = carregar_alertas()
        vencidos = len(resultado.por_tipo(VENCIDO))
        proximos = len(resultado.por_tipo(PROXIMO))
        if not (vencidos or proximos):
            return
        partes = []
        if vencidos:
            partes.append(f"{vencidos} produto(s) vencido(s)")
        if proximos:
            partes.append(f"{proximos} perto de vencer")
        aviso = ft.SnackBar(
            content=ft.Text("Atenção: " + " e ".join(partes) + ".",
                            color=BRANCO),
            bgcolor=VERMELHO,
            action="Ver alertas",
            on_action=lambda e: navegar("validade"),
            duration=8000,
        )
        abrir_dialogo(page, aviso)
    except Exception as erro:
        registrar_erro(erro, "aviso de alertas ao iniciar")
