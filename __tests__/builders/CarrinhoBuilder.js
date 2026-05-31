import { Carrinho } from '../../src/domain/Carrinho.js';
import { Item } from '../../src/domain/Item.js';
import { UserMother } from './UserMother.js';

/**
 * Padrão Data Builder
 * Cria instâncias de Carrinho de forma fluente e customizável.
 * Resolve o Test Smell de "Setup Obscuro" ao tornar explícito
 * apenas o que é relevante para cada cenário de teste.
 */
export class CarrinhoBuilder {

    constructor() {
        // Valores padrão: um carrinho com 1 item e um usuário padrão
        this._user = UserMother.umUsuarioPadrao();
        this._itens = [new Item('Produto Padrão', 100)];
    }

    /**
     * Define o usuário do carrinho.
     * @param {User} user
     * @returns {CarrinhoBuilder}
     */
    comUser(user) {
        this._user = user;
        return this;
    }

    /**
     * Define os itens do carrinho.
     * @param {Item[]} itens
     * @returns {CarrinhoBuilder}
     */
    comItens(itens) {
        this._itens = itens;
        return this;
    }

    /**
     * Adiciona um item ao carrinho.
     * @param {string} nome
     * @param {number} preco
     * @returns {CarrinhoBuilder}
     */
    comItem(nome, preco) {
        this._itens.push(new Item(nome, preco));
        return this;
    }

    /**
     * Cria um carrinho vazio (sem itens).
     * @returns {CarrinhoBuilder}
     */
    vazio() {
        this._itens = [];
        return this;
    }

    /**
     * Constrói e retorna a instância final do Carrinho.
     * @returns {Carrinho}
     */
    build() {
        return new Carrinho(this._user, this._itens);
    }
}
