"""第66弾：カントーの ジムで、リーダーから もらう わざマシン（クリスタルの 同じ 番号）と ちがう 赤の わざマシンの わざを、
   リーダーに 勝った あと ジムの 入口の 案内の 人が 教える。
   ・はじめて 勝って 出口に 向かうと、案内の 人が「ちょっと まって！」と よびとめて 近よって くる（入口の 1つ 上の 2マスの イベント）
   ・その あとは 話しかければ 何度でも 教えて もらえる（おぼえなくても よい）
   ・赤と 同じ わざの ジム（セキチク TM06 どくどく・グレン TM38 だいもんじ）は なし
   ・タマムシジムには 案内の 人が いないので、クチバジムと 同じ 所（7,15）に 足す
   おぼえられる ポケモン：第1世代は 赤の わざマシンの 表。第2世代は 同じ 進化の 仲間に おぼえられる 第1世代が いるか、
   レベルで おぼえるか（10まんボルトは クリスタルの 教え技の 表も）。
   asm/gold_tutor.asm を バンク NB の $4000 に 置く。
"""
import os, re, subprocess, tempfile
import c2g
from jpchar import ENC

def fo(b, a): return b * 0x4000 + a - 0x4000
RGBDS = '/home/claude/rgbds-src'
RED = '/home/claude/work/mod/ref/pokered'
PG = '/home/claude/work/ref_pokegold'
PC = '/home/claude/work/mod/ref/pokecrystal'
HERE = os.path.dirname(os.path.abspath(__file__))

# （マップ, 番号, バッジ, わざ, わざの 名前, リーダー, 案内の 人の 場所（None＝足す）, 入口の 上の マス → (歩く 向き, 向く 向き)）
GYMS = [
    ('PewterGym', 0, 'ENGINE_BOULDERBADGE', 'BIDE', 'がまん', 'タケシ', (6, 11),
     {(4, 12): ('DL', 'L'), (5, 12): ('D', 'L')}),
    ('CeruleanGym', 1, 'ENGINE_CASCADEBADGE', 'BUBBLEBEAM', 'バブルこうせん', 'カスミ', (7, 13),
     {(4, 14): ('DLL', 'L'), (5, 14): ('DL', 'L')}),
    ('VermilionGym', 2, 'ENGINE_THUNDERBADGE', 'THUNDERBOLT', '10まんボルト', 'マチス', (7, 15),
     {(4, 16): ('DLL', 'L'), (5, 16): ('DL', 'L')}),
    ('CeladonGym', 3, 'ENGINE_RAINBOWBADGE', 'MEGA_DRAIN', 'メガドレイン', 'エリカ', None,
     {(4, 16): ('DLL', 'L'), (5, 16): ('DL', 'L')}),
    ('SaffronGym', 4, 'ENGINE_MARSHBADGE', 'PSYWAVE', 'サイコウェーブ', 'ナツメ', (9, 14),
     {(8, 16): ('DD', 'L'), (9, 16): ('RDD', 'L')}),
    ('ViridianGym', 5, 'ENGINE_EARTHBADGE', 'FISSURE', 'じわれ', 'サカキ', (7, 13),
     {(4, 16): ('DDLLD', 'L'), (5, 16): ('DLLLDD', 'R')}),
]
CELADON_GUIDE = (7, 15)
DIRN = {'D': 0, 'U': 1, 'L': 2, 'R': 3}
OPP = {'D': 'U', 'U': 'D', 'L': 'R', 'R': 'L'}
# 金の スクリプト命令
OP = dict(scall=0x00, sjump=0x03, iftrue=0x09, iffalse=0x08, checkflag=0x34, checkevent=0x31, setevent=0x33,
          opentext=0x47, writetext=0x4C, closetext=0x49, waitbutton=0x53, yesorno=0x4E, callasm=0x0E,
          end=0x90, applymovement=0x68, faceplayer=0x6A, turnobject=0x75, showemote=0x74)

def consts(path):
    out = {}; n = 0
    for l in open(path):
        if re.match(r'\s*const_def', l):
            m = re.match(r'\s*const_def\s*(\d+)?', l); n = int(m.group(1)) if m.group(1) else 0
            if out: break
            continue
        m = re.match(r'\s*const (\w+)', l)
        if m: out[m.group(1)] = n; n += 1
    return out

