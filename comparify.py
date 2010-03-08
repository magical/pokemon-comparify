#!/usr/bin/env python

"""
Types of level-up move changes in evolution groups
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
    
    

HOW THE ALGORITHM WORKS

Generally, it works by going through the list of moves and "locking" them
when it feels it has a good match.

It makes 5 passes through the move list, with decreasing standards for what
is a match. Passes 2 and 3 are swapped if the movesets have move levels in
common than moves in common.

Pass 1 locks when both the level and the move match.
Pass 2 locks when the move matches.
Pass 3 locks when the level matches.
Pass 4 looks for "gaps" where some moves aren't locked. If the gap in
one list is the same length as the gap in another list, it locks all those
moves.

Pass 5 does a sort so that levels are more or less in order.

"""

# Pardon my Hungarian. Here is the translation:
#
# i - an index
# c - a count, size, length
# a - an array (list)
# ai - an array of indicies
# l - a lower bound
# u - an upper bound
# s - a set
# m - move

try:
    next
except NameError:
    def next(it):
        return it.__next__()

try:
    range = xrange
except NameError:
    pass

# No effect in py3
__metaclass__ = type

class MoveAligner:
    style = 'LTR'

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, vars(self))

    def match(self, iLeft, iRight, key=lambda x: x, reverse=True):
        needle = key(self.right[iRight])
        haystack = self.left[iLeft]
        if reverse:
            haystack = reversed(haystack)
        for x in haystack:
            if x is None:
                continue
            if needle == key(x):
                return True
        return False

    def sort_levels(self):
        """basically a bounded insertion sort

        alignment must have been previously passed to fill_alignment
        """
        alignment = self.alignment
        left = self.left
        right = self.right

        i = 0
        li = 0
        while i + 1 < len(alignment):
            if alignment[i][0] is not None:
                li = i
            elif alignment[i][1] is not None \
                and alignment[i + 1][1] is None:
                mLeft = next(m for m in reversed(left[alignment[i + 1][0]]) if m is not None)
                if mLeft[0] <= right[alignment[i][1]][0]:
                    r = i
                    while li < r and mLeft[0] < right[alignment[r][1]][0]:
                        r -= 1
                    if r != i:
                        m = alignment.pop(i + 1)
                        alignment.insert(r + 1, m)
                        li = r + 1
                        i -= 1
            i += 1

    def _merge_gap(self, iRight, cGap):
        alignment = self.alignment
        for i in range(iRight, iRight + cGap):
            alignment[i] = alignment[i][0], alignment[i+cGap][1]

        del alignment[iRight+cGap:iRight+cGap+cGap]

    def fill_gaps(self):
        alignment = self.alignment
        left = self.left
        right = self.right

        cGapRight = 0
        iAlignmentRight = 0
        while iAlignmentRight < len(alignment):
            if alignment[iAlignmentRight][1] is None:
                assert alignment[iAlignmentRight][0] is not None
                cGapRight += 1
            elif cGapRight:
                cGapLeft = 0
                for iAlignmentLeft in range(iAlignmentRight, len(alignment)):
                    if alignment[iAlignmentLeft][0] is None:
                        cGapLeft += 1
                    else:
                        break
                if cGapRight == cGapLeft:
                    self._merge_gap(iAlignmentRight - cGapRight, cGapRight)
                    iAlignmentRight -= 1
                cGapRight = 0
            iAlignmentRight += 1

    def apply_alignment(self):
        left = self.left
        right = self.right
        final = []

        cms = len(left[0])
        for iLeft, iRight in self.alignment:
            if iLeft is None:
                final.append([None] * cms + [right[iRight]])
            elif iRight is None:
                final.append(left[iLeft] + [None])
            else:
                final.append(left[iLeft] + [right[iRight]])

        return final

key_levels = lambda x: x[0]
key_moves = lambda x: x[1]

