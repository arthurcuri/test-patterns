# Implementando Padrões de Teste (Test Patterns)

**Disciplina:** Análise e Construção de Software  
**Aluno:** Arthur Curi Kramberger  
**Matrícula:** 729488

---

## Estrutura do Projeto

```
test-pattern/
├── src/
│   ├── domain/
│   │   ├── User.js
│   │   ├── Carrinho.js
│   │   ├── Item.js
│   │   └── Pedido.js
│   └── services/
│       ├── CheckoutService.js    ← SUT (System Under Test)
│       ├── GatewayPagamento.js
│       ├── EmailService.js
│       └── PedidoRepository.js
├── __tests__/
│   ├── builders/
│   │   ├── UserMother.js         ← Padrão Object Mother
│   │   └── CarrinhoBuilder.js    ← Padrão Data Builder
│   └── CheckoutService.test.js   ← Testes com Stubs e Mocks
├── babel.config.js
├── package.json
└── Relatorio_Test_Patterns.pdf
```

---

## Como Executar

```bash
# Instalar dependências
npm install

# Rodar os testes
npm test

# Rodar com cobertura
npm run coverage
```

---

## Resultados dos Testes

```
 PASS  __tests__/CheckoutService.test.js
  CheckoutService
    quando o pagamento falha
      ✓ deve retornar null se o gateway recusar a cobrança
    quando um cliente Premium finaliza a compra
      ✓ deve aplicar 10% de desconto e enviar e-mail de confirmação
    quando um cliente Padrão finaliza a compra
      ✓ deve cobrar o valor total sem desconto
    quando o envio de e-mail falha
      ✓ deve retornar o pedido mesmo se o e-mail falhar

Test Suites: 1 passed, 1 total
Tests:       4 passed, 4 total
```

---

## Relatório: Padrões de Teste Implementados

### I. Introdução

Este trabalho aplica padrões de teste consagrados para resolver dois problemas centrais no desenvolvimento de testes automatizados: (1) a criação de dados de teste de forma legível e flexível, utilizando **Object Mother** e **Data Builder**; e (2) o isolamento de dependências externas, utilizando **Stubs** e **Mocks**.

O sistema sob teste (SUT) é o `CheckoutService`, que processa pedidos de e-commerce integrando gateway de pagamento, repositório de dados e serviço de e-mail.

---

### II. Padrões de Criação de Dados

#### A. Por que CarrinhoBuilder em vez de CarrinhoMother?

O padrão **Object Mother** é ideal para entidades simples e estáveis, como o `User`, que possui poucos atributos e variações previsíveis (`PADRAO` ou `PREMIUM`). Para o User, criamos `UserMother` com métodos estáticos como `umUsuarioPadrao()` e `umUsuarioPremium()`.

Já o `Carrinho` é um objeto complexo: pode ter diferentes usuários, quantidades variáveis de itens, valores distintos, ou estar vazio. Se usássemos um Object Mother para o Carrinho, teríamos uma **explosão combinatória de métodos**: `carrinhoVazio()`, `carrinhoComUmItem()`, `carrinhoPremiumComDoisItens()`, etc. Cada novo cenário de teste exigiria um novo método.

O **Data Builder** resolve isso com uma API fluente que permite compor o objeto passo a passo, tornando explícito apenas o que é relevante para cada teste. Isso elimina o Test Smell de **Setup Obscuro**.

#### B. Exemplo: "Antes" vs. "Depois"

**Antes** (setup manual complexo e obscuro):

```javascript
// Setup manual - difícil de ler, muitos detalhes irrelevantes
const user = new User(2, 'Maria Premium', 'premium@email.com', 'PREMIUM');
const item1 = new Item('Camiseta', 100);
const item2 = new Item('Calça', 100);
const carrinho = new Carrinho(user, [item1, item2]);
```

**Depois** (usando Data Builder):

```javascript
// Setup com Builder - legível, foco no que importa
const carrinho = new CarrinhoBuilder()
    .comUser(UserMother.umUsuarioPremium())
    .comItens([
        new Item('Camiseta', 100),
        new Item('Calça', 100)
    ])
    .build();
```

#### C. Como o Builder melhora legibilidade e manutenção

1. **Legibilidade:** O Builder torna o teste auto-documentado. Ao ler `.comUser(umUsuarioPremium())`, o leitor entende imediatamente o cenário sem precisar decifrar parâmetros de construtores.

2. **Manutenção:** Se o construtor de `Carrinho` mudar (ex: adicionar campo `cupom`), apenas o Builder precisa ser atualizado. Todos os testes que usam o Builder continuam funcionando sem alteração.

