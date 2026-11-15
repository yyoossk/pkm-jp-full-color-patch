"""第47〜51弾の 一部：MOD が 変えた ジョウトの マップ（金と クリスタルで つくりが 同じ もの）。
   マップの スクリプト・イベントは MOD の ものを 入れ（ジムリーダーの 再戦・3年後の セリフ など）、
   MOD が 変えていない セリフは 金の セリフ（同じ 場所の もの）に もどす。ブロック・見出し・つながりは 金のまま。"""
import sys
sys.path.insert(0, '/home/claude/work/scripts')
from cwalk import Walk
from cmaps import maplist
from maps import CMGP, GMGP

SAME = ('OlivineGym MahoganyGym SlowpokeWellB1F TeamRocketBaseB1F SilverCaveRoom3 MoveDeletersHouse AzaleaGym '
        'LakeOfRage VioletGym GoldenrodGym BillsFamilysHouse OlivinePort FastShip1F CianwoodGym NewBarkTown').split()


def gold_texts(walks, VAN, GV, log):
    cv = {m['name']: m for m in maplist(VAN, CMGP, 'pokecrystal')}
    gv = {m['name']: m for m in maplist(GV, GMGP, 'pokegold')}
    n = 0
    for nm in SAME:
        if nm not in walks: log.append('ジョウト：入らなかった %s' % nm); continue
        W, at = walks[nm]
        a = Walk(VAN); a.map(cv[nm]['attr'], nm); a.run()
        b = Walk(GV); b.map(gv[nm]['attr'], nm); b.run()
        ta = [x['data'] for x in a.blobs.values() if x['kind'] == 'text']
        tb = [x['data'] for x in b.blobs.values() if x['kind'] == 'text']
        if len(ta) != len(tb): log.append('ジョウト：セリフの 数が ちがう %s' % nm); continue
        pair = {}
        for x, y in zip(ta, tb): pair.setdefault(x, y)
        for k, bl in W.blobs.items():
            if bl['kind'] == 'text' and bl['data'] in pair and pair[bl['data']] != bl['data']:
                bl['data'] = pair[bl['data']]; bl['fix'] = []; n += 1
    log.append('ジョウト（MOD の 変更）：%d マップ、金の セリフに もどした %d' % (len(SAME), n))


def patch_attrs(E, g, log):
    keep = []
    for ent in E.pending:
        cname, gm, at, gb, sa, ea, bgb, ba, chdr = ent
        if cname in SAME:
            o = gm['attr']
            g[o + 6] = gb; g[o + 7] = sa & 255; g[o + 8] = sa >> 8; g[o + 9] = ea & 255; g[o + 10] = ea >> 8
            E.blk.pop(cname, None)
        else:
            keep.append(ent)
    E.pending[:] = keep
