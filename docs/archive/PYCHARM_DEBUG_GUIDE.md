# Configuration PyCharm pour Debugger avec NCurses

## 🎯 Méthode Recommandée : main_pexpect.py

Le script `main_pexpect.py` a été spécialement créé pour permettre le debugging dans PyCharm.

### Étape 1 : Configuration PyCharm

1. **Ouvrir Run/Debug Configurations**
   - Menu : `Run` → `Edit Configurations...`
   - Ou cliquer sur le dropdown à côté du bouton Run

2. **Créer une nouvelle configuration Python**
   - Cliquer sur `+` → `Python`
   - Nom : `DnD NCurses (with PTY)`

3. **Configurer les paramètres**
   ```
   Script path: /Users/display/PycharmProjects/DnD-5th-Edition-API/main_pexpect.py
   Parameters: ncurses
   Python interpreter: (votre interpréteur virtuel)
   Working directory: /Users/display/PycharmProjects/DnD-5th-Edition-API
   ```

4. **Activer "Emulate terminal in output console"** ✅
   - Cocher cette option dans la configuration

### Étape 2 : Debugging

1. **Placer des breakpoints**
   - Dans `main_ncurses.py`, cliquer dans la marge gauche des lignes où vous voulez pauser
   - Exemple : ligne de `mainloop()`, `_handle_castle()`, etc.

2. **Lancer en mode Debug**
   - Cliquer sur l'icône Debug (🐞) ou `Shift+F9`
   - Le script va démarrer avec pseudo-TTY
   - S'arrêtera aux breakpoints

