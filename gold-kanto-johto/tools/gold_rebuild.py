"""金の マップの スクリプト一式を 新しい バンクへ うつしなおし（中身は 金のまま）、MOD の 変更を 足す しくみ。
   ・金の スクリプトは 金の 命令表（pokegold）で たどる。ポインターは うつした先へ 読みかえる（ほかは そのまま）。
   ・mods：
       'text'：{金の セリフ（バイト列）: 新しい セリフ（バイト列）}
       'obj' ：{金の 人の 番号: (MOD の バンク, 住所)}   … その 人の スクリプトを MOD の もの（c2g で 読みかえ）に
       'bg'  ：{金の 看板の 番号: (MOD の バンク, 住所)}
       'coord'／'scene'／'callback'：同じ
       'add_obj'：[MOD の 人の データ 13 バイト（スクリプトは MOD の 住所）]  … 人を 足す
   MOD の スクリプトは E（c2g.Emit）で 置くので、置く バンクは E.gbank(MOD の スクリプトの バンク)。"""
import sys, importlib.util
sys.path.insert(0, '/home/claude/work/scripts')
import cwalk
_sp = importlib.util.spec_from_file_location('gwalk', cwalk.__file__)
gw = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(gw)
_S = gw.load_spec('pokegold')
for _i, (_n, _a) in enumerate(_S):
    if _n in gw.FIX and gw.FIX[_n] is not None: _S[_i] = (_n, gw.FIX[_n])
gw.SPEC = _S; gw.OP = {n: i for i, (n, a) in enumerate(_S)}
def fo(b, a): return b * 0x4000 + a - 0x4000
def w(r, o): return r[o] | r[o + 1] << 8
NOPTR = ('music_pointer', 'sound_pointer', 'caller_name')


def mod_tree(M, b, a, kind='script', stop=()):
    W = cwalk.Walk(M)
    for k in stop: W.blobs[k] = None          # 金の スクリプトへ もどる 所（たどらない）
    W.add(kind, b, a, 'mod'); W.run()
    for k in stop: W.blobs.pop(k, None)
    return W


