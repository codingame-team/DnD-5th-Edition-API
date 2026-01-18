import random
import sys
from typing import List
from tools.gene_maze_dfs import generate_maze

class Entity:
    def __init__(self, name, x, y, hp, attack):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.attack = attack

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)

    def heal(self, amount):
        self.hp = min(100, self.hp + amount)

class Player(Entity):
    def __init__(self, name="Héros", x=0, y=0):
        super().__init__(name, x, y, 100, 20)

class Enemy(Entity):
    def __init__(self, name="Monstre", x=0, y=0):
        super().__init__(name, x, y, 50, 10)

def load_new_maze(level: int = 1) -> List[str]:
    width = height = 15  # Smaller for simple display
    maze, _, _ = generate_maze(width, height)
    return ["".join("#" if cell else " " for cell in row) for row in maze][:-1]

def display_map(game_map, player, enemies):
    print("\033[2J\033[H")  # Clear screen
    for y, row in enumerate(game_map):
        line = ""
        for x, cell in enumerate(row):
            if (x, y) == (player.x, player.y):
                line += "@"
            elif any((x, y) == (e.x, e.y) for e in enemies):
                line += "E"
            else:
                line += cell
        print(line)
    print(f"HP: {player.hp} | Pos: ({player.x},{player.y})")

def combat(player, enemy):
    print(f"\nCombat avec {enemy.name}!")
    while player.hp > 0 and enemy.hp > 0:
        print(f"{player.name}: {player.hp} HP | {enemy.name}: {enemy.hp} HP")
        action = input("(a)ttaquer, (h)eal, (q)uit: ").lower()
        if action == 'a':
            damage = random.randint(15, player.attack)
            enemy.take_damage(damage)
            print(f"Vous infligez {damage} dégâts!")
        elif action == 'h':
            heal = random.randint(10, 30)
            player.heal(heal)
            print(f"Vous récupérez {heal} HP!")
        elif action == 'q':
            break
        
        if enemy.hp > 0:
            damage = random.randint(5, enemy.attack)
            player.take_damage(damage)
            print(f"{enemy.name} vous inflige {damage} dégâts!")
    
    if enemy.hp <= 0:
        print(f"{enemy.name} est vaincu!")
        return True
    return False

def main():
    game_map = load_new_maze()
    player = Player(x=len(game_map[0]) // 2, y=len(game_map) // 2)
    enemies = [Enemy(x=random.randint(1, len(game_map[0])-2), 
                    y=random.randint(1, len(game_map)-2)) for _ in range(3)]
    
    print("Utilisez z/s/q/d pour vous déplacer, 'quit' pour quitter")
    
    while True:
        display_map(game_map, player, enemies)
        move = input("Mouvement: ").lower()
        
        if move == 'quit':
            break
        
        dx, dy = 0, 0
        if move == 'z': dy = -1
        elif move == 's': dy = 1
        elif move == 'q': dx = -1
        elif move == 'd': dx = 1
        
        new_x, new_y = player.x + dx, player.y + dy
        
        if (0 <= new_x < len(game_map[0]) and 
            0 <= new_y < len(game_map) and 
            game_map[new_y][new_x] != "#"):
            
            player.x, player.y = new_x, new_y
            
            for enemy in enemies[:]:
                if (new_x, new_y) == (enemy.x, enemy.y):
                    if combat(player, enemy):
                        enemies.remove(enemy)
                    break

if __name__ == "__main__":
    main()