3. **Utiliser les contrôles de debug**
   - `F8` : Step Over (ligne suivante)
   - `F7` : Step Into (entrer dans fonction)
   - `F9` : Resume (continuer jusqu'au prochain breakpoint)
   - Variables visibles dans le panneau Debug

---

## 📋 Configuration Visuelle PyCharm

### Configuration Run/Debug

```
┌─────────────────────────────────────────────────┐
│ Run/Debug Configurations                        │
├─────────────────────────────────────────────────┤
│ Name: DnD NCurses (with PTY)                   │
│                                                 │
│ Script path:                                    │
│ [/...../main_pexpect.py                    ] 📁 │
│                                                 │
│ Parameters:                                     │
│ [ncurses                                      ] │
│                                                 │
│ Python interpreter:                             │
│ [Python 3.13 (.venv)                         ▼] │
│                                                 │
│ Working directory:                              │
│ [/...../DnD-5th-Edition-API                 ] 📁│
│                                                 │
│ ☑ Emulate terminal in output console           │
│ ☐ Redirect input from file                     │
│ ☐ Run with Python Console                      │
│                                                 │
│ Environment variables:                          │
│ [TERM=xterm-256color                          ] │
│                                                 │
│         [OK]  [Cancel]  [Apply]                 │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Solution Alternative : Terminal Externe

Si vous préférez ne pas utiliser le debugger PyCharm :

### Option A : Debug avec pdb
```python
# Ajouter dans main_ncurses.py où vous voulez un breakpoint
import pdb; pdb.set_trace()
```

Puis lancer dans un vrai terminal :
```bash
python main_ncurses.py
# Le programme s'arrêtera au breakpoint pdb
```

### Option B : Logging pour Debug
```python
# Dans main_ncurses.py
import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

# Dans vos fonctions
logging.debug(f"Castle cursor: {self.castle_cursor}")
logging.debug(f"Party size: {len(self.party)}")
```

Puis consulter `debug.log` pendant l'exécution.

---

## 🎯 Workflow de Debug Recommandé

### 1. Debugging Initial (Structure/Logique)
```bash
# Utiliser PyCharm avec main_pexpect.py
python main_pexpect.py ncurses
# → Breakpoints dans la logique métier
# → Inspecter variables, état du jeu
```

### 2. Debugging Interface (NCurses)
```bash
# Terminal externe avec logging
python main_ncurses.py
# → Voir l'interface réelle
# → Consulter debug.log pour tracer
```

### 3. Debugging Hybride
```python
# main_ncurses.py - Ajouter logging
def _handle_castle(self, c: int):
    logging.debug(f"Castle handler - key: {c}, cursor: {self.castle_cursor}")
    # ...existing code...
```

```bash
# PyCharm Debug
python main_pexpect.py ncurses
# → Breakpoints + logs simultanés
```

---

## 📝 Exemple Pratique

### Scenario : Debugger le chargement du roster

1. **Ouvrir main_ncurses.py**

2. **Placer breakpoint ligne ~233** (dans `load_game_data`)
   ```python
   def load_game_data(self):
       # ...
       self.roster = get_roster(self.characters_dir)  # ← BREAKPOINT ICI
       # ...
   ```

3. **Configurer PyCharm**
   - Script: `main_pexpect.py`
   - Parameters: `ncurses`

4. **Lancer Debug** (🐞)
   - Le programme s'arrête au breakpoint
   
5. **Inspecter les variables**
   - Dans le panneau Debug, voir :
     - `self.characters_dir` → chemin
     - `self.roster` → liste (après Step Over)
   
6. **Step Over (F8)** pour avancer
   - Voir `self.roster` se remplir

7. **Vérifier le message**
   ```python
   self.push_message(f"Loaded {len(self.roster)} characters")  # ← Step to here
   # Inspecter len(self.roster)
   ```

---

## 🚨 Problèmes Courants et Solutions

### Problème 1 : "setupterm: could not find terminal"
**Solution :** Ajouter variable d'environnement
```
TERM=xterm-256color
```
Dans PyCharm : Run → Edit Configurations → Environment variables

### Problème 2 : "No TTY detected"
**Solution :** C'est normal avec main_pexpect.py
- Il utilise automatiquement pseudo-TTY
- Message informatif, pas une erreur

### Problème 3 : Breakpoints ignorés
**Solution :** Vérifier que :
- Le fichier est bien main_pexpect.py (pas main_ncurses.py direct)
- Les breakpoints sont dans main_ncurses.py (pas main_pexpect.py)
- "Emulate terminal" est coché

### Problème 4 : Interface ncurses illisible
**Solution :** 
- Utiliser logging au lieu de print
- Ne pas mettre de breakpoints dans les fonctions draw_*
- Débugger la logique, pas l'affichage

---

## 🎓 Conseils de Debug NCurses

### ✅ DO
- Débugger la logique métier (handlers, load/save)
- Utiliser logging pour tracer l'exécution
- Tester avec main_pexpect.py en PyCharm
- Valider avec terminal réel ensuite

### ❌ DON'T
- Ne pas débugger pendant draw() (interface corrompue)
- Ne pas utiliser print() (interfère avec ncurses)
- Ne pas lancer main_ncurses.py directement dans PyCharm
- Ne pas oublier curses.endwin() en cas d'erreur

---

## 📊 Tableau Récapitulatif

| Méthode | PyCharm Debug | Interface NCurses | Difficulté |
|---------|---------------|-------------------|------------|
| main_pexpect.py | ✅ Oui | ⚠️ Pseudo-TTY | ⭐ Facile |
| Terminal + pdb | ❌ Non | ✅ Vraie | ⭐⭐ Moyen |
| Logging | ❌ Non | ✅ Vraie | ⭐ Facile |
| Direct PyCharm | ❌ Erreur | ❌ Erreur | ❌ Impossible |

---

## 🎯 Configuration Recommandée

### .idea/runConfigurations/DnD_NCurses_Debug.xml
```xml
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="DnD NCurses (Debug)" type="PythonConfigurationType">
    <option name="INTERPRETER_OPTIONS" value="" />
    <option name="PARENT_ENVS" value="true" />
    <envs>
      <env name="TERM" value="xterm-256color" />
    </envs>
    <option name="SDK_HOME" value="$PROJECT_DIR$/.venv/bin/python" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
    <option name="IS_MODULE_SDK" value="false" />
    <option name="ADD_CONTENT_ROOTS" value="true" />
    <option name="ADD_SOURCE_ROOTS" value="true" />
    <option name="SCRIPT_NAME" value="$PROJECT_DIR$/main_pexpect.py" />
    <option name="PARAMETERS" value="ncurses" />
    <option name="SHOW_COMMAND_LINE" value="false" />
    <option name="EMULATE_TERMINAL" value="true" />
    <option name="MODULE_MODE" value="false" />
    <option name="REDIRECT_INPUT" value="false" />
    <option name="INPUT_FILE" value="" />
    <method v="2" />
  </configuration>
</component>
```

---

## ✅ Vérification

Pour vérifier que tout fonctionne :

```bash
# Test 1 : main_pexpect.py fonctionne
python main_pexpect.py ncurses
# ✓ Devrait lancer le jeu

# Test 2 : Debug simple
# 1. Ouvrir PyCharm
# 2. Breakpoint dans load_game_data()
# 3. Debug configuration avec main_pexpect.py
# 4. Lancer Debug
# ✓ Devrait s'arrêter au breakpoint
```

---

**Résumé :**
1. Utilisez `main_pexpect.py ncurses` dans PyCharm
2. Activez "Emulate terminal in output console"
3. Placez breakpoints dans la logique métier
4. Utilisez logging pour tracer l'interface
5. Testez en terminal réel pour valider l'affichage

**Le script main_pexpect.py a été créé exactement pour ce cas d'usage !** 🎉