def compat_table(move):
    SP = consts(PG + '/constants/pokemon_constants.asm')       # BULBASAUR=1 …
    MV = consts(PG + '/constants/move_constants.asm')
    ok = set()
    # 第1世代：赤の わざマシンの 表
    for f in os.listdir(RED + '/data/pokemon/base_stats'):
        t = open(RED + '/data/pokemon/base_stats/' + f).read()
        dex = re.search(r'db DEX_(\w+)', t).group(1)
        tm = re.search(r'tmhm(.*?); end', t, re.S).group(1)
        if move in re.findall(r'\w+', tm): ok.add(SP[{'MR_MIME': 'MR__MIME', 'FARFETCHD': 'FARFETCH_D'}.get(dex, dex)])
    # 進化の 仲間（pokegold の evos_attacks）と レベルで おぼえる わざ
    t = open(PG + '/data/pokemon/evos_attacks.asm').read()
    blocks = re.split(r'\n(\w+)EvosAttacks:\n', '\n' + t)
    names = {}; edges = []; learn = {}
    for i in range(1, len(blocks), 2):
        nm, body = blocks[i], blocks[i + 1]
        evo, _, att = body.partition('db 0 ; no more evolutions')
        names[nm] = body
        for m in re.finditer(r'db\s*EVOLVE_[^\n]*?(\w+)\s*$', evo, re.M):
            edges.append((nm, m.group(1)))
        learn[nm] = set(re.findall(r'db\s+\d+,\s*(\w+)', att))
    def key(nm): return nm.upper().replace('NIDORANF', 'NIDORAN_F').replace('NIDORANM', 'NIDORAN_M').replace('MRMIME', 'MR__MIME').replace('FARFETCHD', 'FARFETCH_D').replace('HOOH', 'HO_OH')
    sid = {}
    for nm in names:
        k = key(nm)
        for cand in (k, k.replace('MR__MIME', 'MR_MIME')):
            if cand in SP: sid[nm] = SP[cand]; break
    fam = {}
    def find(x):
        while fam.get(x, x) != x: x = fam[x]
        return x
    for a, b in edges:
        if a in sid and key(b) in SP:
            bn = [n for n in sid if sid[n] == SP[key(b)]]
            if bn: fam[find(a)] = find(bn[0])
    groups = {}
    for nm in sid: groups.setdefault(find(nm), set()).add(sid[nm])
    tutor = set()
    if move == 'THUNDERBOLT':                               # クリスタルの 教え技
        for f in os.listdir(PC + '/data/pokemon/base_stats'):
            tt = open(PC + '/data/pokemon/base_stats/' + f).read()
            m = re.search(r'tmhm (.*?)\n\s*; end', tt, re.S)
            if m and 'THUNDERBOLT' in re.findall(r'\w+', m.group(1)):
                key2 = f[:-4].upper()
                for k in (key2, key(f[:-4])):
                    if k in SP: tutor.add(SP[k])
    for nm, s in sid.items():
        if s <= 151: continue
        g = groups[find(nm)]
        if any(x <= 151 and x in ok for x in g) or move in learn.get(nm, ()) or s in tutor: ok.add(s)
    bits = bytearray(32)
    for s in ok:
        if 1 <= s <= 251: bits[(s - 1) >> 3] |= 1 << ((s - 1) & 7)
    return bits, MV[move], sorted(ok)

def asm_bytes(addr, moves, tables):
    src = os.path.join(HERE, 'asm', 'gold_tutor.asm')
    inc = 'TutorMoves:\n\tdb ' + ', '.join('$%02x' % m for m in moves) + '\nTutorCompat:\n'
    for t in tables: inc += '\tdb ' + ', '.join('$%02x' % x for x in t) + '\n'
    with tempfile.TemporaryDirectory() as d:
        open(d + '/compat.inc', 'w').write(inc)
        subprocess.run([RGBDS + '/rgbasm', '-I', d, '-DTUT_ADDR=%d' % addr, '-o', d + '/t.o', src], check=True)
        subprocess.run([RGBDS + '/rgblink', '-n', d + '/t.sym', '-o', d + '/t.gbc', d + '/t.o'], check=True)
        r = open(d + '/t.gbc', 'rb').read()
        sym = {}
        for l in open(d + '/t.sym'):
            m = re.match(r'01:([0-9a-f]+) (\S+)', l)
            if m: sym[m.group(2)] = int(m.group(1), 16)
    end = sym['TutorCompat'] + 6 * 32
    b = r[addr:end]
    return b, sym

