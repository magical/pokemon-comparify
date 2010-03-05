#!/usr/bin/env python



"""
types of level-up move changes in evolution groups
==================================================

No Change
    The moveset is exactly the same in the evolution. Only the levels change.
    Examples: Tentacool line

Some change
    Example: Doduo -> Dodrio in DPPt. Double Hit is swapped out for Tri Attack.

Large change
    examples: Slakoth & Treecko lines

Stone
    Evolution has no attacks (except Lv.0)

Metamorphosis
    The base/baby form has a tiny movepool. The evolution has a large one.
    Examples: Gyarados, Butterfree, Clamperl, Combee

Added attack at level of evolution
    Example: Ninjask
    
    
"""

def lower_bounds(alignment):
    prev_is = []
    prev_i = -1
    for i, _ in alignment:
        prev_is.append(prev_i)
        if i is not None and i > prev_i:
            prev_i = i
    return prev_is

def upper_bounds(alignment, max):
    next_is = []
    next_i = max
    for i, _ in reversed(alignment):
        if i is not None and i < next_i:
            next_i = i
        next_is.append(next_i)
    next_is.reverse()
    return next_is

def calc_bounds(a, alignment):
    return zip(lower_bounds(alignment), upper_bounds(alignment, len(a)))

def lock(a, b, alignment, cmp):
    bounds = calc_bounds(a, alignment)
    for k, ((i, j), (min_i, max_i)) in enumerate(zip(alignment, bounds)):
        if i is not None:
            continue

        for i in range(min_i + 1, max_i):
            if cmp(a[i], b[j]):
                alignment[k] = (i, j)
                break

def align(a, b):
    """
    moveset = [(level, move),]
    """
    alignment = [] # ::[(Maybe i, j)]

    # lock when moves match
    prev_i = 0
    for j in range(len(b)):
        for i in range(prev_i, len(a)):
            if a[i] == b[j]:
                alignment.append((i, j))
                prev_i = i + 1
                break
        else:
            alignment.append((None, j))
    # add extras
    for j in range(j + 1, len(b)):
        alignment.append((None, b))

    cmp_levels = lambda a, b: a[0] == b[0]
    cmp_moves = lambda a, b: a[1] == b[1]

    #movesfirst = list(alignment)
    levelsfirst = alignment

    #lock(movesfirst, cmp_moves)
    #lock(movesfirst, cmp_levels)

    lock(a, b, levelsfirst, cmp_levels)
    lock(a, b, levelsfirst, cmp_moves)

    alignment = levelsfirst

    final = []
    prev_i = 0
    for i, j in alignment:
        if i is None:
            final.append((None, b[j]))
        else:
            while prev_i < i:
                final.append((a[prev_i], None))
                prev_i += 1
            final.append((a[i], b[j]))
            prev_i = i + 1
    for i in range(prev_i, len(a)):
        final.append((a[i], None))

    return final


from time import time
def time_align(movesets, ia, ib):
    a = movesets[ia][1]
    b = movesets[ib][1]
    time_a = time()
    combined = align(a, b)
    time_b = time()
    return (time_b - time_a), combined

if __name__ == '__main__':
    from pprint import pprint
    def do_time(*args):
        time, combined = time_align(*args)
        pprint(combined)
        print ("%f seconds\n" % time)

    poochyena = [
      ((),[
        (1, 'Tackle'),
        (5, 'Howl'),
        (9, 'Sand-Attack'),
        (13, 'Bite'),
        (17, 'Odor Sleuth'),
        (21, 'Roar'),
        (25, 'Swagger'),
        (29, 'Assurance'),
        (33, 'Scary Face'),
        (37, 'Taunt'),
        (41, 'Embargo'),
        (45, 'Take Down'),
        (49, 'Sucker Punch'),
        (53, 'Crunch'),
    ]), ((), [
        (1, 'Tackle'),
        (1, 'Howl'),
        (1, 'Sand-Attack'),
        (1, 'Bite'),
        (5, 'Howl'),
        (9, 'Sand-Attack'),
        (13, 'Bite'),
        (17, 'Odor Sleuth'),
        (22, 'Roar'),
        (27, 'Swagger'),
        (32, 'Assurance'),
        (37, 'Scary Face'),
        (42, 'Taunt'),
        (47, 'Embargo'),
        (52, 'Take Down'),
        (57, 'Thief'),
        (62, 'Sucker Punch'),
    ])]

    nincada = [((290, 'Nincada'),
      [(1, 'Scratch'),
       (1, 'Harden'),
       (5, 'Leech Life'),
       (9, 'Sand-Attack'),
       (14, 'Fury Swipes'),
       (19, 'Mind Reader'),
       (25, 'False Swipe'),
       (31, 'Mud-Slap'),
       (38, 'Metal Claw'),
       (45, 'Dig')]),
     ((291, 'Ninjask'),
      [(1, 'Scratch'),
       (1, 'Sand-Attack'),
       (1, 'Harden'),
       (1, 'Leech Life'),
       (1, 'Bug Bite'),
       (5, 'Leech Life'),
       (9, 'Sand-Attack'),
       (14, 'Fury Swipes'),
       (19, 'Mind Reader'),
       (20, 'Screech'),
       (20, 'Double Team'),
       (20, 'Fury Cutter'),
       (25, 'Swords Dance'),
       (31, 'Slash'),
       (38, 'Agility'),
       (45, 'Baton Pass'),
       (52, 'X-Scissor')]),
     ((292, 'Shedinja'),
      [(1, 'Scratch'),
       (1, 'Harden'),
       (5, 'Leech Life'),
       (9, 'Sand-Attack'),
       (14, 'Fury Swipes'),
       (19, 'Mind Reader'),
       (25, 'Spite'),
       (31, 'Confuse Ray'),
       (38, 'Shadow Sneak'),
       (45, 'Grudge'),
       (52, 'Heal Block'),
       (59, 'Shadow Ball')])]


    pprint(align([
        (1, 'a'),
        (2, 'b'),
        (3, 'c'),
        (4, 'd'),
        (5, 'e'),
    ], [
        (3, 'c'),
    ]))

    do_time(poochyena, 0, 1)
    do_time(nincada, 0, 1)

