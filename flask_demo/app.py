"""
Démo Flask complète utilisant dnd-5e-core
Gestion de création de personnages, constitution de groupes et système de combats
"""
import os
import pickle
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.exceptions import BadRequest

# Import dnd-5e-core
from dnd_5e_core.data.loaders import simple_character_generator
from dnd_5e_core import load_monster
from dnd_5e_core.combat import CombatSystem
from dnd_5e_core.data.loader import list_monsters, list_races, list_classes

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
SAVE_DIR = Path(__file__).parent / 'data' / 'saves'
SAVE_DIR.mkdir(parents=True, exist_ok=True)

ROSTER_DIR = Path(__file__).parent / 'data' / 'roster'
ROSTER_DIR.mkdir(parents=True, exist_ok=True)

# Cache pour les listes
RACES_CACHE = None
CLASSES_CACHE = None
MONSTERS_CACHE = None


def get_races():
    """Récupère la liste des races disponibles."""
    global RACES_CACHE
    if RACES_CACHE is None:
        RACES_CACHE = list_races()
    return RACES_CACHE


def get_classes():
    """Récupère la liste des classes disponibles."""
    global CLASSES_CACHE
    if CLASSES_CACHE is None:
        CLASSES_CACHE = list_classes()
    return CLASSES_CACHE


def get_monsters():
    """Récupère la liste complète des monstres via load_dungeon_collections."""
    global MONSTERS_CACHE
    if MONSTERS_CACHE is None:
        try:
            # Essayer de charger via load_dungeon_collections (bestiaire complet)
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from main_ncurses import load_dungeon_collections

            monsters, _, _, _, _, _ = load_dungeon_collections()
            MONSTERS_CACHE = list(filter(lambda m: m, monsters))
            print(f"✅ Loaded {len(MONSTERS_CACHE)} monsters via load_dungeon_collections")
        except Exception as e:
            # Fallback: utiliser list_monsters
            print(f"⚠️ Could not load via load_dungeon_collections: {e}")
            print("Falling back to list_monsters...")
            MONSTERS_CACHE = list_monsters()
            print(f"✅ Loaded {len(MONSTERS_CACHE)} monsters via list_monsters")

    return MONSTERS_CACHE
    return MONSTERS_CACHE


def save_session_data():
    """Sauvegarde les données de session sur le disque."""
    if 'session_id' in session:
        save_path = SAVE_DIR / f"{session['session_id']}.pkl"
        with open(save_path, 'wb') as f:
            pickle.dump({
                'party': session.get('party', []),
                'combat_state': session.get('combat_state', None),
                'party_gold': session.get('party_gold', 0),
            }, f)


def load_session_data():
    """Charge les données de session depuis le disque."""
    if 'session_id' in session:
        save_path = SAVE_DIR / f"{session['session_id']}.pkl"
        if save_path.exists():
            with open(save_path, 'rb') as f:
                data = pickle.load(f)
                session['party'] = data.get('party', [])
                session['combat_state'] = data.get('combat_state', None)
                session['party_gold'] = data.get('party_gold', 0)


def serialize_character(char):
    """Convertit un personnage en dictionnaire JSON-serializable."""
    # Gérer les armes
    weapon_name = None
    if hasattr(char, 'equipped_weapon') and char.equipped_weapon:
        weapon_name = char.equipped_weapon.name
    elif hasattr(char, 'weapon') and char.weapon:
        weapon_name = char.weapon.name

    # Gérer les armures
    armor_name = None
    if hasattr(char, 'equipped_armor') and char.equipped_armor:
        armor_name = char.equipped_armor.name
    elif hasattr(char, 'armor') and char.armor:
        armor_name = char.armor.name

    # Gérer le bouclier
    shield_name = None
    if hasattr(char, 'equipped_shield') and char.equipped_shield:
        shield_name = char.equipped_shield.name
    elif hasattr(char, 'shield') and char.shield:
        shield_name = char.shield.name

    # Gérer l'inventaire
    inventory = []
    if hasattr(char, 'inventory') and char.inventory:
        for item in char.inventory:
            if item is not None:
                inventory.append({
                    'name': getattr(item, 'name', str(item)),
                    'type': type(item).__name__,
                })

    return {
        'name': char.name,
        'level': char.level,
        'race': char.race.name,
        'class': char.class_type.name,
        'hp': char.hit_points,
        'max_hp': char.max_hit_points,
        'ac': char.armor_class,
        'str': char.abilities.str,
        'dex': char.abilities.dex,
        'con': char.abilities.con,
        'int': char.abilities.int,
        'wis': char.abilities.wis,
        'cha': char.abilities.cha,
        'gold': char.gold,
        'xp': char.xp,
        'weapon': weapon_name,
        'armor': armor_name,
        'shield': shield_name,
        'inventory': inventory,
    }


def serialize_monster(monster):
    """Convertit un monstre en dictionnaire JSON-serializable."""
    return {
        'name': monster.name,
        'type': monster.creature_type if hasattr(monster, 'creature_type') else 'Unknown',
        'hp': monster.hit_points,
        'max_hp': monster.max_hit_points,
        'ac': monster.armor_class,
        'cr': str(monster.challenge_rating) if hasattr(monster, 'challenge_rating') else 'Unknown',
        'xp': monster.xp if hasattr(monster, 'xp') else 0,
    }


# ==================== ROSTER MANAGEMENT ====================

def save_to_roster(character_data):
    """Sauvegarde un personnage dans le roster."""
    try:
        char_file = ROSTER_DIR / f"{character_data['name']}.pkl"
        with open(char_file, 'wb') as f:
            pickle.dump(character_data, f)
        return True
    except Exception as e:
        print(f"Erreur save_to_roster: {e}")
        return False


def load_roster():
    """Charge tous les personnages du roster."""
    roster = []
    try:
        for char_file in ROSTER_DIR.glob("*.pkl"):
            try:
                with open(char_file, 'rb') as f:
                    char_data = pickle.load(f)
                    roster.append(char_data)
            except Exception as e:
                print(f"Erreur loading {char_file}: {e}")
    except Exception as e:
        print(f"Erreur load_roster: {e}")
    return roster


