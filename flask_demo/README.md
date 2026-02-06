# 🎲 D&D 5e Flask Demo

Application web de démonstration utilisant le package **dnd-5e-core** pour gérer la création de personnages, la constitution de groupes et un système de combat complet.

## 🚀 Installation

### Prérequis
- Python 3.9 ou supérieur
- pip

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## 📖 Utilisation

### Lancer l'application

```bash
python app.py
```

L'application sera accessible sur : http://localhost:5000

### Navigation

- **Accueil** (`/`) : Vue d'ensemble des fonctionnalités
- **Créer Personnage** (`/character/create`) : Formulaire de création de personnage
- **Mon Groupe** (`/party`) : Gestion du groupe d'aventuriers
- **Combat** (`/combat`) : Interface de combat tour par tour

## 🎮 Fonctionnalités

### Création de Personnages
- Sélection de race parmi toutes les races disponibles dans D&D 5e
- Sélection de classe (Fighter, Wizard, Cleric, Rogue, etc.)
- Choix du niveau (1-20)
- Génération automatique des caractéristiques
- Attribution de l'équipement de départ

### Constitution de Groupe
- Ajout de personnages au groupe (jusqu'à 6 personnages)
- Visualisation des statistiques complètes
- Gestion du groupe (ajout/suppression)
- Persistance des données en session

### Système de Combat
- Rencontres rapides prédéfinies (Facile, Moyen, Difficile, Mortel)
- Sélection personnalisée de monstres
- Combat tour par tour automatisé
- Journal de combat en temps réel
- Affichage visuel des PV et états
- Mode auto-play

## 📚 Architecture

```
flask_demo/
├── app.py                  # Application Flask principale
├── templates/              # Templates Jinja2
│   ├── base.html          # Template de base
│   ├── index.html         # Page d'accueil
│   ├── character_create.html  # Création de personnage
│   ├── party.html         # Gestion du groupe
│   └── combat.html        # Interface de combat
├── static/                # Fichiers statiques
│   ├── css/
│   │   └── style.css     # Styles CSS
│   └── js/
│       └── main.js       # JavaScript
├── data/                  # Données persistantes
│   └── saves/            # Sauvegardes de sessions
└── requirements.txt       # Dépendances Python
```

## 🔌 API Endpoints

### Personnages
- `POST /api/character/create` - Créer un nouveau personnage
  ```json
  {
    "name": "Conan",
    "race": "human",
    "class": "fighter",
    "level": 5
  }
  ```

### Groupe
- `POST /api/party/remove/<index>` - Retirer un personnage du groupe

### Combat
- `POST /api/combat/start` - Démarrer un nouveau combat
- `POST /api/combat/turn` - Exécuter un tour de combat
- `POST /api/combat/end` - Terminer le combat en cours

### Informations
- `GET /api/info/races` - Liste des races disponibles
- `GET /api/info/classes` - Liste des classes disponibles
- `GET /api/info/monsters` - Liste des monstres disponibles

## 💾 Persistance

Les données de session sont sauvegardées dans le répertoire `data/saves/` sous forme de fichiers pickle. Chaque session utilisateur a un identifiant unique.

## 🎨 Personnalisation

### Thème
Les couleurs et styles sont définis dans `static/css/style.css` avec des variables CSS :
- `--primary-color` : Couleur principale
- `--secondary-color` : Couleur secondaire
- `--success-color` : Couleur de succès
- `--danger-color` : Couleur de danger

### Rencontres prédéfinies
Modifiez la fonction `selectEncounter()` dans `templates/combat.html` pour personnaliser les rencontres rapides.

## 🔧 Configuration

Variables d'environnement disponibles :
- `SECRET_KEY` : Clé secrète Flask (par défaut : 'dev-secret-key-change-in-production')

## 📦 Package dnd-5e-core

Cette démo utilise le package **dnd-5e-core** qui fournit :
- 332+ monstres
- 319+ sorts
- 65+ armes
- 30+ armures
- Système de combat complet
- Gestion des personnages et progressions

Documentation complète : https://github.com/codingame-team/dnd-5e-core

## 🐛 Debug

Mode debug activé par défaut. Pour désactiver :

```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

## 📝 Licence

Cette démo est fournie à titre d'exemple d'utilisation du package dnd-5e-core.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 🔗 Liens

- [dnd-5e-core sur GitHub](https://github.com/codingame-team/dnd-5e-core)
- [dnd-5e-core sur PyPI](https://pypi.org/project/dnd-5e-core/)
- [Documentation IA](https://github.com/codingame-team/dnd-5e-core/blob/main/AI_AGENT_GUIDE.md)

---

**Version:** 1.0.0  
**Dernière mise à jour:** Février 2026
