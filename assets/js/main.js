/**
 * Saia do Vermelho - Scripts compartilhados
 * Simula integração com Hotmart/Kiwify e gerencia estado do aluno
 */

(function() {
    'use strict';

    // ---- Constantes ----
    var STORAGE_KEY = 'aluno_acesso';

    // ---- Verificar acesso ----
    window.temAcesso = function() {
        return localStorage.getItem(STORAGE_KEY) === 'true';
    };

    // ---- Liberar acesso (simula webhook pós-pagamento) ----
    window.liberarAcesso = function(email, nome) {
        localStorage.setItem(STORAGE_KEY, 'true');
        localStorage.setItem('aluno_email', email || '');
        localStorage.setItem('aluno_nome', nome || 'Aluno');
        localStorage.setItem('data_compra', new Date().toLocaleDateString('pt-BR'));
    };

    // ---- Remover acesso ----
    window.removerAcesso = function() {
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem('aluno_email');
        localStorage.removeItem('aluno_nome');
        localStorage.removeItem('data_compra');
        localStorage.removeItem('progresso_aulas');
    };

    // ---- Redirecionar para checkout se não tiver acesso ----
    window.protegerPagina = function() {
        if (!window.temAcesso()) {
            window.location.href = 'index.html';
        }
    };

    // ---- Formatar moeda ----
    window.formatarMoeda = function(valor) {
        return 'R$ ' + parseFloat(valor).toFixed(2).replace('.', ',');
    };

    // ---- Máscara de cartão ----
    document.addEventListener('DOMContentLoaded', function() {
        var cardInput = document.querySelector('input[placeholder*="0000"]');
        if (cardInput) {
            cardInput.addEventListener('input', function(e) {
                var val = e.target.value.replace(/\D/g, '').substring(0, 16);
                var formatted = val.replace(/(\d{4})(?=\d)/g, '$1 ');
                e.target.value = formatted;
            });
        }

        var cpfInput = document.querySelector('input[placeholder*="000.000"]');
        if (cpfInput) {
            cpfInput.addEventListener('input', function(e) {
                var val = e.target.value.replace(/\D/g, '').substring(0, 11);
                var formatted = val.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
                e.target.value = formatted;
            });
        }

        var dateInput = document.querySelector('input[placeholder*="MM/AA"]');
        if (dateInput) {
            dateInput.addEventListener('input', function(e) {
                var val = e.target.value.replace(/\D/g, '').substring(0, 4);
                if (val.length > 2) {
                    val = val.substring(0, 2) + '/' + val.substring(2);
                }
                e.target.value = val;
            });
        }

        var phoneInput = document.querySelector('input[type="tel"]');
        if (phoneInput) {
            phoneInput.addEventListener('input', function(e) {
                var val = e.target.value.replace(/\D/g, '').substring(0, 11);
                if (val.length > 2) {
                    val = '(' + val.substring(0, 2) + ') ' + val.substring(2);
                    if (val.length > 10) {
                        val = val.substring(0, 10) + '-' + val.substring(10);
                    }
                }
                e.target.value = val;
            });
        }
    });

})();
