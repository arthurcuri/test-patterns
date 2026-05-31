export class User {
    constructor(id, nome, email, tipo = 'PADRAO') {
        this.id = id;
        this.nome = nome;
        this.email = email;
        this.tipo = tipo; // 'PADRAO' ou 'PREMIUM'
    }

    isPremium() {
        return this.tipo === 'PREMIUM';
    }
}