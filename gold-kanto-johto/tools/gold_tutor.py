"""第66弾：赤の わざマシンの わざを 教える（クリスタル版 第122弾の キット「赤のわざマシンのわざを教える_キット」を 金へ）。
   カントーで もらう わざマシンは そのまま（金の わざマシン）。赤の わざマシンの わざで 金の わざマシンに ない ものを、
   人が 何度でも 教える。
   ・ジム（ニビ・ハナダ・クチバ・タマムシ・ヤマブキ・トキワ）：リーダーに 勝って はじめて 出るとき、入口の 案内の 人が
     呼び止めて（「<PLAYER>！ ちょっと まって！」）近よって きて 教える（入口の 2つの 扉の 1つ 上の マス、場面 $FF の イベント）。
     その あとも 話しかければ 教える。バッジ前は 赤の 案内の 人の まま。
     タマムシジムは 案内の 人が いないので (7,15) に 足し、バッジが あるときだけ 出す（MAPCALLBACK_OBJECTS）。
     クチバジムは 金の マップの まま なので gold_rebuild で スクリプトを うつしなおして 足す。
   ・ジム以外：タマムシの おじいさん（タマゴうみ）・シルフ 2F（じばく）・グレンの 研究所（ゆびをふる）・デパート 3F（カウンター）・
     ものまねむすめ（ものまね、クリア後の 話の あいだは もとの まま）・デパート 屋上の 女の子（れいとうビーム・いわなだれ・
     トライアタック、わたした ジュースの 分だけ）：わざマシンを くれた あと、その 人が 教える。
   ・金には クリスタルの special MoveTutor が ないので、asm/gold_tutor.asm（MoveTutor を 移した もの）を callasm で よぶ。
     スクリプト：setval わざ ; callasm Tutor ; ifequal 0, おぼえた
   ・おぼえられる ポケモン：赤の わざマシンの 表（第2世代は みな おぼえられない）。predef CanLearnTMHMMove を CanLearnHook に して、
     wScriptVar が その わざの ときだけ 表で 答える（ふつうの わざマシンは もとの まま）。手持ちの 画面の「おぼえられる」も 同じ。
"""
import os, re, glob, subprocess, tempfile
import c2g
from jpchar import ENC

def fo(b, a): return b * 0x4000 + a - 0x4000
RGBDS = '/home/claude/rgbds-src'
RED = '/home/claude/work/mod/ref/pokered'
PG = '/home/claude/work/ref_pokegold'
HERE = os.path.dirname(os.path.abspath(__file__))

