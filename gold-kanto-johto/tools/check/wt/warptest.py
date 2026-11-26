"""全マップの 全ワープに、となりの 歩ける マスから 歩いて 入る テスト（第123弾 キットの warptest_all の 金版）。
   python3 warptest.py ROM 出力.jsonl [ステート] [SHARD a/n]
   となりの マスへは メモリで 飛ぶ（そこまでは テストしない）。そこから 1歩 おして、マップが かわるか
   （マットは もう一度 その 向きに おす）。前の 版と くらべて、新しく 入れなく なった 所が バグ。"""
import sys, os, json
sys.path.insert(0, '/home/claude/sameboy-harness/python'); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gr import GR; from walker import W
R, OUT = sys.argv[1], sys.argv[2]
ST = sys.argv[3] if len(sys.argv) > 3 else '/home/claude/work/wt/jl7.st'
SH = sys.argv[4] if len(sys.argv) > 4 else None
DV = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
CD = {0x70: 'D', 0x76: 'L', 0x78: 'U', 0x7E: 'R'}
g = GR(R); g.load_state(ST); g.wait(5)
w = W(g, R)
for _ in range(6): g.press('B', 4, 20)
base = '/tmp/wtest_base_%d.st' % os.getpid(); g.save_state(base)
keys = sorted(w.maps)
if os.environ.get('BANKS'):   # 環境変数 BANKS=A3,A0 … その スクリプトの バンクの マップだけ（直した マップと 同じ バンクだけ 見る とき）
    _B = {int(x, 16) for x in os.environ['BANKS'].split(',')}; keys = [k for k in keys if w.maps[k]['attr']['scbank'] in _B]
if SH: a_, n_ = map(int, SH.split('/')); keys = [k for j, k in enumerate(keys) if j % n_ == a_]
done = set()
if os.path.exists(OUT):
    for l in open(OUT): d = json.loads(l); done.add((tuple(d['k']), d['i']))
f = open(OUT, 'a')


def where():
    p = w.pos(); return (p[0], p[1]), p[2], p[3]


def jump(k, x, y):
    g.load_state(base); g.wait(2)
    g.poke(0xD9C6, k[0]); g.poke(0xD9C7, k[1]); g.poke(0xD9C9, x); g.poke(0xD9C8, y)
    g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1); g.wait(150)
    for _ in range(3): g.press('B', 4, 10)


for k in keys:
    m = w.maps[k]
    try: c = w.coll(k)
    except Exception: continue
    for i, (wx, wy, dest) in enumerate(m['warps']):
        if (k, i) in done: continue
        cc = c(wx, wy); cd = CD.get(cc)
        order = ([cd] if cd else []) + [d for d in 'UDLR' if d != cd]
        res = 'noapproach'; how = None
        if not w.warp_tile(cc): res = 'notwarptile'; order = []
        for d in order:
            dx, dy = DV[d]; ax, ay = wx - dx, wy - dy
            ca = c(ax, ay)
            if ca is None or not w.passable(ca, (ax, ay), d) or w.warp_tile(ca) and ca not in w.CARPET: continue
            jump(k, ax, ay)
            if where() != (k, ax, ay): res = 'nowarp'; continue
            g.poke(0xD9B1, 250)
            g.down(d); g.wait(20); g.up(d); g.wait(80)
            for _ in range(4):
                if w.textbox(): g.press('B', 4, 30)
            wh = where()
            if wh[0] != k or abs(wh[1] - wx) + abs(wh[2] - wy) > 2: res = 'ok'; how = d; break
            if wh[1:] == (wx, wy):
                dd = cd or d
                g.down(dd); g.wait(24); g.up(dd); g.wait(80)
                wh = where()
                if wh[0] != k or abs(wh[1] - wx) + abs(wh[2] - wy) > 2: res = 'ok'; how = d + '+' + dd; break
            res = 'fail %s' % (wh,)
            break
        rec = {'k': list(k), 'i': i, 'xy': [wx, wy], 'coll': cc, 'dest': list(dest), 'res': res, 'how': how}
        f.write(json.dumps(rec, ensure_ascii=False) + '\n'); f.flush()
print('done')
os.remove(base)
