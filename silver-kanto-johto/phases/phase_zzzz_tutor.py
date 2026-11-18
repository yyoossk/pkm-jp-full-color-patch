"""カントーの ジムの 案内の 人が、赤の ジムリーダーが くれた わざマシンの わざ（この 版では わざマシンに ない もの）を 教える。

   赤の わざマシン → この 版で ジムリーダーが くれる もの（そのまま）：
     ニビ   がまん(34)        → いばる      ハナダ  バブルこうせん(11) → にほんばれ
     クチバ 10まんボルト(24)  → りゅうのいぶき タマムシ メガドレイン(21) → やつあたり
     ヤマブキ サイコウェーブ(46) → どろぼう  トキワ  じわれ(27)        → （なし）
   （セキチクの どくどく・グレンの だいもんじは 同じ わざ なので 教えない）

   ・ジムリーダーに 勝って（バッジ）、出口の 前の マスに 来ると 1回だけ 案内の 人が 呼び止めて 近づき、教えて くれる。
     しるしは $D782（イベントフラグ $BA8〜$BAD）。出口の 前の マスは coord_event（シーン -1）。
   ・案内の 人に 話しかけると、バッジが あれば 何度でも 教えて くれる（なければ 元の ことば）。
   ・タマムシジムには 案内の 人が いない ので (15,7) に 足す。
   ・おぼえられる ポケモン：赤の わざマシン・クリスタルの 技教え（10まんボルト）・クリスタルの レベル／タマゴわざ。
     第2世代で 足された 進化（ハガネール など）と ベイビィ（ピチュー など）は 赤の なかまに 合わせる。
   ・教える 処理は キットの 技教えの 人（src/movetutor_silver.asm の MoveTutor_Teach）と 同じ。
   ・ジムの スクリプトの バンクを 写し（ジムごとに 1つ）、イベントの 表を 作りなおして その 写しの 空きに 置く。
   本体 $FC:$4000〜。写し $F4〜$F9。"""
import os, sys, re, collections
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import asmpatch, cscript
from gsc import fo, r16

CODE_BANK = 0xFC
CALLED = 0xBA8            # $D782 ビット0〜5
MOVES = ['BIDE', 'BUBBLEBEAM', 'THUNDERBOLT', 'MEGA_DRAIN', 'PSYWAVE', 'FISSURE']
# (グループ, マップ, バッジの エンジンフラグ, わざ, 写しの バンク, 足す 案内の 人の 位置)
GYMS = [
    (14, 4, 0x22, 0, 0xF4, None),        # ニビ
    (7, 6, 0x23, 1, 0xF5, None),         # ハナダ
    (12, 11, 0x24, 2, 0xF6, None),       # クチバ
    (21, 21, 0x25, 3, 0xF7, (15, 7)),    # タマムシ（案内の 人を 足す）
    (25, 4, 0x27, 4, 0xF8, None),        # ヤマブキ
    (23, 4, 0x29, 5, 0xF9, None),        # トキワ
]
GUIDE_SPRITE = 72
PASS = {0x00, 0x01, 0x03, 0x04, 0x10, 0x12, 0x14, 0x18, 0x1c, 0x48, 0x49, 0x4a, 0x4b, 0x4c}
KIT = os.path.join(H, 'build', 'kit')