# （マップ, リーダー, バッジ, わざ, わざの 名前, 案内の 人の 場所（None＝足す）, 入口の 上の マス → (歩く 道, 案内の 人の 向き)）
GYMS = [
    ('PewterGym', 'タケシ', 'ENGINE_BOULDERBADGE', 'BIDE', 'がまん', (6, 11),
     {(4, 12): ('DL', 'L'), (5, 12): ('D', 'L')}),
    ('CeruleanGym', 'カスミ', 'ENGINE_CASCADEBADGE', 'BUBBLEBEAM', 'バブルこうせん', (7, 13),
     {(4, 14): ('DLL', 'L'), (5, 14): ('DL', 'L')}),
    ('VermilionGym', 'マチス', 'ENGINE_THUNDERBADGE', 'THUNDERBOLT', '10まんボルト', (7, 15),
     {(4, 16): ('DLL', 'L'), (5, 16): ('DL', 'L')}),
    ('CeladonGym', 'エリカ', 'ENGINE_RAINBOWBADGE', 'MEGA_DRAIN', 'メガドレイン', None,
     {(4, 16): ('DLL', 'L'), (5, 16): ('DL', 'L')}),
    ('SaffronGym', 'ナツメ', 'ENGINE_MARSHBADGE', 'PSYWAVE', 'サイコウェーブ', (9, 14),
     {(8, 16): ('DD', 'L'), (9, 16): ('RDD', 'L')}),
    ('ViridianGym', 'サカキ', 'ENGINE_EARTHBADGE', 'FISSURE', 'じわれ', (7, 13),
     {(4, 16): ('DDLLD', 'L'), (5, 16): ('DLLLDD', 'R')}),
]
CELADON_GUIDE = (7, 15)
NATIVE = ('VermilionGym',)          # 金の マップの まま（MOD の ジムは callasm を 使うので 入れて いない）
# ジム以外：（クリスタル版の マップ, 人の 場所, [(わざマシンを もらった フラグ（クリスタル版）, わざ, 名前)], クリア後の 話の フラグ）
NPCS = [
    ('CeladonCity', (22, 16), [(0x09C4, 'SOFTBOILED', 'タマゴうみ')], None),
    ('G26_026', (10, 1), [(0x0607, 'SELFDESTRUCT', 'じばく')], None),
    ('G26_055', (7, 2), [(0x0849, 'METRONOME', 'ゆびをふる')], None),
    ('G26_128', (16, 5), [(0x09C8, 'COUNTER', 'カウンター')], None),
    ('G26_146', (4, 3), [(0x09DA, 'MIMIC', 'ものまね')], 0xCD),
    ('G26_131', (5, 5), [(0x09C9, 'ICE_BEAM', 'れいとうビーム'), (0x09CA, 'ROCK_SLIDE', 'いわなだれ'),
                         (0x09CB, 'TRI_ATTACK', 'トライアタック')], None),
]
DIRN = {'D': 0, 'U': 1, 'L': 2, 'R': 3}
OPP = {'D': 'U', 'U': 'D', 'L': 'R', 'R': 'L'}
# 金の スクリプト命令（pokegold macros/scripts/events.asm の 順）
OP = dict(scall=0x00, sjump=0x03, ifequal=0x06, iffalse=0x08, iftrue=0x09, callasm=0x0E, setval=0x15, readvar=0x1C,
          checkevent=0x31, clearevent=0x32, setevent=0x33, checkflag=0x34, opentext=0x47, closetext=0x49,
          writetext=0x4C, yesorno=0x4E, waitbutton=0x53, applymovement=0x68, faceplayer=0x6A, appear=0x6E,
          turnobject=0x75, endcallback=0x8F, end=0x90)


def consts(path):
    out = {}; n = 0
    for l in open(path):
        m = re.match(r'\s*const_def\s*(\d+)?', l)
        if m:
            if out: break
            n = int(m.group(1)) if m.group(1) else 0; continue
        m = re.match(r'\s*const (\w+)', l)
        if m: out[m.group(1)] = n; n += 1
    return out


def red_learners(move):
    """赤の わざマシンで その わざを おぼえられる ポケモンの 図鑑番号"""
    dex = {}; i = 0
    for l in open(RED + '/constants/pokedex_constants.asm'):
        m = re.match(r'\s*const (DEX_\w+)', l)
        if m: i += 1; dex[m.group(1)] = i
    out = []
    for f in glob.glob(RED + '/data/pokemon/base_stats/*.asm'):
        t = open(f).read()
        d = re.search(r'db (DEX_\w+)', t).group(1)
        tm = re.search(r'tmhm(.*?)\n\s*; end', t, re.S)
        moves = {x.strip() for x in tm.group(1).replace('\\', ' ').split(',')} if tm else set()
        if move in moves: out.append(dex[d])
    return sorted(out)


def all_moves():
    L = [g[3] for g in GYMS]
    for _, _, teach, _ in NPCS: L += [t[1] for t in teach]
    return L


def asm_bytes(addr, moves, tables):
    src = os.path.join(HERE, 'asm', 'gold_tutor.asm')
    inc = 'TutorMoves:\n\tdb ' + ', '.join('$%02x' % m for m in moves) + ', 0\nTutorCompat:\n'
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
    end = sym['TutorCompat'] + 32 * len(tables)
    return r[addr:end], sym


def enc(s):
    out = bytearray(); i = 0
    CT = (('<LINE>', 0x4F), ('<PARA>', 0x51), ('<CONT>', 0x55), ('<DONE>', 0x57), ('<PLAYER>', 0x52), ('<……>', 0x56))
    while i < len(s):
        for k, v in CT:
            if s.startswith(k, i): out.append(v); i += len(k); break
        else:
            out.append(ENC[s[i]]); i += 1
    return bytes(out)
