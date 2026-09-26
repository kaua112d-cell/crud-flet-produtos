import os
import json
import flet as ft


# ============================================================
# CONFIGURAÇÃO DO ARQUIVO JSON
# ============================================================

PASTA_DO_PROJETO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(PASTA_DO_PROJETO, "produtos.json")


def carregar_produtos():
    """Carrega os produtos salvos no arquivo JSON."""
    if not os.path.exists(ARQUIVO):
        return []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def salvar_produtos(produtos):
    """Salva a lista de produtos no arquivo JSON."""
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)


# ============================================================
# APLICAÇÃO
# ============================================================

def main(page: ft.Page):

    # --------------------------------------------------------
    # CONFIGURAÇÕES DA JANELA
    # --------------------------------------------------------

    page.title = "Gestão de Produtos"
    page.window.width = 1100
    page.window.height = 750
    page.padding = 0
    page.bgcolor = "#D8CDBE"
    page.theme_mode = ft.ThemeMode.LIGHT

    produtos = carregar_produtos()

    # --------------------------------------------------------
    # CAMPOS
    # --------------------------------------------------------

    nome = ft.TextField(
        label="Nome do produto",
        hint_text="Ex.: Caderno escolar",
        prefix_icon=ft.Icons.INVENTORY_2,
        expand=True,
        border_radius=10,
    )

    preco = ft.TextField(
        label="Preço",
        hint_text="Ex.: 39,90",
        prefix_icon=ft.Icons.ATTACH_MONEY,
        width=200,
        border_radius=10,
    )

    estoque = ft.TextField(
        label="Estoque",
        hint_text="Ex.: 10",
        prefix_icon=ft.Icons.NUMBERS,
        width=180,
        border_radius=10,
    )

    busca = ft.TextField(
        hint_text="Pesquisar produto...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        dense=True,
        border_radius=10,
        on_change=lambda e: atualizar_tabela(),
    )

    mensagem = ft.Text(
        "",
        size=13,
    )

    tabela = ft.Column(
        spacing=8,
    )

    # --------------------------------------------------------
    # CARDS DO RESUMO
    # --------------------------------------------------------

    total_produtos = ft.Text(
        "0",
        size=26,
        weight=ft.FontWeight.BOLD,
    )

    total_itens = ft.Text(
        "0",
        size=26,
        weight=ft.FontWeight.BOLD,
    )

    valor_estoque = ft.Text(
        "R$ 0,00",
        size=26,
        weight=ft.FontWeight.BOLD,
    )

    # --------------------------------------------------------
    # FUNÇÕES AUXILIARES
    # --------------------------------------------------------

    def mostrar_mensagem(texto, erro=False):
        mensagem.value = texto
        mensagem.color = (
            ft.Colors.RED_700
            if erro
            else ft.Colors.GREEN_700
        )
        page.update()

    def limpar_campos():
        nome.value = ""
        preco.value = ""
        estoque.value = ""

    def formatar_moeda(valor):
        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def atualizar_resumo():
        quantidade_produtos = len(produtos)

        quantidade_itens = sum(
            produto["estoque"]
            for produto in produtos
        )

        valor_total = sum(
            produto["preco"] * produto["estoque"]
            for produto in produtos
        )

        total_produtos.value = str(
            quantidade_produtos
        )

        total_itens.value = str(
            quantidade_itens
        )

        valor_estoque.value = formatar_moeda(
            valor_total
        )

    def fechar_dialogo(dialogo):
        dialogo.open = False
        page.update()

    # ========================================================
    # CADASTRAR PRODUTO
    # ========================================================

    def criar_produto(e):

        nome_produto = nome.value.strip()

        preco_produto = (
            preco.value
            .strip()
            .replace(",", ".")
        )

        estoque_produto = estoque.value.strip()

        # ----------------------------
        # VALIDAÇÕES
        # ----------------------------

        if not nome_produto:
            mostrar_mensagem(
                "Digite o nome do produto.",
                True,
            )
            return

        if not preco_produto:
            mostrar_mensagem(
                "Digite o preço do produto.",
                True,
            )
            return

        if not estoque_produto:
            mostrar_mensagem(
                "Digite a quantidade em estoque.",
                True,
            )
            return

        try:
            preco_numero = float(preco_produto)
            estoque_numero = int(estoque_produto)

        except ValueError:
            mostrar_mensagem(
                "Preço ou estoque informado de forma inválida.",
                True,
            )
            return

        if preco_numero < 0:
            mostrar_mensagem(
                "O preço não pode ser negativo.",
                True,
            )
            return

        if estoque_numero < 0:
            mostrar_mensagem(
                "O estoque não pode ser negativo.",
                True,
            )
            return

        # ----------------------------
        # GERAR ID
        # ----------------------------

        novo_id = max(
            [produto["id"] for produto in produtos],
            default=0,
        ) + 1

        # ----------------------------
        # CRIAR PRODUTO
        # ----------------------------

        novo_produto = {
            "id": novo_id,
            "nome": nome_produto,
            "preco": preco_numero,
            "estoque": estoque_numero,
        }

        produtos.append(novo_produto)

        salvar_produtos(produtos)

        limpar_campos()

        atualizar_tabela()

        atualizar_resumo()

        mostrar_mensagem(
            "Produto cadastrado com sucesso!"
        )

    # ========================================================
    # EDITAR PRODUTO
    # ========================================================

    def editar_produto(produto):

        nome_editar = ft.TextField(
            label="Nome do produto",
            value=produto["nome"],
            prefix_icon=ft.Icons.INVENTORY_2,
            border_radius=10,
        )

        preco_editar = ft.TextField(
            label="Preço",
            value=str(
                produto["preco"]
            ).replace(".", ","),
            prefix_icon=ft.Icons.ATTACH_MONEY,
            border_radius=10,
        )

        estoque_editar = ft.TextField(
            label="Estoque",
            value=str(produto["estoque"]),
            prefix_icon=ft.Icons.NUMBERS,
            border_radius=10,
        )

        dialogo = None

        def salvar_edicao(e):

            novo_nome = nome_editar.value.strip()

            novo_preco = (
                preco_editar.value
                .strip()
                .replace(",", ".")
            )

            novo_estoque = estoque_editar.value.strip()

            if not novo_nome:
                mostrar_mensagem(
                    "O nome não pode ficar vazio.",
                    True,
                )
                return

            try:
                novo_preco = float(novo_preco)
                novo_estoque = int(novo_estoque)

            except ValueError:
                mostrar_mensagem(
                    "Preço ou estoque inválido.",
                    True,
                )
                return

            if novo_preco < 0:
                mostrar_mensagem(
                    "O preço não pode ser negativo.",
                    True,
                )
                return

            if novo_estoque < 0:
                mostrar_mensagem(
                    "O estoque não pode ser negativo.",
                    True,
                )
                return

            produto["nome"] = novo_nome
            produto["preco"] = novo_preco
            produto["estoque"] = novo_estoque

            salvar_produtos(produtos)

            dialogo.open = False

            atualizar_tabela()

            atualizar_resumo()

            mostrar_mensagem(
                "Produto atualizado com sucesso!"
            )

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.EDIT,
                        size=24,
                    ),
                    ft.Text(
                        "Editar produto",
                        weight=ft.FontWeight.BOLD,
                    ),
                ]
            ),

            content=ft.Column(
                [
                    nome_editar,
                    preco_editar,
                    estoque_editar,
                ],
                tight=True,
                width=420,
                spacing=15,
            ),

            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                    fechar_dialogo(dialogo),
                ),

                ft.Button(
                    "Salvar alterações",
                    icon=ft.Icons.SAVE,
                    on_click=salvar_edicao,
                ),
            ],
        )

        page.overlay.append(dialogo)

        dialogo.open = True

        page.update()

    # ========================================================
    # EXCLUIR PRODUTO
    # ========================================================

    def confirmar_exclusao(produto):

        dialogo = None

        def excluir(e):

            produtos.remove(produto)

            salvar_produtos(produtos)

            dialogo.open = False

            atualizar_tabela()

            atualizar_resumo()

            mostrar_mensagem(
                "Produto excluído com sucesso!"
            )

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.WARNING_AMBER,
                        size=24,
                    ),
                    ft.Text(
                        "Excluir produto",
                        weight=ft.FontWeight.BOLD,
                    ),
                ]
            ),

            content=ft.Text(
                f'Deseja realmente excluir '
                f'"{produto["nome"]}"?'
            ),

            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                    fechar_dialogo(dialogo),
                ),

                ft.Button(
                    "Excluir",
                    icon=ft.Icons.DELETE,
                    on_click=excluir,
                ),
            ],
        )

        page.overlay.append(dialogo)

        dialogo.open = True

        page.update()

    # ========================================================
    # LINHA DO PRODUTO
    # ========================================================

    def criar_linha_produto(produto):

        return ft.Container(

            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            str(produto["id"]),
                            size=14,
                        ),
                        width=55,
                    ),

                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.INVENTORY_2,
                                    size=20,
                                ),
                                ft.Text(
                                    produto["nome"],
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ],
                            spacing=10,
                        ),
                        expand=True,
                    ),

                    ft.Container(
                        content=ft.Text(
                            formatar_moeda(
                                produto["preco"]
                            ),
                            size=14,
                        ),
                        width=150,
                    ),

                    ft.Container(
                        content=ft.Text(
                            str(produto["estoque"]),
                            size=14,
                        ),
                        width=100,
                    ),

                    ft.Container(
                        content=ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e:
                                    editar_produto(produto),
                                ),

                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Excluir",
                                    on_click=lambda e:
                                    confirmar_exclusao(produto),
                                ),
                            ],
                            spacing=2,
                        ),
                        width=110,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),

            padding=ft.Padding(
                left=15,
                right=10,
                top=10,
                bottom=10,
            ),

            border_radius=8,

            bgcolor=ft.Colors.WHITE,
        )

    # ========================================================
    # TABELA
    # ========================================================

    def atualizar_tabela(e=None):

        tabela.controls.clear()

        termo = busca.value.strip().lower()

        produtos_filtrados = [
            produto
            for produto in produtos
            if termo in produto["nome"].lower()
        ]

        # ----------------------------
        # NENHUM PRODUTO
        # ----------------------------

        if not produtos_filtrados:

            if termo:

                titulo = "Nenhum produto encontrado"

                descricao = (
                    "Tente pesquisar por outro nome."
                )

            else:

                titulo = "Nenhum produto cadastrado"

                descricao = (
                    "Cadastre seu primeiro produto "
                    "usando o formulário acima."
                )

            tabela.controls.append(
                ft.Container(

                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.INVENTORY_2,
                                size=50,
                            ),

                            ft.Text(
                                titulo,
                                size=17,
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Text(
                                descricao,
                                size=13,
                            ),
                        ],

                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),

                        spacing=8,
                    ),

                    padding=45,

                    alignment=ft.Alignment.CENTER,

                    bgcolor=ft.Colors.WHITE,

                    border_radius=10,
                )
            )

            page.update()

            return

        # ----------------------------
        # CABEÇALHO DA TABELA
        # ----------------------------

        tabela.controls.append(

            ft.Container(

                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(
                                "ID",
                                weight=ft.FontWeight.BOLD,
                            ),
                            width=55,
                        ),

                        ft.Container(
                            content=ft.Text(
                                "PRODUTO",
                                weight=ft.FontWeight.BOLD,
                            ),
                            expand=True,
                        ),

                        ft.Container(
                            content=ft.Text(
                                "PREÇO",
                                weight=ft.FontWeight.BOLD,
                            ),
                            width=150,
                        ),

                        ft.Container(
                            content=ft.Text(
                                "ESTOQUE",
                                weight=ft.FontWeight.BOLD,
                            ),
                            width=100,
                        ),

                        ft.Container(
                            content=ft.Text(
                                "AÇÕES",
                                weight=ft.FontWeight.BOLD,
                            ),
                            width=110,
                        ),
                    ]
                ),

                padding=ft.Padding(
                    left=15,
                    right=10,
                    top=10,
                    bottom=10,
                ),

                bgcolor=ft.Colors.GREY_200,

                border_radius=8,
            )
        )

        # ----------------------------
        # PRODUTOS
        # ----------------------------

        for produto in produtos_filtrados:

            tabela.controls.append(
                criar_linha_produto(produto)
            )

        page.update()

    # ========================================================
    # CARDS
    # ========================================================

    def criar_card(
        titulo,
        valor,
        icone,
    ):

        return ft.Container(

            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            icone,
                            size=30,
                        ),
                        padding=12,
                    ),

                    ft.Column(
                        [
                            ft.Text(
                                titulo,
                                size=13,
                            ),

                            valor,
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
            ),

            padding=15,

            bgcolor=ft.Colors.WHITE,

            border_radius=12,

            expand=True,
        )

    # ========================================================
    # INTERFACE
    # ========================================================

    cabecalho = ft.Container(

        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            "Produtos da Minha Papelaria",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                        ),

                        ft.Text(
                            "Controle seus produtos e estoque",
                            size=14,
                        ),
                    ],
                    spacing=3,
                ),

                ft.Container(
                    content=ft.Icon(
                        ft.Icons.INVENTORY_2,
                        size=35,
                    ),
                    padding=10,
                ),
            ],

            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),

        padding=ft.Padding(
            left=25,
            right=25,
            top=22,
            bottom=22,
        ),

        bgcolor=ft.Colors.WHITE,
    )

    # --------------------------------------------------------
    # ÁREA DE CADASTRO
    # --------------------------------------------------------

    formulario = ft.Container(

        content=ft.Column(
            [
                ft.Text(
                    "Cadastrar produto",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Row(
                    [
                        nome,
                        preco,
                        estoque,

                        ft.Button(
                            "Cadastrar",
                            icon=ft.Icons.ADD,
                            on_click=criar_produto,
                        ),
                    ],
                    spacing=12,
                ),

                mensagem,
            ],

            spacing=12,
        ),

        padding=20,

        bgcolor=ft.Colors.WHITE,

        border_radius=12,
    )

    # --------------------------------------------------------
    # ÁREA DE PRODUTOS
    # --------------------------------------------------------

    produtos_area = ft.Container(

        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    "Produtos cadastrados",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),

                                ft.Text(
                                    "Consulte, edite ou exclua produtos.",
                                    size=13,
                                ),
                            ],
                            spacing=3,
                        ),

                        busca,
                    ],

                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                    spacing=20,
                ),

                tabela,
            ],

            spacing=15,
        ),

        padding=20,

        bgcolor=ft.Colors.WHITE,

        border_radius=12,
    )

    # --------------------------------------------------------
    # ADICIONAR TUDO NA PÁGINA
    # --------------------------------------------------------

    pagina = ft.Column(
        [
            cabecalho,

            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                criar_card(
                                    "Total de produtos",
                                    total_produtos,
                                    ft.Icons.INVENTORY_2,
                                ),

                                criar_card(
                                    "Itens em estoque",
                                    total_itens,
                                    ft.Icons.STORAGE,
                                ),

                                criar_card(
                                    "Valor do estoque",
                                    valor_estoque,
                                    ft.Icons.ATTACH_MONEY,
                                ),
                            ],
                            spacing=15,
                        ),

                        formulario,

                        produtos_area,
                    ],
                    spacing=15,
                ),

                padding=20,
                expand=True,
            ),
        ],

        spacing=0,

        expand=True,
    )

    page.add(pagina)

    # --------------------------------------------------------
    # PRIMEIRA ATUALIZAÇÃO
    # --------------------------------------------------------

    atualizar_resumo()

    atualizar_tabela()


# ============================================================
# EXECUTAR A APLICAÇÃO
# ============================================================

ft.run(main)
