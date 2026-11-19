"""全マップの 人と 看板に 話しかけて、止まる・リセット する 所を さがす（タマムシの けいひんじょの メニューで リセット した バグを 見て 作った）。
   python3 talkcrash.py ROM ステート 出力.jsonl [SHARD a/n]
   話しかけて A を 何度か（メニューは いちばん上を えらぶ）、B で 閉じる。そのあと：
     ・マップが (0,0)・タイトル（リセット）・PC が RAM の 中（$8000〜$FF7F、HRAM の ルーチン を のぞく）なら 'crash'
     ・1歩 動けるか（動けなければ 'stuck'。話の 中で 動かない ことも あるので 目で 見る）"""
import sys, os, json
sys.path.insert(0, '/home/claude/sameboy-harness/python'); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gr import GR; from walker import W, DIRS
R, ST, OUT = sys.argv[1:4]
SH = sys.argv[4] if len(sys.argv) > 4 else None
g = GR(R); g.load_state(ST); g.wait(3); w = W(g, R)
for _ in range(4): g.press('B', 4, 20)
_n = g.peek(0xD5D4)[0]; _it = g.peek(0xD5D5, _n + 1)
if 0x36 not in _it[:_n]: g.poke(0xD5D5 + _n, 0x36); g.poke(0xD5D6 + _n, 0xFF); g.poke(0xD5D4, _n + 1)   # コインケース
g.poke(0xD56D, 0x27); g.poke(0xD56E, 0x0F)                                                            # コイン 9999
g.cmd('render 0')
base = '/tmp/tc_base_%d.st' % os.getpid(); g.save_state(base)
keys = sorted(w.maps)
if SH: a_, n_ = map(int, SH.split('/')); keys = [k for j, k in enumerate(keys) if j % n_ == a_]
done = set()
if os.path.exists(OUT):
    for l in open(OUT): d = json.loads(l); done.add((tuple(d['k']), d['kind'], d['i']))
f = open(OUT, 'a')
SHOT = '/tmp/tc_shots'; os.makedirs(SHOT, exist_ok=True)


def pc():
    s = g.pc(); p = int(s.split('pc=')[1][:4], 16); return p


for mid in keys:
    m = w.maps[mid]; a = m['attr']
    try: c = w.coll(mid)
    except Exception: continue
    occ = {(o[2] - 4, o[1] - 4) for o in a['objs']}
    tg = [('o', i, (o[2] - 4, o[1] - 4)) for i, o in enumerate(a['objs'])] + [('b', i, (b[1], b[0])) for i, b in enumerate(a['bgs'])]
    for kind, i, (tx, ty) in tg:
        if (mid, kind, i) in done: continue
        job = None
        for d, (dx, dy) in DIRS.items():
            sx, sy = tx - dx, ty - dy
            if (sx, sy) in occ: continue
            v = c(sx, sy)
            if v is None or (w.rom[w.CP + v] & 0x0F) != 0 or w.warp_tile(v) and v >= 0x60: continue
            job = (sx, sy, d); break
        rec = {'k': list(mid), 'kind': kind, 'i': i, 't': [tx, ty]}
        if job is None:
            rec['res'] = 'noapproach'; f.write(json.dumps(rec) + '\n'); f.flush(); continue
        sx, sy, d = job
        g.load_state(base); g.wait(2)
        g.poke(0xD9C6, mid[0]); g.poke(0xD9C7, mid[1]); g.poke(0xD9C9, sx); g.poke(0xD9C8, sy)
        g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1); g.wait(130)
        g.poke(0xD9B1, 250); g.poke(0xDE36, 0xA5)   # リセットで 0 に なる しるし
        g.press(d, 2, 12); g.press('A', 4, 40)
        bad = None
        for k in range(12):
            g.press('A', 4, 30)
            p = pc()
            if 0x8000 <= p < 0xFF80: bad = 'pc %04X' % p; break
            if w.pos()[:2] == (0, 0) or g.peek(0xDE36)[0] != 0xA5: bad = 'reset'; break
        if not bad:
            for k in range(6): g.press('B', 4, 24)
            if w.in_battle():
                for k in range(60):
                    g.press('A', 4, 30)
                    if not w.in_battle(): break
                g.wait(200)
            p = pc()
            if 0x8000 <= p < 0xFF80: bad = 'pc %04X' % p
            elif w.pos()[:2] == (0, 0) or g.peek(0xDE36)[0] != 0xA5: bad = 'reset'
        rec['job'] = [sx, sy, d]; rec['res'] = bad or 'ok'; rec['end'] = list(w.pos())
        if bad:
            g.cmd('render 1'); g.wait(2); g.shot('%s/%d_%d_%s%d.png' % (SHOT, mid[0], mid[1], kind, i)); g.cmd('render 0')
        f.write(json.dumps(rec) + '\n'); f.flush()
print('done'); os.remove(base)
