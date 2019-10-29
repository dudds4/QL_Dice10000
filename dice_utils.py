import numpy as np
import math

from dice_combos import *

def usedFromRemaining(dice_list, remaining):
    used = dice_list + []
    for num in remaining:
        used.remove(num)
    return used

def augment(option_tuple, dice_list):
    points, remaining = option_tuple
    used = usedFromRemaining(dice_list, remaining)
    return (points, remaining, used)

def not_mutually_exclusive(option1, option2):
    _, remaining1, used1 = option1
    _, remaining2, used2 = option2

    original_dice = sorted(used1 + remaining1)
    assert(sorted(used2 + remaining2) == original_dice)

    used = used1 + used2

    usedCounts = [0]*6
    for d in used:
        usedCounts[d-1] += 1

    diceCounts = [0]*6
    for d in original_dice:
        diceCounts[d-1] += 1

    return all(o >= u for o,u in zip(diceCounts, usedCounts))

def combine(option1, option2):
    points1, remaining1, used1 = option1
    points2, remaining2, used2 = option2  
    original_dice = sorted(used1 + remaining1)
    assert(sorted(used2 + remaining2) == original_dice)
    points = points1 + points2
    used = sorted(used1 + used2)
    for d in used:
        original_dice.remove(d)
    return (points, original_dice, used)

