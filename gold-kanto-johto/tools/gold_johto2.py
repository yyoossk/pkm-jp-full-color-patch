"""第47〜51弾の つづき：金と クリスタルで つくりが ちがう ジョウトの マップ。
   金の スクリプトを 新しい バンクへ うつしなおし（gold_rebuild）、MOD の 変更だけを 足す：
   ・ジムリーダーの 再戦（MOD は はじめを farsjump に して 再戦の しらべを 足した → 同じ ように つなぐ）
   ・セリフの 書きかえ（金の セリフの 同じ 所を MOD と 同じ 意味に）"""
import sys
sys.path.insert(0, '/home/claude/work/scripts')
import cwalk, jpchar, gold_rebuild as gr
from cmaps import maplist
from maps import CMGP, GMGP
def w(r, o): return r[o] | r[o + 1] << 8

# 金の セリフの 書きかえ：(マップ, もとの 一部, あたらしい 一部)。一部は jpchar の 文字（金の セリフを decode した もの）で
TEXT = [
    ('BlackthornGym1F', 'まさか　そんな　はず　ないよ', 'さすが　チャンピオン　だね！'),
    ('BlackthornGym1F', 'あなたの　じつりょく　じゃ<CONT><POKEMON>りーグに　ちょうせん　なんて<CONT>むり　よ',
                        'りーグの　チャンピオン　でも<CONT>いまの　あなたは　みとめられない'),
    ('Route27', 'カントーちほう　への<LINE>だいいっぽを　ふみだした！', 'ふるさとの　カントーちほうは<LINE>もう　すぐ　そこだ！'),
]
# 再戦を 足す 人：(マップ, MOD の 人の 番号, 金の 人の 番号)
GRAFT = [('EcruteakGym', 0, 0), ('BlackthornGym1F', 0, 0)]


def _ins(R, b, a, spec, n=24):
    """はじめから n 命令：[(住所, 名前, とび先)]"""
    o = cwalk.fo(b, a); p = o; out = []
    for _ in range(n):
        name, args = spec[R[p]]; q = p + 1; tgt = None
        for t, sem in args:
            if t == 'dw' and name in ('iftrue', 'iffalse', 'ifequal', 'ifnotequal', 'ifgreater', 'ifless', 'sjump'): tgt = w(R, q)
            q += cwalk.SIZE[t]
        out.append((a + p - o, name, tgt)); p = q
        if name in cwalk.END: break
    return out


def auto_back(M, V, GV, mb, ma, vb, va, gb, ga, gspec):
    """MOD の 再戦の しらべが もどる 先（クリスタルの 住所）→ 金の 住所"""
    T = gr.mod_tree(M, mb, ma)
    tg = set()
    for k, bl in T.blobs.items():
        for off, t, sem, name in bl['fix']:
            if t == 'dba' and name == 'farsjump' and bl['bank'] == mb:
                o = cwalk.fo(bl['bank'], bl['addr']) + off; bb, aa = M[o], w(M, o + 1)
                if bb == vb: tg.add(aa)
    iv = _ins(V, vb, va, cwalk.SPEC); ig = _ins(GV, gb, ga, gspec)
    back = {}
    for x in tg:
        hit = None
        for (a1, n1, t1), (a2, n2, t2) in zip(iv, ig):
            if n1 != n2: break
            if a1 == x: hit = a2
            if t1 == x: hit = t2
        assert hit is not None, hex(x)
        back[(vb, x)] = hit
    return back


def apply(E, g, GV, M, V, log):
    cm = {m['name']: m for m in maplist(M, CMGP, 'pokecrystal')}
    cv = {m['name']: m for m in maplist(V, CMGP, 'pokecrystal')}
    gm = {m['name']: m for m in maplist(GV, GMGP, 'pokegold')}
    names = sorted(set([t[0] for t in TEXT] + [x[0] for x in GRAFT]))
    for nm in names:
        mods = {'text': {}, 'obj': {}, 'back': {}}
        gat = gr.gw.Walk(GV); at = gat.map(gm[nm]['attr'], nm); gat.run()
        gtexts = [bl['data'] for bl in gat.blobs.values() if bl['kind'] == 'text']
        for m_, old, new in TEXT:
            if m_ != nm: continue
            hit = [t for t in gtexts if old in jpchar.decode(t, False)]
            assert len(hit) == 1, (nm, old, len(hit))
            t = mods['text'].get(hit[0], hit[0])
            src = hit[0]
            mods['text'][src] = jpchar.encode(jpchar.decode(t, False).replace(old, new))
        mat = cwalk.Walk(M).map(cm[nm]['attr'], nm); vat = cwalk.Walk(V).map(cv[nm]['attr'], nm)
        for m_, mi, gi in GRAFT:
            if m_ != nm: continue
            mp = w(mat['objs'][mi], 9); vp = w(vat['objs'][mi], 9); gp = w(at['objs'][gi], 9)
            # MOD の 人の スクリプト：faceplayer / opentext / farsjump（再戦の しらべ）
            o = cwalk.fo(mat['scbank'], mp); assert M[o + 2] == cwalk.OP['farsjump'], nm
            rb, ra = M[o + 3], w(M, o + 4)
            mods['obj'][gi] = (mat['scbank'], mp)
            mods['back'].update(auto_back(M, V, GV, rb, ra, vat['scbank'], vp, at['scbank'], gp, gr.gw.SPEC))
        gr.rebuild(E, g, GV, gm[nm], nm, mods, M, mat['scbank'], log)