def T(s): return b'\x00' + enc(s + '<DONE>')


class S:
    """金の スクリプトを 組む（ラベルつき）"""
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
    def tutor(s, mv, nb, sym, ok):
        s.op('setval', mv); s.op('callasm', nb, (sym['Tutor'],)); s.op('ifequal', 0, ok)


def gym_script(base, gym, gid, orig_ptr, called, hide, badge, mv, nb, sym):
    cname, leader, _, _, mname, _, cells = gym
    s = S(base)
    s.L('teach'); s.op('yesorno'); s.op('iffalse', 't_no'); s.tutor(mv, nb, sym, 't_ok')
    s.L('t_no'); s.op('writetext', 'no'); s.op('waitbutton'); s.op('closetext'); s.op('end')
    s.L('t_ok'); s.op('writetext', 'ok'); s.op('waitbutton'); s.op('closetext'); s.op('end')
    s.L('guide'); s.op('checkflag', (badge,))
    if orig_ptr is not None: s.op('iffalse', 'g_red')
    s.op('faceplayer'); s.op('opentext'); s.op('setevent', (called,)); s.op('writetext', 'ask2'); s.op('scall', 'teach'); s.op('end')
    if orig_ptr is not None: s.L('g_red'); s.op('sjump', (orig_ptr,))
    if hide is not None:
        s.L('cb_obj'); s.op('checkflag', (badge,)); s.op('iffalse', 'cb_hide'); s.op('clearevent', (hide,)); s.op('endcallback')
        s.L('cb_hide'); s.op('setevent', (hide,)); s.op('endcallback')
    for i, ((px, py), (walk, face)) in enumerate(sorted(cells.items())):
        L = 'lv%d' % i
        # 第127弾：入って きた とき（上向きで この ますを 通った とき）は 呼び止めない（そらをとぶ などで 出て また 入る とき）
        s.L(L); s.op('readvar', 0x09); s.op('ifequal', 1, L + 'x')
        s.op('checkflag', (badge,)); s.op('iffalse', L + 'x'); s.op('checkevent', (called,)); s.op('iftrue', L + 'x')
        if hide is not None: s.op('appear', gid)
        # （showemote は 使わない：連れ歩きの 絵を こわす）
        s.op('opentext'); s.op('writetext', 'call'); s.op('waitbutton'); s.op('closetext')
        s.op('applymovement', gid, L + 'm')
        s.op('turnobject', gid, DIRN[face]); s.op('turnobject', 0, DIRN[OPP[face]])
        s.op('setevent', (called,))
        s.op('opentext'); s.op('writetext', 'ask1'); s.op('scall', 'teach')
        s.op('applymovement', gid, L + 'b')
        s.L(L + 'x'); s.op('end')
        s.L(L + 'm'); s.raw(bytes([0x0C + DIRN[d] for d in walk] + [0x47]))
        s.L(L + 'b'); s.raw(bytes([0x0C + DIRN[OPP[d]] for d in reversed(walk)] + [0x00, 0x47]))
    texts = {'call': T('<PLAYER>！　ちょっと　まって！'),
             'ask1': T(leader + 'に　かった　おいわいに<LINE>わざを　ひとつ　おしえて　あげよう！<PARA>' + mname + 'を<LINE>おぼえさせるかい？'),
             'ask2': T('<PLAYER>！<LINE>' + mname + 'を　おぼえさせるかい？'),
             'ok': T('これで　' + mname + 'も<LINE>ばっちりだ！<PARA>また　いつでも<LINE>おしえて　あげるからな！'),
             'no': T('そうか<……><PARA>おぼえさせたく　なったら<LINE>いつでも　はなしかけてくれ！')}
    for k, v in texts.items(): s.L(k); s.raw(v)
    return s


