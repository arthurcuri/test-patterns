#!/usr/bin/env python3
"""
Gera o relatório do trabalho de Test Patterns em formato IEEE (duas colunas).
Sem capa, com fonte serifada (Times New Roman), layout correto sem sobreposição.
"""

from fpdf import FPDF


class IEEEReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False)

        # Fontes serifadas (Times New Roman) - padrão IEEE
        self.add_font("TNR", "", "/System/Library/Fonts/Supplemental/Times New Roman.ttf")
        self.add_font("TNR", "B", "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf")
        self.add_font("TNR", "I", "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf")
        self.add_font("TNR", "BI", "/System/Library/Fonts/Supplemental/Times New Roman Bold Italic.ttf")

        # Courier para código
        self.add_font("CourierNew", "", "/System/Library/Fonts/Supplemental/Courier New.ttf")

    def footer(self):
        self.set_y(-12)
        self.set_font("TNR", "I", 8)
        self.set_text_color(80, 80, 80)
        self.cell(0, 10, f"{self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)


def write_col(pdf, col_x, col_w, blocks, page_h, bottom_margin):
    """
    Escreve blocos de texto em uma coluna específica.
    Cada bloco é um dict com: type, text, font, size, style, line_h
    Retorna a posição Y final.
    """
    pdf.set_xy(col_x, pdf.get_y() if pdf.get_y() > 20 else 20)

    for block in blocks:
        btype = block.get("type", "text")
        
        if btype == "spacing":
            pdf.set_y(pdf.get_y() + block.get("h", 3))
            pdf.set_x(col_x)
            continue

        if btype == "code":
            pdf.set_font("CourierNew", "", block.get("size", 7))
            pdf.set_fill_color(235, 235, 235)
            for line in block["lines"]:
                if pdf.get_y() + 3.5 > page_h - bottom_margin:
                    return pdf.get_y()
                pdf.set_x(col_x)
                pdf.cell(col_w, 3.3, "  " + line, fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.set_y(pdf.get_y() + 2)
            pdf.set_x(col_x)
            continue

        if btype == "table":
            pdf.set_font("TNR", "B", 8)
            headers = block["headers"]
            rows = block["rows"]
            cw = col_w / len(headers)
            pdf.set_x(col_x)
            for h in headers:
                pdf.cell(cw, 4, h, border=1, new_x="RIGHT")
            pdf.ln()
            pdf.set_font("TNR", "", 8)
            for row in rows:
                pdf.set_x(col_x)
                for cell in row:
                    pdf.cell(cw, 4, cell, border=1, new_x="RIGHT")
                pdf.ln()
            pdf.set_y(pdf.get_y() + 2)
            pdf.set_x(col_x)
            continue

        # Normal text
        font = block.get("font", "TNR")
        style = block.get("style", "")
        size = block.get("size", 9)
        line_h = block.get("line_h", 4)
        text = block.get("text", "")

        pdf.set_font(font, style, size)
        pdf.set_x(col_x)

        # Use multi_cell with explicit width
        old_l = pdf.l_margin
        old_r = pdf.r_margin
        pdf.set_left_margin(col_x)
        pdf.set_right_margin(pdf.w - col_x - col_w)
        pdf.multi_cell(col_w, line_h, text)
        pdf.set_left_margin(old_l)
        pdf.set_right_margin(old_r)
        pdf.set_x(col_x)

    return pdf.get_y()


def main():
    pdf = IEEEReport()
    pdf.set_margins(12.7, 15, 12.7)  # ~0.5 inch margins (IEEE)

    page_w = pdf.w
    page_h = pdf.h
    left_m = 12.7
    right_m = 12.7
    top_m = 15
    bottom_m = 18
    col_gap = 5
    usable_w = page_w - left_m - right_m
    col_w = (usable_w - col_gap) / 2
    col1_x = left_m
    col2_x = left_m + col_w + col_gap

    # ===== PÁGINA 1 =====
    pdf.add_page()

    # Título centralizado (full width) - estilo IEEE
    pdf.set_font("TNR", "B", 14)
    pdf.set_xy(left_m, top_m)
    pdf.multi_cell(usable_w, 6, "Implementando Padrões de Teste (Test Patterns)\nem um Serviço de Checkout de E-commerce", align="C")
    pdf.ln(3)

    # Autor
    pdf.set_font("TNR", "", 11)
    pdf.set_x(left_m)
    pdf.multi_cell(usable_w, 5, "Arthur Curi Kramberger\nMatrícula: 729488\nAnálise e Construção de Software", align="C")
    pdf.ln(2)

    # Linha separadora
    y_line = pdf.get_y()
    pdf.line(left_m, y_line, page_w - right_m, y_line)
    pdf.ln(4)

    y_cols_start = pdf.get_y()

    # --- Conteúdo coluna 1, página 1 ---
    col1_blocks_p1 = [
        {"type": "text", "text": "Resumo", "style": "B", "size": 9, "line_h": 4},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "I", "size": 9, "line_h": 3.8,
         "text": "Este relatório apresenta a implementação de padrões de teste "
                 "(Test Patterns) aplicados a um serviço de Checkout de E-commerce. "
                 "São abordados os padrões Object Mother e Data Builder para criação "
                 "de dados de teste, além dos padrões Stub e Mock para isolamento de "
                 "dependências externas. O trabalho demonstra como esses padrões "
                 "previnem Test Smells e contribuem para uma suíte de testes sustentável."},
        {"type": "spacing", "h": 4},
        {"type": "text", "text": "I. INTRODUÇÃO", "style": "B", "size": 9, "line_h": 4.5},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "No desenvolvimento de software, testes automatizados são fundamentais "
                 "para garantir a qualidade do código. Porém, testes mal escritos podem "
                 "se tornar um fardo: difíceis de ler, frágeis e custosos de manter. "
                 "Os Test Smells, como Setup Obscuro e Testes Frágeis, são sintomas de "
                 "testes que não seguem boas práticas de design."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "Este trabalho aplica padrões de teste consagrados para resolver dois "
                 "problemas centrais: (1) a criação de dados de teste de forma legível "
                 "e flexível, utilizando Object Mother e Data Builder; e (2) o isolamento "
                 "de dependências externas, utilizando Stubs e Mocks. O sistema sob teste "
                 "(SUT) é um CheckoutService que processa pedidos de e-commerce, integrando "
                 "gateway de pagamento, repositório de dados e serviço de e-mail."},
        {"type": "spacing", "h": 4},
        {"type": "text", "text": "II. PADRÕES DE CRIAÇÃO DE DADOS", "style": "B", "size": 9, "line_h": 4.5},
        {"type": "spacing", "h": 1},
        {"type": "text", "text": "A. Por que CarrinhoBuilder em vez de CarrinhoMother?", "style": "BI", "size": 9, "line_h": 4},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "O padrão Object Mother é ideal para entidades simples e estáveis, como "
                 "o User, que possui poucos atributos e variações previsíveis (PADRAO ou "
                 "PREMIUM). Para o User, criamos UserMother com métodos estáticos como "
                 "umUsuarioPadrao() e umUsuarioPremium()."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "Já o Carrinho é um objeto complexo: pode ter diferentes usuários, "
                 "quantidades variáveis de itens, valores distintos, ou estar vazio. "
                 "Se usássemos um Object Mother para o Carrinho, teríamos uma explosão "
                 "combinatória de métodos: carrinhoVazio(), carrinhoComUmItem(), "
                 "carrinhoPremiumComDoisItens(), etc."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "O Data Builder resolve isso com uma API fluente que permite compor o "
                 "objeto passo a passo, tornando explícito apenas o que é relevante para "
                 "cada teste. Isso elimina o Test Smell de Setup Obscuro."},
    ]

    pdf.set_y(y_cols_start)
    write_col(pdf, col1_x, col_w, col1_blocks_p1, page_h, bottom_m)

    # --- Conteúdo coluna 2, página 1 ---
    col2_blocks_p1 = [
        {"type": "text", "text": 'B. Exemplo: "Antes" vs. "Depois"', "style": "BI", "size": 9, "line_h": 4},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "Antes (setup manual complexo e obscuro):"},
        {"type": "spacing", "h": 1},
        {"type": "code", "size": 7, "lines": [
            "// Setup manual - dificil de ler",
            "const user = new User(2, 'Maria',",
            "  'premium@email.com', 'PREMIUM');",
            "const item1 = new Item('Camiseta', 100);",
            "const item2 = new Item('Calca', 100);",
            "const carrinho = new Carrinho(",
            "  user, [item1, item2]);",
        ]},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "Depois (usando Data Builder):"},
        {"type": "spacing", "h": 1},
        {"type": "code", "size": 7, "lines": [
            "// Setup com Builder - legivel e claro",
            "const carrinho = new CarrinhoBuilder()",
            "  .comUser(UserMother.umUsuarioPremium())",
            "  .comItens([",
            "    new Item('Camiseta', 100),",
            "    new Item('Calca', 100)",
            "  ])",
            "  .build();",
        ]},
        {"type": "spacing", "h": 3},
        {"type": "text", "text": "C. Como o Builder melhora legibilidade e manutenção", "style": "BI", "size": 9, "line_h": 4},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "1) Legibilidade: O Builder torna o teste auto-documentado. Ao ler "
                 ".comUser(umUsuarioPremium()), o leitor entende imediatamente o cenário "
                 "sem precisar decifrar parâmetros de construtores."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "2) Manutenção: Se o construtor de Carrinho mudar (ex: adicionar campo "
                 "'cupom'), apenas o Builder precisa ser atualizado. Todos os testes que "
                 "usam o Builder continuam funcionando sem alteração."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "3) Foco: Cada teste explicita apenas os dados relevantes para seu "
                 "cenário. Valores padrão sensatos no construtor do Builder eliminam ruído."},
        {"type": "spacing", "h": 4},
        {"type": "text", "text": "III. PADRÕES DE TEST DOUBLES", "style": "B", "size": 9, "line_h": 4.5},
        {"type": "spacing", "h": 1},
        {"type": "text", "text": "A. Identificação no teste de sucesso Premium", "style": "BI", "size": 9, "line_h": 4},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "No teste 'quando um cliente Premium finaliza a compra', três "
                 "dependências externas são substituídas por dublês de teste:"},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "- GatewayPagamento: Stub (retorna {success: true})\n"
                 "- PedidoRepository: Stub (retorna pedido com ID)\n"
                 "- EmailService: Mock (verificamos a chamada)"},
    ]

    pdf.set_y(y_cols_start)
    write_col(pdf, col2_x, col_w, col2_blocks_p1, page_h, bottom_m)

    # ===== PÁGINA 2 =====
    pdf.add_page()
    y_cols_start = top_m + 2

    col1_blocks_p2 = [
        {"type": "text", "text": "B. Por que GatewayPagamento é um Stub?", "style": "BI", "size": 9, "line_h": 4},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "Um Stub é um dublê que fornece respostas pré-definidas para controlar "
                 "o fluxo de execução do SUT. O GatewayPagamento é configurado para "
                 "retornar {success: true}, permitindo que o teste avance para as etapas "
                 "seguintes do checkout."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "A verificação principal sobre o gateway é de Estado: verificamos que o "
                 "valor passado ao método cobrar() foi R$180,00 (com desconto aplicado). "
                 "Não estamos interessados em como o gateway processa internamente, apenas "
                 "que recebeu o valor correto. Isso caracteriza Verificação de Estado "
                 "(State Verification)."},
        {"type": "spacing", "h": 4},
        {"type": "text", "text": "C. Por que EmailService é um Mock?", "style": "BI", "size": 9, "line_h": 4},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "Um Mock é um dublê usado para Verificação de Comportamento (Behavior "
                 "Verification). O EmailService representa um efeito colateral: o envio "
                 "de e-mail não retorna um valor que afete o fluxo do checkout, mas é uma "
                 "ação importante que deve ocorrer."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "Por isso, verificamos:\n"
                 "- Que enviarEmail() foi chamado exatamente 1 vez\n"
                 "- Que foi chamado com o e-mail correto do usuário\n"
                 "- Que a mensagem contém o ID do pedido"},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "Essa é a essência da distinção proposta por Martin Fowler [1]: Stubs "
                 "controlam entradas indiretas (o que o SUT recebe), enquanto Mocks "
                 "verificam saídas indiretas (o que o SUT faz com o mundo externo)."},
        {"type": "spacing", "h": 4},
        {"type": "text", "text": "D. Resumo comparativo", "style": "BI", "size": 9, "line_h": 4},
        {"type": "spacing", "h": 2},
        {"type": "table",
         "headers": ["Dependência", "Tipo", "Verificação"],
         "rows": [
             ["Gateway", "Stub", "Estado (valor)"],
             ["Repository", "Stub", "Estado (retorno)"],
             ["EmailService", "Mock", "Comportamento"],
         ]},
        {"type": "spacing", "h": 3},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "O código do teste demonstra claramente essa separação. O jest.fn() "
                 "com mockResolvedValue configura o Stub (controle de retorno), enquanto "
                 "as asserções toHaveBeenCalledWith e toHaveBeenCalledTimes verificam o "
                 "comportamento do Mock."},
    ]

    pdf.set_y(y_cols_start)
    write_col(pdf, col1_x, col_w, col1_blocks_p2, page_h, bottom_m)

    col2_blocks_p2 = [
        {"type": "text", "text": "IV. CONCLUSÃO", "style": "B", "size": 9, "line_h": 4.5},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "O uso deliberado de Padrões de Teste demonstrou ser uma estratégia "
                 "eficaz para prevenir Test Smells e construir uma suíte de testes "
                 "sustentável. Os principais benefícios observados foram:"},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "1) Prevenção de Setup Obscuro: O Data Builder torna cada teste "
                 "auto-explicativo, eliminando a necessidade de decifrar construtores "
                 "complexos com múltiplos parâmetros posicionais."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "2) Eliminação de Testes Frágeis: Ao isolar dependências externas com "
                 "Stubs e Mocks, os testes não quebram por mudanças em serviços externos "
                 "(banco de dados, APIs de pagamento, servidores SMTP)."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "3) Separação de responsabilidades na verificação: Stubs permitem focar "
                 "na lógica de negócio (o desconto foi calculado corretamente?), enquanto "
                 "Mocks garantem que efeitos colaterais importantes ocorrem (o e-mail foi "
                 "enviado?)."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "4) Manutenibilidade: Quando o domínio evolui, apenas os Builders "
                 "precisam ser atualizados, não dezenas de testes individuais. Isso reduz "
                 "drasticamente o custo de manutenção da suíte."},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "5) Padrão AAA (Arrange-Act-Assert): Os padrões aplicados naturalmente "
                 "guiam o desenvolvedor a estruturar testes com separação clara entre "
                 "preparação, execução e verificação, melhorando a legibilidade."},
        {"type": "spacing", "h": 3},
        {"type": "text", "style": "", "size": 9, "line_h": 3.8,
         "text": "Em suma, investir em padrões de teste não é overhead — é uma prática "
                 "de engenharia que transforma testes de um custo contínuo em um ativo de "
                 "longo prazo, capaz de evoluir junto com o sistema que protege."},
        {"type": "spacing", "h": 6},
        {"type": "text", "text": "REFERÊNCIAS", "style": "B", "size": 9, "line_h": 4.5},
        {"type": "spacing", "h": 2},
        {"type": "text", "style": "", "size": 8, "line_h": 3.5,
         "text": '[1] M. Fowler, "Mocks Aren\'t Stubs", martinfowler.com, 2007.'},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 8, "line_h": 3.5,
         "text": '[2] G. Meszaros, "xUnit Test Patterns: Refactoring Test Code", '
                 "Addison-Wesley, 2007."},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 8, "line_h": 3.5,
         "text": '[3] Jest Documentation, "Mock Functions", jestjs.io/docs/mock-functions.'},
        {"type": "spacing", "h": 1},
        {"type": "text", "style": "", "size": 8, "line_h": 3.5,
         "text": '[4] R. C. Martin, "Clean Code: A Handbook of Agile Software '
                 'Craftsmanship", Prentice Hall, 2008.'},
    ]

    pdf.set_y(y_cols_start)
    write_col(pdf, col2_x, col_w, col2_blocks_p2, page_h, bottom_m)

    output_path = "/Users/ak/Downloads/acds/test-pattern/Relatorio_Test_Patterns.pdf"
    pdf.output(output_path)
    print(f"PDF gerado: {output_path}")


if __name__ == "__main__":
    main()