3. **Foco:** Cada teste explicita apenas os dados relevantes para seu cenário. Valores padrão sensatos no construtor do Builder eliminam ruído.

---

### III. Padrões de Test Doubles (Mocks vs. Stubs)

#### A. Identificação no teste de sucesso Premium

No teste `'quando um cliente Premium finaliza a compra'`, três dependências externas são substituídas por dublês:

| Dependência | Tipo de Dublê | Verificação |
|---|---|---|
| `GatewayPagamento` | **Stub** | Estado (valor passado) |
| `PedidoRepository` | **Stub** | Estado (retorno) |
| `EmailService` | **Mock** | Comportamento (chamada) |

#### B. Por que GatewayPagamento é um Stub?

Um **Stub** é um dublê que fornece respostas pré-definidas para controlar o fluxo de execução do SUT. O `GatewayPagamento` é configurado para retornar `{ success: true }`, permitindo que o teste avance para as etapas seguintes do checkout.

A verificação principal sobre o gateway é de **Estado**: verificamos que o valor passado ao método `cobrar()` foi R$180,00 (com desconto aplicado). Não estamos interessados em como o gateway processa internamente, apenas que recebeu o valor correto. Isso caracteriza **Verificação de Estado** (State Verification).

```javascript
// Stub: controla o retorno
const gatewayStub = {
    cobrar: jest.fn().mockResolvedValue({ success: true })
};

// Verificação de Estado: o valor correto foi passado?
expect(gatewayStub.cobrar).toHaveBeenCalledWith(180, cartaoCredito);
```

#### C. Por que EmailService é um Mock?

Um **Mock** é um dublê usado para **Verificação de Comportamento** (Behavior Verification). O `EmailService` representa um efeito colateral: o envio de e-mail não retorna um valor que afete o fluxo do checkout, mas é uma ação importante que deve ocorrer.

Por isso, verificamos:
- Que `enviarEmail()` foi chamado exatamente 1 vez
- Que foi chamado com o e-mail correto do usuário
- Que a mensagem contém o ID do pedido

```javascript
// Mock: verificamos o comportamento
expect(emailMock.enviarEmail).toHaveBeenCalledTimes(1);
expect(emailMock.enviarEmail).toHaveBeenCalledWith(
    'premium@email.com',
    'Seu Pedido foi Aprovado!',
    expect.stringContaining('pedido-123')
);
```

Essa é a essência da distinção proposta por Martin Fowler [1]: **Stubs controlam entradas indiretas** (o que o SUT recebe), enquanto **Mocks verificam saídas indiretas** (o que o SUT faz com o mundo externo).

---

### IV. Conclusão

O uso deliberado de Padrões de Teste demonstrou ser uma estratégia eficaz para prevenir Test Smells e construir uma suíte de testes sustentável:

1. **Prevenção de Setup Obscuro:** O Data Builder torna cada teste auto-explicativo, eliminando a necessidade de decifrar construtores complexos com múltiplos parâmetros posicionais.

2. **Eliminação de Testes Frágeis:** Ao isolar dependências externas com Stubs e Mocks, os testes não quebram por mudanças em serviços externos (banco de dados, APIs de pagamento, servidores SMTP).

3. **Separação de responsabilidades na verificação:** Stubs permitem focar na lógica de negócio (o desconto foi calculado corretamente?), enquanto Mocks garantem que efeitos colaterais importantes ocorrem (o e-mail foi enviado?).

4. **Manutenibilidade:** Quando o domínio evolui, apenas os Builders precisam ser atualizados, não dezenas de testes individuais.

5. **Padrão AAA (Arrange-Act-Assert):** Os padrões aplicados naturalmente guiam o desenvolvedor a estruturar testes com separação clara entre preparação, execução e verificação.

Em suma, investir em padrões de teste não é overhead — é uma prática de engenharia que transforma testes de um custo contínuo em um ativo de longo prazo, capaz de evoluir junto com o sistema que protege.

---

### Referências

- [1] M. Fowler, "Mocks Aren't Stubs", martinfowler.com, 2007. https://martinfowler.com/articles/mocksArentStubs.html
- [2] G. Meszaros, "xUnit Test Patterns: Refactoring Test Code", Addison-Wesley, 2007. http://xunitpatterns.com/
- [3] Jest Documentation, "Mock Functions". https://jestjs.io/docs/mock-functions
- [4] R. C. Martin, "Clean Code: A Handbook of Agile Software Craftsmanship", Prentice Hall, 2008.
