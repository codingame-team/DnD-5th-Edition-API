# 🚀 Guide de Démarrage Rapide - Démo Flask

## Installation

1. **Naviguer vers le répertoire de la démo**
   ```bash
   cd flask_demo
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

   Ou si vous utilisez le package local dnd-5e-core :
   ```bash
   pip install -e ../dnd-5e-core
   pip install Flask==3.0.0 Werkzeug==3.0.1
   ```

3. **Lancer l'application**
   ```bash
   python app.py
   ```

   Ou utilisez le script :
   ```bash
   ./run.sh
   ```

4. **Ouvrir dans votre navigateur**
   ```
   http://localhost:5000
   ```

## 🎮 Utilisation

### Créer un Personnage

1. Cliquez sur "Créer Personnage"
2. Remplissez le formulaire :
   - Nom du personnage
   - Race (human, elf, dwarf, etc.)
   - Classe (fighter, wizard, cleric, etc.)
   - Niveau (1-20)
3. Cliquez sur "Créer le Personnage"
4. Le personnage est automatiquement ajouté à votre groupe

### Gérer votre Groupe

1. Cliquez sur "Mon Groupe"
2. Visualisez tous vos personnages
3. Consultez leurs statistiques complètes
4. Retirez un personnage si nécessaire (bouton ❌)

### Lancer un Combat

1. Créez au moins un personnage dans votre groupe
2. Cliquez sur "Combat"
3. Sélectionnez des monstres :
   - **Rencontres rapides** : Facile, Moyen, Difficile, Mortel
   - **Personnalisé** : Choisissez vos monstres dans la liste
4. Cliquez sur "Commencer le Combat"
5. Utilisez les boutons :
   - **Tour Suivant** : Exécute un tour de combat
   - **Auto** : Mode automatique (tours successifs)
6. Le combat se termine quand tous les monstres ou tous les personnages sont vaincus

## 📝 Notes

- Les données sont sauvegardées en session
- Chaque session a un identifiant unique
- Les sauvegardes sont stockées dans `data/saves/`
- Le mode debug est activé par défaut

## 🐛 Dépannage

**Erreur d'import dnd-5e-core**
```bash
# Installer depuis le répertoire local
pip install -e ../dnd-5e-core
```

**Port 5000 déjà utilisé**
- Modifiez le port dans `app.py` :
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```

**Problème de session**
- Supprimez les fichiers dans `data/saves/`
- Videz le cache de votre navigateur

## 🔗 Liens Utiles

- [Documentation complète](README.md)
- [dnd-5e-core sur GitHub](https://github.com/codingame-team/dnd-5e-core)
- [Guide IA](https://github.com/codingame-team/dnd-5e-core/blob/main/AI_AGENT_GUIDE.md)
