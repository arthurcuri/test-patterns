import { CheckoutService } from '../src/services/CheckoutService.js';
import { UserMother } from './builders/UserMother.js';
import { CarrinhoBuilder } from './builders/CarrinhoBuilder.js';
import { Item } from '../src/domain/Item.js';

describe('CheckoutService', () => {

    // =========================================================================
    // ETAPA 4: Padrão Stub (Verificação de Estado)
    // =========================================================================
    describe('quando o pagamento falha', () => {

        it('deve retornar null se o gateway recusar a cobrança', async () => {
            // Arrange
            const carrinho = new CarrinhoBuilder().build();

            // Stub do GatewayPagamento: retorna falha
            const gatewayStub = {
                cobrar: jest.fn().mockResolvedValue({ success: false })
            };

            // Dummies: não devem ser chamados neste cenário
            const repositoryDummy = {
                salvar: jest.fn()
            };
            const emailDummy = {
                enviarEmail: jest.fn()
            };

            const checkoutService = new CheckoutService(
                gatewayStub,
                repositoryDummy,
                emailDummy
            );

            // Act
            const pedido = await checkoutService.processarPedido(carrinho, '4111111111111111');

            // Assert (Verificação de Estado)
            expect(pedido).toBeNull();

            // Verificações adicionais: as dependências posteriores NÃO devem ter sido chamadas
            expect(repositoryDummy.salvar).not.toHaveBeenCalled();
            expect(emailDummy.enviarEmail).not.toHaveBeenCalled();
        });
    });

    // =========================================================================
    // ETAPA 5: Padrão Mock (Verificação de Comportamento)
    // =========================================================================
    describe('quando um cliente Premium finaliza a compra', () => {

        it('deve aplicar 10% de desconto e enviar e-mail de confirmação', async () => {
            // Arrange
            const usuarioPremium = UserMother.umUsuarioPremium();

            const carrinho = new CarrinhoBuilder()
                .comUser(usuarioPremium)
                .comItens([
                    new Item('Camiseta', 100),
                    new Item('Calça', 100)
                ])
                .build();

            // Total: R$ 200,00 → com desconto Premium (10%): R$ 180,00
            const cartaoCredito = '4111111111111111';

            // Stub do GatewayPagamento: retorna sucesso
            const gatewayStub = {
                cobrar: jest.fn().mockResolvedValue({ success: true })
            };

            // Stub do PedidoRepository: retorna o pedido salvo com ID
            const repositoryStub = {
                salvar: jest.fn().mockImplementation(async (pedido) => {
                    return { ...pedido, id: 'pedido-123' };
                })
            };

            // Mock do EmailService: queremos verificar se foi chamado corretamente
            const emailMock = {
                enviarEmail: jest.fn().mockResolvedValue(true)
            };

            const checkoutService = new CheckoutService(
                gatewayStub,
                repositoryStub,
                emailMock
            );

            // Act
            const pedidoSalvo = await checkoutService.processarPedido(carrinho, cartaoCredito);

            // Assert (Verificação de Comportamento)

            // 1. O gateway foi chamado com o valor COM desconto (180)
            expect(gatewayStub.cobrar).toHaveBeenCalledWith(180, cartaoCredito);

            // 2. O repositório foi chamado para salvar o pedido
            expect(repositoryStub.salvar).toHaveBeenCalledTimes(1);

            // 3. O e-mail foi enviado exatamente 1 vez
            expect(emailMock.enviarEmail).toHaveBeenCalledTimes(1);

            // 4. O e-mail foi enviado com os argumentos corretos
            expect(emailMock.enviarEmail).toHaveBeenCalledWith(
                'premium@email.com',
                'Seu Pedido foi Aprovado!',
                expect.stringContaining('pedido-123')
            );

            // 5. O pedido retornado está correto (Verificação de Estado)
            expect(pedidoSalvo).not.toBeNull();
            expect(pedidoSalvo.id).toBe('pedido-123');
            expect(pedidoSalvo.totalFinal).toBe(180);
        });
    });

    // =========================================================================
    // Cenário adicional: Cliente Padrão (sem desconto)
    // =========================================================================
    describe('quando um cliente Padrão finaliza a compra', () => {

        it('deve cobrar o valor total sem desconto', async () => {
            // Arrange
            const usuarioPadrao = UserMother.umUsuarioPadrao();

            const carrinho = new CarrinhoBuilder()
                .comUser(usuarioPadrao)
                .comItens([new Item('Tênis', 250)])
                .build();

            const cartaoCredito = '5500000000000004';

            const gatewayStub = {
                cobrar: jest.fn().mockResolvedValue({ success: true })
            };

            const repositoryStub = {
                salvar: jest.fn().mockImplementation(async (pedido) => {
                    return { ...pedido, id: 'pedido-456' };
                })
            };

            const emailMock = {
                enviarEmail: jest.fn().mockResolvedValue(true)
            };

            const checkoutService = new CheckoutService(
                gatewayStub,
                repositoryStub,
                emailMock
            );

            // Act
            const pedidoSalvo = await checkoutService.processarPedido(carrinho, cartaoCredito);

            // Assert
            // Sem desconto: valor total = R$ 250,00
            expect(gatewayStub.cobrar).toHaveBeenCalledWith(250, cartaoCredito);
            expect(pedidoSalvo).not.toBeNull();
            expect(pedidoSalvo.totalFinal).toBe(250);
            expect(emailMock.enviarEmail).toHaveBeenCalledWith(
                'joao@email.com',
                'Seu Pedido foi Aprovado!',
                expect.stringContaining('pedido-456')
            );
        });
    });

    // =========================================================================
    // Cenário adicional: Falha no envio de e-mail não impede o checkout
    // =========================================================================
    describe('quando o envio de e-mail falha', () => {

        it('deve retornar o pedido mesmo se o e-mail falhar', async () => {
            // Arrange
            const carrinho = new CarrinhoBuilder().build();

            const gatewayStub = {
                cobrar: jest.fn().mockResolvedValue({ success: true })
            };

            const repositoryStub = {
                salvar: jest.fn().mockImplementation(async (pedido) => {
                    return { ...pedido, id: 'pedido-789' };
                })
            };

            // Mock que simula falha no envio de e-mail
            const emailMock = {
                enviarEmail: jest.fn().mockRejectedValue(new Error('SMTP timeout'))
            };

            const checkoutService = new CheckoutService(
                gatewayStub,
                repositoryStub,
                emailMock
            );

            // Act
            const pedidoSalvo = await checkoutService.processarPedido(carrinho, '4111111111111111');

            // Assert: o pedido foi salvo mesmo com falha no e-mail
            expect(pedidoSalvo).not.toBeNull();
            expect(pedidoSalvo.id).toBe('pedido-789');
            // O e-mail foi tentado
            expect(emailMock.enviarEmail).toHaveBeenCalledTimes(1);
        });
    });
});