def npc_script(base, teach, guard, orig_ptr, MV, nb, sym):
    s = S(base)
    if len(teach) == 1:
        fl, mv, nm = teach[0]
        s.L('new'); s.op('checkevent', (fl,)); s.op('iffalse', 'orig')
        if guard is not None: s.op('checkevent', (guard,)); s.op('iftrue', 'orig')
        s.op('faceplayer'); s.op('opentext'); s.op('writetext', 'ask'); s.op('yesorno'); s.op('iffalse', 't_no')
        s.tutor(MV[mv], nb, sym, 't_ok')
        s.L('t_no'); s.op('writetext', 'no'); s.op('waitbutton'); s.op('closetext'); s.op('end')
        s.L('t_ok'); s.op('writetext', 'ok'); s.op('waitbutton'); s.op('closetext'); s.op('end')
        texts = {'ask': T(nm + 'を<LINE>おしえて　あげようか？'),
                 'ok': T('これで　' + nm + 'も<LINE>ばっちりだね！<PARA>また　いつでも<LINE>おしえて　あげるよ！'),
                 'no': T('そうか<……><PARA>おぼえさせたく　なったら<LINE>いつでも　はなしかけてね！')}
    else:
        s.L('new')
        for fl, mv, nm in teach: s.op('checkevent', (fl,)); s.op('iftrue', 'any')
        s.op('sjump', 'orig')
        # いいえ：ジュースの 会話へ（文を とじて もとの スクリプトの はじめから）
        s.L('any'); s.op('faceplayer'); s.op('opentext'); s.op('writetext', 'ask'); s.op('yesorno'); s.op('iffalse', 'juice')
        texts = {'ask': T('わざマシンの　わざを<LINE>おしえて　あげようか？'), 'bye': T('また　いつでも<LINE>おしえて　あげるね！')}
        for k, (fl, mv, nm) in enumerate(teach):
            s.op('checkevent', (fl,)); s.op('iffalse', 'n%d' % k)
            s.op('writetext', 'q%d' % k); s.op('yesorno'); s.op('iffalse', 'n%d' % k)
            s.op('setval', MV[mv]); s.op('callasm', nb, (sym['Tutor'],))
            s.L('n%d' % k)
            texts['q%d' % k] = T(nm + 'を<LINE>おぼえさせる？')
        s.op('writetext', 'bye'); s.op('waitbutton'); s.op('closetext'); s.op('end')
        s.L('juice'); s.op('closetext')
    s.L('orig'); s.op('sjump', (orig_ptr,))
    for k, v in texts.items(): s.L(k); s.raw(v)
    return s


