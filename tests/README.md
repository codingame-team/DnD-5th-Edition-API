# Tests - Scripts de Test

Ce dossier contient tous les scripts de test pour le projet DnD-5th-Edition-API.

## Structure

```
tests/
├── test_combat_actions.py      # Test des actions de combat
├── test_dnd_core.py             # Test du package dnd-5e-core
├── test_executable.py           # Test des exécutables
├── test_imports.py              # Test des imports
├── test_integration_5etools.py  # Test intégration 5e.tools
├── test_main_imports.py         # Test imports main
├── test_monster_status.py       # Test statut monstres
├── test_ncurses_fixes.py        # Test corrections ncurses
├── test_phase2_migration.py     # Test migration phase 2
└── validate_migration.py        # Validation de la migration
```

## Scripts de Test

### Tests d'Intégration

**test_dnd_core.py**
- Test de l'intégration avec dnd-5e-core
- Vérification des imports
- Test des fonctionnalités principales

**test_integration_5etools.py**
- Test de l'intégration 5e.tools
- Vérification des monstres étendus
- Test de chargement des données

**test_phase2_migration.py**
- Test de la migration phase 2
- Vérification de compatibilité
- Test des nouvelles fonctionnalités

### Tests Fonctionnels

**test_combat_actions.py**
- Test des actions de combat
- Vérification des attaques
- Test des capacités spéciales

**test_monster_status.py**
- Test du statut des monstres
- Vérification des HP
- Test des conditions

**test_ncurses_fixes.py**
- Test des corrections ncurses
- Vérification de l'interface
- Test des interactions

### Tests de Build

**test_executable.py**
- Test des exécutables générés
- Vérification du build
- Test de lancement

**test_imports.py**
- Test de tous les imports
- Vérification des dépendances
- Détection de problèmes

**test_main_imports.py**
- Test des imports du main
- Vérification de compatibilité

### Validation

**validate_migration.py**
- Validation complète de la migration
- Vérification de toutes les fonctionnalités
- Rapport de validation

## Exécution des Tests

### Tous les tests
```bash
pytest tests/
```

### Test spécifique
```bash
python tests/test_dnd_core.py
```

### Validation de migration
```bash
python tests/validate_migration.py
```

## Notes

- Les tests utilisent le package dnd-5e-core
- Certains tests nécessitent ncurses
- Les tests PyQt nécessitent un environnement graphique

## Contribution

Pour ajouter des tests :
1. Créer un fichier `test_*.py`
2. Suivre la structure des tests existants
3. Documenter le test
4. S'assurer que tous les tests passent

Voir **README.md** pour plus de détails.