# ---------------- おぼえられる ポケモンの 表
def compat_tables():
    R = '/home/claude/ref'
    N = []
    for l in open(R + '/pokecrystal/constants/pokemon_constants.asm'):
        m = re.match(r'\s*const (\w+)', l)
        if m and len(N) < 251: N.append(m.group(1))
    norm = lambda x: x.lower().replace('_', '')

    def file_for(base, name):
        for c in os.listdir(base):
            if c[:-4].replace('_', '') == norm(name): return os.path.join(base, c)
        raise Exception(name)

    def tmhm(path):
        s = open(path).read(); m = re.search(r'tmhm(.*?)(\n\s*;|\n\s*db|\Z)', s, re.S)
        return set(re.findall(r'[A-Z_]+', m.group(1).replace('\\', '')))

    learn = {mv: set() for mv in MOVES}; red = {mv: set() for mv in MOVES}
    for i, n in enumerate(N):
        if i < 151:
            t = tmhm(file_for(R + '/pokered/data/pokemon/base_stats', n))
            for mv in MOVES:
                if mv in t: learn[mv].add(i + 1); red[mv].add(i + 1)
        t = tmhm(file_for(R + '/pokecrystal/data/pokemon/base_stats', n))
        for mv in MOVES:
            if mv in t: learn[mv].add(i + 1)

    def blocks(path, suf):
        cur = None; out = {}
        for l in open(path):
            m = re.match(r'(\w+)' + suf + r':', l)
            if m: cur = norm(m.group(1)); out[cur] = set(); continue
            if cur: out[cur] |= set(re.findall(r'\b([A-Z][A-Z_]+)\b', l.split(';')[0]))
        return out
    ev = blocks(R + '/pokecrystal/data/pokemon/evos_attacks.asm', 'EvosAttacks')
    eg = blocks(R + '/pokecrystal/data/pokemon/egg_moves.asm', 'EggMoves')
    for i, n in enumerate(N):
        s = ev.get(norm(n), set()) | eg.get(norm(n), set())
        for mv in MOVES:
            if mv in s: learn[mv].add(i + 1)
    idx = {norm(n): i + 1 for i, n in enumerate(N)}; evo = {}; cur = None
    for l in open(R + '/pokecrystal/data/pokemon/evos_attacks.asm'):
        m = re.match(r'(\w+)EvosAttacks:', l)
        if m: cur = idx.get(norm(m.group(1))); continue
        m = re.match(r'\s*db EVOLVE_\w+,.*?(\w+)\s*$', l.split(';')[0].rstrip())
        if m and cur:
            t = idx.get(norm(m.group(1)))
            if t: evo.setdefault(cur, set()).add(t)
    for mv in MOVES:
        for a, bs in evo.items():
            for b in bs:
                if a in red[mv] and b > 151: learn[mv].add(b)
                if b in red[mv] and a > 151: learn[mv].add(a)
    out = b''
    for mv in MOVES:
        t = bytearray(32)
        for sp in learn[mv]: t[(sp - 1) // 8] |= 1 << ((sp - 1) % 8)
        out += bytes(t)
    return out, {mv: len(learn[mv]) for mv in MOVES}


# ---------------- マップ
def header(rom, G, M):
    gt = fo(0x25, 0x40ED); hp = fo(0x25, r16(rom, gt + 2 * (G - 1))) + 9 * (M - 1)
    h = rom[hp:hp + 9]; ao = fo(h[0], r16(h, 3))
    return h, ao


def grid(rom, G, M):
    h, ao = header(rom, G, M); ts = h[1]
    Hh, W = rom[ao + 1], rom[ao + 2]; bb, bp = rom[ao + 3], r16(rom, ao + 4)
    blocks = rom[fo(bb, bp):fo(bb, bp) + W * Hh]
    te = fo(0xE1, 0x4000) + 15 * ts; coll = rom[fo(rom[te + 6], r16(rom, te + 7)):]
    out = [[0x07] * (2 * W) for _ in range(2 * Hh)]
    for y in range(Hh):
        for x in range(W):
            c = coll[4 * blocks[y * W + x]:4 * blocks[y * W + x] + 4]
            out[2 * y][2 * x], out[2 * y][2 * x + 1], out[2 * y + 1][2 * x], out[2 * y + 1][2 * x + 1] = c
    return out


def read_events(rom, b, ep):
    o = fo(b, ep); s = o; ev = {'pre': bytes(rom[o:o + 2])}; o += 2
    n = rom[o]; o += 1; ev['warps'] = [bytes(rom[o + 5 * i:o + 5 * i + 5]) for i in range(n)]; o += 5 * n
    n = rom[o]; o += 1; ev['coords'] = [bytes(rom[o + 8 * i:o + 8 * i + 8]) for i in range(n)]; o += 8 * n
    n = rom[o]; o += 1; ev['bgs'] = [bytes(rom[o + 5 * i:o + 5 * i + 5]) for i in range(n)]; o += 5 * n
    n = rom[o]; o += 1; ev['objects'] = [bytes(rom[o + 13 * i:o + 13 * i + 13]) for i in range(n)]; o += 13 * n
    ev['range'] = (s, o)
    return ev


def build_events(ev):
    d = bytearray(ev['pre'])
    for k in ('warps', 'coords', 'bgs', 'objects'):
        d.append(len(ev[k]))
        for e in ev[k]: d += e
    return bytes(d)


# ---------------- 写しの バンクの 中で 使って いる 所（空きを さがす ため）
def text_extent(rom, b, a):
    o = fo(b, a); end = fo(b, 0x8000)
    while o < end:
        c = rom[o]; o += 1
        if c == 0x00:
            while o < end:
                ch = rom[o]; o += 1
                if ch == 0x50: break
                if ch in (0x57, 0x58): return o
        elif c == 0x01 or c == 0x03: o += 2
        elif c == 0x02: o += 3
        elif c == 0x04: o += 4
        elif c == 0x09: o += 3
        elif c == 0x0c or c == 0x14: o += 1
        elif c == 0x16: o += 3
        elif c == 0x50: return o
        elif c in (0x05, 0x06, 0x07, 0x0a, 0x0b, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x15): pass
        else: return o + 0x40          # text_asm など：多めに
    return end


def used_ranges(rom, b, sp, ev):
    used = []
    def mark(o, e): used.append((o, e))
    # マップの スクリプトの 見出し
    o = fo(b, sp); s = o; n = rom[o]; o += 1; scenes = []
    for i in range(n): scenes.append(r16(rom, o)); o += 4
    n = rom[o]; o += 1; cbs = []
    for i in range(n): cbs.append(r16(rom, o + 1)); o += 3
    mark(s, o); mark(*ev['range'])
    starts = list(scenes) + cbs
    for c in ev['coords']: starts.append(c[4] | c[5] << 8)
    for g in ev['bgs']:
        p = g[3] | g[4] << 8; f = g[2]
        if f <= 4: starts.append(p)
        elif f in (5, 6): mark(fo(b, p), fo(b, p) + 4); starts.append(r16(rom, fo(b, p) + 2))
        else: mark(fo(b, p), fo(b, p) + 8)
    texts = []
    for obj in ev['objects']:
        typ = obj[7] & 0x0f; p = obj[9] | obj[10] << 8
        if not p or not (0x4000 <= p < 0x8000): continue
        if typ == 0: starts.append(p)
        elif typ == 2:
            o = fo(b, p); mark(o, o + 12)
            texts += [r16(rom, o + 4), r16(rom, o + 6), r16(rom, o + 8)]; starts.append(r16(rom, o + 10))
        else: mark(fo(b, p), fo(b, p) + 16)            # 1 = どうぐ など
    seen, refs = set(), {}
    for a in starts:
        if 0x4000 <= a < 0x8000: cscript.walk(rom, b, a, seen, refs)
    assert not refs.get('bad'), refs.get('bad')
    for (bb, a) in seen:
        if bb != b: continue
        op, name, args, ln, end = cscript.decode(rom, bb, a); mark(fo(bb, a), fo(bb, a) + ln)
    for f, items in refs.items():
        for (v, p, bb) in items:
            if bb != b or not isinstance(v, int): continue
            if f == 't': texts.append(v)
            elif f == 'm':
                o = fo(b, v); e = o
                while rom[e] != 0x47 and e < o + 64: e += 1
                mark(o, e + 1)
            elif f in ('R', 'U', 'N'): mark(fo(b, v), fo(b, v) + 48)
    for t in texts:
        if 0x4000 <= t < 0x8000: mark(fo(b, t), text_extent(rom, b, t))
    return used


def find_gap(used, b, need):
    lo, hi = fo(b, 0x4000), fo(b, 0x8000)
    occ = bytearray(hi - lo)
    for s, e in used:
        for i in range(max(s - 8, lo), min(e + 8, hi)): occ[i - lo] = 1
    run = 0
    for i in range(len(occ)):
        run = run + 1 if not occ[i] else 0
        if run >= need: return lo + i - need + 1 + 0     # 先頭
    raise Exception('空きが ない %02X' % b)


# ---------------- 近づく 動き
def approach(cg, objs, guide, t):
    """guide から t の となりへ（横を さきに）。戻り値 (動きの 列, 最後に 向く 向き)"""
    Hh, W = len(cg), len(cg[0])
    D = {'D': (1, 0), 'U': (-1, 0), 'L': (0, -1), 'R': (0, 1)}
    goals = [(t[0], t[1] - 1), (t[0], t[1] + 1), (t[0] + 1, t[1]), (t[0] - 1, t[1])]
    best = None
    for gi, gl in enumerate(goals):
        if not (0 <= gl[0] < Hh and 0 <= gl[1] < W) or cg[gl[0]][gl[1]] not in PASS: continue
        prev = {guide: None}; q = collections.deque([guide])
        while q:
            c = q.popleft()
            if c == gl: break
            for k, (dy, dx) in D.items():
                n = (c[0] + dy, c[1] + dx)
                if n in prev or n == t or n in objs: continue
                if 0 <= n[0] < Hh and 0 <= n[1] < W and (cg[n[0]][n[1]] in PASS or n == gl):
                    prev[n] = (c, k); q.append(n)
        if gl not in prev: continue
        path = []; c = gl
        while prev[c]: c, k = prev[c]; path.append(k)
        path = path[::-1]
        cost = len(path) + (3 if gi == 3 else 0)      # 上（連れ歩きの いる 所）は さいごに
        if best is None or cost < best[0]: best = (cost, path, gl)
    assert best, ('近づけない', guide, t)
    _, path, gl = best
    face = 'R' if gl[1] < t[1] else 'L' if gl[1] > t[1] else 'U' if gl[0] > t[0] else 'D'
    return path, face


DIRN = {'D': 'DOWN', 'U': 'UP', 'L': 'LEFT', 'R': 'RIGHT'}


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    assert not any(rom[fo(CODE_BANK, 0x4000):fo(CODE_BANK, 0x8000)])
    tables, counts = compat_tables()
    gyms = []
    for gi, (G, M, badge, mv, nb, addpos) in enumerate(GYMS):
        assert not any(rom[fo(nb, 0x4000):fo(nb, 0x8000)])
        h, ao = header(rom, G, M); b = rom[ao + 6]; sp = r16(rom, ao + 7); ep = r16(rom, ao + 9)
        ev = read_events(rom, b, ep); cg = grid(rom, G, M)
        objs = [(o[1] - 4, o[2] - 4) for o in ev['objects']]
        gidx = [i for i, o in enumerate(ev['objects']) if o[0] == GUIDE_SPRITE]
        if addpos:
            assert not gidx
            _, va = header(rom, 12, 11)
            tmpl = [o for o in read_events(rom, rom[va + 6], r16(rom, va + 9))['objects'] if o[0] == GUIDE_SPRITE][0]
            new = bytearray(tmpl); new[1] = addpos[0] + 4; new[2] = addpos[1] + 4; new[9] = new[10] = 0
            ev['objects'].append(bytes(new)); gidx = [len(ev['objects']) - 1]; orig = None
        else:
            assert len(gidx) == 1
            o = ev['objects'][gidx[0]]; p = o[9] | o[10] << 8
            # 元の 案内の 人の スクリプト（farsjump なら その 先）
            q = fo(b, p)
            orig = (rom[q + 1], r16(rom, q + 2)) if rom[q] == 0x04 else (b, p)
        gpos = (ev['objects'][gidx[0]][1] - 4, ev['objects'][gidx[0]][2] - 4)
        gid = gidx[0] + 2
        trig = []
        for w in ev['warps']:
            y, x = w[0], w[1]
            if (w[3], w[4]) != (G, M) and y == len(cg) - 1 and cg[y - 1][x] in PASS: trig.append((y - 1, x))
        assert trig, (G, M)
        mvs = [approach(cg, set(objs) - {gpos}, gpos, t) for t in trig]
        gyms.append(dict(G=G, M=M, badge=badge, mv=mv, nb=nb, b=b, sp=sp, ep=ep, ev=ev, ao=ao, gid=gid,
                         gidx=gidx[0], orig=orig, trig=trig, mvs=mvs, gpos=gpos))

    # ---- 本体（アセンブリ）
    src = ['INCLUDE "includes.asm"', 'INCLUDE "src/jp_all_silver.inc"', 'INCLUDE "src/charmap_jp.inc"',
           'DEF KT_LEARNMOVE EQU $67ae', 'DEF KT_LEARNMOVE_BANK EQU $01', 'DEF KT_KNOWSMOVE EQU $7f70',
           'DEF KT_KNOWSMOVE_BANK EQU $03', 'DEF KT_SELECTMON EQU $4000', 'DEF KT_SELECTMON_BANK EQU $14',
           'DEF wKTWhich EQU wBufferMon + 32',
           'SECTION "kt table", ROMX[$4000], BANK[$%02X]' % CODE_BANK]
    for gi, gy in enumerate(gyms):
        src.append('\tdw KT_Guide_%d' % gi)
        for k in range(len(gy['trig'])): src.append('\tdw KT_Call_%d_%d' % (gi, k))
    src.append('SECTION "kt", ROMX[$4100], BANK[$%02X]' % CODE_BANK)
    src.append(open(os.path.join(H, 'src', 'kantotutor.inc'), encoding='utf-8').read())
    for gi, gy in enumerate(gyms):
        fl = CALLED + gi
        src.append('KT_Guide_%d:' % gi)
        src.append('\tdb checkflag_command\n\tdw $%04X' % gy['badge'])
        src.append('\tiffalse .orig')
        src.append('\tfaceplayer\n\topentext\n\tsetval %d\n\tsjump KT_Offer' % gy['mv'])
        if gy['orig']:
            src.append('.orig\n\tdb farsjump_command\n\tdb $%02X\n\tdw $%04X' % gy['orig'])
        else:
            src.append('.orig\n\tjumptextfaceplayer KT_CeladonGuideText')
        for k, (path, face) in enumerate(gy['mvs']):
            src.append('KT_Call_%d_%d:' % (gi, k))
            src.append('\tdb checkflag_command\n\tdw $%04X\n\tiffalse .end' % gy['badge'])
            src.append('\tdb checkevent_command\n\tdw $%04X\n\tiftrue .end' % fl)
            src.append('\tdb setevent_command\n\tdw $%04X' % fl)
            src.append('\tshowemote EMOTE_SHOCK, %d, 15' % gy['gid'])
            src.append('\topentext\n\twritetext KT_WaitText\n\twaitbutton\n\tclosetext')
            if path: src.append('\tapplymovement %d, .move\n\twriteobjectxy %d' % (gy['gid'], gy['gid']))
            src.append('\tturnobject %d, %s' % (gy['gid'], DIRN[face]))
            src.append('\tfaceobject PLAYER, %d' % gy['gid'])
            src.append('\topentext\n\twritetext KT_IntroText\n\tpromptbutton\n\tsetval %d\n\tsjump KT_Offer' % gy['mv'])
            src.append('.end\n\tend')
            if path:
                src.append('.move\n' + '\n'.join('\tstep %s' % DIRN[c] for c in path) + '\n\tstep_end')
    src.append('KT_Compat:')
    for i in range(0, len(tables), 16): src.append('\tdb ' + ', '.join('$%02X' % x for x in tables[i:i + 16]))
    asmpatch.overlay(rom, '\n'.join(src) + '\n', inc=[os.path.join(KIT, 'pokegold'), KIT], cwd=KIT)

    # ---- ジムごとの 写しと イベントの 表
    t = fo(CODE_BANK, 0x4000)
    for gi, gy in enumerate(gyms):
        b, nb, ev = gy['b'], gy['nb'], gy['ev']
        guide_a = r16(rom, t); t += 2
        call_a = []
        for k in range(len(gy['trig'])): call_a.append(r16(rom, t)); t += 2
        rom[fo(nb, 0x4000):fo(nb, 0x8000)] = rom[fo(b, 0x4000):fo(b, 0x8000)]
        used = [(s0 + (nb - b) * 0x4000, e0 + (nb - b) * 0x4000) for s0, e0 in used_ranges(rom, b, gy['sp'], ev)]
        stubs = 4 * (1 + len(call_a))
        size = len(build_events(ev)) + 8 * len(call_a) + stubs
        o = find_gap(used, nb, size + 16) + 8
        a = 0x4000 + o - fo(nb, 0x4000)
        st = a; code = bytearray()
        code += bytes([0x04, CODE_BANK, guide_a & 0xFF, guide_a >> 8])
        for ca in call_a: code += bytes([0x04, CODE_BANK, ca & 0xFF, ca >> 8])
        # 案内の 人の スクリプト → 写しの スタブ
        obj = bytearray(ev['objects'][gy['gidx']]); obj[9] = st & 0xFF; obj[10] = st >> 8
        ev['objects'][gy['gidx']] = bytes(obj)
        for k, (y, x) in enumerate(gy['trig']):
            sa = st + 4 * (k + 1)
            ev['coords'].append(bytes([0xFF, y, x, 0, sa & 0xFF, sa >> 8, 0, 0]))
        evd = build_events(ev); ea = st + len(code)
        rom[o:o + len(code)] = code; rom[o + len(code):o + len(code) + len(evd)] = evd
        assert len(code) + len(evd) <= size
        rom[gy['ao'] + 6] = nb; rom[gy['ao'] + 9] = ea & 0xFF; rom[gy['ao'] + 10] = ea >> 8
        log.append('%d:%d %s → 写し $%02X（イベント $%04X）案内 %d番 %s 出口の 前 %s' % (
            gy['G'], gy['M'], MOVES[gy['mv']], nb, ea, gy['gid'], gy['gpos'], gy['trig']))
    log.append('おぼえられる 数 %s' % counts)
    return rom
