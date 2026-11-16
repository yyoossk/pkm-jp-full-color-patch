"""移植版の マップと 赤（pokered）の マップの 対応を 作る。
   外の マップは ブロックの ならびで、建物の 中は 入口（warp）を たどって 決める（同じ 形の 家が 多いので）"""
import re, os, glob, sys
sys.path.insert(0, '/home/claude/work/scripts')
from cwalk import Walk
RED = '/home/claude/work/mod/ref/pokered'
fo = lambda b, a: b * 0x4000 + a - 0x4000

def red_maps(R=RED):
    rd = lambda p: open(os.path.join(R, p), encoding='utf-8').read()
    dims = {c: (int(w), int(h)) for c, w, h in re.findall(r'map_const (\w+),\s*(\d+),\s*(\d+)', rd('constants/map_constants.asm'))}
    out = {}; c2n = {}
    for f in glob.glob(os.path.join(R, 'data/maps/headers/*.asm')):
        m = re.search(r'map_header (\w+), (\w+), (\w+)', open(f, encoding='utf-8').read())
        if not m: continue
        name, const, ts = m.groups(); c2n[const] = name
        blk = os.path.join(R, 'maps', name + '.blk')
        if not os.path.exists(blk) or const not in dims: continue
        ob = os.path.join(R, 'data/maps/objects', name + '.asm'); t = open(ob, encoding='utf-8').read() if os.path.exists(ob) else ''
        out[name] = dict(name=name, const=const, ts=ts, w=dims[const][0], h=dims[const][1], blk=open(blk, 'rb').read(),
                         warps=[(int(x), int(y), d) for x, y, d in re.findall(r'warp_event\s+(\d+),\s*(\d+),\s*(\w+)', t)],
                         objs=[(int(x), int(y), s) for x, y, s in re.findall(r'object_event\s+(\d+),\s*(\d+),\s*(SPRITE_\w+)', t)])
    return out, c2n

def port_maps(g):
    r16 = lambda o: g[o] | g[o + 1] << 8
    mg = fo(0x25, 0x40ED); gp = []; o = mg
    while not gp or o < fo(0x25, min(gp)): gp.append(r16(o)); o += 2
    srt = sorted(set(gp)); out = {}
    for gi in range(1, len(gp) + 1):
        p = gp[gi - 1]; nx = [q for q in srt if q > p]; cnt = (fo(0x25, nx[0]) - fo(0x25, p)) // 9 if nx else 160
        for mi in range(1, cnt + 1):
            h = fo(0x25, p) + 9 * (mi - 1)
            try:
                a = Walk(g).map(fo(g[h], r16(h + 3)), 'x'); w, hh = a['w'], a['h']
                if not (0 < w <= 60 and 0 < hh <= 60): continue
                blk = bytes(g[fo(a['blkbank'], a['blk']):][:w * hh])
            except Exception: continue
            out[(gi, mi)] = dict(id=(gi, mi), hdr=h, w=w, h=hh, blk=blk, ts=g[h + 1], attr=a,
                                 warps=[(wp[1], wp[0], (wp[3], wp[4])) for wp in a['warps']])
    return out

def match(red, port):
    """赤の 名前 → 移植版の (グループ, 番号)"""
    def sim(r, p):
        if (p['w'], p['h']) != (r['w'], r['h']): return 0
        return sum(a == b for a, b in zip(p['blk'], r['blk'])) / len(r['blk'])
    M = {}
    for n, r in red.items():
        sc = sorted(((sim(r, p), pid) for pid, p in port.items()), reverse=True)
        if sc and sc[0][0] >= 0.9 and (len(sc) < 2 or sc[1][0] < sc[0][0]) and r['w'] * r['h'] >= 30: M[n] = sc[0][1]
    c2n = {r['const']: n for n, r in red.items()}
    changed = True
    while changed:
        changed = False
        for n, pid in list(M.items()):
            pw = {(x, y): d for x, y, d in port[pid]['warps']}
            for x, y, d in red[n]['warps']:
                dn = c2n.get(d)
                if dn and dn not in M and (x, y) in pw and pw[(x, y)] in port:
                    M[dn] = pw[(x, y)]; changed = True
    return M
