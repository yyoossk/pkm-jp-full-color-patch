"""移植版を 歩いて 進める ための 道具（ワープ・メモリの 書きかえ なし）。
   W(g).goto(x, y) で 今の マップの 中を 歩く（当たりは ROM の マップから、ふさがれたら 道を さがしなおす）"""
import sys, os, collections
sys.path.insert(0, '/home/claude/repo/gold-kanto-johto/tools/check')
from redmap import port_maps, fo
WRAM_MAP = 0xD9C6          # グループ, 番号, Y, X
PSTRUCT = 0xD1F2; OSZ = 0x28          # 金（日本版）の wObjectStructs（0 番は 主人公）
DIRS = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}

class W:
    def __init__(s, g, rom, wmap=None, pstruct=None, wbattle=None, wbank=None):
        """rom：当たりを 読む 移植版。クリスタル版を 動かす ときは wmap=0xDC7B, pstruct=0xD4C9 など（マップは 同じ 番号の 移植版の ものを 使う）"""
        s.g = g; s.rom = bytearray(open(rom, 'rb').read()); s.maps = port_maps(s.rom)
        s.WBANK = wbank; s.WMAP = wmap or WRAM_MAP; s.PS = pstruct or PSTRUCT; s.WB = 0xD108 if wbattle is None else wbattle
        r16 = lambda o: s.rom[o] | s.rom[o + 1] << 8
        s.TS = fo(s.rom[0x2DB8 + 19], r16(0x2DB9)); s.CP = fo(0x3E, 0x734A); s.r16 = r16
        s.log = []
        import spins; s.jumps = spins.all_jumps()
    def rd(s, a, n=1):
        if s.WBANK and a >= 0xD000: return s.g.wpeek(s.WBANK, a, n)
        return s.g.peek(a, n)
    def pos(s):
        a = s.rd(s.WMAP, 4); return (a[0], a[1], a[3], a[2])
    def coll(s, mid):
        m = s.maps[mid]; t = s.TS + 15 * m['ts']; co = fo(s.rom[t + 6], s.r16(t + 7))
        def c(x, y):
            if not (0 <= x < m['w'] * 2 and 0 <= y < m['h'] * 2): return None
            return s.rom[co + m['blk'][(y // 2) * m['w'] + x // 2] * 4 + (y % 2) * 2 + (x % 2)]
        s._lastc = c
        return c
    def npcs(s):
        out = set()
        for i in range(1, 13):
            b = s.rd(s.PS + OSZ * i, 0x14)
            if b[1] == 0x13 and s.WMAP == WRAM_MAP: continue   # 連れ歩きの ポケモン（すりぬけて 入れかわれる）
            if b[0] and b[0x10] >= 4 and b[0x11] >= 4: out.add((b[0x10] - 4, b[0x11] - 4))
        return out
    CARPET = (0x70, 0x76, 0x78, 0x7E)      # その 向きに 押した ときだけの 入口（上を 歩ける）
    SIDE = {0xB0: 'R', 0xB1: 'L', 0xB2: 'U', 0xB3: 'D', 0xB4: 'DR', 0xB5: 'DL', 0xB6: 'UR', 0xB7: 'UL'}
    OPP = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}
    def passable(s, c, frm, d):
        if c is None: return False
        if c == 0x12 and getattr(s, 'can_cut', False): return True
        lc = getattr(s, '_lastc', None)
        if lc:                                        # 横の かべ（b0〜b7）：今 いる マスの かべの 向きへは 出られない・となりの かべの 向きからは 入れない
            f = lc(*frm)
            if f is not None and d in s.SIDE.get(f, ''): return False
            if s.OPP[d] in s.SIDE.get(c, ''): return False
        pm = s.rom[s.CP + c] & 0x0F
        if 0xA0 <= c <= 0xA7:                         # 段差：その 向きだけ
            return {0xA0: 'R', 0xA1: 'L', 0xA2: 'U', 0xA3: 'D', 0xA4: 'D', 0xA5: 'D', 0xA6: 'U', 0xA7: 'U'}.get(c) == d
        return pm == 0
    def path(s, tx, ty, avoid=()):
        gi, mi, x, y = s.pos(); c = s.coll((gi, mi)); blocked = set(avoid) | s.npcs()
        blocked |= {(wx, wy) for wx, wy, _ in s.maps[(gi, mi)]['warps'] if c(wx, wy) not in s.CARPET}    # ほかの 入口（ドア・階段）を ふまない
        prev = {(x, y): None}; q = collections.deque([(x, y)])
        while q:
            p = q.popleft()
            if p == (tx, ty): break
            for d, (dx, dy) in DIRS.items():
                n = (p[0] + dx, p[1] + dy)
                if 0xA0 <= (c(*n) or 0) <= 0xA7 and s.passable(c(*n), p, d): n = (n[0] + dx, n[1] + dy)   # 段差は とびこえる
                elif not s.passable(c(*n), p, d): 
                    if n != (tx, ty): continue
                if n in prev or n in blocked and n != (tx, ty): continue
                j = s.jumps.get(((gi, mi), p, d))
                if j is not None:                                # 回る 床：ふむと べつの 所へ（ためして おぼえた）
                    if j in prev: continue
                    n = j
                prev[n] = (p, d); q.append(n)
        if (tx, ty) not in prev: return None
        out = []; p = (tx, ty); s._exp = []
        while prev[p]: s._exp.append(p); p, d = prev[p]; out.append(d)
        s._exp.reverse()
        return out[::-1]
    def explore_to(s, tx, ty, tries=40):
        """回る 床の マップで (tx, ty) へ：知らない 回る 床を 1つずつ ためして おぼえる（jumps は ファイルに のこす）"""
        import pickle, os
        jf = '/home/claude/work/wt/jumps.pkl'
        if os.path.exists(jf): s.jumps.update(pickle.load(open(jf, 'rb')))
        mid = s.pos()[:2]
        for _ in range(tries):
            if s.pos()[:2] != mid or s.pos()[2:] == (tx, ty): break
            if s.path(tx, ty) is not None:
                s.goto(tx, ty, tries=2); pickle.dump(s.jumps, open(jf, 'wb')); continue
            spins = s.spin_tiles(mid); c = s.coll(mid); _, _, x, y = s.pos()
            seen = {(x, y)}; q = collections.deque([(x, y)]); cand = None
            blocked = s.npcs()
            while q and cand is None:
                p = q.popleft()
                for d, (dx, dy) in DIRS.items():
                    n = (p[0] + dx, p[1] + dy)
                    if not s.passable(c(*n), p, d) or n in blocked: continue
                    j = s.jumps.get((mid, p, d))
                    if n in spins and j is None: cand = (p, d); break
                    if j is not None: n = j
                    if n not in seen: seen.add(n); q.append(n)
            if cand is None: s.log.append('回る 床：もう ためす 所が ない'); break
            (px, py), d = cand
            if (px, py) != s.pos()[2:] and not s.goto(px, py, tries=2): continue
            if s.pos()[2:] != (px, py): continue
            s.step(d)
            for _ in range(30):
                a1 = s.pos(); s.g.wait(8)
                if s.pos() == a1: break
            s.jumps[(mid, (px, py), d)] = s.pos()[2:]; pickle.dump(s.jumps, open(jf, 'wb'))
        return s.pos()[2:] == (tx, ty)
    def spin_tiles(s, mid):
        cs = s.maps[mid]['attr'].get('coords', [])
        return {(e[2], e[1]) for e in cs} if len(cs) >= 6 else set()
    def tcheck(s):
        import time
        if getattr(s, 'budget', None) and time.time() - s.t0 > s.budget: raise TimeoutError
    def step(s, d):
        s.tcheck(); before = s.pos(); s.g.down(d)
        for _ in range(40):
            s.g.wait(2)
            if s.pos() != before: break
        s.g.up(d); s.g.wait(10)
        if s.pos() == before and getattr(s, 'can_cut', False):
            gi, mi, x, y = before; dx, dy = DIRS[d]
            if s.coll((gi, mi))(x + dx, y + dy) == 0x12:     # いあいぎりで きれる 木
                s.g.press('A', 4, 60)
                for _ in range(6):
                    if s.menu_kind() == 'yesno': s.g.press('A', 4, 60); break
                    if s.textbox(): s.g.press('A', 4, 40)
                    else: s.g.wait(20)
                s.g.wait(120); s.advance()
                s.log.append('いあいぎり %s' % ((x + dx, y + dy),))
                return s.step(d)
        return s.pos() != before
    def settle(s):
        """うごきが おわるまで（階段に 着いた あとの ひとりでの 1歩 など）"""
        same = 0
        for _ in range(30):
            a1 = s.pos(); s.g.wait(10)
            same = same + 1 if s.pos() == a1 else 0
            if same >= 4: return
    def goto(s, tx, ty, tries=8):
        for _ in range(tries):
            s.settle(); gi, mi, x, y = s.pos()
            if (x, y) == (tx, ty): return True
            p = s.path(tx, ty)
            if p is None: s.log.append('道が ない %s → %s' % ((gi, mi, x, y), (tx, ty))); return False
            spins = s.spin_tiles((gi, mi)); exp = list(s._exp)
            for k, d in enumerate(p):
                frm = s.pos()[2:]
                if not s.step(d):
                    s.g.press('B', 4, 20); break
                if s.pos()[:2] != (gi, mi): return True        # マップが かわった（入口・つながり）
                if spins:
                    for _ in range(30):                           # 回る 床の うごきが おわるまで
                        a1 = s.pos(); s.g.wait(8)
                        if s.pos() == a1: break
                    dx, dy = DIRS[d]
                    if (frm[0] + dx, frm[1] + dy) in spins and s.pos()[2:] != exp[k]:
                        s.jumps[((gi, mi), frm, d)] = s.pos()[2:]; break
                    if s.pos()[2:] != exp[k]: break
        return s.pos()[2:] == (tx, ty)
    def face(s, d): s.g.press(d, 2, 10)
    def talk(s, d=None, n=12, key='A'):
        if d: s.face(d)
        for _ in range(n): s.g.press(key, 4, 40)

    def textbox(s):
        from PIL import Image
        p = '/tmp/_walker_tb.ppm'; s.g.cmd('shot ' + p); s.g.sync(); im = Image.open(p).convert('RGB')
        return im.getpixel((2, 110)) == (0, 0, 0) and im.getpixel((2, 130)) == (0, 0, 0)
    def clear(s, key='A', n=40, wait=40):
        """文が 出て いる あいだ key を 押す（押した 数を かえす）"""
        for i in range(n):
            if not s.textbox(): return i
            s.g.press(key, 4, wait)
        return n

    def in_battle(s): return bool(s.WB) and s.rd(s.WB)[0] != 0
    def battle(s, shot=None, maxn=400):
        """A を 押しつづけて 戦う（たたかう → 1番めの わざ）。shot(tag) が あれば 場面ごとに 写真"""
        n = 0
        while s.in_battle() and n < maxn:
            s.g.press('A', 4, 30); n += 1
            if shot and n % 15 == 1: shot('戦い')
        return n
    def advance(s, shot=None, n=60):
        """文・戦いが おわるまで すすめる"""
        for i in range(n):
            s.tcheck()
            if s.in_battle(): s.fight(run=getattr(s, 'run_wild', False), shot=shot); continue
            if s.textbox():
                if shot: shot('文')
                s.g.press('A', 4, 40); continue
            s.g.wait(30)
            if not s.textbox() and not s.in_battle():
                s.g.wait(50)       # 戦いの 前の 間（リーダーの「かかって こい!」の あと など）
                if not s.textbox() and not s.in_battle(): return i

    def reach(s):
        """今 いる 所から 歩いて 行ける マス"""
        gi, mi, x, y = s.pos(); c = s.coll((gi, mi)); seen = {(x, y)}; q = collections.deque([(x, y)])
        while q:
            p = q.popleft()
            for d, (dx, dy) in DIRS.items():
                n = (p[0] + dx, p[1] + dy)
                if 0xA0 <= (c(*n) or 0) <= 0xA7 and s.passable(c(*n), p, d): n = (n[0] + dx, n[1] + dy)
                elif not s.passable(c(*n), p, d): continue
                if n not in seen: seen.add(n); q.append(n)
        return seen
    def cross_ok(s, mid, d, x, y):
        """(x, y) から d へ つながりを こえた 先が 歩けるか"""
        a = s.maps[mid]['attr']; f = a['conn']; c = a['connections']; i = 0
        for bit, dd in ((8, 'U'), (4, 'D'), (2, 'L'), (1, 'R')):
            if not f & bit: continue
            e = c[i:i + 12]; i += 12
            if dd != d: continue
            dm = (e[0], e[1])
            if dm not in s.maps: return False
            yo, xo = (e[8] ^ 0x80) - 0x80, (e[9] ^ 0x80) - 0x80
            nx, ny = (x + xo, yo) if d in 'UD' else (xo, y + yo)
            ok = s.passable(s.coll(dm)(nx, ny), (nx, ny), 'U'); s.coll(mid); return ok
        return False
    def leave(s, d, shot=None, tries=4):
        """マップの はしから d の 向きへ 出る（つながり）。戦い・文は すすめる"""
        for _ in range(tries):
            mid = s.pos()[:2]; m = s.maps[mid]; W2, H2 = m['w'] * 2, m['h'] * 2
            edge = [p for p in s.reach() if (d == 'U' and p[1] == 0) or (d == 'D' and p[1] == H2 - 1) or
                    (d == 'L' and p[0] == 0) or (d == 'R' and p[0] == W2 - 1)]
            if not edge: s.log.append('はしが ない %s %s' % (mid, d)); return False
            ok = [p for p in edge if s.cross_ok(mid, d, *p)]
            if ok: edge = ok
            _, _, x, y = s.pos(); edge.sort(key=lambda p: abs(p[0] - x) + abs(p[1] - y))
            s.goto_safe(*edge[0], shot=shot)
            if s.pos()[:2] != mid: return True
            s.step(d); s.g.wait(30); s.advance(shot)
            if s.pos()[:2] != mid: return True
        return False
    def goto_safe(s, tx, ty, shot=None, tries=12):
        """とちゅうの 戦い・文を すすめながら goto"""
        for _ in range(tries):
            if s.in_battle() or s.textbox(): s.advance(shot)
            mid = s.pos()[:2]
            if s.goto(tx, ty, tries=2): return True
            if s.pos()[:2] != mid: return True
        return False
    def hold(s, d, frames=60):
        """d を 押しつづけて マップが かわるのを 待つ"""
        mid = s.pos()[:2]; s.g.down(d)
        for _ in range(frames // 4):
            s.g.wait(4)
            if s.pos()[:2] != mid: break
        s.g.up(d); s.g.wait(20); return s.pos()[:2] != mid
    def door(s, x, y, d, shot=None):
        """(x, y) の 入口まで 歩いて、d へ 押して 出入りする"""
        mid = s.pos()[:2]
        s.goto_safe(x, y, shot=shot)
        if s.pos()[:2] != mid: return True
        return s.hold(d)
    def objs(s, all=False):
        """マップの 人（イベントフラグで 消えている 人は のぞく）"""
        a = s.maps[s.pos()[:2]]['attr']
        return [(o[2] - 4, o[1] - 4, o[0]) for o in a['objs']
                if all or len(o) < 13 or (o[11] | o[12] << 8) == 0xFFFF or not s.flag(o[11] | o[12] << 8)]
    # ---- ゲームの 中の 記録（済んだ ことを とばす）
    def flag(s, n):
        """イベントフラグ n（gold_flags：$800〜$997 は $D70D〜、$998〜 は $D790〜、それより 前は wEventFlags $D7AA）"""
        if n < 0x800: a, k = 0xD7AA, n
        elif n < 0x998: a, k = 0xD70D, n - 0x800
        else: a, k = 0xD790, n - 0x998
        return bool(s.rd(a + k // 8)[0] >> (k % 8) & 1)
    def badges(s): return s.rd(0xD570)[0]
    def has_key(s, item):
        n = s.rd(0xD5D4)[0]
        return n <= 25 and item in s.rd(0xD5D5, n)
    def talk_to(s, ox, oy, shot=None, counter=True):
        """(ox, oy) の 人に となりから 話しかける（カウンターごしも ためす）"""
        cand = []
        for d, (dx, dy) in DIRS.items():
            for k in ((1, 2) if counter else (1,)):
                cand.append(((ox - dx * k, oy - dy * k), d, k))
        r = s.reach(); _, _, x, y = s.pos()
        cand = [c[:2] for c in sorted((c for c in cand if c[0] in r), key=lambda c: (c[2], abs(c[0][0] - x) + abs(c[0][1] - y)))]
        if not cand: return False
        (tx, ty), d = cand[0]; s.goto_safe(tx, ty, shot=shot); s.face(d); s.g.press('A', 4, 40)
        if shot: shot('話す')
        s.advance(shot); return True
    def warp_to(s, dest):
        """dest（グループ, 番号）へ 行く 入口を さがして 入る"""
        m = s.maps[s.pos()[:2]]
        for x, y, dd in m['warps']:
            if dd == dest:
                c = s.coll(s.pos()[:2])(x, y)
                d = {0x70: 'D', 0x76: 'L', 0x78: 'U', 0x7E: 'R'}.get(c, 'U')
                return s.door(x, y, d)
        return False

    # ---- 戦い（わざを えらぶ）
    MOVES = (0x10, 0x5C6C); BASE = (0x14, 0x5AA9); TCHART = (0x0D, 0x4CFD)
    W_BMON, W_EMON, W_CURSOR = 0xCB02, 0xD0E1, 0xCF14
    def _rom(s, ba, i=0): return s.rom[fo(ba[0], ba[1]) + i]
    def eff(s, t, defs):
        e = 1.0; o = fo(*s.TCHART)
        while s.rom[o] != 0xFF:
            if s.rom[o] == 0xFE: o += 1; continue
            a, d, x = s.rom[o:o + 3]
            if a == t and d in defs: e *= x / 10
            o += 3
        return e
    def types(s, sp):
        o = fo(*s.BASE) + (sp - 1) * 0x20; return {s.rom[o + 7], s.rom[o + 8]}
    def best_move(s, ex=()):
        b = s.rd(s.W_BMON, 0x20); e = s.rd(s.W_EMON, 2)
        mine, theirs = s.types(b[0]), s.types(e[0]); best = (-1, 0)
        for i in range(4):
            m = b[2 + i]; pp = b[8 + i] & 0x3F
            if not m or not pp or i in ex: continue
            o = fo(*s.MOVES) + (m - 1) * 7; pw, t, acc = s.rom[o + 2], s.rom[o + 3], s.rom[o + 4]
            sc = pw * s.eff(t, theirs) * (1.5 if t in mine else 1) * (acc / 255) if pw else 0.1
            if sc > best[0]: best = (sc, i)
        return best[1]
    def screen(s):
        from PIL import Image
        p = '/tmp/_walker_sc_%d.ppm' % os.getpid(); s.g.cmd('shot ' + p); s.g.sync(); return Image.open(p).convert('RGB')
    def menu_kind(s):
        im = s.screen(); k = lambda x, y: im.getpixel((x, y)) == (0, 0, 0)
        if all(k(x, y) for x in (114, 156) for y in (70, 80)) and not k(112, 70): return 'yesno'
        if k(70, 66) and k(70, 68) and k(2, 120): return 'move'
        if all(k(x, y) for x in (82, 84) for y in (90, 110, 130)) and k(100, 66) and k(150, 66) and not k(84, 62) and not k(70, 66): return 'forget'
        if k(66, 120) and k(68, 120) and k(2, 120): return 'main'
        if k(2, 110) and k(2, 130): return 'text'
        return None
    # ---- どうぐ（戦いの リュック）
    def pocket_is(s, name):
        from PIL import Image
        ref = Image.open('/home/claude/repo/gold-kanto-johto/tools/check/pocket_%s.png' % name).convert('RGB')
        cur = s.screen().crop((0, 56, 48, 72))
        return sum(a != b for a, b in zip(ref.getdata(), cur.getdata())) < 10
    def bag_use(s, pocket, idx=0, party=None):
        """戦いの 一番 上の メニューから リュック → pocket の idx 番めを つかう（party：だれに）"""
        for k in 'UL': s.g.press(k, 2, 6)
        s.g.press('R', 2, 6); s.g.press('A', 4, 40)
        for _ in range(5):
            if s.pocket_is(pocket): break
            s.g.press('R', 2, 20)
        else:
            s.g.press('B', 4, 30); return False
        for _ in range(12): s.g.press('U', 2, 4)
        for _ in range(idx): s.g.press('D', 2, 6)
        s.g.press('A', 4, 30); s.g.press('A', 4, 40)
        if party is not None:
            s.g.wait(30)
            for _ in range(party): s.g.press('D', 2, 6)
            s.g.press('A', 4, 40)
        return True
    def count_item(s, item):
        """どうぐの ポケット（$D5B7〜：数, (番号, 個数)…）・ボールの ポケットの 数"""
        for base in s.POCKETS:
            n = s.rd(base)[0]
            if n > 40: continue
            b = s.rd(base + 1, 2 * n)
            for i in range(n):
                if b[2 * i] == item: return b[2 * i + 1]
        return 0
    POCKETS = (0xD5AA, 0xD5EF)      # どうぐ・ボール（金 日本版。キーアイテムは $D5D4）
    def item_index(s, base, item):
        n = s.rd(base)[0]; b = s.rd(base + 1, 2 * n)
        for i in range(n):
            if b[2 * i] == item: return i
        return None
    def switch_to(s, i):
        """戦いの 一番 上の メニューから i ばんめに いれかえる"""
        for k in 'UL': s.g.press(k, 2, 6)
        s.g.press('D', 2, 6); s.g.press('A', 8, 60)
        for _ in range(6): s.g.press('U', 2, 6)
        for _ in range(i): s.g.press('D', 2, 6)
        s.g.press('A', 8, 60); s.g.press('A', 8, 60)
        s.log.append('いれかえ %d' % i)
    def learn_ctx(s):
        """わざを おぼえる はい/いいえ の 中か（スタックに 01:689F／01:68BE の もどり先）"""
        sp = int(s.g.pc().split('sp=')[1], 16); st = s.rd(sp, 0x30)
        return any(st[i + 1] == 0x68 and st[i] in (0x9F, 0xBE) for i in range(0, 0x2F))
    def fight(s, run=False, shot=None, maxn=600):
        """戦いを 終わりまで。run=True なら 野生は にげる"""
        n = 0; s._bn = getattr(s, '_bn', 0) + 1
        while s.in_battle() and n < maxn:
            n += 1; s.tcheck(); s._lastk = getattr(s, '_curk', None); kind = s.menu_kind(); s._curk = kind
            if kind == 'main':
                if shot and n % 4 == 1: shot('戦い')
                wild = s.rd(0xD108)[0] == 1
                lf = getattr(s, 'lead_for', None)
                if lf and getattr(s, '_sw', None) != s._bn:
                    i = lf(s.rd(s.W_EMON)[0], wild)
                    pt = s.party()
                    if i is not None and i < len(pt) and pt[i]['hp'] > 0 and pt[i]['sp'] != s.rd(s.W_BMON)[0]:
                        s._sw = s._bn; s.switch_to(i); continue
                    s._sw = s._bn
                want = getattr(s, 'want', None)
                if wild and want and want(s.rd(s.W_EMON)[0]) and s.count_item(5):
                    s.bag_use('ball', s.item_index(0xD5EF, 5)); s.log.append('ボール %d' % s.rd(s.W_EMON)[0]); continue
                bm = s.rd(s.W_BMON, 0x14); hp, mx = bm[0x10] << 8 | bm[0x11], bm[0x12] << 8 | bm[0x13]
                if not wild and hp * 2 < mx and s.count_item(0x12):
                    s.bag_use('item', s.item_index(0xD5AA, 0x12), party=0); s.log.append('キズぐすり'); continue
                for k in 'UL': s.g.press(k, 2, 6)
                if run and wild: s.g.press('D', 2, 6); s.g.press('R', 2, 6)
                s.g.press('A', 4, 30)
            elif kind == 'yesno':
                # わざを おぼえる ときの「わすれさせますか」「あきらめますか」（追加機能パッチで はじめが いいえ）は はい
                if s.learn_ctx(): s.g.press('U', 2, 6); s.g.press('A', 4, 40)
                else: s.g.press('B', 4, 40)      # ニックネーム・いれかえ などは いいえ
            elif kind == 'forget':
                b = s.rd(s.W_BMON, 0x20); pw = []
                for i in range(4):
                    m = b[2 + i]
                    pw.append(s.rom[fo(*s.MOVES) + (m - 1) * 7 + 2] if m else 999)
                i = pw.index(min(pw)); cur = s.rd(s.W_CURSOR)[0] - 1
                for _ in range((i - cur) % 4): s.g.press('D', 2, 6)
                s.log.append('わすれる わざ %d' % b[2 + i]); s.g.press('A', 4, 40)
            elif kind == 'move':
                ex = s._mex if getattr(s, '_lastk', None) == 'move' else set()
                i = s.best_move(ex)
                s._mex = ex | {i}; cur = s.rd(s.W_CURSOR)[0] - 1
                for _ in range((i - cur) % 4): s.g.press('D', 2, 6)
                s.g.press('A', 4, 40)
            else:
                unk = getattr(s, '_unk', 0) + 1; s._unk = unk
                if unk % 13 == 0: s.g.press('B', 4, 30)              # 手持ちの 画面 などで 止まったら B
                elif unk % 4 == 0: s.g.press('D', 4, 20); s.g.press('A', 4, 30)   # ひんしの ポケモンに カーソルが あるとき
                else: s.g.press('A', 4, 30)
                continue
            s._unk = 0
        return n

    # ---- マップを またいで 行く
    def conns(s, mid):
        a = s.maps[mid]['attr']; f = a['conn']; c = a['connections']; out = {}; i = 0
        for bit, d in ((8, 'U'), (4, 'D'), (2, 'L'), (1, 'R')):
            if f & bit: out[d] = (c[i], c[i + 1]); i += 12
        return out
    def _reach(s, mid, x, y):
        """マップ mid の (x, y) から 歩いて 行ける マス（人は 考えない）"""
        key = (mid, x, y)
        if not hasattr(s, '_rc'): s._rc = {}
        if key in s._rc: return s._rc[key]
        c = s.coll(mid); seen = {(x, y)}; q = collections.deque([(x, y)])
        wp = {(wx, wy) for wx, wy, _ in s.maps[mid]['warps'] if c(wx, wy) not in s.CARPET}
        while q:
            p = q.popleft()
            if p in wp and p != (x, y): continue      # 入口の マスからは 先へ 行かない
            for d, (dx, dy) in DIRS.items():
                n = (p[0] + dx, p[1] + dy)
                if 0xA0 <= (c(*n) or 0) <= 0xA7 and s.passable(c(*n), p, d): n = (n[0] + dx, n[1] + dy)
                elif not s.passable(c(*n), p, d): continue
                if n not in seen: seen.add(n); q.append(n)
        fs = frozenset(seen)
        for p in seen:
            if p not in wp: s._rc[(mid,) + p] = fs
        return fs
    def _hops(s, mid, comp):
        """つながる 先：(how, 次の マップ, 次の 入った 所)"""
        m = s.maps[mid]; W2, H2 = m['w'] * 2, m['h'] * 2; out = []
        for raw in m['attr']['warps']:
            y, x, wi, gg, mm = raw[0], raw[1], raw[2], raw[3], raw[4]
            if not ((x, y) in comp or any((x + dx, y + dy) in comp for dx, dy in DIRS.values())): continue
            dm = (gg, mm)
            if dm not in s.maps: continue
            dw = s.maps[dm]['attr']['warps']
            if not (1 <= wi <= len(dw)): continue
            out.append((('w', (x, y)), dm, (dw[wi - 1][1], dw[wi - 1][0])))
        a = m['attr']; f = a['conn']; c = a['connections']; i = 0
        for bit, d in ((8, 'U'), (4, 'D'), (2, 'L'), (1, 'R')):
            if not f & bit: continue
            e = c[i:i + 12]; i += 12; dm = (e[0], e[1])
            if dm not in s.maps: continue
            yo, xo = (e[8] ^ 0x80) - 0x80, (e[9] ^ 0x80) - 0x80
            edge = [p for p in comp if (d == 'U' and p[1] == 0) or (d == 'D' and p[1] == H2 - 1) or
                    (d == 'L' and p[0] == 0) or (d == 'R' and p[0] == W2 - 1)]
            for (x, y) in edge[:1] if False else edge:
                nx, ny = (x + xo, yo) if d in 'UD' else (xo, y + yo)
                c2 = s.coll(dm); s.coll(mid)
                if not s.passable(c2(nx, ny), (nx, ny), 'U'):
                    for k in (1, -1, 2, -2, 3, -3, 4, -4):
                        tx, ty = (nx + k, ny) if d in 'UD' else (nx, ny + k)
                        if s.passable(c2(tx, ty), (tx, ty), 'U'): nx, ny = tx, ty; break
                out.append((('c', d), dm, (nx, ny))); break
        return out
    def _comp(s, mid, x, y):
        c = s.coll(mid)
        if s.passable(c(x, y), (x, y), 'U') or True:
            r = s._reach(mid, x, y)
        return r
    def route(s, dest, avoid=()):
        avoid = set(avoid) | set(getattr(s, 'avoid', ()))
        gi, mi, x, y = s.pos(); start = ((gi, mi), s._reach((gi, mi), x, y))
        prev = {start: None}; q = collections.deque([start]); goal = None
        while q:
            node = q.popleft(); mid, comp = node
            if mid == dest: goal = node; break
            if mid not in s.maps or mid in avoid: continue
            for how, dm, (nx, ny) in s._hops(mid, comp):
                if dm not in s.maps: continue
                n = (dm, s._reach(dm, nx, ny))
                if n not in prev: prev[n] = (node, how); q.append(n)
        if goal is None: return None
        out = []; node = goal
        while prev[node]: pn, how = prev[node]; out.append((how, node[0])); node = pn
        return out[::-1]
    def travel(s, dest, shot=None, tries=3):
        for _ in range(tries):
            r = s.route(dest)
            if r is None: s.log.append('行けない %s' % (dest,)); return False
            for (kind, v), m in r:
                if kind == 'c': s.leave(v, shot)
                else:
                    x, y = v; c = s.coll(s.pos()[:2])(x, y)
                    d = {0x70: 'D', 0x76: 'L', 0x78: 'U', 0x7E: 'R'}.get(c, 'U')
                    s.door(x, y, d, shot)
                s.g.wait(30); s.advance(shot)
                if s.pos()[:2] != m: break
            if s.pos()[:2] == dest: return True
        return s.pos()[:2] == dest
    # ---- 手持ち
    def party(s):
        n = s.rd(0xD9E8)[0] if False else None
        out = []
        for i in range(6):
            b = s.rd(0xD9F0 + 0x30 * i, 0x30)
            if not b[0] or b[0] == 0xFF: break
            out.append(dict(sp=b[0], lv=b[0x1F], hp=b[0x22] << 8 | b[0x23], mx=b[0x24] << 8 | b[0x25]))
        return out
    def heal(s, center, shot=None):
        """center（ポケモンセンターの マップ）へ 行って 回復"""
        if not s.travel(center, shot): return False
        nurse = [o for o in s.objs()][0]
        s.talk_to(nurse[0], nurse[1], shot)
        for _ in range(6): s.advance(shot); s.g.wait(20)
        return True
    def grass(s):
        mid = s.pos()[:2]; c = s.coll(mid); r = s.reach()
        return [p for p in r if c(*p) in (0x14, 0x18)]
    def grind(s, center, lv, shot=None, maxb=200, hp_min=0.4):
        """草むらで 戦って 先頭を lv まで。HP が へったら center で 回復"""
        home = s.pos()[:2]; b = 0
        while b < maxb:
            p = s.party()
            if p[0]['lv'] >= lv: return True
            if p[0]['hp'] < p[0]['mx'] * hp_min:
                s.heal(center, shot); s.travel(home, shot); continue
            gr = s.grass()
            if not gr: s.log.append('草むらが ない'); return False
            _, _, x, y = s.pos()
            if (x, y) not in gr: s.goto_safe(*min(gr, key=lambda q: abs(q[0] - x) + abs(q[1] - y)), shot=shot)
            for d in 'UDLR':
                _, _, x, y = s.pos(); dx, dy = DIRS[d]
                if (x + dx, y + dy) in gr:
                    s.step(d)
                    if s.in_battle():
                        b += 1; s.fight(run=False, shot=shot); s.advance(shot)
                    break
            if s.pos()[:2] != home: s.travel(home, shot)
        return False
