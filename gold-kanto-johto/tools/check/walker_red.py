"""赤フルカラー（日本版の 赤が 元）を 歩かせる 道具。walker.W と 同じ つかいかた（比べる 画面を とる ため）。
   RAM（日本版）：wCurMap $D2DD、wYCoord $D2E0、wXCoord $D2E1"""
import sys, os, re, collections
sys.path.insert(0, '/home/claude/repo/gold-kanto-johto/tools/check')
from redmap import red_maps, RED
DIRS = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}

def _tables(R=RED):
    rd = lambda p: open(os.path.join(R, p), encoding='utf-8').read()
    bst = {}
    for m in re.finditer(r'((?:\w+_Block::\s*\n?)+)\s*INCBIN "(gfx/blocksets/\w+\.bst)"', rd('gfx/tilesets.asm')):
        for n in re.findall(r'(\w+)_Block::', m.group(1)): bst[n] = open(os.path.join(R, m.group(2)), 'rb').read()
    coll = {}; pend = []
    for l in rd('data/tilesets/collision_tile_ids.asm').splitlines():
        m = re.match(r'(\w+)_Coll::', l)
        if m: pend.append(m.group(1)); continue
        m = re.match(r'\s*coll_tiles\s*(.*)', l)
        if m and pend:
            for n in pend: coll[n] = {int(x.strip().lstrip('$'), 16) for x in m.group(1).split(',') if x.strip()}
            pend = []
    tsn = re.findall(r'^\s*tileset (\w+),', rd('data/tilesets/tileset_headers.asm'), re.M)
    tsc = {c: i for i, c in enumerate(re.findall(r'^\s*const (\w+)', rd('constants/tileset_constants.asm'), re.M))}
    ids = [c for c, w, h in re.findall(r'map_const (\w+),\s*(\d+),\s*(\d+)', rd('constants/map_constants.asm'))]
    return bst, coll, tsn, tsc, ids

class WR:
    def __init__(s, g):
        s.g = g; s.maps, _ = red_maps(); s.bst, s.coll, s.tsn, s.tsc, s.ids = _tables()
        s.byconst = {m['const']: m for m in s.maps.values()}
    def pos(s):
        a = s.g.peek(0xD2DD, 5); return (a[0], a[4], a[3])
    def cur(s): return s.byconst.get(s.ids[s.pos()[0]])
    def ok(s, m, x, y):
        if not (0 <= x < m['w'] * 2 and 0 <= y < m['h'] * 2): return False
        t = s.tsn[s.tsc[m['ts']]]; b = m['blk'][(y // 2) * m['w'] + x // 2]
        return s.bst[t][b * 16 + ((y % 2) * 2 + 1) * 4 + (x % 2) * 2] in s.coll[t]
    def path(s, tx, ty):
        m = s.cur(); _, x, y = s.pos(); prev = {(x, y): None}; q = collections.deque([(x, y)])
        while q:
            p = q.popleft()
            if p == (tx, ty): break
            for d, (dx, dy) in DIRS.items():
                n = (p[0] + dx, p[1] + dy)
                if n in prev or (not s.ok(m, *n) and n != (tx, ty)): continue
                prev[n] = (p, d); q.append(n)
        if (tx, ty) not in prev: return None
        out = []; p = (tx, ty)
        while prev[p]: p, d = prev[p]; out.append(d)
        return out[::-1]
    def step(s, d):
        before = s.pos(); s.g.down(d)
        for _ in range(40):
            s.g.wait(2)
            if s.pos() != before: break
        s.g.up(d); s.g.wait(8); return s.pos() != before
    def goto(s, tx, ty, tries=8):
        for _ in range(tries):
            mp, x, y = s.pos()
            if (x, y) == (tx, ty): return True
            p = s.path(tx, ty)
            if p is None: return False
            for d in p:
                if not s.step(d): s.g.press('B', 4, 20); break
                if s.pos()[0] != mp: return True
        return s.pos()[1:] == (tx, ty)
    def face(s, d): s.g.press(d, 2, 10)
    def textbox(s):
        from PIL import Image
        p = '/tmp/_walker_tbr.ppm'; s.g.cmd('shot ' + p); s.g.sync(); im = Image.open(p).convert('RGB')
        return im.getpixel((2, 110)) == (0, 0, 0) and im.getpixel((2, 130)) == (0, 0, 0)
    def clear(s, key='A', n=40, wait=40):
        for i in range(n):
            if not s.textbox(): return i
            s.g.press(key, 4, wait)
        return n
