"""赤の わざマシンの わざを 教える（クリスタル版 第122弾の キット「赤のわざマシンのわざを教える_キット」を 銀へ）。

   カントーで もらう わざマシンは そのまま（金銀の わざマシン）。赤の わざマシンの わざで 金銀の わざマシンに ない ものを、
   人が 何度でも 教える。覚えられる ポケモンは 赤の わざマシンの 表（data/red_tm_learners.txt）と 同じ。

   ・ジム（ニビ がまん・ハナダ バブルこうせん・クチバ 10まんボルト・タマムシ メガドレイン・ヤマブキ サイコウェーブ・トキワ じわれ）：
     バッジの あと 入口の 扉の 1つ上の マス（coord_event シーン $FF）で 1回だけ「<PLAYER>！ ちょっと まって！」→
     案内の 人が 歩いて きて 向き合い、教えて、もとの 場所へ もどる。そのあとも 話しかければ 教える（バッジ前は 元の ことば）。
     「！」（showemote）は 連れ歩きの 絵を こわすので 使わない。しるし $D782 ビット0〜5（フラグ $BA8〜$BAD）。
     タマムシジムは 案内の 人を (15,7) に 足し、エリカに 勝つまで かくす（$BAE。MAPCALLBACK_OBJECTS）。
     ジムの スクリプトの バンクを $F4〜$F9 に 写し、見出し・イベントの 表を 作りなおして 写しの 空きに 置く。
   ・ジム以外（わざマシンを もらった あと その人が 教える）：タマムシの おじいさん タマゴうみ・シルフ2F じばく・
     グレンの 研究所 ゆびをふる・デパート3F カウンター・ものまねむすめ ものまね・屋上の 女の子 れいとうビーム／いわなだれ／
     トライアタック（もらった 分だけ）。もとの スクリプトの はじめ 4バイトを farsjump に。
   ・わざ教えの 本体：クリスタルの MoveTutor・CheckCanLearnMoveTutorMove を 移した もの（callasm。wScriptVar ＝ わざ番号、
     教えたら 0・やめたら $FF）。predef CanLearnTMHMMove（表 $02:$4B85）を 包んで、wScriptVar と わざが 同じ ときだけ
     赤の 表で 答える（わざマシンを 使う ときは もとのまま）。本体 $FC:$4000〜。"""
import os, sys, re, collections
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import asmpatch, cscript
from gsc import fo, r16

CODE_BANK = 0xFC
CALLED = 0xBA8            # $D782 ビット0〜5（ジムごとの 呼び止めた しるし）
CELADON_HIDE = 0xBAE      # タマムシの 案内の 人を かくす
PREDEF_CANLEARN = 0x8B85  # predef の 表の CanLearnTMHMMove（$04:$59BF）
GUIDE_SPRITE = 72
PASS = {0x00, 0x01, 0x03, 0x04, 0x10, 0x12, 0x14, 0x18, 0x1c, 0x48, 0x49, 0x4a, 0x4b, 0x4c}
KIT = os.path.join(H, 'build', 'kit')
# (グループ, マップ, リーダー, バッジの エンジンフラグ, わざ, わざの 名前, 写しの バンク, 足す 案内の 人)
GYMS = [
    (14, 4, 'タケシ', 0x22, 'BIDE', 'がまん', 0xF4, None),
    (7, 6, 'カスミ', 0x23, 'BUBBLEBEAM', 'バブルこうせん', 0xF5, None),
    (12, 11, 'マチス', 0x24, 'THUNDERBOLT', '10まんボルト', 0xF6, None),
    (21, 21, 'エリカ', 0x25, 'MEGA_DRAIN', 'メガドレイン', 0xF7, (15, 7)),
    (25, 4, 'ナツメ', 0x27, 'PSYWAVE', 'サイコウェーブ', 0xF8, None),
    (23, 4, 'サカキ', 0x29, 'FISSURE', 'じわれ', 0xF9, None),
]
# ジム以外：(もとの スクリプトの バンク, 場所), [(わざマシンを もらった フラグ, わざ, 名前)]
NPCS = [
    ((0x69, 0x6448), [(0x9C4, 'SOFTBOILED', 'タマゴうみ')]),             # タマムシシティの おじいさん
    ((0x7A, 0x570C), [(0xC66, 'SELFDESTRUCT', 'じばく')]),               # シルフカンパニー 2F
    ((0x63, 0x41EF), [(0x849, 'METRONOME', 'ゆびをふる')]),              # グレンの 研究所
    ((0x68, 0x6812), [(0x9C8, 'COUNTER', 'カウンター')]),                # デパート 3F
    ((0xD9, 0x6A59), [(0x9DA, 'MIMIC', 'ものまね')]),                    # ものまねむすめ
    ((0x68, 0x6890), [(0x9C9, 'ICE_BEAM', 'れいとうビーム'), (0x9CA, 'ROCK_SLIDE', 'いわなだれ'),
                      (0x9CB, 'TRI_ATTACK', 'トライアタック')]),             # デパート 屋上の 女の子
]
DV = {'D': (1, 0), 'U': (-1, 0), 'L': (0, -1), 'R': (0, 1)}
OPP = {'D': 'U', 'U': 'D', 'L': 'R', 'R': 'L'}
DIRN = {'D': 'DOWN', 'U': 'UP', 'L': 'LEFT', 'R': 'RIGHT'}