def get_roster_character(name):
    """Récupère un personnage du roster par nom."""
    try:
        char_file = ROSTER_DIR / f"{name}.pkl"
        if char_file.exists():
            with open(char_file, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Erreur get_roster_character: {e}")
    return None


def delete_from_roster(name):
    """Supprime un personnage du roster."""
    try:
        char_file = ROSTER_DIR / f"{name}.pkl"
        if char_file.exists():
            char_file.unlink()
            return True
    except Exception as e:
        print(f"Erreur delete_from_roster: {e}")
    return False


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Page d'accueil."""
    if 'session_id' not in session:
        import uuid
        session['session_id'] = str(uuid.uuid4())
        session['party'] = []
        session['combat_state'] = None

    load_session_data()
    return render_template('index.html')


@app.route('/character/create', methods=['GET', 'POST'])
def character_create():
    """Formulaire de création de personnage."""
    races = get_races()
    classes = get_classes()

    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            name = request.form.get('name')
            race = request.form.get('race')
            class_name = request.form.get('class')
            level = int(request.form.get('level', 1))

            # Créer le personnage
            char = simple_character_generator(
                level=level,
                race_name=race,
                class_name=class_name,
                name=name
            )

            # Sérialiser le personnage
            char_data = serialize_character(char)

            # Sauvegarder SEULEMENT dans le roster (pas dans le groupe)
            save_to_roster(char_data)

            # Rediriger avec le personnage créé
            return render_template('character_create.html',
                                   races=races,
                                   classes=classes,
                                   character=char_data,
                                   success=True,
                                   message="Personnage créé et ajouté au roster ! Recrutez-le aux Training Grounds pour l'ajouter au groupe.")
        except Exception as e:
            return render_template('character_create.html',
                                   races=races,
                                   classes=classes,
                                   error=str(e))

    return render_template('character_create.html', races=races, classes=classes)


@app.route('/api/character/create', methods=['POST'])
def api_character_create():
    """API pour créer un personnage."""
    try:
        data = request.json

        # Validation
        if not all(k in data for k in ['name', 'race', 'class', 'level']):
            raise BadRequest("Champs manquants")

        # Créer le personnage
        char = simple_character_generator(
            level=int(data['level']),
            race_name=data['race'],
            class_name=data['class'],
            name=data['name']
        )

        # Sérialiser
        char_data = serialize_character(char)

        # Sauvegarder SEULEMENT dans le roster (pas dans le groupe)
        save_to_roster(char_data)

        return jsonify({
            'success': True,
            'character': char_data,
            'message': 'Personnage créé et ajouté au roster ! Allez aux Training Grounds pour le recruter dans le groupe.'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/party')
def party_view():
    """Affiche le groupe de personnages."""
    load_session_data()
    party = session.get('party', [])
    return render_template('party.html', party=party)


@app.route('/api/party/remove/<int:index>', methods=['POST'])
def api_party_remove(index):
    """Retire un personnage du groupe."""
    try:
        party = session.get('party', [])
        if 0 <= index < len(party):
            removed = party.pop(index)
            session['party'] = party
            session.modified = True
            save_session_data()
            return jsonify({'success': True, 'removed': removed})
        else:
            raise BadRequest("Index invalide")
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/combat')
def combat_view():
    """Interface de combat."""
    load_session_data()
    party = session.get('party', [])
    monsters = get_monsters()

    # Types de rencontres disponibles
    encounter_types = ['easy', 'medium', 'hard', 'deadly', 'random']

    return render_template('combat.html', party=party, monsters=monsters, encounter_types=encounter_types)


@app.route('/combat/auto', methods=['POST'])
def combat_auto():
    """Démarre un combat avec génération automatique depuis un formulaire."""
    try:
        encounter_type = request.form.get('encounter_type', 'random')
        if encounter_type == 'random':
            encounter_type = None  # None = aléatoire

        # Utiliser la même logique que api_combat_start
        load_session_data()
        party = session.get('party', [])

        if not party:
            return redirect(url_for('party_view'))

        # Vérifier qu'aucun personnage n'est mort
        dead_chars = [c for c in party if c.get('status') == 'DEAD']
        if dead_chars:
            session['error_message'] = f"Impossible de démarrer un combat ! {len(dead_chars)} personnage(s) sont morts. Ressuscitez-les au Temple de Cant."
            session.modified = True
            save_session_data()
            return redirect(url_for('combat_view'))

        # Créer les personnages
        characters = []
        for p in party:
            char = simple_character_generator(
                level=p['level'],
                race_name=p['race'],
                class_name=p['class'],
                name=p['name']
            )
            char.hit_points = p['hp']
            char.xp = p.get('xp', 0)
            char.gold = p.get('gold', 0)
            characters.append(char)

        # Calculer le niveau moyen du groupe
        party_level = sum(c.level for c in characters) // len(characters)

        # Charger les monstres disponibles
        available_monsters = get_monsters()

        # Déterminer le niveau de rencontre selon la difficulté
        if encounter_type == 'easy':
            # Facile: niveau inférieur au groupe
            encounter_level = max(1, party_level - 1)
        elif encounter_type == 'medium':
            # Moyen: niveau égal au groupe
            encounter_level = party_level
        elif encounter_type == 'hard':
            # Difficile: niveau supérieur
            encounter_level = min(20, party_level + 2)
        elif encounter_type == 'deadly':
            # Mortel: niveau très supérieur
            encounter_level = min(20, party_level + 4)
        else:
            # Aléatoire: utiliser generate_encounter_distribution
            from dnd_5e_core.mechanics import generate_encounter_distribution
            from random import choice
            encounter_levels = generate_encounter_distribution(party_level=party_level)
            encounter_level = choice(encounter_levels)

        # Charger les monstres via le système de rencontres
        from dnd_5e_core.mechanics.encounter_builder import select_monsters_by_encounter_table

        # Sélectionner les monstres
        monsters_result, actual_encounter_type = select_monsters_by_encounter_table(
            encounter_level=encounter_level,
            available_monsters=available_monsters,
            spell_casters_only=False,
            allow_pairs=True
        )

        if not monsters_result:
            return redirect(url_for('combat_view'))

        monsters = monsters_result

        # Initialiser le combat
        combat_messages = [
            "⚔️ Le combat commence !",
            f"📊 Rencontre {actual_encounter_type}",
            f"👥 Groupe de niveau {party_level}",
            f"👹 {len(monsters)} monstre(s): {', '.join(m.name.title() for m in monsters)}"
        ]

        # Sauvegarder l'état du combat
        session['combat_state'] = {
            'round': 1,
            'party': [serialize_character(c) for c in characters],
            'monsters': [serialize_monster(m) for m in monsters],
            'active': True,
            'messages': combat_messages,
            'encounter_type': actual_encounter_type
        }
        session.modified = True
        save_session_data()

        return redirect(url_for('combat_active'))

    except Exception as e:
        import traceback
        print(f"Erreur combat_auto: {e}")
        print(traceback.format_exc())
        return redirect(url_for('combat_view'))


@app.route('/api/combat/start', methods=['POST'])
def api_combat_start():
    """Démarre un combat (API JSON) avec génération automatique des monstres."""
    try:
        data = request.json
        party = session.get('party', [])

        if not party:
            raise BadRequest("Aucun personnage dans le groupe")

        # Créer les personnages
        characters = []
        for p in party:
            char = simple_character_generator(
                level=p['level'],
                race_name=p['race'],
                class_name=p['class'],
                name=p['name']
            )
            char.hit_points = p['hp']
            char.xp = p.get('xp', 0)
            char.gold = p.get('gold', 0)
            characters.append(char)

        # Calculer le niveau moyen du groupe
        party_level = sum(c.level for c in characters) // len(characters)

        # Déterminer le type de rencontre (facile, moyen, difficile, mortel)
        # Peut être spécifié ou aléatoire
        encounter_type = data.get('encounter_type', None)

        # Charger les monstres disponibles
        available_monsters = get_monsters()

        # Charger les monstres via le système de rencontres
        from dnd_5e_core.mechanics.encounter_builder import select_monsters_by_encounter_table

        try:
            # Déterminer le niveau de rencontre selon la difficulté
            if encounter_type == 'easy':
                encounter_level = max(1, party_level - 1)
            elif encounter_type == 'medium':
                encounter_level = party_level
            elif encounter_type == 'hard':
                encounter_level = min(20, party_level + 2)
            elif encounter_type == 'deadly':
                encounter_level = min(20, party_level + 4)
            else:
                # Aléatoire
                from dnd_5e_core.mechanics import generate_encounter_distribution
                from random import choice
                encounter_levels = generate_encounter_distribution(party_level=party_level)
                encounter_level = choice(encounter_levels)

            # Sélectionner les monstres
            monsters_result, actual_encounter_type = select_monsters_by_encounter_table(
                encounter_level=encounter_level,
                available_monsters=available_monsters,
                spell_casters_only=False,
                allow_pairs=True
            )

            if not monsters_result:
                raise Exception("Aucun monstre généré")

            monsters = monsters_result
            encounter_info = f"Rencontre {actual_encounter_type}"

        except Exception as e:
            # Fallback: utiliser la sélection manuelle si disponible
            monster_names = data.get('monsters', [])
            if monster_names:
                monsters = []
                for name in monster_names:
                    monster = load_monster(name)
                    if monster:
                        monsters.append(monster)
                encounter_info = "Rencontre personnalisée"
            else:
                raise BadRequest(f"Erreur lors de la génération de la rencontre: {str(e)}")

        if not monsters:
            raise BadRequest("Aucun monstre sélectionné")

        # Initialiser le combat
        combat_messages = [
            "⚔️ Le combat commence !",
            f"📊 {encounter_info}",
            f"👥 Groupe de niveau {party_level}",
            f"👹 {len(monsters)} monstre(s): {', '.join(m.name.title() for m in monsters)}"
        ]

        # Sauvegarder l'état du combat
        session['combat_state'] = {
            'round': 1,
            'party': [serialize_character(c) for c in characters],
            'monsters': [serialize_monster(m) for m in monsters],
            'active': True,
            'messages': combat_messages,
            'encounter_type': actual_encounter_type if 'actual_encounter_type' in locals() else 'custom'
        }
        session.modified = True
        save_session_data()

        return jsonify({
            'success': True,
            'redirect': '/combat/active'
        })

    except Exception as e:
        import traceback
        print(f"Erreur api_combat_start: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/combat/active')
def combat_active():
    """Page de combat actif."""
    load_session_data()
    combat_state = session.get('combat_state')

    if not combat_state:
        return redirect(url_for('combat_view'))

    # Vérifier victoire/défaite
    alive_party = [c for c in combat_state['party'] if c['hp'] > 0]
    alive_monsters = [m for m in combat_state['monsters'] if m['hp'] > 0]
    combat_won = len(alive_party) > 0 and len(alive_monsters) == 0

    return render_template('combat_active.html',
                          combat_state=combat_state,
                          combat_won=combat_won)


@app.route('/combat/turn', methods=['POST'])
def combat_turn():
    """Exécute un tour de combat (form POST)."""
    try:
        load_session_data()
        combat_state = session.get('combat_state')

        if not combat_state or not combat_state.get('active'):
            return redirect(url_for('combat_view'))

        # Recréer les personnages et monstres
        characters = []
        for p in combat_state['party']:
            char = simple_character_generator(
                level=p['level'],
                race_name=p['race'],
                class_name=p['class'],
                name=p['name']
            )
            char.hit_points = p['hp']
            char.xp = p.get('xp', 0)
            char.gold = p.get('gold', 0)
            characters.append(char)

        monsters = []
        for m in combat_state['monsters']:
            monster = load_monster(m['name'])
            if monster:
                monster.hit_points = m['hp']
                monsters.append(monster)

        # Exécuter le tour
        combat_messages = []

        def message_callback(msg):
            combat_messages.append(msg)

        combat = CombatSystem(verbose=False, message_callback=message_callback)

        alive_chars = [c for c in characters if c.hit_points > 0]
        alive_monsters = [m for m in monsters if m.hit_points > 0]

        if alive_chars and alive_monsters:
            # Tour des personnages
            for char in alive_chars:
                if alive_monsters:  # Vérifier qu'il reste des monstres
                    combat.character_turn(char, alive_chars, alive_monsters, characters)
                    alive_monsters = [m for m in monsters if m.hit_points > 0]

            # Tour des monstres
            for monster in alive_monsters[:]:
                if alive_chars and monster.hit_points > 0:
                    combat.monster_turn(monster, alive_monsters, alive_chars, characters, combat_state['round'])
                    alive_chars = [c for c in characters if c.hit_points > 0]

        # Mettre à jour l'état
        combat_state['party'] = [serialize_character(c) for c in characters]
        combat_state['monsters'] = [serialize_monster(m) for m in monsters]
        combat_state['round'] += 1
        combat_state['messages'].extend(combat_messages)

        # Vérifier fin du combat
        alive_party = [c for c in characters if c.hit_points > 0]
        alive_monsters = [m for m in monsters if m.hit_points > 0]

        if not alive_party or not alive_monsters:
            combat_state['active'] = False

            # TOUJOURS mettre à jour le groupe principal avec les stats du combat
            party = session.get('party', [])
            for p in party:
                for char in characters:
                    if p['name'] == char.name:
                        p['hp'] = char.hit_points
                        p['xp'] = char.xp
                        p['gold'] = char.gold
                        # Marquer le personnage comme mort si nécessaire
                        if char.hit_points <= 0:
                            p['status'] = 'DEAD'
                            # Sauvegarder immédiatement dans le roster
                            save_to_roster(p)
                        break
            session['party'] = party

            if not alive_party:
                combat_state['messages'].append("💀 Défaite ! Le groupe a été vaincu...")
                combat_state['messages'].append("⚠️ Les personnages morts doivent être ressuscités au Temple de Cant")
            else:
                # Calcul XP et or
                total_xp = sum(getattr(m, 'xp', 0) for m in monsters)
                xp_per_char = total_xp // len(alive_party)

                # Calculer l'or des monstres (environ 10% de leur XP)
                total_gold = sum(max(1, getattr(m, 'xp', 0) // 10) for m in monsters)
                gold_per_char = total_gold // len(alive_party)

                # Appliquer les gains
                for char in alive_party:
                    char.xp += xp_per_char
                    char.gold += gold_per_char

                combat_state['party'] = [serialize_character(c) for c in characters]
                combat_state['messages'].append(f"🏆 Victoire ! Tous les monstres sont vaincus !")
                combat_state['messages'].append(f"✨ Chaque personnage gagne {xp_per_char} XP et {gold_per_char} PO !")

        session['combat_state'] = combat_state
        session.modified = True
        save_session_data()

        return redirect(url_for('combat_active'))

    except Exception as e:
        import traceback
        print(f"Erreur combat: {e}")
        print(traceback.format_exc())
        return redirect(url_for('combat_view'))


@app.route('/combat/end', methods=['POST'])
def combat_end():
    """Termine le combat en cours."""
    session['combat_state'] = None
    session.modified = True
    save_session_data()
    return redirect(url_for('combat_view'))


@app.route('/character/<int:index>')
def character_sheet(index):
    """Affiche la fiche d'un personnage."""
    load_session_data()
    party = session.get('party', [])

    if 0 <= index < len(party):
        character = party[index]
        # S'assurer que l'inventaire existe et est une liste
        if 'inventory' not in character or not isinstance(character.get('inventory'), list):
            character['inventory'] = []
        # S'assurer que status existe
        if 'status' not in character:
            character['status'] = 'OK'
        return render_template('character_sheet.html', character=character, index=index)
    else:
        return redirect(url_for('party_view'))


@app.route('/character/<int:index>/inventory')
def character_inventory(index):
    """Affiche l'inventaire détaillé d'un personnage."""
    load_session_data()
    party = session.get('party', [])

    if 0 <= index < len(party):
        character = party[index]
        # S'assurer que l'inventaire existe
        if 'inventory' not in character or not isinstance(character.get('inventory'), list):
            character['inventory'] = []
        return render_template('character_inventory.html', character=character, index=index)
    else:
        return redirect(url_for('party_view'))


@app.route('/api/character/<int:index>/equip', methods=['POST'])
def character_equip(index):
    """Équipe un item de l'inventaire."""
    try:
        data = request.json
        item_name = data.get('item_name')
        item_type = data.get('item_type')

        load_session_data()
        party = session.get('party', [])

        if index < 0 or index >= len(party):
            raise BadRequest("Personnage invalide")

        character = party[index]
        inventory = character.get('inventory', [])
        if not isinstance(inventory, list):
            inventory = []

        # Trouver l'item dans l'inventaire
        item_to_equip = None
        for item in inventory:
            if item.get('name') == item_name:
                item_to_equip = item
                break

        if not item_to_equip:
            return jsonify({'success': False, 'error': 'Item non trouvé dans l\'inventaire'}), 400

        # Équiper selon le type
        if item_type == 'Weapon':
            # Déséquiper l'arme actuelle si présente
            if character.get('weapon'):
                old_weapon = character['weapon']
                # Vérifier que l'ancienne arme n'est pas déjà dans l'inventaire
                if not any(item.get('name') == old_weapon for item in inventory):
                    inventory.append({'name': old_weapon, 'type': 'Weapon'})
            character['weapon'] = item_name
            inventory.remove(item_to_equip)
            message = f"{item_name} équipé comme arme !"

        elif item_type == 'Armor':
            if character.get('armor'):
                old_armor = character['armor']
                if not any(item.get('name') == old_armor for item in inventory):
                    inventory.append({'name': old_armor, 'type': 'Armor'})
            character['armor'] = item_name
            inventory.remove(item_to_equip)
            message = f"{item_name} équipé comme armure !"

        elif item_type == 'Shield':
            if character.get('shield'):
                old_shield = character['shield']
                if not any(item.get('name') == old_shield for item in inventory):
                    inventory.append({'name': old_shield, 'type': 'Shield'})
            character['shield'] = item_name
            inventory.remove(item_to_equip)
            message = f"{item_name} équipé comme bouclier !"
        else:
            return jsonify({'success': False, 'error': 'Type d\'item non équipable'}), 400

        character['inventory'] = inventory
        session['party'] = party
        session.modified = True
        save_session_data()

        # Sauvegarder aussi dans le roster pour synchronisation
        save_to_roster(character)

        return jsonify({'success': True, 'message': message})

    except Exception as e:
        import traceback
        print(f"Erreur character_equip: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/character/<int:index>/unequip-all', methods=['POST'])
def character_unequip_all(index):
    """Déséquipe tout l'équipement et le remet dans l'inventaire."""
    try:
        load_session_data()
        party = session.get('party', [])

        if index < 0 or index >= len(party):
            raise BadRequest("Personnage invalide")

        character = party[index]
        inventory = character.get('inventory', [])
        if not isinstance(inventory, list):
            inventory = []

        unequipped = []

        # Vérifier et déséquiper l'arme
        if character.get('weapon'):
            weapon_name = character['weapon']
            # Vérifier que l'arme n'est pas déjà dans l'inventaire
            if not any(item.get('name') == weapon_name for item in inventory):
                inventory.append({'name': weapon_name, 'type': 'Weapon'})
            unequipped.append(weapon_name)
            character['weapon'] = None

        # Vérifier et déséquiper l'armure
        if character.get('armor'):
            armor_name = character['armor']
            if not any(item.get('name') == armor_name for item in inventory):
                inventory.append({'name': armor_name, 'type': 'Armor'})
            unequipped.append(armor_name)
            character['armor'] = None

        # Vérifier et déséquiper le bouclier
        if character.get('shield'):
            shield_name = character['shield']
            if not any(item.get('name') == shield_name for item in inventory):
                inventory.append({'name': shield_name, 'type': 'Shield'})
            unequipped.append(shield_name)
            character['shield'] = None

        character['inventory'] = inventory
        session['party'] = party
        session.modified = True
        save_session_data()

        # Sauvegarder aussi dans le roster pour synchronisation
        save_to_roster(character)

        if unequipped:
            message = f"Déséquipé: {', '.join(unequipped)}"
        else:
            message = "Aucun équipement à retirer"

        return jsonify({'success': True, 'message': message})

    except Exception as e:
        import traceback
        print(f"Erreur character_unequip_all: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/character/<int:index>/drop', methods=['POST'])
def character_drop(index):
    """Jette un item de l'inventaire."""
    try:
        data = request.json
        item_name = data.get('item_name')

        load_session_data()
        party = session.get('party', [])

        if index < 0 or index >= len(party):
            raise BadRequest("Personnage invalide")

        character = party[index]
        inventory = character.get('inventory', [])

        # Trouver et retirer l'item
        item_found = None
        for item in inventory:
            if item.get('name') == item_name:
                item_found = item
                break

        if item_found:
            inventory.remove(item_found)
            character['inventory'] = inventory
            session['party'] = party
            session.modified = True
            save_session_data()

            # Sauvegarder aussi dans le roster pour synchronisation
            save_to_roster(character)

            return jsonify({'success': True, 'message': f"{item_name} a été jeté"})
        else:
            return jsonify({'success': False, 'error': 'Item non trouvé'}), 400

    except Exception as e:
        import traceback
        print(f"Erreur character_drop: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


# ==================== PARTY MANAGEMENT ====================

@app.route('/api/party/remove/<int:index>', methods=['POST'])
def party_remove(index):
    """Retire un personnage du groupe."""
    try:
        load_session_data()
        party = session.get('party', [])

        if 0 <= index < len(party):
            removed = party.pop(index)
            session['party'] = party
            session.modified = True
            save_session_data()
            return jsonify({'success': True, 'message': f"{removed['name']} a été retiré du groupe"})
        else:
            return jsonify({'success': False, 'error': 'Index invalide'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/party/reorder', methods=['POST'])
def party_reorder():
    """Réorganise le groupe selon l'ordre donné."""
    try:
        data = request.json
        name_order = data.get('order', [])

        load_session_data()
        party = session.get('party', [])

        # Créer un nouveau groupe dans l'ordre spécifié
        new_party = []
        for name in name_order:
            for char in party:
                if char['name'] == name:
                    new_party.append(char)
                    break

        if len(new_party) == len(party):
            session['party'] = new_party
            session.modified = True
            save_session_data()
            return jsonify({'success': True, 'message': 'Groupe réorganisé !'})
        else:
            return jsonify({'success': False, 'error': 'Erreur de réorganisation'}), 400
    except Exception as e:
        import traceback
        print(f"Erreur party_reorder: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/party/divvy-gold', methods=['POST'])
def party_divvy_gold():
    """Répartit équitablement l'or du groupe entre tous les personnages."""
    try:
        load_session_data()
        party = session.get('party', [])

        if not party:
            return jsonify({'success': False, 'error': 'Aucun personnage dans le groupe'}), 400

        # Calculer le total d'or et la part de chacun
        total_gold = sum(char.get('gold', 0) for char in party)
        share = total_gold // len(party)

        # Répartir équitablement
        for char in party:
            char['gold'] = share

        session['party'] = party
        session.modified = True
        save_session_data()

        return jsonify({
            'success': True,
            'message': f"Or réparti équitablement : {share} PO par personnage (total: {total_gold} PO)"
        })
    except Exception as e:
        import traceback
        print(f"Erreur party_divvy_gold: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/party/disband', methods=['POST'])
def party_disband():
    """Dissout le groupe en sauvegardant les personnages dans le roster."""
    try:
        load_session_data()
        party = session.get('party', [])

        if not party:
            return jsonify({'success': False, 'error': 'Aucun groupe à dissoudre'}), 400

        # Sauvegarder tous les personnages dans le roster
        count = 0
        for char in party:
            if save_to_roster(char):
                count += 1

        # Vider le groupe
        session['party'] = []
        session.modified = True
        save_session_data()

        return jsonify({
            'success': True,
            'message': f"Le groupe a été dissous. {count} personnage(s) sauvegardé(s) dans le roster."
        })
    except Exception as e:
        import traceback
        print(f"Erreur party_disband: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


# ==================== LOCATIONS ====================

@app.route('/castle')
def castle_view():
    """Vue principale du château avec toutes les locations."""
    load_session_data()
    party = session.get('party', [])

    # Nettoyer automatiquement les personnages morts du groupe
    dead_chars = [c for c in party if c.get('status') == 'DEAD']
    if dead_chars:
        # Sauvegarder les morts dans le roster
        for char in dead_chars:
            save_to_roster(char)

        # Retirer du groupe
        party = [c for c in party if c.get('status') != 'DEAD']
        session['party'] = party
        session['info_message'] = f"{len(dead_chars)} personnage(s) mort(s) ont été retirés du groupe et sauvegardés. Ressuscitez-les au Temple avant de les réintégrer."
        session.modified = True
        save_session_data()

    return render_template('castle.html', party=party)


@app.route('/tavern')
def tavern_view():
    """Taverne de Gilgamesh - Recrutement et gestion du groupe."""
    load_session_data()
    party = session.get('party', [])

    # Récupérer tous les personnages du roster (hors du groupe actuel)
    # Pour l'instant, on utilise juste les personnages sauvegardés dans la session
    available_chars = []  # TODO: Charger depuis le roster

    return render_template('tavern.html', party=party, available_chars=available_chars)


@app.route('/inn')
def inn_view():
    """Auberge - Repos et récupération."""
    load_session_data()
    party = session.get('party', [])
    return render_template('inn.html', party=party)


@app.route('/api/inn/rest', methods=['POST'])
def inn_rest():
    """Fait reposer un personnage à l'auberge."""
    try:
        data = request.json
        char_index = int(data.get('character_index', 0))
        room_type = data.get('room_type', 'stables')  # stables, cot, economy, merchant, royal

        load_session_data()
        party = session.get('party', [])

        if char_index < 0 or char_index >= len(party):
            raise BadRequest("Personnage invalide")

        character = party[char_index]

        # Coûts des chambres (en PO)
        room_costs = {
            'stables': 1,
            'cot': 5,
            'economy': 25,
            'merchant': 50,
            'royal': 200
        }

        cost = room_costs.get(room_type, 1)

        # Vérifier l'or
        if character.get('gold', 0) < cost:
            return jsonify({
                'success': False,
                'error': f"Pas assez d'or ! Nécessaire: {cost} PO"
            }), 400

        # Déduire l'or
        character['gold'] -= cost

        # Restaurer les HP et les spell slots
        character['hp'] = character['max_hp']

        # Restaurer les spell slots si le personnage est un lanceur de sorts
        # TODO: Implémenter la restauration des spell slots via simple_character_generator

        session['party'] = party
        session.modified = True
        save_session_data()

        return jsonify({
            'success': True,
            'message': f"{character['name']} a bien reposé dans {room_type} pour {cost} PO !",
            'remaining_gold': character['gold'],
            'hp_restored': character['max_hp']
        })

    except Exception as e:
        import traceback
        print(f"Erreur inn_rest: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/temple')
def temple_view():
    """Temple de Cant - Soins et résurrection."""
    load_session_data()
    party = session.get('party', [])

    # Charger le roster et filtrer les personnages morts
    roster = load_roster()
    dead_chars = [c for c in roster if c.get('status') == 'DEAD']

    return render_template('temple.html', party=party, dead_chars=dead_chars)


@app.route('/api/temple/heal', methods=['POST'])
def temple_heal():
    """Soigne un personnage au temple."""
    try:
        data = request.json
        char_index = int(data.get('character_index', 0))

        load_session_data()
        party = session.get('party', [])

        if char_index < 0 or char_index >= len(party):
            raise BadRequest("Personnage invalide")

        character = party[char_index]

        # Vérifier si le personnage est mort
        if character.get('status') == 'DEAD':
            return jsonify({
                'success': False,
                'error': "Ce personnage est mort ! Utilisez la résurrection."
            }), 400

        # Calculer le coût des soins (10 PO par HP manquant)
        hp_missing = character['max_hp'] - character['hp']
        cost = hp_missing * 10

        if cost == 0:
            return jsonify({
                'success': False,
                'error': "Ce personnage est déjà en pleine santé !"
            }), 400

        # Vérifier l'or
        if character.get('gold', 0) < cost:
            return jsonify({
                'success': False,
                'error': f"Pas assez d'or ! Nécessaire: {cost} PO pour restaurer {hp_missing} HP"
            }), 400

        # Déduire l'or et restaurer les HP
        character['gold'] -= cost
        character['hp'] = character['max_hp']

        session['party'] = party
        session.modified = True
        save_session_data()

        return jsonify({
            'success': True,
            'message': f"{character['name']} a été soigné de {hp_missing} HP pour {cost} PO !",
            'remaining_gold': character['gold'],
            'hp_restored': hp_missing
        })

    except Exception as e:
        import traceback
        print(f"Erreur temple_heal: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/temple/resurrect', methods=['POST'])
def temple_resurrect():
    """Ressuscite un personnage mort au temple."""
    try:
        data = request.json
        char_index = int(data.get('character_index', 0))

        load_session_data()
        party = session.get('party', [])

        if char_index < 0 or char_index >= len(party):
            raise BadRequest("Personnage invalide")

        character = party[char_index]

        # Vérifier si le personnage est mort
        if character.get('status') != 'DEAD':
            return jsonify({
                'success': False,
                'error': "Ce personnage n'est pas mort !"
            }), 400

        # Coût de la résurrection (1000 PO)
        cost = 1000

        # Vérifier l'or
        if character.get('gold', 0) < cost:
            return jsonify({
                'success': False,
                'error': f"Pas assez d'or ! La résurrection coûte {cost} PO"
            }), 400

        # Déduire l'or et ressusciter
        character['gold'] -= cost
        character['hp'] = character['max_hp'] // 2  # Revient à 50% HP
        character['status'] = 'OK'

        session['party'] = party
        session.modified = True
        save_session_data()

        return jsonify({
            'success': True,
            'message': f"{character['name']} a été ressuscité pour {cost} PO ! (HP: {character['hp']}/{character['max_hp']})",
            'remaining_gold': character['gold']
        })

    except Exception as e:
        import traceback
        print(f"Erreur temple_resurrect: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/temple/resurrect-roster', methods=['POST'])
def temple_resurrect_roster():
    """Ressuscite un personnage mort du roster, payé par un personnage du groupe."""
    try:
        data = request.json
        dead_char_name = data.get('character_name')
        payer_index = int(data.get('payer_index', 0))

        load_session_data()
        party = session.get('party', [])

        # Vérifier le payeur
        if payer_index < 0 or payer_index >= len(party):
            raise BadRequest("Payeur invalide")

        payer = party[payer_index]

        # Charger le personnage mort du roster
        dead_char = get_roster_character(dead_char_name)

        if not dead_char or dead_char.get('status') != 'DEAD':
            return jsonify({
                'success': False,
                'error': "Personnage non trouvé ou pas mort"
            }), 400

        # Coût basé sur le niveau (comme main_ncurses.py)
        cost = 250 * dead_char.get('level', 1)

        # Vérifier l'or du payeur
        if payer.get('gold', 0) < cost:
            return jsonify({
                'success': False,
                'error': f"Pas assez d'or ! Nécessaire: {cost} PO, disponible: {payer.get('gold', 0)} PO"
            }), 400

        # Déduire l'or du payeur
        payer['gold'] -= cost

        # Ressusciter le personnage
        dead_char['hp'] = dead_char['max_hp'] // 2
        dead_char['status'] = 'OK'

        # Sauvegarder dans le roster
        save_to_roster(dead_char)

        # Sauvegarder le groupe
        session['party'] = party
        session.modified = True
        save_session_data()

        return jsonify({
            'success': True,
            'message': f"{dead_char['name']} a été ressuscité pour {cost} PO par {payer['name']} ! (HP: {dead_char['hp']}/{dead_char['max_hp']})",
            'payer_remaining_gold': payer['gold']
        })

    except Exception as e:
        import traceback
        print(f"Erreur temple_resurrect_roster: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/edge-of-town')
def edge_of_town_view():
    """Edge of Town - Accès au donjon et aux terrains d'entraînement."""
    load_session_data()
    party = session.get('party', [])
    return render_template('edge_of_town.html', party=party)


@app.route('/training-grounds')
def training_grounds_view():
    """Terrains d'entraînement - Création et gestion des personnages."""
    load_session_data()
    party = session.get('party', [])

    # Charger le roster complet
    roster = load_roster()

    return render_template('training_grounds.html', party=party, roster=roster)


@app.route('/api/roster/recruit/<name>', methods=['POST'])
def roster_recruit(name):
    """Recrute un personnage du roster dans le groupe."""
    try:
        load_session_data()
        party = session.get('party', [])

        # Vérifier la limite du groupe (max 6)
        if len(party) >= 6:
            return jsonify({
                'success': False,
                'error': 'Groupe complet ! Maximum 6 personnages.'
            }), 400

        # Charger le personnage du roster
        char = get_roster_character(name)

        if not char:
            return jsonify({
                'success': False,
                'error': 'Personnage non trouvé dans le roster.'
            }), 404

        # Vérifier que le personnage n'est pas déjà dans le groupe
        if any(p['name'] == name for p in party):
            return jsonify({
                'success': False,
                'error': f'{name} est déjà dans le groupe !'
            }), 400

        # Vérifier que le personnage n'est pas mort
        if char.get('status') == 'DEAD':
            return jsonify({
                'success': False,
                'error': f'{name} est mort ! Ressuscitez-le au Temple avant de le recruter.'
            }), 400

        # Ajouter au groupe
        party.append(char)
        session['party'] = party
        session.modified = True
        save_session_data()

        return jsonify({
            'success': True,
            'message': f'{name} a rejoint le groupe !'
        })

    except Exception as e:
        import traceback
        print(f"Erreur roster_recruit: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/combat/turn', methods=['POST'])
def api_combat_turn():
    """Exécute un tour de combat."""
    try:
        data = request.json
        combat_state = session.get('combat_state')

        if not combat_state or not combat_state.get('active'):
            raise BadRequest("Aucun combat actif")

        # Recréer les personnages et monstres
        characters = []
        for p in combat_state['party']:
            char = simple_character_generator(
                level=p['level'],
                race_name=p['race'],
                class_name=p['class'],
                name=p['name']
            )
            char.hit_points = p['hp']
            characters.append(char)

        monsters = []
        for m in combat_state['monsters']:
            monster = load_monster(m['name'])
            monster.hit_points = m['hp']
            monsters.append(monster)

        # Exécuter le tour
        combat_messages = []

        def message_callback(msg):
            combat_messages.append(msg)

        combat = CombatSystem(verbose=False, message_callback=message_callback)

        char_index = data.get('character_index', 0)
        target_index = data.get('target_index', 0)
        action_type = data.get('action_type', 'melee')

        if char_index < len(characters) and target_index < len(monsters):
            # Tour du personnage
            alive_chars = [c for c in characters if c.hit_points > 0]
            alive_monsters = [m for m in monsters if m.hit_points > 0]

            if alive_chars and alive_monsters:
                combat.character_turn(
                    characters[char_index],
                    alive_chars,
                    alive_monsters,
                    characters
                )

                # Tour des monstres
                for monster in alive_monsters[:]:
                    if monster.hit_points > 0:
                        combat.monster_turn(monster, alive_monsters, alive_chars, characters, combat_state['round'])

        # Mettre à jour l'état
        combat_state['party'] = [serialize_character(c) for c in characters]
        combat_state['monsters'] = [serialize_monster(m) for m in monsters]
        combat_state['round'] += 1
        combat_state['messages'].extend(combat_messages)

        # Vérifier fin du combat
        alive_party = [c for c in characters if c.hit_points > 0]
        alive_monsters = [m for m in monsters if m.hit_points > 0]

        if not alive_party or not alive_monsters:
            combat_state['active'] = False
            if not alive_party:
                combat_messages.append("💀 Défaite ! Le groupe a été vaincu...")
            else:
                combat_messages.append("🏆 Victoire ! Tous les monstres sont vaincus !")

        session['combat_state'] = combat_state
        session.modified = True
        save_session_data()

        return jsonify({
            'success': True,
            'combat_state': combat_state,
            'messages': combat_messages
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/combat/end', methods=['POST'])
def api_combat_end():
    """Termine le combat en cours."""
    session['combat_state'] = None
    session.modified = True
    save_session_data()
    return jsonify({'success': True})


@app.route('/api/info/races')
def api_info_races():
    """Liste toutes les races disponibles."""
    races = get_races()
    return jsonify({'races': races})


@app.route('/api/info/classes')
def api_info_classes():
    """Liste toutes les classes disponibles."""
    classes = get_classes()
    return jsonify({'classes': classes})


@app.route('/api/info/monsters')
def api_info_monsters():
    """Liste tous les monstres disponibles."""
    monsters = get_monsters()
    return jsonify({'monsters': monsters})


# ==================== CHEAT MODE ====================

@app.route('/api/cheat/heal_party', methods=['POST'])
def cheat_heal_party():
    """CHEAT: Soigne tout le groupe au maximum."""
    try:
        load_session_data()
        party = session.get('party', [])

        for char in party:
            char['hp'] = char['max_hp']

        session['party'] = party
        session.modified = True
        save_session_data()

        return jsonify({'success': True, 'message': '✨ Le groupe a été complètement soigné !'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/cheat/add_gold', methods=['POST'])
def cheat_add_gold():
    """CHEAT: Ajoute de l'or à tout le groupe."""
    try:
        data = request.json
        amount = int(data.get('amount', 1000))

        load_session_data()
        party = session.get('party', [])

        for char in party:
            char['gold'] = char.get('gold', 0) + amount

        session['party'] = party
        session.modified = True
        save_session_data()

        return jsonify({'success': True, 'message': f'✨ {amount} PO ajoutées à chaque personnage !'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/cheat/level_up', methods=['POST'])
def cheat_level_up():
    """CHEAT: Fait monter tout le groupe de niveau."""
    try:
        load_session_data()
        party = session.get('party', [])

        for char_data in party:
            # Recréer le personnage avec le nouveau niveau
            new_level = char_data['level'] + 1
            if new_level > 20:
                continue

            char = simple_character_generator(
                level=new_level,
                race_name=char_data['race'],
                class_name=char_data['class'],
                name=char_data['name']
            )

            # Préserver l'or et l'XP
            char.gold = char_data.get('gold', 0)
            char.xp = char_data.get('xp', 0)

            # Mettre à jour les données
            char_data.update(serialize_character(char))

        session['party'] = party
        session.modified = True
        save_session_data()

        return jsonify({'success': True, 'message': '✨ Le groupe a gagné un niveau !'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==================== SHOP ====================

@app.route('/shop')
def shop_view():
    """Interface du magasin Boltac."""
    load_session_data()
    party = session.get('party', [])

    # Importer le magasin Boltac
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    try:
        from boltac_shop import BoltacShop
        shop = BoltacShop()

        # Récupérer le catalogue (méthodes correctes)
        weapons = shop.get_all_weapons()
        armors = shop.get_all_armors()
        magic_items_with_stock = shop.get_magic_items_in_stock()

        # Convertir magic_items en liste simple
        magic_items = [item for item, stock in magic_items_with_stock]

        return render_template('shop.html',
                             party=party,
                             weapons=weapons,
                             armors=armors,
                             magic_items=magic_items,
                             shop_gold=shop.shop_gold)
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        return render_template('shop.html',
                             party=party,
                             error=error_detail)


@app.route('/api/shop/buy', methods=['POST'])
def shop_buy():
    """Acheter un item au magasin Boltac."""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from boltac_shop import BoltacShop
        from dnd_5e_core.data.loader import load_weapon, load_armor, load_equipment
        from dnd_5e_core.equipment import get_magic_item, get_special_weapon, get_special_armor

        data = request.json
        char_index = int(data.get('character_index', 0))
        item_index = data.get('item_index')
        item_type = data.get('item_type', 'weapon')

        load_session_data()
        party = session.get('party', [])

        if char_index < 0 or char_index >= len(party):
            raise BadRequest("Personnage invalide")

        character = party[char_index]

        # Charger l'item
        item = None
        if item_type == 'magic':
            item = get_magic_item(item_index)
            if not item:
                item = get_special_weapon(item_index)
            if not item:
                item = get_special_armor(item_index)
        elif item_type == 'weapon':
            item = load_weapon(item_index)
        elif item_type == 'armor':
            item = load_armor(item_index)
        else:
            item = load_equipment(item_index)

        if not item:
            raise BadRequest(f"Item '{item_index}' introuvable")

        # Obtenir le prix (gérer l'objet Cost correctement)
        price_cp = 0
        if hasattr(item, 'cost') and item.cost:
            if hasattr(item.cost, 'value'):
                # Cost object avec propriété value (en copper pieces)
                price_cp = item.cost.value
            elif isinstance(item.cost, int):
                # Simple entier (déjà en CP probablement)
                price_cp = item.cost
            else:
                # Fallback
                price_cp = 0

        # Convertir en PO
        price_gp = price_cp / 100 if price_cp > 0 else 0

        # Si le prix est à 0, utiliser un prix par défaut basé sur le type
        if price_gp == 0:
            if item_type == 'magic':
                price_gp = 500  # Prix par défaut pour items magiques
            elif item_type == 'weapon':
                price_gp = 10
            elif item_type == 'armor':
                price_gp = 50
            else:
                price_gp = 5

        # Vérifier l'or du personnage
        char_gold = character.get('gold', 0)
        if char_gold < price_gp:
            return jsonify({
                'success': False,
                'error': f"Pas assez d'or ! Nécessaire: {price_gp} PO, disponible: {char_gold} PO"
            }), 400

        # Vérifier le stock
        shop = BoltacShop()
        stock = shop.get_item_stock(item)

        if stock == 0:
            return jsonify({'success': False, 'error': "Item en rupture de stock !"}), 400

        # Acheter l'item
        if not shop.buy_item(item, 1):
            return jsonify({'success': False, 'error': "Erreur lors de l'achat"}), 400

        # Déduire l'or
        character['gold'] = char_gold - price_gp

        # Ajouter à l'inventaire
        if 'inventory' not in character:
            character['inventory'] = []

        character['inventory'].append({
            'name': item.name,
            'type': type(item).__name__,
        })

        session['party'] = party
        session.modified = True
        save_session_data()

        # Synchroniser avec le roster
        save_to_roster(character)

        return jsonify({
            'success': True,
            'message': f"{item.name} acheté pour {price_gp} PO !",
            'remaining_gold': character['gold']
        })

    except Exception as e:
        import traceback
        print(f"Erreur shop_buy: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/shop/sell', methods=['POST'])
def shop_sell():
    """Vendre un item au magasin Boltac."""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from boltac_shop import BoltacShop

        data = request.json
        char_index = int(data.get('character_index', 0))
        item_name = data.get('item_name')

        load_session_data()
        party = session.get('party', [])

        if char_index < 0 or char_index >= len(party):
            raise BadRequest("Personnage invalide")

        character = party[char_index]
        inventory = character.get('inventory', [])

        # Trouver l'item
        item_data = None
        item_idx = -1
        for i, inv_item in enumerate(inventory):
            if inv_item.get('name') == item_name:
                item_data = inv_item
                item_idx = i
                break

        if not item_data:
            raise BadRequest(f"Item '{item_name}' non trouvé dans l'inventaire")

        # Prix de vente (50% du prix d'achat estimé)
        sell_price = 5  # Prix par défaut

        # Retirer de l'inventaire
        inventory.pop(item_idx)
        character['inventory'] = inventory

        # Ajouter l'or
        character['gold'] = character.get('gold', 0) + sell_price

        session['party'] = party
        session.modified = True
        save_session_data()

        # Synchroniser avec le roster
        save_to_roster(character)

        # Note: On pourrait aussi ajouter l'item au magasin via shop.sell_item()

        return jsonify({
            'success': True,
            'message': f"{item_name} vendu pour {sell_price} PO !",
            'remaining_gold': character['gold']
        })

    except Exception as e:
        import traceback
        print(f"Erreur shop_sell: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