def rebuild(E, g, GV, gm, nm, mods, M, MB, log):
    """gm：金の マップ（maplist の dict）。MB：MOD の この マップの スクリプトの バンク（置く バンクを そろえる）"""
    W = gw.Walk(GV); at = W.map(gm['attr'], nm); W.run()
    bad = [n for n in W.notes if 'raw' in n or 'menu' in n or '不明' in n or 'COPY' in n]
    sb = at['scbank']
    # MOD の 木
    trees = {}
    for k in ('obj', 'bg', 'coord', 'scene', 'callback'):
        for i, (b, a) in mods.get(k, {}).items():
            trees[(k, i)] = mod_tree(M, b, a, stop=mods.get('back', {}))
    for i, (t_, (b, a)) in enumerate(mods.get('add_cb', [])):
        trees[('addcb', i)] = mod_tree(M, b, a, stop=mods.get('back', {}))
    for i, ob in enumerate(mods.get('add_obj', [])):
        trees[('add', i)] = mod_tree(M, MB, w(ob, 9), 'trainer' if (ob[7] & 0xF) == 2 else 'script')
    for T in trees.values():
        for k, bl in T.blobs.items(): E.place(k, bl)
    NB = E.gbank(MB)
    # 金の かたまりを 置く
    tsub = mods.get('text', {})
    loc = {}
    for k, bl in W.blobs.items():
        if bl['kind'] == 'text' and bl['data'] in tsub: bl['data'] = tsub[bl['data']]; bl['fix'] = []; bl['_sub'] = True
        n = len(bl['data']); a = E.fill[NB]; assert a + n <= 0x8000, 'バンクが いっぱい %02X' % NB
        loc[k] = a; E.fill[NB] = a + n
    def rel(v):
        if v < 0x4000 or v in (0xFFFF,): return v
        if (sb, v) in loc: return loc[(sb, v)]
        bad.append('うつせない ポインター %02X:%04X' % (sb, v)); return v
    for k, bl in W.blobs.items():
        d = bytearray(bl['data'])
        for off, t, sem, name in bl['fix']:
            if t == 'dw' and ('pointer' in sem or sem == 'data') and sem not in NOPTR:
                v = w(d, off)
                if bl['bank'] == sb: nv = rel(v)
                else: nv = v
                d[off] = nv & 255; d[off + 1] = nv >> 8
            elif t == 'dba':
                bb, aa = d[off], w(d, off + 1)
                if (bb, aa) in loc and bb == sb: d[off] = NB; na = loc[(bb, aa)]; d[off + 1] = na & 255; d[off + 2] = na >> 8
        o = fo(NB, loc[k]); g[o:o + len(d)] = d
    def relin(v):                                   # 金の もとの 住所（かたまりの 中でも よい）→ うつした先
        for (bb, aa), bl in W.blobs.items():
            if bb == sb and aa <= v < aa + max(1, len(bl['data'])): return loc[(bb, aa)] + v - aa
        raise Exception('もどり先が ない %04X' % v)
    back = mods.get('back', {})
    for T in trees.values():
        for k, bl in T.blobs.items():
            E.write(k, bl)
            gb_, ga_ = E.loc[k]
            for off, t, sem, name in bl['fix']:
                if t == 'dba':
                    o_ = fo(bl['bank'], bl['addr']) + off; key = (M[o_], w(M, o_ + 1))
                    if key in back:
                        na = relin(back[key]); q = fo(gb_, ga_) + off; g[q] = NB; g[q + 1] = na & 255; g[q + 2] = na >> 8
    def mptr(key):
        T = trees[key]; k = next(iter(T.blobs)); b_, a_ = E.loc[k]; assert b_ == NB, (key, hex(b_), hex(NB)); return a_
    E.homemiss[:] = [m for m in E.homemiss if not any(('未配置 %02X:%04X' % k) in m for k in back)]
    # スクリプトの 見出し
    sh = bytearray([len(at['scenes'])])
    for i, p in enumerate(at['scenes']):
        p = mptr(('scene', i)) if ('scene', i) in trees else rel(p); sh += p.to_bytes(2, 'little') + b'\0\0'
    sh.append(len(at['callbacks']) + len(mods.get('add_cb', [])))
    for i, (t, p) in enumerate(at['callbacks']):
        p = mptr(('callback', i)) if ('callback', i) in trees else rel(p); sh += bytes([t]) + p.to_bytes(2, 'little')
    for i, (t, ba) in enumerate(mods.get('add_cb', [])): sh += bytes([t]) + mptr(('addcb', i)).to_bytes(2, 'little')
    # イベント
    ev = bytearray(at['ev0']); ev.append(len(at['warps']))
    for wv in at['warps']: ev += wv
    coords = []
    for i, c in enumerate(at['coords']):
        p = mptr(('coord', i)) if ('coord', i) in trees else rel(w(c, 4)); coords.append(bytes(c[:4] + p.to_bytes(2, 'little') + c[6:8]))
    bgs = []
    for i, b_ in enumerate(at['bgs']):
        p = mptr(('bg', i)) if ('bg', i) in trees else rel(w(b_, 3)); bgs.append(bytes(b_[:3] + p.to_bytes(2, 'little')))
    objs_l = []
    for i, ob in enumerate(list(at['objs'])):
        ob = bytearray(ob); p = mptr(('obj', i)) if ('obj', i) in trees else rel(w(ob, 9)); ob[9:11] = p.to_bytes(2, 'little'); objs_l.append(ob)
    for i, ob in enumerate(mods.get('add_obj', [])):
        ob = bytearray(ob); X = E.X
        ob[0] = X.sprite(ob[0], nm); ob[9:11] = (mptr(('add', i)) if (ob[7] & 0xF) != 1 else 0).to_bytes(2, 'little')
        ob[11:13] = X.event(w(ob, 11), nm).to_bytes(2, 'little'); objs_l.append(ob)
    if 'hook' in mods:                               # 第66弾など：イベントを 足す（f(E, バンク, alloc, g, coords, objs)）
        def alloc(n, bank):
            a_ = E.fill[bank]; assert a_ + n <= 0x8000; E.fill[bank] = a_ + n; return a_
        mods['hook'](E, NB, alloc, g, coords, objs_l)
    ev.append(len(coords))
    for c in coords: ev += c
    ev.append(len(bgs))
    for b_ in bgs: ev += b_
    ev.append(len(objs_l))
    for ob in objs_l: ev += ob
    sa = E.fill[NB]; E.fill[NB] += len(sh); g[fo(NB, sa):fo(NB, sa) + len(sh)] = sh
    ea = E.fill[NB]; E.fill[NB] += len(ev); g[fo(NB, ea):fo(NB, ea) + len(ev)] = ev
    o = gm['attr']; g[o + 6] = NB; g[o + 7:o + 9] = sa.to_bytes(2, 'little'); g[o + 9:o + 11] = ea.to_bytes(2, 'little')
    nsub = sum(1 for bl in W.blobs.values() if bl.get('_sub'))
    log.append('%s：金の スクリプトを %02X へ（%d かたまり、セリフ %d/%d、MOD %d）%s' % (
        nm, NB, len(W.blobs), nsub, len(tsub), len(trees), ' ／ '.join(sorted(set(bad))) if bad else ''))
    assert nsub == len(tsub), (nm, 'セリフが 見つからない')