def red_learners():
    out = {}
    lines = open(os.path.join(H, 'data', 'red_tm_learners.txt'), encoding='utf-8').read().split('\n')
    for i, l in enumerate(lines):
        m = re.search(r'（([A-Z_]+)、', l)
        if m: out[m.group(1)] = [int(x) for x in lines[i + 1].split()]
    return out


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


def read_mapscripts(rom, b, sp):
    o = fo(b, sp); s = o; n = rom[o]; o += 1; scenes = []
    for i in range(n): scenes.append(bytes(rom[o:o + 4])); o += 4
    n = rom[o]; o += 1; cbs = []
    for i in range(n): cbs.append(bytes(rom[o:o + 3])); o += 3
    return scenes, cbs, (s, o)


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
        else: return o + 0x40
    return end


def used_ranges(rom, b, sp, ev):
    used = []
    def mark(o, e): used.append((o, e))
    scenes, cbs, rng = read_mapscripts(rom, b, sp)
    mark(*rng); mark(*ev['range'])
    starts = [r16(s, 0) for s in scenes] + [r16(c, 1) for c in cbs]
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
        else: mark(fo(b, p), fo(b, p) + 16)
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
        if run >= need: return lo + i - need + 1
    raise Exception('空きが ない %02X' % b)


def bfs(cg, block, start, goals):
    Hh, W = len(cg), len(cg[0])
    q = collections.deque([start]); prev = {start: None}
    while q:
        p = q.popleft()
        if p in goals:
            goal = p; out = []
            while prev[p]: d, p = prev[p]; out.append(d)
            return out[::-1], goal
        for d, (dy, dx) in DV.items():
            n = (p[0] + dy, p[1] + dx)
            if n in prev or not (0 <= n[0] < Hh and 0 <= n[1] < W): continue
            if cg[n[0]][n[1]] not in PASS or n in block: continue
            prev[n] = (d, p); q.append(n)
    return None, None


def _end(start, path):
    y, x = start
    for d in path: y += DV[d][0]; x += DV[d][1]
    return (y, x)


