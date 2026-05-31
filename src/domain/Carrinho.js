export class Carrinho {
    constructor(user, itens = []) {
        this.user = user;
        this.itens = itens;
    }

    calcularTotal() {
        return this.itens.reduce((total, item) => total + item.preco, 0);
    }
}