class HeuristicMoveAligner(MoveAligner):
    def __init__(self, left, right):
        """
        left :: [[(level, move)]]
        right :: [(level, move)]
        """
        self.left = left
        self.right = right

    def clear(self):
        self.alignment = [] # :: [(Maybe i, j)]

    def align(self):
        self.clear()

        self.lock_both()

        movesfirst = self.alignment
        levelsfirst = list(self.alignment)

        self.lock(key_moves)
        self.lock(key_levels)
        self.fill_alignment()

        self.alignment = levelsfirst
        self.lock(key_levels)
        self.lock(key_moves)
        self.fill_alignment()

        if len(levelsfirst) < len(movesfirst):
            self.alignment = levelsfirst
            self.strategy = 'levelsfirst'
        else:
            self.alignment = movesfirst
            self.strategy = 'movesfirst'
        print (self.strategy)

        self.sort_levels()
        self.fill_gaps()

        return self.apply_alignment()

    # XXX unused
    def lower_bounds(self):
        ali = []
        li = 0
        for i, _ in self.alignment:
            if i is None:
                ali.append(li)
            else:
                li = i+1
                ali.append(None)
        return ali

    def upper_bounds(self, max):
        aui = []
        ui = max
        for i, _ in reversed(self.alignment):
            if i is None:
                aui.append(ui)
            else:
                ui = i
                aui.append(None)
        aui.reverse()
        return aui


    def skip_lv1(self):
        iLeft = iRight = 0
        for iLeft in range(len(self.left)):
            if any(key_levels(x) == 1 for x in self.left[iLeft] if x is not None):
                break
        for iRight in range(len(self.right)):
            if key_levels(self.right[iRight]) == 1:
                break
        return iLeft, iRight

    def lock_both(self):
        """locks when both the levels and moves match.

        this must be called first. assumes that alignment is empty."""
        alignment = self.alignment

        liLeft = 0
        cLeft = len(self.left)
        for iRight in range(len(self.right)):
            for iLeft in range(liLeft, cLeft):
                if self.match(iLeft, iRight):
                    alignment.append((iLeft, iRight))
                    liLeft = iLeft + 1
                    break
            else:
                alignment.append((None, iRight))

        for iRight in range(iRight + 1, len(self.right)):
            alignment.append((None, iRight))


    def lock(self, key):
        alignment = self.alignment
        left = self.left
        right = self.right
        bounds = self.upper_bounds(len(left))
        #bounds = list(bounds); print(bounds)

        liLeft = 0
        for iAlignment, ((iLeft, iRight), uiLeft) \
            in enumerate(zip(alignment, bounds)):
            if iLeft is not None:
                liLeft = iLeft + 1
                continue

            for iLeft in range(liLeft,  uiLeft):
                if self.match(iLeft, iRight, key=key):
                    alignment[iAlignment] = (iLeft, iRight)
                    liLeft = iLeft + 1
                    break

        return

    def lock_while(self, left, right, liLeft, liRight, key):
        """locks while the left and right are equal or already locked"""
        alignment = self.alignment

        loop = zip(range(liRight, len(alignment)),
                   range(liLeft, len(left)),
                   range(liRight, len(right)))
        for iAlignment, iLeft, iRight in loop:
            if alignment[iAlignment][0] is not None:
                continue

            if self.match(iLeft, iRight, key=key):
                alignment[iAlignment] = (iLeft, iRight)
            else:
                break

        return

    def fill_alignment(self):
        left = self.left
        right = self.right

        uiLeft = len(left)-1
        newalignment = []
        for iLeft, iRight in reversed(self.alignment):
            if iLeft is None:
                newalignment.append((None, iRight))
            else:
                while iLeft < uiLeft:
                    newalignment.append((uiLeft, None))
                    uiLeft -= 1
                newalignment.append((iLeft, iRight))
                uiLeft = iLeft - 1
        for iLeft in range(uiLeft):
            newalignment.append((iLeft, None))

        newalignment.reverse()
        self.alignment[:] = newalignment


