import sys
import math

TYPE_QUEEN  = -1
TYPE_KNIGHT = 0
TYPE_ARCHER = 1
TYPE_GIANT  = 2

TYPE_NOSTRUC = -1
TYPE_MINE    = 0
TYPE_TOWER   = 1
TYPE_BARRACK = 2

ALL_UNIT_TYPES = [TYPE_KNIGHT, TYPE_ARCHER, TYPE_GIANT]
BRK_STR = ['KNIGHT', 'ARCHER', 'GIANT']

PRICE_KNIGHT = 80
PRICE_ARCHER = 100

OWNER_FRIEND = 0
OWNER_ENEMY  = 1

def building_name(site):
    g, m, t, o, p1, p2 = site
    if t == TYPE_MINE:
        return 'MINE'
    elif t == TYPE_TOWER:
        return 'TOWER'
    elif t == TYPE_BARRACK:
        return 'BARRACKS-%s' % BRK_STR[p2]
    else:
        assert False

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

class State(object):
    def __init__(self):
        self.num_sites = int(input())
        x = [[int(j) for j in input().split()] for _ in range(self.num_sites)]
        self.site_pos = {j[0] : j[1:3] for j in x}

    def read_input(self):
        self.gold, self.touched_site = [int(i) for i in input().split()]
        x = [[int(j) for j in input().split()] for _ in range(self.num_sites)]
        self.sites = {j[0] : j[1:] for j in x}

        self.num_units = int(input())
        self.units = [[int(j) for j in input().split()]
                                        for _ in range(self.num_units)]

        # queen position
        self.qp = self.get_queen_pos(OWNER_FRIEND)

        # get building stats
        self.barracks, self.towers, self.mines \
                                    = self.get_building_stats(OWNER_FRIEND)
        self.enemy_barracks, self.enemy_towers, self.enemy_mines \
                                    = self.get_building_stats(OWNER_ENEMY)

        # get unit stats
        self.nfunt, self.neunt = self.get_unit_stats()

    def get_queen_pos(self, owner):
        for x, y, o, t, h in self.units:
            if o == owner and t == TYPE_QUEEN:
                return (x, y)
        assert False

    def get_building_stats(self, owner):
        barracks = [[] for _ in ALL_UNIT_TYPES]
        towers = []
        mines = []
        for i, (_, _, t, o, p1, p2) in self.sites.items():
            if o == owner:
                if t == TYPE_BARRACK:
                    barracks[p2].append(i)
                elif t == TYPE_TOWER:
                    towers.append(i)
                elif t == TYPE_MINE:
                    mines.append(i)
        return barracks, towers, mines

    def get_unit_stats(self):
        nfunt = [0 for _ in ALL_UNIT_TYPES]
        neunt = [0 for _ in ALL_UNIT_TYPES]
        for x, y, o, t, h in self.units:
            if t >= 0:
                if o == OWNER_FRIEND:
                    nfunt[t] += 1
                else:
                    assert(o == OWNER_ENEMY)
                    neunt[t] += 1
        return nfunt, neunt

    def can_build(self, i):
        _, _, t, o, p1, p2 = self.sites[i]
        return o != OWNER_FRIEND and t != TYPE_TOWER

    def can_upgrade(self, i):
        g, m, t, o, p1, p2 = self.sites[i]
        if o == OWNER_FRIEND:
            if t == TYPE_MINE:
                assert m > 0
                return p1 < m
            elif t == TYPE_TOWER:
                return True
        return False

    def has_gold(self, i):
        g, m, t, o, p1, p2 = self.sites[i]
        return g == -1 or g > 0

    def safe_path(self, begin, end):
        for t in self.enemy_towers:
            if self.point_in_range(begin, t):
                return True     # when in tower range always move
        for t in self.enemy_towers:
            if self.path_in_range(begin, end, t):
                return False
        return True

    def point_in_range(self, p, t):
        print('point_in_range %s %s %s' % (str(p), str(t), str(distance(p, self.site_pos[t]) <= self.tower_range(t))), file=sys.stderr)
        return distance(p, self.site_pos[t]) <= self.tower_range(t)

    def path_in_range(self, b, e, t):
        if distance(b, e) < 1:
            return self.point_in_range(b, t)

        nx = - (e[1] - b[1])
        ny = e[0] - b[0]
        nn = math.sqrt(nx ** 2.0 + ny ** 2.0)
        tx, ty = self.site_pos[t]
        sx = tx - b[0]
        sy = ty - b[1]
        dn = (sx * nx + sy * ny) / nn

        print('path_in_range %s %s %s %s' % (str(b), str(e), str(t), str(dn <= self.tower_range(t))), file=sys.stderr)
        return dn <= self.tower_range(t)

    def tower_range(self, t):
        g, m, t, o, p1, p2 = self.sites[t]
        return p2

def what_to_build(state, i):
    if len(state.mines) < 4 and state.has_gold(i):
        return 'MINE'
    elif len(state.barracks[TYPE_KNIGHT]) < state.gold // 100:
        return 'BARRACKS-KNIGHT'
    else:
        return 'TOWER'

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
state = State()

# game loop
while True:
    state.read_input()

    # check if have enough mines
    ts = state.touched_site
    if ts >= 0 and state.can_build(ts):
        btype = what_to_build(state, ts)
        qcmd = 'BUILD %d %s' % (ts, btype)
    else:
        # goto the nearest avaiable and safe site
        npos = [state.site_pos[i] for i in range(state.num_sites)
                        if state.can_build(i)
                        and state.safe_path(state.qp, state.site_pos[i])]
        if len(npos) > 0:
            dest = get_nearest(state.qp, npos)
            qcmd = 'MOVE %d %d' % tuple(dest)
        elif ts >= 0 and state.can_upgrade(ts):
            btype = building_name(state.sites[ts])
            qcmd = 'BUILD %d %s' % (ts, btype)
        else:
            # go to nearest upgradable mine
            npos = [state.site_pos[i] for i in state.mines
                            if state.has_gold(i) and state.can_upgrade(i)]
            if len(npos) > 0:
                dest = get_nearest(state.qp, npos)
                qcmd = 'MOVE %d %d' % tuple(dest)
            else:
                # go to nearest upgradable tower
                npos = [state.site_pos[i] for i in state.towers
                                          if state.can_upgrade(i)]
                if len(npos) > 0:
                    dest = get_nearest(state.qp, npos)
                    qcmd = 'MOVE %d %d' % tuple(dest)
                else:
                    qcmd = 'WAIT'

    train = []
    if state.nfunt[TYPE_ARCHER] < 4 and state.gold >= PRICE_ARCHER:
        # check archer barrack is free
        for i in state.barracks[TYPE_ARCHER]:
            _, _, t, o, p1, p2 = state.sites[i]
            if p1 == 0:
                train.append(i)
                state.gold -= PRICE_ARCHER
                break
    for i in state.barracks[TYPE_KNIGHT]:
        if state.gold < PRICE_KNIGHT:
            break
        _, _, t, o, p1, p2 = state.sites[i]
        if p1 == 0:
            train.append(i)
            state.gold -= PRICE_KNIGHT

    tcmd = 'TRAIN ' + ' '.join(['%d' % i for i in train])
    tcmd = tcmd.strip()

    # First line: A valid queen action
    # Second line: A set of training instructions
    print(qcmd)
    print(tcmd)

