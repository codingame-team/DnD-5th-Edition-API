"""
Algorithmes sur les graphes: Labyrinthe - Algorithme de Lee
"""
from collections import deque
from typing import List

"""
    Règles à respecter
    
    - Il faut rester dans la carte
    - Les murs sont infranchissables
    - Il faut noter les cases visitées
    0 -----> y
    |
    v
    x
"""

# Liste des déplacements possibles
directions: List[tuple] = [(-1, 0), (0, -1), (1, 0), (0, 1)]

from typing import List, Tuple
from collections import deque
import heapq

def heuristic(x1: int, y1: int, x2: int, y2: int) -> int:
    """
    Heuristic function to estimate the cost from (x1, y1) to (x2, y2).
    In this case, we use the Manhattan distance.
    """
    return abs(x1 - x2) + abs(y1 - y2)

def parcours_a_star(carte: List[List[int]], start_x: int, start_y: int, end_x: int, end_y: int, obstacles: List[tuple] = None) -> Tuple[int, dict]:
    width, height = len(carte[0]), len(carte)
    visited = [[False] * width for _ in range(height)]
    to_visit: list = [(0, start_x, start_y, 0)]  # (f_cost, x, y, g_cost)
    min_dist = float('inf')
    pred: dict = {}

    if obstacles is None:
        obstacles = []

    while to_visit:
        _, x, y, g_cost = heapq.heappop(to_visit)
        if (x, y) == (end_x, end_y):
            min_dist = g_cost
            break

        if not visited[y][x]:
            visited[y][x] = True

            for dx, dy in directions:
                neigh_x, neigh_y = x + dx, y + dy
                if 0 <= neigh_x < width and 0 <= neigh_y < height:
                    # si le voisin est accessible
                    if (neigh_x, neigh_y) not in obstacles and carte[neigh_y][neigh_x] == 1:
                        if not visited[neigh_y][neigh_x]:
                            # f_cost = g_cost + h_cost
                            # g_cost is the actual cost of the path from the start node to the current node.
                            # h_cost is the estimated cost from the current node to the goal node.
                            f_cost = g_cost + 1 + abs(end_x - neigh_x) + abs(end_y - neigh_y)
                            heapq.heappush(to_visit, (f_cost, neigh_x, neigh_y, g_cost + 1))
                            pred[(neigh_x, neigh_y)] = x, y

    return min_dist, pred


# Retrouver la distance minimum entre le point (i, j) et la destination (x, y)
def parcours_largeur(carte: List[List[int]], start_x: int, start_y: int, end_x: int, end_y: int, obstacles: List[tuple] = None) -> int:
    width, height = len(carte[0]), len(carte)
    visited = [[False] * width for _ in range(height)]
    to_visit: deque = deque([(start_x, start_y, 0)])
    min_dist = float('inf')

    pred: dict() = {}

    if obstacles is None:
        obstacles = []
    while to_visit:
        x, y, dist = to_visit.popleft()
        if (x, y) == (end_x, end_y):
            min_dist = dist
            break

        for dx, dy in directions:
            neigh_x, neigh_y = x + dx, y + dy
            # Si le voisin est bien sur la carte
            if 0 <= neigh_x < width and 0 <= neigh_y < height:
                # si le voisin est accessible
                if (neigh_x, neigh_y) not in obstacles and carte[neigh_y][neigh_x] == 1:
                    # si le voisin n'a pas encore été visité
                    if not visited[neigh_y][neigh_x]:
                        visited[neigh_y][neigh_x] = True
                        to_visit.append((neigh_x, neigh_y, dist + 1))

                        pred[(neigh_x, neigh_y)] = x, y

    return min_dist, pred

# algorithme de Lee
if __name__ == '__main__':
    # Définition du labyrithne
    carte = [
        [1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
        [0, 0, 1, 0, 1, 1, 1, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
        [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [0, 0, 1, 0, 0, 1, 1, 0, 0, 1]
    ]
    start, end = (0, 0), (9, 9)

    # Trouver le chemin le plus court entre le point (0, 0) et la destination (9,9)
    dist, pred = parcours_largeur(carte, *start, *end)

    if dist != float('inf'):
        print(f"Le chemin le plus court jusqu'à la destination a une longueur de {dist}")
        print("Voici le chemin à parcourir: ")
        print(end)
        while end != start:
            end = pred[end]
            print(end)
    else:
        print("La destination ne peut pas être atteinte")



