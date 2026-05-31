export class GatewayPagamento {
    // Retorna { success: true } ou { success: false, error: '...' }
    async cobrar(valor, cartao) {
        throw new Error("Não deve chamar o Gateway real");
    }
}