def enc(s):
    out = bytearray()
    i = 0
    while i < len(s):
        for k, v in (('<LINE>', 0x4F), ('<PARA>', 0x51), ('<CONT>', 0x55), ('<DONE>', 0x57), ('<PLAYER>', 0x52)):
            if s.startswith(k, i): out.append(v); i += len(k); break
        else:
            c = s[i]; i += 1
            if c in ENC: out.append(ENC[c]); continue
            raise KeyError(c)
    return bytes(out)

class S:
    """金の スクリプトを 組む（ラベルつき、2回 組んで 住所を きめる）"""
    def __init__(s, base): s.base = base; s.b = bytearray(); s.lab = {}; s.fix = []
    def L(s, n): s.lab[n] = s.base + len(s.b)
    def op(s, n, *args):
        s.b.append(OP[n])
        for a in args:
            if isinstance(a, str): s.fix.append((len(s.b), a)); s.b += b'\0\0'
            elif isinstance(a, tuple): s.b += bytes([a[0] & 0xFF, a[0] >> 8])      # (dw,)
            else: s.b.append(a)
    def raw(s, data): s.b += data
    def done(s):
        for o, n in s.fix: v = s.lab[n]; s.b[o] = v & 0xFF; s.b[o + 1] = v >> 8
        return bytes(s.b)

def build_script(base, gym, guide_obj, orig_ptr, called_flag, badge, nb, sym):
    cname, idx, _, _, mname, leader, _, cells = gym
    s = S(base)
    # 案内の 人に 話しかけた とき
    s.L('Guide'); s.op('faceplayer'); s.op('checkflag', (badge,)); s.op('iffalse', 'Orig')
    s.op('setevent', (called_flag,)); s.op('scall', 'Teach'); s.op('end')
    s.L('Orig')
    if orig_ptr is None:
        s.op('opentext'); s.op('writetext', 'TxPre'); s.op('waitbutton'); s.op('closetext'); s.op('end')
    else: s.op('sjump', (orig_ptr,))
    # 教える ところ
    s.L('Teach'); s.op('opentext'); s.op('writetext', 'TxOffer'); s.op('yesorno'); s.op('iffalse', 'No')
    s.op('callasm', nb, (sym['Tutor%d' % idx],))
    s.op('writetext', 'TxAfter'); s.op('waitbutton'); s.op('closetext'); s.op('end')
    s.L('No'); s.op('writetext', 'TxNo'); s.op('waitbutton'); s.op('closetext'); s.op('end')
    # 入口の 上の マス
    for i, ((px, py), (walk, face)) in enumerate(sorted(cells.items())):
        s.L('C%d' % i)
        s.op('checkflag', (badge,)); s.op('iffalse', 'CEnd'); s.op('checkevent', (called_flag,)); s.op('iftrue', 'CEnd')
        s.op('showemote', 0, guide_obj, 15)
        s.op('opentext'); s.op('writetext', 'TxWait'); s.op('waitbutton'); s.op('closetext')
        s.op('applymovement', guide_obj, 'M%d' % i)
        s.op('turnobject', 0, DIRN[OPP[face]])
        s.op('setevent', (called_flag,)); s.op('scall', 'Teach')
        s.op('applymovement', guide_obj, 'B%d' % i)
        s.op('end')
    s.L('CEnd'); s.op('end')
    for i, ((px, py), (walk, face)) in enumerate(sorted(cells.items())):
        s.L('M%d' % i); s.raw(bytes([0x0C + DIRN[d] for d in walk] + [0x00 + DIRN[face], 0x47]))
        s.L('B%d' % i); s.raw(bytes([0x0C + DIRN[OPP[d]] for d in reversed(walk)] + [0x00, 0x47]))
    # 文
    s.L('TxWait'); s.raw(b'\x00' + enc('あっ！ ちょっと まって！<DONE>'))
    s.L('TxOffer'); s.raw(b'\x00' + enc('%sに かった きねんに<LINE>いい わざを おしえて あげよう！<PARA>%sを<LINE>ポケモンに おしえようか？<DONE>' % (leader, mname)))
    s.L('TxAfter'); s.raw(b'\x00' + enc('また おしえて ほしく なったら<LINE>いつでも はなしかけて くれ！<DONE>'))
    s.L('TxNo'); s.raw(b'\x00' + enc('そうか！ おしえて ほしく なったら<LINE>いつでも はなしかけて くれ！<DONE>'))
    if orig_ptr is None:
        s.L('TxPre'); s.raw(b'\x00' + enc('おーす！ みらいの チャンピオン！<PARA>ここの リーダー エリカは<LINE>くさタイプの つかいてだ！<PARA>ほのおや こおりの わざで<LINE>せめるのが いいぜ！<DONE>'))
    return s

