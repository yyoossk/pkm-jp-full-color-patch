"""移植版を 歩いて 進める ための 道具（ワープ・メモリの 書きかえ なし）。
   W(g).goto(x, y) で 今の マップの 中を 歩く（当たりは ROM の マップから、ふさがれたら 道を さがしなおす）"""
import sys, collections
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
        return c
    def npcs(s):
        out = set()
        for i in range(1, 13):
            b = s.rd(s.PS + OSZ * i, 0x14)
            if b[0] and b[0x10] >= 4 and b[0x11] >= 4: out.add((b[0x10] - 4, b[0x11] - 4))
        return out
    def passable(s, c, frm, d):
        if c is None: return False
        pm = s.rom[s.CP + c] & 0x0F
        if 0xA0 <= c <= 0xA7:                         # 段差：その 向きだけ
            return {0xA0: 'R', 0xA1: 'L', 0xA2: 'U', 0xA3: 'D', 0xA4: 'D', 0xA5: 'D', 0xA6: 'U', 0xA7: 'U'}.get(c) == d
        return pm == 0
    def path(s, tx, ty, avoid=()):
        gi, mi, x, y = s.pos(); c = s.coll((gi, mi)); blocked = set(avoid) | s.npcs()
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
        s.g.up(d); s.g.wait(10)
        return s.pos() != before
    def goto(s, tx, ty, tries=8):
        for _ in range(tries):
            gi, mi, x, y = s.pos()
            if (x, y) == (tx, ty): return True
            p = s.path(tx, ty)
            if p is None: s.log.append('道が ない %s → %s' % ((gi, mi, x, y), (tx, ty))); return False
            for d in p:
                if not s.step(d):
                    s.g.press('B', 4, 20); break
                if s.pos()[:2] != (gi, mi): return True        # マップが かわった（入口・つながり）
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
            if s.in_battle(): s.battle(shot); continue
            if s.textbox():
                if shot: shot('文')
                s.g.press('A', 4, 40); continue
            s.g.wait(30)
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
    def leave(s, d, shot=None, tries=4):
        """マップの はしから d の 向きへ 出る（つながり）。戦い・文は すすめる"""
        for _ in range(tries):
            mid = s.pos()[:2]; m = s.maps[mid]; W2, H2 = m['w'] * 2, m['h'] * 2
            edge = [p for p in s.reach() if (d == 'U' and p[1] == 0) or (d == 'D' and p[1] == H2 - 1) or
                    (d == 'L' and p[0] == 0) or (d == 'R' and p[0] == W2 - 1)]
            if not edge: s.log.append('はしが ない %s %s' % (mid, d)); return False
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
    def objs(s):
        a = s.maps[s.pos()[:2]]['attr']; return [(o[2] - 4, o[1] - 4, o[0]) for o in a['objs']]
    def talk_to(s, ox, oy, shot=None, counter=True):
        """(ox, oy) の 人に となりから 話しかける（カウンターごしも ためす）"""
        cand = []
        for d, (dx, dy) in DIRS.items():
            for k in ((1, 2) if counter else (1,)):
                cand.append(((ox - dx * k, oy - dy * k), d))
        r = s.reach(); _, _, x, y = s.pos()
        cand = [c for c in cand if c[0] in r]; cand.sort(key=lambda c: abs(c[0][0] - x) + abs(c[0][1] - y))
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
