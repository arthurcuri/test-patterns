export class Pedido {
    constructor(id, carrinho, totalFinal, status) {
        this.id = id;
        this.carrinho = carrinho;
        this.totalFinal = totalFinal;
        this.status = status; // 'PROCESSADO' ou 'FALHOU'
    }
}