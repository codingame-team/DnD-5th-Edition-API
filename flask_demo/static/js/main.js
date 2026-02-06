/**
 * Fonctions JavaScript communes pour l'application Flask D&D 5e
 */

// Utilitaires généraux
const utils = {
    /**
     * Affiche un message de notification
     */
    notify: function(message, type = 'info') {
        // TODO: Implémenter un système de notifications toast
        console.log(`[${type.toUpperCase()}] ${message}`);
    },

    /**
     * Formate un nombre avec séparateurs de milliers
     */
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    },

    /**
     * Calcule le modificateur de caractéristique
     */
    getModifier: function(score) {
        return Math.floor((score - 10) / 2);
    },

    /**
     * Formate le modificateur avec le signe
     */
    formatModifier: function(score) {
        const mod = this.getModifier(score);
        return mod >= 0 ? `+${mod}` : `${mod}`;
    }
};

// API Helpers
const api = {
    /**
     * Effectue une requête GET à l'API
     */
    get: async function(endpoint) {
        try {
            const response = await fetch(endpoint);
            return await response.json();
        } catch (error) {
            utils.notify('Erreur de connexion à l\'API', 'error');
            throw error;
        }
    },

    /**
     * Effectue une requête POST à l'API
     */
    post: async function(endpoint, data) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            utils.notify('Erreur de connexion à l\'API', 'error');
            throw error;
        }
    }
};

// Validation de formulaires
const validation = {
    /**
     * Valide qu'un champ n'est pas vide
     */
    required: function(value, fieldName) {
        if (!value || value.trim() === '') {
            throw new Error(`${fieldName} est requis`);
        }
        return true;
    },

    /**
     * Valide qu'un nombre est dans une plage
     */
    inRange: function(value, min, max, fieldName) {
        const num = parseInt(value);
        if (isNaN(num) || num < min || num > max) {
            throw new Error(`${fieldName} doit être entre ${min} et ${max}`);
        }
        return true;
    }
};

// Animations
const animations = {
    /**
     * Fait apparaître un élément avec un effet de fade
     */
    fadeIn: function(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';

        let opacity = 0;
        const timer = setInterval(function() {
            opacity += 50 / duration;
            element.style.opacity = opacity.toString();
            if (opacity >= 1) {
                clearInterval(timer);
            }
        }, 50);
    },

    /**
     * Fait disparaître un élément avec un effet de fade
     */
    fadeOut: function(element, duration = 300) {
        let opacity = 1;
        const timer = setInterval(function() {
            opacity -= 50 / duration;
            element.style.opacity = opacity.toString();
            if (opacity <= 0) {
                clearInterval(timer);
                element.style.display = 'none';
            }
        }, 50);
    }
};

// Export global
window.dndApp = {
    utils,
    api,
    validation,
    animations
};

// Gestion des erreurs globales
window.addEventListener('error', function(event) {
    console.error('Erreur JavaScript:', event.error);
});

// Log de chargement
console.log('🎲 D&D 5e Demo - JavaScript loaded');
