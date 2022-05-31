import random


def ability_rolls():
    """ Lancez quatre dés à 6 faces et notez le total des trois dés les plus élevés sur une feuille de papier brouillon.
        Faites cela cinq fois de plus, de sorte que vous ayez six chiffres"""
    random.seed()
    ability_scores = []
    for _ in range(6):
        dice_roll = [random.randint(1, 6) for _ in range(4)]
        dice_roll.sort()
        dice_roll.pop(0)
        ability_scores.append(sum(dice_roll))
    return ability_scores
