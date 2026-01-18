# DnD-5th-Edition-API - Documentation Index

Guide complet pour naviguer dans la documentation du projet.

## 📚 Documentation Principale

### Pour Commencer
1. **[README.md](README.md)** - Vue d'ensemble du projet
   - Toutes les versions disponibles
   - Installation
   - Guides de lancement

2. **[CHANGELOG.md](CHANGELOG.md)** - Historique des versions
   - Nouvelles fonctionnalités
   - Corrections de bugs

3. **[NCURSES_README.md](NCURSES_README.md)** - Guide interface ncurses
   - Utilisation de la version ncurses
   - Fonctionnalités

### Documentation Complète

**[docs/](docs/)** - Documentation technique :
- **[docs/ARCHITECTURE_JEUX.md](docs/ARCHITECTURE_JEUX.md)** - Architecture détaillée
- **[docs/GUIDE_DEPLOIEMENT.md](docs/GUIDE_DEPLOIEMENT.md)** - Guide de déploiement
- Manuels pour chaque version

## 🎮 Versions Disponibles

### Console (Terminal)
→ [manual/manual_console_version.md](manual/manual_console_version.md)
```bash
python main.py
```

### Ncurses (Interface Texte)
→ [manual/manual_ncurses_version.md](manual/manual_ncurses_version.md)
```bash
python main_ncurses.py
```

### Pygame (Graphique)
→ [README_pygame_version.md](README_pygame_version.md)
```bash
python dungeon_menu_pygame.py
```

### PyQt5 (Interface Qt)
→ [manual/manual_pyQT_version.md](manual/manual_pyQT_version.md)
```bash
python pyQTApp/wizardry.py
```

### Tkinter (Simplifié)
→ [manual/manual_tk_version.md](manual/manual_tk_version.md)
```bash
python dungeon_tk.py
```

## 📦 Structure du Projet

```
DnD-5th-Edition-API/
├── README.md                 # Documentation principale
├── CHANGELOG.md              # Historique
├── NCURSES_README.md         # Guide ncurses
│
├── main.py                   # Console version
├── main_ncurses.py           # Ncurses version
├── dungeon_menu_pygame.py    # Pygame menu
├── dungeon_pygame.py         # Pygame dungeon
├── pyQTApp/                  # PyQt5 version
│   └── wizardry.py
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE_JEUX.md
│   └── GUIDE_DEPLOIEMENT.md
│
├── manual/                   # Manuels utilisateur
│   ├── manual_console_version.md
│   ├── manual_ncurses_version.md
│   └── manual_pyQT_version.md
│
├── tests/                    # Scripts de test
│   ├── README.md
│   └── test_*.py
│
└── archive/                  # Documents historiques
    └── README.md
```

## 🧪 Tests

**[tests/](tests/)** - Scripts de test

**[tests/README.md](tests/README.md)** - Guide des tests
- Tests d'intégration
- Tests fonctionnels
- Validation de migration

### Principaux Tests
- `test_dnd_core.py` - Test dnd-5e-core
- `test_combat_actions.py` - Test combat
- `test_integration_5etools.py` - Test 5e.tools
- `validate_migration.py` - Validation migration

## 🎯 Par Cas d'Usage

### Je veux jouer
→ [README.md](README.md#available-versions)
→ Choisir une version et lancer

### Je veux développer
→ [README.md](README.md#for-developers)
→ [docs/ARCHITECTURE_JEUX.md](docs/ARCHITECTURE_JEUX.md)

### Je veux builder
→ [docs/GUIDE_DEPLOIEMENT.md](docs/GUIDE_DEPLOIEMENT.md)
```bash
./build_all.sh  # macOS/Linux
build_all.bat   # Windows
```

### Je veux tester
→ [tests/README.md](tests/README.md)
```bash
pytest tests/
```

## 📝 Notes

- **Utilise dnd-5e-core** - Package pour la logique D&D 5e
- **Multiple frontends** - Console, ncurses, pygame, PyQt5, tkinter
- **Version standalone** - Executables disponibles
- **Tests complets** - Suite de tests dans tests/
- **Archive** - Documents historiques dans archive/

## 🔗 Liens Utiles

### Projets Liés
- **[dnd-5e-core](https://github.com/codingame-team/dnd-5e-core)** - Package de règles D&D 5e
- **[DnD5e-Scenarios](https://github.com/codingame-team/DnD5e-Scenarios)** - Scénarios

### Données D&D 5e
- **[D&D 5e API](https://www.dnd5eapi.co/)** - Source de données
- **[5e.tools](https://5e.tools/)** - Monstres étendus

## 🔍 Recherche Rapide

| Sujet | Fichier |
|-------|---------|
| Installation | [README.md](README.md#installation) |
| Versions | [README.md](README.md#available-versions) |
| Architecture | [docs/ARCHITECTURE_JEUX.md](docs/ARCHITECTURE_JEUX.md) |
| Build | [docs/GUIDE_DEPLOIEMENT.md](docs/GUIDE_DEPLOIEMENT.md) |
| Tests | [tests/README.md](tests/README.md) |
| Historique | [CHANGELOG.md](CHANGELOG.md) |
| Archive | [archive/](archive/) |

---

**Pour commencer** : Lisez [README.md](README.md) et choisissez votre version préférée !