class HeuristicMoveAlignerRTL(HeuristicMoveAligner):
    style = 'RTL'
    def __init__(self, left, right):
        """
        left :: [(level, move)]
        right :: [[(level, move)]]
        """
        self.left = right
        self.right = left

    def fill_alignment(self):
        left = self.left
        right = self.right

        liLeft = 0
        newalignment = []
        for iLeft, iRight in self.alignment:
            if iLeft is None:
                newalignment.append((None, iRight))
            else:
                while liLeft < iLeft:
                    newalignment.append((liLeft, None))
                    liLeft += 1
                newalignment.append((iLeft, iRight))
                liLeft = iLeft + 1
        for iLeft in range(liLeft, len(left)):
            newalignment.append((iLeft, None))

        self.alignment[:] = newalignment

    def _merge_gap(self, i, cGap):
        alignment = self.alignment
        for j in range(i, i + cGap):
            alignment[j] = alignment[j+cGap][0], alignment[j][1]

        #print (i+cGap,i+cGap*2,alignment[i+cGap:i+cGap*2])
        del alignment[i+cGap:i+cGap+cGap]

    def fill_gaps(self):
        alignment = self.alignment
        left = self.left
        right = self.right

        cGapLeft = 0
        iAlignmentLeft = min(self.skip_lv1())
        while iAlignmentLeft < len(alignment):
            if alignment[iAlignmentLeft][0] is None:
                assert alignment[iAlignmentLeft][1] is not None
                cGapLeft += 1
            elif cGapLeft:
                cGapRight = 0
                for iAlignmentRight in range(iAlignmentLeft, len(alignment)):
                    if alignment[iAlignmentRight][1] is None:
                        cGapRight += 1
                    else:
                        break
                if cGapLeft == cGapRight:
                    assert cGapLeft != 0
                    print (iAlignmentLeft, cGapLeft)
                    self._merge_gap(iAlignmentLeft - cGapLeft, cGapLeft)
                    iAlignmentLeft -= 1
                cGapLeft = 0
            iAlignmentLeft += 1

    def apply_alignment(self):
        left = self.right
        right = self.left
        final = []

        cm = len(right[0])
        for iRight, iLeft in self.alignment:
            if iLeft is None:
                final.append([None] + right[iRight])
            elif iRight is None:
                final.append([left[iLeft]] + [None]*cm)
            else:
                final.append([left[iLeft]] + right[iRight])

        return final


class NeedlemanWunschMoveAligner(MoveAligner):
    zero = (0, 0, 0)
    gap_penalty = (0, 0, 1)

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def clear(self):
        self.alignment = []
        self.matrix = NeedlemanWunschMatrix(len(self.left), len(self.right),
                                            default=self.zero)

    def align(self):
        self.clear()

        self.compute_matrix()
        self.compute_alignment()

        #self.sort_levels()
        #self.fill_gaps()

        return self.apply_alignment()

    def similarity(self, iLeft, iRight):
        return (
            int(self.match(iLeft, iRight)),
            2 * int(self.match(iLeft, iRight, key=key_moves))
              + int(self.match(iLeft, iRight, key=key_levels)),
            0
        )

    def add(self, a, b):
        return tuple(m + n for m, n in zip(a, b))

    def compute_matrix(self):
        m = self.matrix
        for iLeft in range(len(self.left)):
            for iRight in range(len(self.right)):
                m[iLeft,iRight] = max(
                    self.add(m[iLeft-1,iRight-1],
                             self.similarity(iLeft, iRight)),
                    self.add(m[iLeft-1,iRight],
                             self.gap_penalty),
                    self.add(m[iLeft,iRight-1],
                             self.gap_penalty),
                )

    def compute_alignment(self):
        matrix = self.matrix

        iLeft, iRight = len(self.left)-1, len(self.right)-1
        alignment = []
        while 0 <= iLeft and 0 <= iRight:
            score = matrix[iLeft, iRight]
            if score == self.add(matrix[iLeft-1,iRight-1],
                                 self.similarity(iLeft, iRight)):
                alignment.append((iLeft, iRight))
                iLeft, iRight = iLeft-1, iRight-1
            elif score == self.add(matrix[iLeft,iRight-1],
                                   self.gap_penalty):
                alignment.append((None, iRight))
                iRight -= 1
            elif score == self.add(matrix[iLeft-1,iRight],
                                   self.gap_penalty):
                alignment.append((iLeft, None))
                iLeft -= 1
            else:
                raise Exception

        while 0 <= iRight:
            alignment.append((None,iRight))
            iRight -= 1

        while 0 <= iLeft:
            alignment.append((iLeft,None))
            iLeft -= 1

        alignment.reverse()
        self.alignment = alignment


class NeedlemanWunschMatrix(list):
    """A 2-dimensional matrix used in the Needleman-Wunsch algorithm"""
    def __init__(self, m, n, default):
        self.m = m
        self.n = n
        self.default = default
        list.__init__(self, [0] * m * n)

    def __getitem__(self, ij):
        i, j = ij
        if i < 0 or j < 0:
            return self.default
        if self.m < i or self.n < j:
            raise IndexError(ij)
        return list.__getitem__(self, i*self.n+j)

    def __setitem__(self, ij, v):
        i, j = ij
        if not (0 <= i < self.m and 0 <= j < self.n):
            raise IndexError(ij)
        list.__setitem__(self, i*self.n+j, v)

    def __repr__(self):
        return 'Matrix(%s)' % list.__repr__(self)

    def __str__(self):
        return "\n".join(" ".join("%2d" % self[i, j] for j in range(self.n)) for i in range(self.m))


