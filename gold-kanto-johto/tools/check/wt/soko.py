"""かいりきの 岩を 目的の マスへ 押す（1つの 岩、同じ マップ）"""
from collections import deque
DIRS = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
def region(w, mid, start, block):
    c = w.coll(mid); seen = {start}; q = deque([start])
    while q:
        p = q.popleft()
        for d, (dx, dy) in DIRS.items():
            n = (p[0] + dx, p[1] + dy)
            if n in block or n in seen: continue
            if not w.passable(c(*n), p, d): continue
            seen.add(n); q.append(n)
    return seen
def plan(w, mid, player, boulder, target, others):
    c = w.coll(mid)
    st = (boulder, frozenset(region(w, mid, player, others | {boulder})))
    prev = {(boulder, player): None}; q = deque([(boulder, player)])
    while q:
        b, p = q.popleft()
        if b == target:
            out = []; k = (b, p)
            while prev[k]: k, mv = prev[k]; out.append(mv)
            return out[::-1]
        reg = region(w, mid, p, others | {b})
        for d, (dx, dy) in DIRS.items():
            stand = (b[0] - dx, b[1] - dy); nb = (b[0] + dx, b[1] + dy)
            if stand not in reg or nb in others: continue
            if not w.passable(c(*nb), b, d): continue
            k = (nb, stand)
            if k not in prev: prev[k] = ((b, p), (stand, d)); q.append(k)
    return None
def push(w, s, boulder, target, others=frozenset()):
    """boulder を target へ。押す たびに 岩の 位置は RAM から 読みなおす"""
    mid = w.pos()[:2]
    pl = plan(w, mid, w.pos()[2:], boulder, target, set(others))
    if pl is None: w.log.append('岩を 押せない %s→%s' % (boulder, target)); return False
    b = boulder; used = False
    for stand, d in pl:
        w.goto_safe(*stand, shot=s); w.face(d)
        if w.pos()[2:] != stand: w.log.append('岩の うしろに 行けない %s' % (stand,)); return False
        if not used:
            w.g.press('A', 8, 60)
            for _ in range(8):
                if w.menu_kind() == 'yesno': w.g.press('A', 8, 60)
                elif w.textbox(): w.g.press('A', 8, 40)
                else: break
            used = True
        w.g.press(d, 16, 40); w.g.wait(30)
        while w.textbox(): w.g.press('A', 8, 40)
        b = (b[0] + DIRS[d][0], b[1] + DIRS[d][1])
        w.settle()
    s('岩')
    return True

def solve(w, mid, start, boulders, goal, switches=None, maxn=200000):
    """全部の 岩を 考えて goal（マスの 集合）へ 行く 押し方。switches：{岩を 置く マス: あく マスの 集合}"""
    c0 = w.coll(mid); switches = switches or {}
    def opened(bs):
        o = set()
        for sw, cells in switches.items():
            if sw in bs: o |= cells
        return o
    def pas(n, p, d, op):
        if n in op: return True
        return w.passable(c0(*n), p, d)
    def reg(p, block, op):
        seen = {p}; q = deque([p])
        while q:
            a = q.popleft()
            for d, (dx, dy) in DIRS.items():
                n = (a[0] + dx, a[1] + dy)
                if n in block or n in seen or not pas(n, a, d, op): continue
                seen.add(n); q.append(n)
        return seen
    bs0 = frozenset(boulders)
    r0 = reg(start, bs0, opened(bs0))
    key0 = (bs0, min(r0)); prev = {key0: None}; q = deque([(bs0, start)])
    while q and len(prev) < maxn:
        bs, p = q.popleft(); op = opened(bs); r = reg(p, bs, op)
        if r & goal:
            out = []; k = (bs, min(r))
            while prev[k]: k, mv = prev[k]; out.append(mv)
            return out[::-1]
        for b in bs:
            for d, (dx, dy) in DIRS.items():
                st = (b[0] - dx, b[1] - dy); nb = (b[0] + dx, b[1] + dy)
                if st not in r or nb in bs or not pas(nb, b, d, op): continue
                nbs = (bs - {b}) | {nb}
                if nb in op and nb not in switches: pass
                nr = reg(b, nbs, opened(nbs))
                k = (nbs, min(nr))
                if k not in prev: prev[k] = ((bs, min(r)), (b, st, d)); q.append((nbs, b))
    return None
def run_pushes(w, s, moves):
    used = False
    for b, st, d in moves:
        w.goto_safe(*st, shot=s); w.face(d)
        if w.pos()[2:] != st: w.log.append('岩の うしろに 行けない %s' % (st,)); return False
        if True:
            w.g.press('A', 8, 60)
            for _ in range(10):
                if w.menu_kind() == 'yesno': w.g.press('A', 8, 60)
                elif w.textbox(): w.g.press('A', 8, 40)
                else: break
            used = True
        w.g.press(d, 16, 40); w.g.wait(30)
        for _ in range(10):
            if w.textbox(): w.g.press('A', 8, 40)
            else: break
        w.settle()
    s('岩')
    return True