def install(E, g, log):
    """バンクを 1つ つかって asm を 置き、c2g.EXTRA_TUTOR に マップごとの 処理を 入れる"""
    nb = E.next_bank; E.next_bank += 1
    tabs = []; moves = []
    for gym in GYMS:
        bits, mv, ok = compat_table(gym[3]); tabs.append(bits); moves.append(mv)
        log.append('教え技 %s：%s %d ひき' % (gym[0], gym[3], len(ok)))
    code, sym = asm_bytes(0x4000, moves, tabs)
    o = fo(nb, 0x4000); assert not any(x not in (0, 0xFF) for x in g[o:o + len(code)])
    g[o:o + len(code)] = code
    log.append('教え技の asm：%02X:4000（%d バイト）' % (nb, len(code)))
    pp = fo(0x02, 0x4B5B) + 3 * 0x0E                       # predef CanLearnTMHMMove → CanLearnHook（パーティの 画面の「おぼえられる」も）
    assert g[pp:pp + 3] == bytes([0xBF, 0x59, 0x04]), g[pp:pp + 3].hex()
    h = sym['CanLearnHook']; g[pp:pp + 3] = bytes([h & 0xFF, h >> 8, nb])
    for gym in GYMS:
        flag = c2g.EV_POOL.pop(0)
        badge = c2g.G['engine'][gym[2]]
        def f(E_, gb, alloc, grom, coords, objs, gym=gym, flag=flag, badge=badge):
            cname, idx, _, _, _, _, gpos, cells = gym
            if gpos is None:                                       # 案内の 人を 足す（クチバジムと 同じ 形）
                gpos = CELADON_GUIDE
                ob = bytearray([0x48, gpos[1] + 4, gpos[0] + 4, 0x06, 0x00, 0xFF, 0xFF, 0x90, 0x01, 0, 0, 0xFF, 0xFF])
                objs.append(ob); gi = len(objs) - 1; orig = None
            else:
                gi = [i for i, ob in enumerate(objs) if (ob[2] - 4, ob[1] - 4) == gpos]
                assert len(gi) == 1 and objs[gi[0]][0] == 0x48, (cname, gi)
                gi = gi[0]; orig = objs[gi][9] | objs[gi][10] << 8
            n = len(build_script(0x4000, gym, gi + 2, orig, flag, badge, nb, sym).done())
            a = alloc(n, gb)
            sc = build_script(a, gym, gi + 2, orig, flag, badge, nb, sym)
            data = sc.done()
            grom[fo(gb, a):fo(gb, a) + len(data)] = data
            objs[gi][9:11] = sc.lab['Guide'].to_bytes(2, 'little')
            for i, (px, py) in enumerate(sorted(cells)):
                coords.append(bytes([0xFF, py, px, 0]) + sc.lab['C%d' % i].to_bytes(2, 'little') + b'\0\0')
            log.append('教え技 %s：案内 %d番 %s、フラグ %03X、スクリプト %02X:%04X（%d バイト）' % (cname, gi + 2, gpos, flag, gb, a, len(data)))
        c2g.EXTRA_TUTOR[gym[0]] = f
    return nb

NATIVE = ('VermilionGym',)          # 金の マップの まま（MOD の ジムは callasm を 使うので 入れて いない）

def native(E, g, M, cm, log):
    """金の マップの ままの ジム：金の スクリプトを うつしなおして（gold_rebuild）、案内の 人と 入口の イベントを 足す"""
    import gold_rebuild as gr
    from cmaps import maplist, GMGP
    GV = open('/home/claude/work/ref/kin64.gbc', 'rb').read()
    gm = {m['name']: m for m in maplist(GV, GMGP, 'pokegold')}
    for nm in NATIVE:
        f = c2g.EXTRA_TUTOR.pop(nm)
        MB = cwalk_bank(M, cm[nm])
        gr.rebuild(E, g, GV, gm[nm], nm, {'text': {}, 'hook': f}, M, MB, log)

def cwalk_bank(M, m):
    import cwalk
    return cwalk.Walk(M).map(m['attr'], m['name'])['scbank']
