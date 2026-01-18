# 🚀 Guide de Déploiement - D&D 5e Games

**Date:** 24 décembre 2025  
**Pour:** DnD-5th-Edition-API avec dnd-5e-core

---

## 📋 Table des Matières

1. [Préparation de l'Environnement](#1-préparation-de-lenvironnement)
2. [Build Local (Développement)](#2-build-local-développement)
3. [Build Multi-OS](#3-build-multi-os)
4. [Publication sur GitHub Releases](#4-publication-sur-github-releases)
5. [Publication dnd-5e-core sur PyPI](#5-publication-dnd-5e-core-sur-pypi)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Préparation de l'Environnement

### Installation Initiale

```bash
# Clone les repositories
git clone <url>/dnd-5e-core.git
git clone <url>/DnD-5th-Edition-API.git

# Install dnd-5e-core en mode développement
cd dnd-5e-core
pip install -e .

# Install les dépendances des jeux
cd ../DnD-5th-Edition-API
pip install -r requirements-dev-new.txt
```

### Vérification

```bash
# Test que dnd-5e-core est accessible
python -c "from dnd_5e_core.entities import Character; print('✅ dnd-5e-core OK')"

# Test les jeux
python main.py          # Console version
python dungeon_menu_pygame.py  # Pygame version
```

---

## 2. Build Local (Développement)

### macOS/Linux

```bash
cd DnD-5th-Edition-API

# Build tous les jeux
./build_all.sh

# Ou build individuellement
pyinstaller main.spec --clean
pyinstaller dungeon_menu_pygame.spec --clean
```

### Windows

```cmd
cd DnD-5th-Edition-API

REM Build tous les jeux
build_all.bat

REM Ou build individuellement
pyinstaller main.spec --clean
pyinstaller dungeon_menu_pygame.spec --clean
```

### Résultats

```
dist/
├── dnd-console       # ou dnd-console.exe sur Windows
└── dnd-pygame        # ou dnd-pygame.exe sur Windows
```

### Test des Executables

```bash
# macOS/Linux
./dist/dnd-console
./dist/dnd-pygame

# Windows
dist\dnd-console.exe
dist\dnd-pygame.exe
```

---

## 3. Build Multi-OS

### Approche 1: GitHub Actions (Recommandé)

Créer `.github/workflows/build.yml` :

```yaml
name: Build Multi-OS

on:
  push:
    tags:
      - 'v*'  # Trigger sur tags version (v1.0.0, etc.)

jobs:
  build:
    name: Build on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10']

    steps:
    - uses: actions/checkout@v3
    
    - name: Checkout dnd-5e-core
      uses: actions/checkout@v3
      with:
        repository: your-org/dnd-5e-core
        path: dnd-5e-core
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e dnd-5e-core
        pip install -r requirements-dist.txt
        pip install pyinstaller
    
    - name: Build with PyInstaller
      run: |
        pyinstaller main.spec --clean
        pyinstaller dungeon_menu_pygame.spec --clean
    
    - name: Rename executables (Linux/macOS)
      if: runner.os != 'Windows'
      run: |
        mv dist/dnd-console dist/dnd-console-${{ runner.os }}
        mv dist/dnd-pygame dist/dnd-pygame-${{ runner.os }}
    
    - name: Rename executables (Windows)
      if: runner.os == 'Windows'
      run: |
        ren dist\dnd-console.exe dnd-console-Windows.exe
        ren dist\dnd-pygame.exe dnd-pygame-Windows.exe
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: builds-${{ runner.os }}
        path: dist/*
```

### Approche 2: Build Manuel par OS

#### Sur macOS
```bash
./build_all.sh
mv dist/dnd-console dist/dnd-console-1.0-macos
mv dist/dnd-pygame dist/dnd-pygame-1.0-macos
```

#### Sur Windows
```cmd
build_all.bat
ren dist\dnd-console.exe dnd-console-1.0-windows.exe
ren dist\dnd-pygame.exe dnd-pygame-1.0-windows.exe
```

#### Sur Linux
```bash
./build_all.sh
mv dist/dnd-console dist/dnd-console-1.0-linux
mv dist/dnd-pygame dist/dnd-pygame-1.0-linux
```

---

## 4. Publication sur GitHub Releases

### Étape 1: Créer un Tag

```bash
# Dans DnD-5th-Edition-API
git tag -a v1.0.0 -m "Version 1.0.0 - First stable release"
git push origin v1.0.0
```

### Étape 2: Créer la Release sur GitHub

1. Aller sur GitHub → Releases → "Draft a new release"
2. Choisir le tag `v1.0.0`
3. Titre: "D&D 5e Games v1.0.0"
4. Description:

```markdown
# D&D 5e Games v1.0.0

Complete D&D 5th Edition games with multiple interfaces.

## 🎮 Available Games

### Console Version
Text-based D&D 5e experience with full rules implementation.

### Pygame Version
Graphical dungeon crawler with:
- Spell casting
- Inventory management
- Melee & ranged combat
- Trading post
- Monster statistics

## 📥 Download

### Windows
- [dnd-console-1.0-windows.exe](link) (15 MB)
- [dnd-pygame-1.0-windows.exe](link) (25 MB)

### macOS
- [dnd-console-1.0-macos](link) (15 MB)
- [dnd-pygame-1.0-macos](link) (25 MB)

### Linux
- [dnd-console-1.0-linux](link) (15 MB)
- [dnd-pygame-1.0-linux](link) (25 MB)

## 🚀 Installation

See [INSTALLATION.md](link) for detailed instructions.

## 📚 Documentation

- [User Manual](link)
- [Developer Guide](link)
- [dnd-5e-core Documentation](link)

## 🐛 Known Issues

None reported yet!

## ✨ What's New

- First stable release
- Complete D&D 5e rules
- Multi-platform support
- Optimized executables
```

### Étape 3: Upload des Executables

Drag & drop les fichiers compilés :
- dnd-console-1.0-windows.exe
- dnd-console-1.0-macos
- dnd-console-1.0-linux
- dnd-pygame-1.0-windows.exe
- dnd-pygame-1.0-macos
- dnd-pygame-1.0-linux

### Étape 4: Publier

Cliquer sur "Publish release"

---

## 5. Publication dnd-5e-core sur PyPI

### Prérequis

```bash
pip install build twine
```

### Étape 1: Préparer le Package

```bash
cd dnd-5e-core

# Vérifier setup.py
python setup.py check

# Nettoyer builds précédents
rm -rf dist/ build/ *.egg-info
```

### Étape 2: Build

```bash
# Créer distributions source et wheel
python -m build

# Résultat dans dist/
# - dnd-5e-core-0.1.0.tar.gz
# - dnd_5e_core-0.1.0-py3-none-any.whl
```

### Étape 3: Test sur TestPyPI

```bash
# Upload sur TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ dnd-5e-core

# Vérifier
python -c "from dnd_5e_core.entities import Character; print('✅ Package OK')"
```

### Étape 4: Publication Production

```bash
# Upload sur PyPI
python -m twine upload dist/*

# Vérifier sur https://pypi.org/project/dnd-5e-core/

# Test installation
pip install dnd-5e-core
```

### Étape 5: Mettre à Jour DnD-5th-Edition-API

```bash
cd ../DnD-5th-Edition-API

# Mettre à jour requirements-dist.txt
# dnd-5e-core>=0.1.0  # Déjà présent

# Test
pip install -r requirements-dist.txt
python main.py
```

---

## 6. Troubleshooting

### Problème: "dnd-5e-core not found"

**Solution:**
```bash
# Vérifier l'installation
pip show dnd-5e-core

# Réinstaller en mode développement
pip install -e ../dnd-5e-core
```

### Problème: "Module not found in executable"

**Solution:** Ajouter le module à `hiddenimports` dans le `.spec` file.

```python
hiddenimports=[
    'missing_module',
    # ...
],
```

### Problème: "Data files not found"

**Solution:** Vérifier que les données sont dans `datas` du `.spec`:

```python
datas=[
    ('path/to/data', 'data'),  # Format: (source, destination)
],
```

### Problème: Executable trop gros

**Solutions:**
1. Activer UPX compression: `upx=True`
2. Exclure modules inutiles: `excludes=['matplotlib', 'tkinter']`
3. Vérifier que data/ n'est pas dupliqué (doit être dans dnd-5e-core)

### Problème: Import Error au runtime

**Solution:** Test avec `--debug=imports`:
```bash
pyinstaller main.spec --debug=imports
./dist/dnd-console  # Voir les imports manquants
```

### Problème: Permission denied (macOS/Linux)

**Solution:**
```bash
chmod +x dist/dnd-console
chmod +x dist/dnd-pygame
```

---

## 📊 Checklist de Déploiement

### Avant Build
- [ ] Tests unitaires passent
- [ ] Jeux fonctionnent en mode développement
- [ ] dnd-5e-core est à jour
- [ ] Version bump dans setup.py et __init__.py

### Build
- [ ] Build réussi sur macOS
- [ ] Build réussi sur Windows
- [ ] Build réussi sur Linux
- [ ] Executables testés sur chaque OS
- [ ] Tailles des executables vérifiées

### Publication
- [ ] Tag Git créé
- [ ] GitHub Release créée
- [ ] Executables uploadés
- [ ] Documentation à jour
- [ ] CHANGELOG.md mis à jour

### dnd-5e-core (si nouvelle version)
- [ ] Tests passent
- [ ] Version bump
- [ ] Build package
- [ ] Upload TestPyPI
- [ ] Test installation TestPyPI
- [ ] Upload PyPI production
- [ ] Tag Git créé

---

## 📝 Notes

### Tailles Estimées

| Jeu | Windows | macOS | Linux |
|-----|---------|-------|-------|
| Console | ~15 MB | ~15 MB | ~15 MB |
| Pygame | ~25 MB | ~25 MB | ~25 MB |

### Performance

- Temps de build: 2-5 minutes par jeu
- Temps de startup: < 2 secondes
- Mémoire utilisée: 50-100 MB

### Support OS

- Windows: 10, 11
- macOS: 10.15+ (Catalina et plus)
- Linux: Ubuntu 20.04+, Debian 10+, Fedora 33+

---

## 🔗 Ressources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [GitHub Actions](https://docs.github.com/actions)
- [PyPI Publishing](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)

---

**Dernière mise à jour:** 24 décembre 2025  
**Version:** 1.0

