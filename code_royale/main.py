import sys
import math

TYPE_QUEEN  = -1
TYPE_KNIGHT = 0
TYPE_ARCHER = 1
TYPE_GIANT  = 2
ALL_UNIT_TYPES = [TYPE_KNIGHT, TYPE_ARCHER, TYPE_GIANT]

TYPE_NOSTRUC = -1
TYPE_TOWER   = 1
TYPE_BARRACK = 2

BRK_STR = ['KNIGHT', 'ARCHER']

PRICE_KNIGHT = 80
PRICE_ARCHER = 100

OWNER_FRIEND = 0
OWNER_ENEMY  = 1

def get_queen_pos(units, owner):
    for x, y, o, t, h in units:
        if o == owner and t == TYPE_QUEEN:
            return (x, y)
    assert False

def get_building_stats(sites):
    ifbrk = [[] for _ in ALL_UNIT_TYPES]
    iftwr = []
    iebrk = [[] for _ in ALL_UNIT_TYPES]
    ietwr = []
    for i, (_, _, t, o, p1, p2) in sites.items():
        if t == TYPE_BARRACK:
            if o == OWNER_FRIEND:
                ifbrk[p2].append(i)
            else:
                assert(o == OWNER_ENEMY)
                iebrk[p2].append(i)
        elif t == TYPE_TOWER:
            if o == OWNER_FRIEND:
                iftwr.append(i)
            else:
                assert(o == OWNER_ENEMY)
                ietwr.append(i)
            
    return ifbrk, iebrk, iftwr, ietwr

def can_build(site):
    _, _, t, o, p1, p2 = site
    return o != OWNER_FRIEND and t != TYPE_TOWER

def get_unit_stats(units):
    nfunt = [0 for _ in ALL_UNIT_TYPES]
    neunt = [0 for _ in ALL_UNIT_TYPES]
    for x, y, o, t, h in units:
        if t >= 0:
            if o == OWNER_FRIEND:
                nfunt[t] += 1
            else:
                assert(o == OWNER_ENEMY)
                neunt[t] += 1
    return nfunt, neunt

def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2.0 + (a[1] - b[1]) ** 2.0)

def get_nearest(p, l):
    min_dist = float('+inf')
    nearest = None
    for a in l:
        dist = distance(p, a)
        if dist < min_dist:
            min_dist = dist
            nearest = a
    return nearest

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

num_sites = int(input())
site_pos = [[int(j) for j in input().split()] for _ in range(num_sites)]
site_pos = {j[0] : j[1:] for j in site_pos}

# game loop
while True:
    # touched_site: -1 if none
    gold, touched_site = [int(i) for i in input().split()]
    sites = [[int(j) for j in input().split()] for _ in range(num_sites)]
    sites = {j[0] : j[1:] for j in sites}

    num_units = int(input())
    units = [[int(j) for j in input().split()] for _ in range(num_units)]


    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    # queen position
    qp = get_queen_pos(units, OWNER_FRIEND)

    # get building stats
    ifbrk, iebrk, iftwr, ietwr = get_building_stats(sites)

    # get unit stats
    nfunt, neunt = get_unit_stats(units)

    # check if have enough baracks
    if len(ifbrk[TYPE_KNIGHT]) < 2 or len(ifbrk[TYPE_ARCHER]) < 1:
        # build another barack
        if touched_site >= 0 and sites[touched_site][3] != OWNER_FRIEND:
            btype = TYPE_ARCHER if len(ifbrk[TYPE_ARCHER]) < 1 else TYPE_KNIGHT
            qcmd = 'BUILD %d BARRACKS-%s' % (touched_site, BRK_STR[btype])
        else:
            # goto the nearest unfriendly site
            npos = [site_pos[i][:2] for i in range(num_sites) if can_build(sites[i])]
            dest = get_nearest(qp, npos)
            qcmd = 'MOVE %d %d' % tuple(dest)
    elif len(iftwr) < 5:
        # build a tower
        if touched_site >= 0 and sites[touched_site][3] != OWNER_FRIEND:
            qcmd = 'BUILD %d TOWER' % touched_site
        else:
            # goto the nearest unfriendly site
            npos = [site_pos[i][:2] for i in range(num_sites) if can_build(sites[i])]
            dest = get_nearest(qp, npos)
            qcmd = 'MOVE %d %d' % tuple(dest)
    else:
        # go back to the first archer barack
        dest = site_pos[ifbrk[TYPE_ARCHER][0]][:2]
        qcmd = 'MOVE %d %d' % tuple(dest)

    train = []

    if nfunt[TYPE_ARCHER] < 4 and gold >= PRICE_ARCHER:
        # check archer barack is free
        for i in ifbrk[TYPE_ARCHER]:
            _, _, t, o, p1, p2 = sites[i]
            if p1 == 0:
                train.append(i)
                gold -= PRICE_ARCHER
                break
    else:
        for i in ifbrk[TYPE_KNIGHT]:
            if gold < PRICE_KNIGHT:
                break
            _, _, t, o, p1, p2 = sites[i]
            if p1 == 0:
                train.append(i)
                gold -= PRICE_KNIGHT
   
    tcmd = 'TRAIN ' + ' '.join(['%d' % i for i in train])
    tcmd = tcmd.strip()

    # First line: A valid queen action
    # Second line: A set of training instructions
    print(qcmd)
    print(tcmd)

