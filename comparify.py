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

#Hungarian Notation:
# i - an index
# a - an array
# ai - an array of indicies
# l - a lower bound
# u - an upper bound



def lower_bounds(alignment):
    ali = []
    li = 0
    for i, _ in alignment:
        if i is None:
            ali.append(li)
        else:
            li = i+1
            ali.append(None)
    return ali

def upper_bounds(alignment, max):
    aui = []
    ui = max
    for i, _ in reversed(alignment):
        if i is None:
            aui.append(ui)
        else:
            ui = i
            aui.append(None)
    aui.reverse()
    return aui

def search(target, a, key):
    target = key(target)
    for x in a:
        if x is None:
            continue
        if target == key(x):
            return True
    return False

def lock(left, right, alignment, key):
    bounds = upper_bounds(alignment, len(left))
    #bounds = list(bounds); print(bounds)

    liLeft = 0
    for iAlignment, ((iLeft, iRight), uiLeft) \
        in enumerate(zip(alignment, bounds)):
        if iLeft is not None:
            liLeft = iLeft + 1
            continue

        for iLeft in range(liLeft,  uiLeft):
            if search(right[iRight], reversed(left[iLeft]), key):
                alignment[iAlignment] = (iLeft, iRight)
                liLeft = iLeft + 1
                break

    return

def align(left, right):
    """
    left :: [[(level, move)]]
    right :: [(level, move)]
    """
    alignment = [] # :: [(Maybe i, j)]

    # lock when moves match
    liLeft = 0
    for iRight in range(len(right)):
        for iLeft in range(liLeft, len(left)):
            if search(right[iRight], reversed(left[iLeft]), key=lambda x: x):
                alignment.append((iLeft, iRight))
                liLeft = iLeft + 1
                break
        else:
            alignment.append((None, iRight))
    # add extras
    for iRight in range(iRight + 1, len(right)):
        alignment.append((None, iRight))

    key_levels = lambda x: x[0]
    key_moves = lambda x: x[1]

    movesfirst = alignment
    lock(left, right, movesfirst, key_moves)
    lock(left, right, movesfirst, key_levels)

    #levelsfirst = alignment
    #lock(left, right, levelsfirst, key_levels)
    #lock(left, right, levelsfirst, key_moves)

    alignment = movesfirst
    #alignment = levelsfirst

    #print(alignment)

    final = []
    cms = len(left[0])
    for iLeft, iRight in alignment:
        if iLeft is None:
            final.append([None] * cms + [right[iRight]])
        else:
            while liLeft < iLeft:
                final.append(left[liLeft] + [None])
                liLeft += 1
            final.append(left[iLeft] + [right[iRight]])
            liLeft = iLeft + 1
    for iLeft in range(liLeft, len(left)):
        final.append(left[iLeft] + [None])

    return final

def alignn(movesets):
    combined = [[x] for x in movesets[0]]
    for moveset in movesets[1:]:
        combined = align(combined, moveset)
    return combined
        


from time import time
def time_align(movesets, ia, ib):
    a = movesets[ia][1]
    b = movesets[ib][1]

    a = [[x] for x in a]

    time_a = time()
    combined = align(a, b)
    time_b = time()
    return (time_b - time_a), combined

def time_alignn(movesets):
    movesets = [x[1] for x in movesets]

    time_a = time()
    combined = alignn(movesets)
    time_b = time()
    return (time_b - time_a), combined


if __name__ == '__main__':
    from pprint import pprint
    def do_time(*args):
        time, combined = time_align(*args)
        pprint(combined)
        print ("%f seconds\n" % time)
    def do_time_n(*args):
        time, combined = time_alignn(*args)
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


#    pprint(align([
#        (1, 'a'),
#        (2, 'b'),
#        (3, 'c'),
#        (4, 'd'),
#        (5, 'e'),
#    ], [
#        (3, 'c'),
#    ]))

    do_time(poochyena, 0, 1)
    do_time(nincada, 0, 1)
    do_time_n(nincada)



