"""移植版の カントーの マップの 当たり判定を、pokeyellow（ピカチュウ＝赤フルカラーの 元）の マップと 1マスずつ 比べる。
   python3 coll_vs_yellow.py ROM [YELLOW_DIR]
   表示：W 歩ける  X 壁  ~ 水  L 段差  D 出入口（移植版の warp の 当たり）。ちがう マスを 出す"""
import sys, os, re, glob
sys.path.insert(0, '/home/claude/work/scripts')
from cwalk import Walk
ROM = sys.argv[1]; Y = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/work/mod/ref/pokeyellow'
g = bytearray(open(ROM, 'rb').read())
fo = lambda b, a: b * 0x4000 + a - 0x4000
r16 = lambda o: g[o] | g[o + 1] << 8

# ---- 黄
def rd(p): return open(os.path.join(Y, p), encoding='utf-8').read()
bst = {}
for m in re.finditer(r'((?:\w+_Block::\s*\n?)+)\s*INCBIN "(gfx/blocksets/\w+\.bst)"', rd('gfx/tilesets.asm')):
    for n in re.findall(r'(\w+)_Block::', m.group(1)): bst[n] = open(os.path.join(Y, m.group(2)), 'rb').read()
coll = {}; pend = []
for l in rd('data/tilesets/collision_tile_ids.asm').splitlines():
    m = re.match(r'(\w+)_Coll::', l)
    if m: pend.append(m.group(1)); continue
    m = re.match(r'\s*coll_tiles\s*(.*)', l)
    if m and pend:
        t = [int(x.strip().lstrip('$'), 16) for x in m.group(1).split(',') if x.strip()]
        for n in pend: coll[n] = set(t)
        pend = []
tsn = re.findall(r'^\s*tileset (\w+),', rd('data/tilesets/tileset_headers.asm'), re.M)
TSCONST = {}
for i, l in enumerate(re.findall(r'^\s*const (\w+)', rd('constants/tileset_constants.asm'), re.M)): TSCONST[l] = i
dims = {c: (int(w), int(h)) for c, w, h in re.findall(r'map_const (\w+),\s*(\d+),\s*(\d+)', rd('constants/map_constants.asm'))}
ledge = set()
for a, b, c, d in re.findall(r'db \$(\w+), \$(\w+), \$(\w+), \$(\w+)', rd('data/tilesets/ledge_tiles.asm')): ledge.add(int(c, 16))
WATER = {'Overworld', 'Forest', 'Gym', 'Dojo', 'Ship', 'ShipPort', 'Cavern', 'Facility', 'Plateau'}
ymaps = {}
for f in glob.glob(os.path.join(Y, 'data/maps/headers/*.asm')):
    m = re.search(r'map_header (\w+), (\w+), (\w+)', open(f, encoding='utf-8').read())
    if not m: continue
    name, const, ts = m.groups(); blk = os.path.join(Y, 'maps', name + '.blk')
    if not os.path.exists(blk) or const not in dims: continue
    tsname = tsn[TSCONST[ts]]
    ob = os.path.join(Y, 'data/maps/objects', name + '.asm')
    warps = [(int(x), int(y)) for x, y in re.findall(r'warp_event\s+(\d+),\s*(\d+)', open(ob, encoding='utf-8').read())] if os.path.exists(ob) else []
    ymaps[name] = dict(w=dims[const][0], h=dims[const][1], blk=open(blk, 'rb').read(), ts=tsname, warps=warps)

