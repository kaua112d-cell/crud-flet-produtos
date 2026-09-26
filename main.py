import os
import json
import flet as ft

PASTA_DO_PROJETO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(PASTA_DO_PROJETO, "produtos.json")

def carregar_produtos():
    if not os.path.exists(ARQUIVO):
        return []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def salvar_produtos(produtos):
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(
            produtos,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def main(page: ft.Page):
    page.title = "Sistema de Cadastro de Produtos"
    page.window.width = 950
    page.window.height = 650
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    produtos = carregar_produtos()

    nome = ft.TextField(
        label="Nome do produto",
        hint_text="Digite o nome",
        expand=True,
    )

    preco = ft.TextField(
        label="Preço",
        hint_text="Ex: 39.90",
        expand=True,
    )

    estoque = ft.TextField(
        label="Estoque",
        hint_text="Ex: 10",
        expand=True,
    )

    tabela = ft.Column(spacing=8)

    mensagem = ft.Text()

    titulo = ft.Text(
        "Sistema de Cadastro de Produtos",
        size=28,
        weight=ft.FontWeight.BOLD,
    )

    subtitulo = ft.Text(
        "CRUD desenvolvido com Flet e Python",
        size=15,
    )

    contador = ft.Text(
        size=15,
        weight=ft.FontWeight.BOLD,
    )

    def mostrar_mensagem(texto, erro=False):
        mensagem.value = texto

        if erro:
            mensagem.color = ft.Colors.RED
        else:
            mensagem.color = ft.Colors.GREEN

        page.update()

    def atualizar_contador():
        contador.value = f"Total de produtos cadastrados: {len(produtos)}"

    def limpar_campos():
        nome.value = ""
        preco.value = ""
        estoque.value = ""

    def criar_produto(e):
        nome_produto = nome.value.strip()
        preco_produto = preco.value.strip().replace(",", ".")
        estoque_produto = estoque.value.strip()

        if not nome_produto:
            mostrar_mensagem("Digite o nome do produto.", True)
            return

        if not preco_produto:
            mostrar_mensagem("Digite o preço do produto.", True)
            return

        if not estoque_produto:
            mostrar_mensagem("Digite a quantidade em estoque.", True)
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
            mostrar_mensagem("O preço não pode ser negativo.", True)
            return

        if estoque_numero < 0:
            mostrar_mensagem(
                "O estoque não pode ser negativo.",
                True,
            )
            return

        novo_id = max(
            [produto["id"] for produto in produtos],
            default=0,
        ) + 1

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
        atualizar_contador()

        mostrar_mensagem("Produto cadastrado com sucesso!")

    def editar_produto(produto):
        nome_editar = ft.TextField(
            label="Nome",
            value=produto["nome"],
        )

        preco_editar = ft.TextField(
            label="Preço",
            value=str(produto["preco"]),
        )

        estoque_editar = ft.TextField(
            label="Estoque",
            value=str(produto["estoque"]),
        )

        def salvar_edicao(e):
            novo_nome = nome_editar.value.strip()
            novo_preco = preco_editar.value.strip().replace(",", ".")
            novo_estoque = estoque_editar.value.strip()

            if not novo_nome:
                mostrar_mensagem("O nome não pode ficar vazio.", True)
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

            if novo_preco < 0 or novo_estoque < 0:
                mostrar_mensagem(
                    "Preço e estoque não podem ser negativos.",
                    True,
                )
                return

            produto["nome"] = novo_nome
            produto["preco"] = novo_preco
            produto["estoque"] = novo_estoque

            salvar_produtos(produtos)

            dialogo.open = False

            atualizar_tabela()
            mostrar_mensagem("Produto atualizado com sucesso!")

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar produto"),
            content=ft.Column(
                [
                    nome_editar,
                    preco_editar,
                    estoque_editar,
                ],
                tight=True,
                width=400,
            ),
            actions=[
                ft.Button(
                    "Cancelar",
                    on_click=lambda e: fechar_dialogo(),
                ),
                ft.Button(
                    "Salvar alterações",
                    on_click=salvar_edicao,
                ),
            ],
        )

        def fechar_dialogo():
            dialogo.open = False
            page.update()

        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def confirmar_exclusao(produto):
        def excluir(e):
            produtos.remove(produto)
            salvar_produtos(produtos)

            dialogo.open = False

            atualizar_tabela()
            atualizar_contador()

            mostrar_mensagem("Produto excluído com sucesso!")

        def cancelar(e):
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar exclusão"),
            content=ft.Text(
                f'Deseja realmente excluir "{produto["nome"]}"?'
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=cancelar,
                ),
               ft.Button(
                    "Excluir",
                    on_click=excluir,
                ),
            ],
        )

        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def atualizar_tabela():
        tabela.controls.clear()

        if not produtos:
            tabela.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nenhum produto cadastrado.",
                        size=16,
                    ),
                    padding=20,
                )
            )

        else:
            cabecalho = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(
                            "ID",
                            weight=ft.FontWeight.BOLD,
                            width=50,
                        ),
                        ft.Text(
                            "Produto",
                            weight=ft.FontWeight.BOLD,
                            expand=True,
                        ),
                        ft.Text(
                            "Preço",
                            weight=ft.FontWeight.BOLD,
                            width=120,
                        ),
                        ft.Text(
                            "Estoque",
                            weight=ft.FontWeight.BOLD,
                            width=100,
                        ),
                        ft.Text(
                            "Ações",
                            weight=ft.FontWeight.BOLD,
                            width=150,
                        ),
                    ],
                ),
                padding=10,
            )

            tabela.controls.append(cabecalho)

            for produto in produtos:
                linha = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                str(produto["id"]),
                                width=50,
                            ),
                            ft.Text(
                                produto["nome"],
                                expand=True,
                            ),
                            ft.Text(
                                f'R$ {produto["preco"]:.2f}',
                                width=120,
                            ),
                            ft.Text(
                                str(produto["estoque"]),
                                width=100,
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        tooltip="Editar",
                                        on_click=lambda e, p=produto:
                                        editar_produto(p),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        tooltip="Excluir",
                                        on_click=lambda e, p=produto:
                                        confirmar_exclusao(p),
                                    ),
                                ],
                                width=150,
                            ),
                        ],
                    ),
                    padding=10,
                )

                tabela.controls.append(linha)

        atualizar_contador()
        page.update()

    formulario = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Cadastrar novo produto",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    [
                        nome,
                        preco,
                        estoque,
                    ]
                ),
               ft.Button(
                    "Cadastrar produto",
                    icon=ft.Icons.ADD,
                    on_click=criar_produto,
                ),
                mensagem,
            ],
            spacing=15,
        ),
        padding=20,
    )

    lista = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Produtos cadastrados",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(expand=True),
                        contador,
                    ]
                ),
                ft.Divider(),
                tabela,
            ],
            spacing=10,
        ),
        padding=20,
    )

    page.add(
        ft.Column(
            [
                titulo,
                subtitulo,
                ft.Divider(),
                formulario,
                ft.Divider(),
                lista,
            ],
            spacing=10,
        )
    )

    atualizar_tabela()


ft.run(main)