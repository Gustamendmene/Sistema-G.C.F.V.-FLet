# Sistema G.C.F.V. — Mercadinho São José

Sistema de controle de estoque e validade, feito em Python com Flet e MySQL.

## Como executar (Windows)

1. Abra a pasta do projeto no VS Code (File > Open Folder).
2. Crie o ambiente virtual: `python -m venv .venv`
3. Ative: `.\.venv\Scripts\Activate.ps1`
4. Instale as dependências: `python -m pip install -r requirements.txt`
5. **Copie** `.env.example` para `.env` e coloque a sua senha do MySQL.
6. Execute sempre pelo main: `python main.py`

## Estrutura

```
main.py          ponto de entrada: menu lateral e navegação entre telas
tema.py          cores usadas em todo o sistema
banco/           conexao.py: conectar() e transacao() (abre, confirma, desfaz e fecha)
funcoes/         acesso ao banco, sem interface:
                   produto.py (CRUD), categoria.py, estoque.py (consultas), alertas.py
telas/           uma tela por arquivo (inicio, produtos, estoque, validade)
componentes/     peças de interface reutilizáveis:
                   ui.py, listagem.py, alertas_ui.py (sino), seletor_categoria.py
utils/           datas.py, mascaras.py, textos.py, validacao.py, erros.py (log + mensagens)
logs/            erros.log (criado sozinho; fica fora do GitHub)
```

## Onde procurar quando algo der errado

| Sintoma | Onde olhar |
|---|---|
| Mensagem vermelha na tela | O texto já explica; o detalhe técnico está em `logs/erros.log` |
| Erro de senha/conexão | Arquivo `.env` (veja `.env.example`) |
| Dado salvo errado ou erro de SQL | `funcoes/` |
| Campo rejeitado indevidamente | `utils/validacao.py` |
| Visual / botão | `telas/` e `componentes/` |

## Regras do formulário de produto

| Campo | Regra |
|---|---|
| Nome | obrigatório; ao menos 1 letra (números só junto com letras); até 100 caracteres |
| Categoria | escolhida numa lista pesquisável (ordem alfabética); o botão "Nova categoria" cria outra na hora |
| Marca / Fornecedor | opcionais; se preenchidos, ao menos 1 letra |
| Código de barras | opcional; só números, com 8, 12, 13 ou 14 dígitos e dígito verificador válido (ajuste em `VALIDAR_DIGITO_VERIFICADOR`, `utils/validacao.py`) |
| Preço de venda | obrigatório; até 2 casas decimais |
| Entrega / Validade | `dd/mm/aaaa` (as barras entram sozinhas); ano entre 2000 e 2100; validade não pode ser anterior à entrega |
| Lote / Localização | letras, números, espaço e `- / . , # ( )` |

Editar um produto: clique no lápis da tabela, altere e use **Salvar produto**.
Para desistir da edição, clique em **Limpar campos**.

## Alertas

Vêm da view `alerta_estoque` do MySQL (tratados em `funcoes/alertas.py`):

| Alerta | Quando | Cor |
|---|---|---|
| VENCIDO | validade já passou | vermelho |
| PRÓXIMO DO VENCIMENTO | vence em até 7 dias | amarelo |
| ESTOQUE BAIXO | quantidade atual <= mínima | laranja |

Aparecem no sino do cabeçalho (contador; clique abre a tela Validade), na caixa
"Alertas em destaque" do Início, num aviso ao abrir o sistema e na tela Validade.

A tabela `categoria` é criada sozinha na primeira vez que a lista de categorias abre.