class DTWMoveAligner(MoveAligner):
    zero = 0
    inf = 100000

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def clear(self):
        self.alignment = []
        self.matrix = DTWMatrix(len(self.left), len(self.right),
                                inf=self.inf, zero=self.zero)

    def align(self):
        self.clear()

        self.compute_matrix()
        self.compute_alignment()

        #self.sort_levels()
        #self.fill_gaps()

        return self.apply_alignment()

    def distance(self, iLeft, iRight):
        mLeft = next(m for m in reversed(self.left[iLeft]) if m is not None)
        return abs(key_levels(mLeft) -
                   key_levels(self.right[iRight]))

    def add(self, a, b):
        return a + b

    def compute_matrix(self):
        m = self.matrix
        for iLeft in range(len(self.left)):
            for iRight in range(len(self.right)):
                cost = self.distance(iLeft, iRight)
                m[iLeft,iRight] = self.add(cost, min(
                    m[iLeft-1,iRight-1],
                    m[iLeft-1,iRight],
                    m[iLeft,iRight-1],
                ))

    def compute_alignment(self):
        matrix = self.matrix

        iLeft, iRight = len(self.left)-1, len(self.right)-1
        alignment = []
        while 0 <= iLeft and 0 <= iRight:
            score = matrix[iLeft, iRight]
            cost = self.distance(iLeft, iRight)
            if score == self.add(cost, matrix[iLeft-1,iRight-1]):
                alignment.append((iLeft, iRight))
                iLeft, iRight = iLeft-1, iRight-1
            elif score == self.add(cost, matrix[iLeft,iRight-1]):
                alignment.append((None, iRight))
                iRight -= 1
            elif score == self.add(cost, matrix[iLeft-1,iRight]):
                alignment.append((iLeft, None))
                iLeft -= 1
            else:
                raise Exception #(score, cost, iLeft, iRight, self)

        while 0 <= iRight:
            alignment.append((None,iRight))
            iRight -= 1

        while 0 <= iLeft:
            alignment.append((iLeft,None))
            iLeft -= 1

        alignment.reverse()
        self.alignment = alignment


class DTWMatrix(list):
    """A 2-dimensional matrix used in the Dynamic Time Warping algorithm"""
    def __init__(self, m, n, inf, zero=0):
        self.m = m
        self.n = n
        self.inf = inf
        self.zero = zero
        list.__init__(self, [None] * m * n)

    def __getitem__(self, ij):
        i, j = ij
        if ij == (-1, -1):
            return self.zero
        if i == -1 or j == -1:
            return self.inf
        if self.m < i or self.n < j:
            raise IndexError(ij)
        return list.__getitem__(self, i*self.n+j)

    def __setitem__(self, ij, v):
        i, j = ij
        if not (0 <= i < self.m and 0 <= j < self.n):
            raise IndexError(ij)
        list.__setitem__(self, i*self.n+j, v)

    def __repr__(self):
        return 'Matrix(%s)' % list.__repr__(self)

    def __str__(self):
        return "\n".join(" ".join("%2d" % self[i, j] for j in range(self.n)) for i in range(self.m))


def align(movesets, aligner_class=HeuristicMoveAligner):
    if aligner_class.style == 'LTR':
        combined = [[x] for x in movesets[0]]
        for moveset in movesets[1:]:
            aligner = aligner_class(combined, moveset)
            combined = aligner.align()
    elif aligner_class.style == 'RTL':
        combined = [[x] for x in movesets[-1]]
        for moveset in movesets[-2::-1]:
            aligner = aligner_class(moveset, combined)
            combined = aligner.align()
    return combined


from time import time
def time_align2(movesets, ia, ib):
    a = movesets[ia][1]
    b = movesets[ib][1]

    a = [[x] for x in a]

    aligner = HeuristicMoveAligner(a, b)
    time_a = time()
    combined = aligner.align()
    time_b = time()
    return (time_b - time_a), combined

def time_align(movesets, aligner_class=HeuristicMoveAligner):
    time_a = time()
    combined = align(movesets, aligner_class)
    time_b = time()
    return (time_b - time_a), combined


if __name__ == '__main__':
    from pprint import pprint
    def do_time(*args):
        time, combined = time_align2(*args)
        pprint(combined)
        print ("%f seconds\n" % time)
    def do_time_n(moves, *args):
        pokemon, movesets = zip(*moves)
        time, combined = time_align(movesets, *args)
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