def txt(s):
    """文を rgbasm の db に（<P>＝名前 $52・<L>＝$4F・<PARA>＝$51・<CONT>＝$55、さいごに $57）"""
    out = []
    for p in re.split(r'(<P>|<L>|<PARA>|<CONT>)', s):
        if not p: continue
        out.append({'<P>': '$52', '<L>': '$4f', '<PARA>': '$51', '<CONT>': '$55'}.get(p, '"%s"' % p))
    return '\tdb $00, ' + ', '.join(out) + ', $57'


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    assert not any(rom[fo(CODE_BANK, 0x4000):fo(CODE_BANK, 0x8000)])
    assert rom[PREDEF_CANLEARN:PREDEF_CANLEARN + 3] == bytes([0xBF, 0x59, 0x04])
    learners = red_learners()
    gyms = []
    for gi, (G, M, leader, badge, mv, mname, nb, addpos) in enumerate(GYMS):
        assert not any(rom[fo(nb, 0x4000):fo(nb, 0x8000)])
        h, ao = header(rom, G, M); b = rom[ao + 6]; sp = r16(rom, ao + 7); ep = r16(rom, ao + 9)
        ev = read_events(rom, b, ep); cg = grid(rom, G, M)
        scenes, cbs, _ = read_mapscripts(rom, b, sp)
        gidx = [i for i, o in enumerate(ev['objects']) if o[0] == GUIDE_SPRITE]
        orig = None
        if addpos:
            assert not gidx
            _, va = header(rom, 12, 11)
            tmpl = [o for o in read_events(rom, rom[va + 6], r16(rom, va + 9))['objects'] if o[0] == GUIDE_SPRITE][0]
            new = bytearray(tmpl); new[1] = addpos[0] + 4; new[2] = addpos[1] + 4; new[9] = new[10] = 0
            new[11] = CELADON_HIDE & 0xFF; new[12] = CELADON_HIDE >> 8
            ev['objects'].append(bytes(new)); gidx = [len(ev['objects']) - 1]
        else:
            assert len(gidx) == 1
            o = ev['objects'][gidx[0]]; p = o[9] | o[10] << 8; q = fo(b, p)
            orig = (rom[q + 1], r16(rom, q + 2)) if rom[q] == 0x04 else (b, p)
        gpos = (ev['objects'][gidx[0]][1] - 4, ev['objects'][gidx[0]][2] - 4)
        gid = gidx[0] + 2                                   # wMapObjects の 1番は 連れ歩き
        block = {(o[1] - 4, o[2] - 4) for o in ev['objects']} - {gpos}
        doors = [(w[0], w[1]) for w in ev['warps']][:2]
        legs = []
        for (dy, dx) in doors:
            t = (dy - 1, dx); assert cg[t[0]][t[1]] in PASS, (G, M, t)
            goals = {}
            for d, (ddy, ddx) in DV.items():
                if d == 'D': continue                          # 扉の 上は さける
                g = (t[0] + ddy, t[1] + ddx)
                if 0 <= g[0] < len(cg) and 0 <= g[1] < len(cg[0]) and cg[g[0]][g[1]] in PASS and g not in block:
                    goals[g] = OPP[d]                          # 案内の 人の 向き（プレイヤーの ほう）
            pth, end = bfs(cg, block | {t}, gpos, set(goals))
            assert pth is not None, (G, M, gpos, t)
            legs.append((t, pth, goals[end]))
        gyms.append(dict(G=G, M=M, leader=leader, badge=badge, mv=mv, mname=mname, nb=nb, b=b, sp=sp, ev=ev,
                         ao=ao, gid=gid, gidx=gidx[0], orig=orig, legs=legs, gpos=gpos, scenes=scenes, cbs=cbs,
                         addpos=addpos))

    # ---- 本体（アセンブリ）
    S = ['INCLUDE "includes.asm"', 'INCLUDE "src/jp_all_silver.inc"', 'INCLUDE "src/charmap_jp.inc"',
         'SECTION "kt table", ROMX[$4000], BANK[$%02X]' % CODE_BANK, '\tdw KT_Wrap']
    for gi, gy in enumerate(gyms):
        S.append('\tdw KT_Guide_%d' % gi)
        for k in range(len(gy['legs'])): S.append('\tdw KT_Leave_%d_%d' % (gi, k))
        if gy['addpos']: S.append('\tdw KT_CeladonCallback')
    for ni in range(len(NPCS)): S.append('\tdw KT_Npc_%d' % ni)
    S.append('SECTION "kt", ROMX[$4100], BANK[$%02X]' % CODE_BANK)
    S.append(open(os.path.join(H, 'src', 'kantotutor.inc'), encoding='utf-8').read())
    allmv = [g[4] for g in GYMS] + [m for _, t in NPCS for _, m, _ in t]
    S.append('KT_RedTable:')
    for k, m in enumerate(allmv): S.append('\tdb %s\n\tdw KT_RedList_%d' % (m, k))
    S.append('\tdb 0')
    for k, m in enumerate(allmv):
        S.append('KT_RedList_%d:\n\tdb %s, $ff' % (k, ', '.join(str(x) for x in learners[m])))
    # ジム
    for gi, gy in enumerate(gyms):
        fl = CALLED + gi; G = 'KT_G%d_' % gi
        S.append('%steach:' % G)
        S.append('\tyesorno\n\tiffalse .no\n\tsetval %s\n\tcallasm KT_MoveTutor\n\tifequal 0, .ok' % gy['mv'])
        S.append('.no\n\twritetext %sno\n\twaitbutton\n\tclosetext\n\tend' % G)
        S.append('.ok\n\twritetext %sok\n\twaitbutton\n\tclosetext\n\tend' % G)
        S.append('KT_Guide_%d:' % gi)
        S.append('\tdb checkflag_command\n\tdw $%04X\n\tiffalse .orig' % gy['badge'])
        S.append('\tfaceplayer\n\topentext\n\tdb setevent_command\n\tdw $%04X\n\twritetext %sask2\n\tscall %steach\n\tend' % (fl, G, G))
        if gy['orig']: S.append('.orig\n\tdb farsjump_command\n\tdb $%02X\n\tdw $%04X' % gy['orig'])
        else: S.append('.orig\n\tend')
        for k, (t, pth, gface) in enumerate(gy['legs']):
            S.append('KT_Leave_%d_%d:' % (gi, k))
            S.append('\tdb checkflag_command\n\tdw $%04X\n\tiffalse .x' % gy['badge'])
            S.append('\tdb checkevent_command\n\tdw $%04X\n\tiftrue .x' % fl)
            S.append('\topentext\n\twritetext %scall\n\twaitbutton\n\tclosetext' % G)
            if pth: S.append('\tapplymovement %d, .m' % gy['gid'])
            S.append('\tturnobject %d, %s\n\tturnobject PLAYER, %s' % (gy['gid'], DIRN[gface], DIRN[OPP[gface]]))
            S.append('\tdb setevent_command\n\tdw $%04X' % fl)
            S.append('\topentext\n\twritetext %sask1\n\tscall %steach' % (G, G))
            if pth: S.append('\tapplymovement %d, .b' % gy['gid'])
            S.append('.x\n\tend')
            if pth:
                S.append('.m\n' + '\n'.join('\tstep %s' % DIRN[d] for d in pth) + '\n\tstep_end')
                S.append('.b\n' + '\n'.join('\tstep %s' % DIRN[OPP[d]] for d in reversed(pth)) + '\n\tstep_end')
        if gy['addpos']:
            S.append('KT_CeladonCallback:')
            S.append('\tdb checkflag_command\n\tdw $%04X\n\tiffalse .hide' % gy['badge'])
            S.append('\tdb clearevent_command\n\tdw $%04X\n\tendcallback' % CELADON_HIDE)
            S.append('.hide\n\tdb setevent_command\n\tdw $%04X\n\tendcallback' % CELADON_HIDE)
        S.append('%scall:\n%s' % (G, txt('<P>！　ちょっと　まって！')))
        S.append('%sask1:\n%s' % (G, txt(gy['leader'] + 'に　かった　おいわいに<L>わざを　ひとつ　おしえて　あげよう！<PARA>'
                                         + gy['mname'] + 'を<L>おぼえさせるかい？')))
        S.append('%sask2:\n%s' % (G, txt('<P>！<L>' + gy['mname'] + 'を　おぼえさせるかい？')))
        S.append('%sok:\n%s' % (G, txt('これで　' + gy['mname'] + 'も<L>ばっちりだ！<PARA>また　いつでも<L>おしえて　あげるからな！')))
        S.append('%sno:\n%s' % (G, txt('そうか……<PARA>おぼえさせたく　なったら<L>いつでも　はなしかけてくれ！')))
    # ジム以外
    npc_heads = []
    for ni, ((ob, oa), teach) in enumerate(NPCS):
        q = fo(ob, oa)
        assert rom[q:q + 2] == bytes([0x6A, 0x47]), (hex(ob), hex(oa), rom[q:q + 6].hex())
        n = {0x31: 5, 0x21: 4}[rom[q + 2]]; head = bytes(rom[q + 2:q + n])
        if rom[q + 2] == 0x31: assert r16(rom, q + 3) == teach[0][0], (hex(oa), hex(r16(rom, q + 3)))
        npc_heads.append((q, n))
        N = 'KT_N%d_' % ni; L = 'KT_Npc_%d' % ni
        S.append(L + ':')
        if len(teach) == 1:
            fl, mv, nm = teach[0]
            S.append('\tdb checkevent_command\n\tdw $%04X\n\tiffalse .orig' % fl)
            S.append('\tfaceplayer\n\topentext\n\twritetext %sask\n\tyesorno\n\tiffalse .no' % N)
            S.append('\tsetval %s\n\tcallasm KT_MoveTutor\n\tifequal 0, .ok' % mv)
            S.append('.no\n\twritetext %sno\n\twaitbutton\n\tclosetext\n\tend' % N)
            S.append('.ok\n\twritetext %sok\n\twaitbutton\n\tclosetext\n\tend' % N)
            S.append('.orig\n\tfaceplayer\n\topentext\n\tdb ' + ', '.join('$%02X' % x for x in head))
            S.append('\tdb farsjump_command\n\tdb $%02X\n\tdw $%04X' % (ob, oa + n))
            S.append('%sask:\n%s' % (N, txt(nm + 'を<L>おしえて　あげようか？')))
            S.append('%sok:\n%s' % (N, txt('これで　' + nm + 'も<L>ばっちりだね！<PARA>また　いつでも<L>おしえて　あげるよ！')))
            S.append('%sno:\n%s' % (N, txt('そうか……<PARA>おぼえさせたく　なったら<L>いつでも　はなしかけてね！')))
        else:
            for fl, mv, nm in teach: S.append('\tdb checkevent_command\n\tdw $%04X\n\tiftrue .any' % fl)
            S.append('\tsjump .orig')
            S.append('.any\n\tfaceplayer\n\topentext\n\twritetext %sask\n\tyesorno\n\tiffalse .orig2' % N)
            for k, (fl, mv, nm) in enumerate(teach):
                S.append('\tdb checkevent_command\n\tdw $%04X\n\tiffalse .n%d' % (fl, k))
                S.append('\twritetext %sq%d\n\tyesorno\n\tiffalse .n%d' % (N, k, k))
                S.append('\tsetval %s\n\tcallasm KT_MoveTutor' % mv)
                S.append('.n%d' % k)
            S.append('\twritetext %sbye\n\twaitbutton\n\tclosetext\n\tend' % N)
            S.append('.orig\n\tfaceplayer\n\topentext\n.orig2\n\tdb ' + ', '.join('$%02X' % x for x in head))
            S.append('\tdb farsjump_command\n\tdb $%02X\n\tdw $%04X' % (ob, oa + n))
            S.append('%sask:\n%s' % (N, txt('わざマシンの　わざを<L>おしえて　あげようか？')))
            S.append('%sbye:\n%s' % (N, txt('また　いつでも<L>おしえて　あげるね！')))
            for k, (fl, mv, nm) in enumerate(teach): S.append('%sq%d:\n%s' % (N, k, txt(nm + 'を<L>おぼえさせる？')))
    asmpatch.overlay(rom, '\n'.join(S) + '\n', inc=[os.path.join(KIT, 'pokegold'), KIT], cwd=KIT)

    # ---- 表を 読む
    t = [fo(CODE_BANK, 0x4000)]
    def nxt():
        v = r16(rom, t[0]); t[0] += 2; return v
    wrap = nxt()
    rom[PREDEF_CANLEARN:PREDEF_CANLEARN + 3] = bytes([wrap & 0xFF, wrap >> 8, CODE_BANK])
    for gi, gy in enumerate(gyms):
        b, nb, ev = gy['b'], gy['nb'], gy['ev']
        guide_a = nxt(); leave_a = [nxt() for _ in gy['legs']]; cb_a = nxt() if gy['addpos'] else None
        rom[fo(nb, 0x4000):fo(nb, 0x8000)] = rom[fo(b, 0x4000):fo(b, 0x8000)]
        used = [(s0 + (nb - b) * 0x4000, e0 + (nb - b) * 0x4000) for s0, e0 in used_ranges(rom, b, gy['sp'], ev)]
        stubs = 4 * (1 + len(leave_a) + (1 if cb_a else 0))
        hdr_size = 2 + 4 * len(gy['scenes']) + 3 * (len(gy['cbs']) + (1 if cb_a else 0))
        size = stubs + hdr_size + len(build_events(ev)) + 8 * len(leave_a)
        o = find_gap(used, nb, size + 16) + 8
        st = 0x4000 + o - fo(nb, 0x4000)
        code = bytearray(bytes([0x04, CODE_BANK, guide_a & 0xFF, guide_a >> 8]))
        for la in leave_a: code += bytes([0x04, CODE_BANK, la & 0xFF, la >> 8])
        cbs = list(gy['cbs'])
        if cb_a:
            ca = st + len(code); code += bytes([0x04, CODE_BANK, cb_a & 0xFF, cb_a >> 8])
            cbs.append(bytes([2, ca & 0xFF, ca >> 8]))           # MAPCALLBACK_OBJECTS
        obj = bytearray(ev['objects'][gy['gidx']]); obj[9] = st & 0xFF; obj[10] = st >> 8
        ev['objects'][gy['gidx']] = bytes(obj)
        for k, (tt, pth, gface) in enumerate(gy['legs']):
            sa = st + 4 * (k + 1)
            ev['coords'].append(bytes([0xFF, tt[0], tt[1], 0, sa & 0xFF, sa >> 8, 0, 0]))
        hdr = bytes([len(gy['scenes'])]) + b''.join(gy['scenes']) + bytes([len(cbs)]) + b''.join(cbs)
        ha = st + len(code); code += hdr
        evd = build_events(ev); ea = st + len(code); code += evd
        assert len(code) <= size
        rom[o:o + len(code)] = code
        rom[gy['ao'] + 6] = nb
        rom[gy['ao'] + 7] = ha & 0xFF; rom[gy['ao'] + 8] = ha >> 8
        rom[gy['ao'] + 9] = ea & 0xFF; rom[gy['ao'] + 10] = ea >> 8
        log.append('%d:%d %s %s → 写し $%02X（見出し $%04X・イベント $%04X）案内 %d番 %s 扉の 前 %s' % (
            gy['G'], gy['M'], gy['leader'], gy['mname'], nb, ha, ea, gy['gid'], gy['gpos'],
            ['%s %s' % (tt, ''.join(p) or '-') for tt, p, f in gy['legs']]))
    for ni, ((ob, oa), teach) in enumerate(NPCS):
        na = nxt(); q, n = npc_heads[ni]
        rom[q:q + 4] = bytes([0x04, CODE_BANK, na & 0xFF, na >> 8])
        log.append('$%02X:$%04X %s → $%02X:$%04X' % (ob, oa, '・'.join(x[2] for x in teach), CODE_BANK, na))
    log.append('CanLearnTMHMMove の predef → $%02X:$%04X（赤の 表 %s）' % (CODE_BANK, wrap,
               {m: len(learners[m]) for m in allmv}))
    return rom
