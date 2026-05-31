import { User } from '../../src/domain/User.js';

/**
 * Padrão Object Mother
 * Cria instâncias de User com dados pré-definidos e fixos.
 * Útil para entidades simples que raramente mudam entre os testes.
 */
export class UserMother {

    static umUsuarioPadrao() {
        return new User(1, 'João Silva', 'joao@email.com', 'PADRAO');
    }

    static umUsuarioPremium() {
        return new User(2, 'Maria Premium', 'premium@email.com', 'PREMIUM');
    }

    static umUsuarioComEmail(email) {
        return new User(3, 'Usuário Teste', email, 'PADRAO');
    }
}
