# 🎲 D&D 5e Flask Demo - Bootstrap Edition

Application web de démonstration utilisant **dnd-5e-core** avec interface Bootstrap 5.

## ✨ Nouveautés v2.0

### Interface Modernisée
- ✅ **Bootstrap 5.3** pour un design professionnel et responsive
- ✅ **Bootstrap Icons** pour les icônes
- ✅ Thème sombre personnalisé
- ✅ **Minimal JavaScript** - Logique principalement côté serveur (Flask)

### Architecture Simplifiée
- ✅ Templates Flask avec Jinja2
- ✅ Formulaires HTML standards (POST)
- ✅ Utilisation maximale des structures de données dnd-5e-core
- ✅ JavaScript uniquement pour l'interactivité essentielle

## 🚀 Installation

### Prérequis
- Python 3.9+
- pip

### Installation

```bash
cd flask_demo
pip install -r requirements.txt
```

## 📖 Utilisation

### Lancer l'Application

```bash
python app.py
```

Ou avec le script :
```bash
./run.sh
```

Puis ouvrez : **http://localhost:5000**

## 🎮 Fonctionnalités

### 1. Création de Personnages
- Formulaire HTML classique
- Sélection de race et classe
- Niveau de 1 à 20
- Affichage immédiat des caractéristiques après création

### 2. Gestion de Groupe
- Visualisation de tous vos personnages
- Statistiques complètes (PV, CA, XP, caractéristiques)
- Suppression de personnages
- Design en cartes Bootstrap

### 3. Système de Combat
- Sélection de monstres prédéfinis
- Rencontres rapides (Facile, Moyen, Difficile, Mortel)
- Interface simplifiée avec JavaScript minimal

## 🏗️ Architecture

### Backend (Flask)
```python
# Routes principales
GET  /                      # Page d'accueil
GET  /character/create      # Formulaire de création
POST /character/create      # Traitement côté serveur
GET  /party                 # Vue du groupe
GET  /combat                # Interface de combat

# API REST (minimal JavaScript)
POST /api/character/create  # Création via AJAX (optionnel)
POST /api/party/remove/{id} # Suppression via AJAX
POST /api/combat/start      # Démarrage combat
```

### Frontend (Bootstrap + Jinja2)
```
templates/
├── base.html               # Template de base avec Bootstrap
├── index.html              # Page d'accueil
├── character_create.html   # Création côté serveur
├── party.html              # Gestion du groupe
└── combat.html             # Interface de combat
```

### Pas de CSS/JS personnalisé
- Utilisation exclusive de Bootstrap 5.3 (CDN)
- Bootstrap Icons pour les icônes
- JavaScript minimal (< 100 lignes au total)

## 🔧 Différences avec v1.0

### Avant (v1.0)
❌ CSS personnalisé complexe (800+ lignes)  
❌ JavaScript lourd côté client  
❌ Gestion d'état côté client  
❌ Erreurs DOM (`addEventListener` sur null)  

### Maintenant (v2.0)
✅ Bootstrap 5.3 (CDN)  
✅ Logique côté serveur (Flask)  
✅ Templates Jinja2  
✅ Formulaires HTML standards  
✅ JavaScript minimal et robuste  

## 📦 Structures de Données

### Utilisation directe de dnd-5e-core

```python
from dnd_5e_core.data.loaders import simple_character_generator
from dnd_5e_core import load_monster
from dnd_5e_core.combat import CombatSystem
from dnd_5e_core.data.loader import list_races, list_classes, list_monsters

# Création de personnage
char = simple_character_generator(
    level=5,
    race_name='human',
    class_name='fighter',
    name='Conan'
)

# Accès aux propriétés
char.name           # Nom
char.level          # Niveau
char.hit_points     # PV actuels
char.armor_class    # CA
char.abilities      # Caractéristiques (STR, DEX, etc.)
char.race           # Race (objet)
char.class_type     # Classe (objet)
```

## 🐛 Corrections

### Erreur JavaScript Résolue
**Avant:** `Cannot read properties of null (reading 'addEventListener')`
```javascript
// Problème: document.getElementById() avant chargement du DOM
document.getElementById('character-form').addEventListener(...)
```

**Maintenant:** Formulaire HTML standard
```html
<form method="POST" action="/character/create">
    <!-- Traitement côté serveur -->
</form>
```

### Avantages
1. **Pas d'erreur DOM** - Le serveur Flask génère le HTML complet
2. **SEO friendly** - Contenu rendu côté serveur
3. **Plus rapide** - Moins de JavaScript à charger
4. **Plus simple** - Logique centralisée en Python
5. **Plus robuste** - Pas de problèmes de timing JavaScript

## 💡 Philosophie

### Côté Serveur d'Abord
- **Flask/Jinja2** pour la logique et le rendu
- **Bootstrap** pour le design
- **JavaScript** uniquement pour l'interactivité critique

### Quand utiliser JavaScript ?
✅ **Oui** - Sélection interactive (ajout de monstres)  
✅ **Oui** - Validation temps réel  
✅ **Oui** - Confirmation d'actions destructives  
❌ **Non** - Création de formulaires  
❌ **Non** - Gestion d'état complexe  
❌ **Non** - Rendu de contenu  

## 🔗 Ressources

- **dnd-5e-core** : https://github.com/codingame-team/dnd-5e-core
- **Bootstrap 5.3** : https://getbootstrap.com/docs/5.3/
- **Bootstrap Icons** : https://icons.getbootstrap.com/
- **Flask** : https://flask.palletsprojects.com/

## 📝 Changelog

### v2.0 (5 février 2026)
- ✨ Migration vers Bootstrap 5.3
- ✨ Suppression du CSS personnalisé
- ✨ JavaScript minimal (<100 lignes)
- ✨ Logique côté serveur (Flask)
- ✨ Formulaires HTML standards
- 🐛 Correction erreur `addEventListener`
- 🔧 Simplification de l'architecture

### v1.0 (5 février 2026)
- 🎉 Version initiale
- CSS personnalisé (800+ lignes)
- JavaScript client lourd

---

**Version:** 2.0.0  
**Date:** 5 février 2026  
**License:** MIT