def ygrid(m):
    w, h, b, t = m['w'], m['h'], m['blk'], m['ts']; bs = bst[t]; pas = coll[t]; G = []
    for y in range(h * 2):
        row = ''
        for x in range(w * 2):
            blk = b[(y // 2) * w + x // 2]; tile = bs[blk * 16 + ((y % 2) * 2 + 1) * 4 + (x % 2) * 2]
            row += 'W' if tile in pas else 'L' if (t == 'Overworld' and tile in ledge) else '~' if (tile == 0x14 and t in WATER) else 'X'
        G.append(row)
    for x, y in m['warps']:
        if y < len(G) and x < len(G[0]): G[y] = G[y][:x] + 'D' + G[y][x + 1:]
    return G

# ---- 移植版
TS = fo(g[0x2DB8 + 19], r16(0x2DB9)); CP = fo(0x3E, 0x734A)
mg = fo(0x25, 0x40ED); gp = []; o = mg
while not gp or o < fo(0x25, min(gp)): gp.append(r16(o)); o += 2
srt = sorted(set(gp)); pmaps = []
for gi in range(1, len(gp) + 1):
    p = gp[gi - 1]; nx = [q for q in srt if q > p]; cnt = (fo(0x25, nx[0]) - fo(0x25, p)) // 9 if nx else 160
    for mi in range(1, cnt + 1):
        h = fo(0x25, p) + 9 * (mi - 1)
        try:
            a = Walk(g).map(fo(g[h], r16(h + 3)), 'x'); w, hh = a['w'], a['h']
            if not (0 < w <= 60 and 0 < hh <= 60): continue
            blk = bytes(g[fo(a['blkbank'], a['blk']):][:w * hh])
        except Exception: continue
        pmaps.append(dict(id=(gi, mi), hdr=h, w=w, h=hh, blk=blk, ts=g[h + 1], warps=[(wp[1], wp[0]) for wp in a['warps']]))

def pgrid(m):
    t = TS + 15 * m['ts']; co = fo(g[t + 6], r16(t + 7)); G = []
    for y in range(m['h'] * 2):
        row = ''
        for x in range(m['w'] * 2):
            c = g[co + m['blk'][(y // 2) * m['w'] + x // 2] * 4 + (y % 2) * 2 + (x % 2)]; pm = g[CP + c] & 0x0F
            row += 'D' if 0x70 <= c <= 0x7F else 'L' if 0xA0 <= c <= 0xAF else 'W' if pm == 0 else '~' if pm == 1 else 'X'
        G.append(row)
    return G, [(x, y) for x, y in m['warps']]

out = []; nd = 0
for name, ym in sorted(ymaps.items()):
    best = None
    for pm in pmaps:
        if (pm['w'], pm['h']) != (ym['w'], ym['h']): continue
        s = sum(a == b for a, b in zip(pm['blk'], ym['blk'])) / len(ym['blk'])
        if not best or s > best[0]: best = (s, pm)
    if not best or best[0] < 0.5: continue
    pm = best[1]; YG = ygrid(ym); PG, pw = pgrid(pm)
    diff = [(x, y, YG[y][x], PG[y][x]) for y in range(len(YG)) for x in range(len(YG[0]))
            if YG[y][x] != PG[y][x] and not (YG[y][x] == 'D' and PG[y][x] in 'WD') and not (YG[y][x] == 'W' and PG[y][x] == 'D' and (x, y) in pw)]
    extra = [(x, y) for y in range(len(PG)) for x in range(len(PG[0])) if PG[y][x] == 'D' and (x, y) not in pw]
    wy = sorted(set(ym['warps'])); wp = sorted(set(pw))
    if diff or extra or wy != wp:
        nd += 1
        out.append('== %s → %s（一致 %.0f%%）' % (name, '%d.%d' % pm['id'], best[0] * 100))
        if wy != wp: out.append('  出入口：黄 %s / 移植 %s' % (wy, wp))
        if extra: out.append('  出入口でないのに出入口の当たり：%s' % extra)
        if diff: out.append('  ちがう マス（x,y 黄→移植）：%s' % ' '.join('%d,%d %s→%s' % d for d in diff[:40]) + (' …ほか%d' % (len(diff) - 40) if len(diff) > 40 else ''))
print('\n'.join(out)); print('ちがいの ある マップ：%d' % nd, file=sys.stderr)