def install(E, g, log):
    """バンクを 1つ つかって asm を 置き、c2g.EXTRA_TUTOR に マップごとの 処理を 入れる"""
    nb = E.next_bank; E.next_bank += 1
    MV = consts(PG + '/constants/move_constants.asm')
    names = all_moves(); moves = [MV[m] for m in names]; tabs = []
    for m in names:
        lst = red_learners(m); bits = bytearray(32)
        for sp in lst: bits[(sp - 1) >> 3] |= 1 << ((sp - 1) & 7)
        tabs.append(bits); log.append('教え技 %s：%d ひき' % (m, len(lst)))
    code, sym = asm_bytes(0x4000, moves, tabs)
    o = fo(nb, 0x4000); assert not any(x not in (0, 0xFF) for x in g[o:o + len(code)])
    g[o:o + len(code)] = code
    log.append('教え技の asm：%02X:4000（%d バイト）' % (nb, len(code)))
    pp = fo(0x02, 0x4B5B) + 3 * 0x0E                       # predef CanLearnTMHMMove → CanLearnHook
    assert g[pp:pp + 3] == bytes([0xBF, 0x59, 0x04]), g[pp:pp + 3].hex()
    h = sym['CanLearnHook']; g[pp:pp + 3] = bytes([h & 0xFF, h >> 8, nb])
    X = E.X
    for gym in GYMS:
        called = c2g.EV_POOL.pop(0)
        hide = c2g.EV_POOL.pop(0) if gym[5] is None else None
        badge = c2g.G['engine'][gym[2]]
        def f(E_, gb, alloc, grom, coords, objs, cbs, gym=gym, called=called, hide=hide, badge=badge):
            cname, _, _, mv, _, gpos, cells = gym
            if gpos is None:                                       # 案内の 人を 足す（クチバジムの 案内の 人と 同じ 形）
                gpos = CELADON_GUIDE
                ob = bytearray([0x48, gpos[1] + 4, gpos[0] + 4, 0x06, 0x00, 0xFF, 0xFF, 0x90, 0x01, 0, 0, hide & 0xFF, hide >> 8])
                objs.append(ob); gi = len(objs) - 1; orig = None
            else:
                gi = [i for i, ob in enumerate(objs) if (ob[2] - 4, ob[1] - 4) == gpos]
                assert len(gi) == 1 and objs[gi[0]][0] == 0x48, (cname, gi)
                gi = gi[0]; orig = objs[gi][9] | objs[gi][10] << 8
            gid = gi + 2                                           # 人の 番号：0 プレイヤー、1 連れ歩き、マップの 人は 2 から
            args = (gym, gid, orig, called, hide, badge, MV[mv], nb, sym)
            n = len(gym_script(0x4000, *args).done())
            a = alloc(n, gb); sc = gym_script(a, *args); data = sc.done()
            grom[fo(gb, a):fo(gb, a) + len(data)] = data
            objs[gi][9:11] = sc.lab['guide'].to_bytes(2, 'little')
            for i, (px, py) in enumerate(sorted(cells)):
                coords.append(bytes([0xFF, py, px, 0]) + sc.lab['lv%d' % i].to_bytes(2, 'little') + b'\0\0')
            if hide is not None: cbs.append((2, sc.lab['cb_obj']))   # MAPCALLBACK_OBJECTS
            log.append('教え技 %s：案内 %d番 %s、フラグ %03X%s、スクリプト %02X:%04X（%d バイト）' % (
                cname, gid, gpos, called, '・%03X' % hide if hide is not None else '', gb, a, len(data)))
        c2g.EXTRA_TUTOR[gym[0]] = f
    for cname, pos, teach, guard in NPCS:
        def f(E_, gb, alloc, grom, coords, objs, cbs, cname=cname, pos=pos, teach=teach, guard=guard):
            gi = [i for i, ob in enumerate(objs) if (ob[2] - 4, ob[1] - 4) == pos]
            assert len(gi) == 1, (cname, pos, gi)
            gi = gi[0]; orig = objs[gi][9] | objs[gi][10] << 8
            tc = [(X.event(fl, cname), mv, nm) for fl, mv, nm in teach]
            gd = X.event(guard, cname) if guard is not None else None
            n = len(npc_script(0x4000, tc, gd, orig, MV, nb, sym).done())
            a = alloc(n, gb); sc = npc_script(a, tc, gd, orig, MV, nb, sym); data = sc.done()
            grom[fo(gb, a):fo(gb, a) + len(data)] = data
            objs[gi][9:11] = sc.lab['new'].to_bytes(2, 'little')
            log.append('教え技 %s %s：%s フラグ %s、スクリプト %02X:%04X（%d バイト）' % (
                cname, pos, '/'.join(t[1] for t in tc), ' '.join('%03X' % t[0] for t in tc), gb, a, len(data)))
        c2g.EXTRA_TUTOR[cname] = f
    return nb


def native(E, g, M, cm, log):
    """金の マップの ままの ジム：金の スクリプトを うつしなおして（gold_rebuild）、案内の 人と 入口の イベントを 足す"""
    import gold_rebuild as gr, cwalk
    from cmaps import maplist, GMGP
    GV = open('/home/claude/work/ref/kin64.gbc', 'rb').read()
    gm = {m['name']: m for m in maplist(GV, GMGP, 'pokegold')}
    for nm in NATIVE:
        f = c2g.EXTRA_TUTOR.pop(nm)
        MB = cwalk.Walk(M).map(cm[nm]['attr'], nm)['scbank']
        gr.rebuild(E, g, GV, gm[nm], nm, {'text': {}, 'hook': f}, M, MB, log)
    left = sorted(k for k in c2g.EXTRA_TUTOR if k not in NATIVE)
    return left
