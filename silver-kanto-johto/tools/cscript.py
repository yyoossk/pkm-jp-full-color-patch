"""日本版クリスタル（と 銀）の スクリプトを 読む 道具。
   命令の 番号は 英語版 pokecrystal から farjumptext（$52）を 抜いた もの（$00〜$A3）。
   $00〜$9D は 日本版の 銀と 同じ 番号・同じ 形。"""
import re, os
from gsc import fo, r16, H

# 引数の 形：b=1バイト w=2バイト p=同じバンクの スクリプト t=同じバンクの テキスト m=同じバンクの 動き
#            F=3バイト（バンク+アドレス）の スクリプト T=3バイトの テキスト A=3バイトの アセンブリ
#            E=イベントフラグ(2) G=エンジンフラグ(2) S=special(2) D=std(2) M=マップ(2) I=どうぐ
#            K=ポケモン X=そのほか 3バイト  N=ネームの ポインタ(2) Q=曲(2) Y=効果音(2) C=鳴き声(2)
#            R=読む データの ポインタ(2) U=メニューの ヘッダー(2) O=人の 番号 P=人の絵(sprite) L=トレーナーの グループ
# 最後の 'end' は ここで スクリプトが 終わる（つぎを 読まない）
CMDS = {
    0x00: ('scall', 'p'), 0x01: ('farscall', 'F'), 0x02: ('memcall', 'w'), 0x03: ('sjump', 'p', 'end'),
    0x04: ('farsjump', 'F', 'end'), 0x05: ('memjump', 'w', 'end'), 0x06: ('ifequal', 'bp'), 0x07: ('ifnotequal', 'bp'),
    0x08: ('iffalse', 'p'), 0x09: ('iftrue', 'p'), 0x0a: ('ifgreater', 'bp'), 0x0b: ('ifless', 'bp'),
    0x0c: ('jumpstd', 'D', 'end'), 0x0d: ('callstd', 'D'), 0x0e: ('callasm', 'A'), 0x0f: ('special', 'S'),
    0x10: ('memcallasm', 'w'), 0x11: ('checkmapscene', 'M'), 0x12: ('setmapscene', 'Mb'), 0x13: ('checkscene', ''),
    0x14: ('setscene', 'b'), 0x15: ('setval', 'b'), 0x16: ('addval', 'b'), 0x17: ('random', 'b'), 0x18: ('checkver', ''),
    0x19: ('readmem', 'w'), 0x1a: ('writemem', 'w'), 0x1b: ('loadmem', 'wb'), 0x1c: ('readvar', 'b'),
    0x1d: ('writevar', 'b'), 0x1e: ('loadvar', 'bb'), 0x1f: ('giveitem', 'Ib'), 0x20: ('takeitem', 'Ib'),
    0x21: ('checkitem', 'I'), 0x22: ('givemoney', 'bbbb'), 0x23: ('takemoney', 'bbbb'), 0x24: ('checkmoney', 'bbbb'),
    0x25: ('givecoins', 'w'), 0x26: ('takecoins', 'w'), 0x27: ('checkcoins', 'w'), 0x28: ('addcellnum', 'b'),
    0x29: ('delcellnum', 'b'), 0x2a: ('checkcellnum', 'b'), 0x2b: ('checktime', 'b'), 0x2c: ('checkpoke', 'K'),
    0x2d: ('givepoke', 'GIVEPOKE'), 0x2e: ('giveegg', 'Kb'), 0x2f: ('givepokemail', 'R'), 0x30: ('checkpokemail', 'R'),
    0x31: ('checkevent', 'E'), 0x32: ('clearevent', 'E'), 0x33: ('setevent', 'E'), 0x34: ('checkflag', 'G'),
    0x35: ('clearflag', 'G'), 0x36: ('setflag', 'G'), 0x37: ('wildon', ''), 0x38: ('wildoff', ''),
    0x39: ('xycompare', 'R'), 0x3a: ('warpmod', 'bM'), 0x3b: ('blackoutmod', 'M'), 0x3c: ('warp', 'Mbb'),
    0x3d: ('getmoney', 'bb'), 0x3e: ('getcoins', 'b'), 0x3f: ('getnum', 'b'), 0x40: ('getmonname', 'Kb'),
    0x41: ('getitemname', 'Ib'), 0x42: ('getcurlandmarkname', 'b'), 0x43: ('gettrainername', 'Lbb'),
    0x44: ('getstring', 'tb'), 0x45: ('itemnotify', ''), 0x46: ('pocketisfull', ''), 0x47: ('opentext', ''),
    0x48: ('reanchormap', 'b'), 0x49: ('closetext', ''), 0x4a: ('writeunusedbyte', 'b'), 0x4b: ('farwritetext', 'T'),
    0x4c: ('writetext', 't'), 0x4d: ('repeattext', 'bb'), 0x4e: ('yesorno', ''), 0x4f: ('loadmenu', 'U'),
    0x50: ('closewindow', ''), 0x51: ('jumptextfaceplayer', 't', 'end'), 0x52: ('jumptext', 't', 'end'),
    0x53: ('waitbutton', ''), 0x54: ('promptbutton', ''), 0x55: ('pokepic', 'K'), 0x56: ('closepokepic', ''),
    0x57: ('_2dmenu', ''), 0x58: ('verticalmenu', ''), 0x59: ('loadpikachudata', ''), 0x5a: ('randomwildmon', ''),
    0x5b: ('loadtemptrainer', ''), 0x5c: ('loadwildmon', 'Kb'), 0x5d: ('loadtrainer', 'Lb'), 0x5e: ('startbattle', ''),
    0x5f: ('reloadmapafterbattle', ''), 0x60: ('catchtutorial', 'b'), 0x61: ('trainertext', 'b'),
    0x62: ('trainerflagaction', 'b'), 0x63: ('winlosstext', 'tt'), 0x64: ('scripttalkafter', ''),
    0x65: ('endifjustbattled', ''), 0x66: ('checkjustbattled', ''), 0x67: ('setlasttalked', 'O'),
    0x68: ('applymovement', 'Om'), 0x69: ('applymovementlasttalked', 'm'), 0x6a: ('faceplayer', ''),
    0x6b: ('faceobject', 'OO'), 0x6c: ('variablesprite', 'bP'), 0x6d: ('disappear', 'O'), 0x6e: ('appear', 'O'),
    0x6f: ('follow', 'OO'), 0x70: ('stopfollow', ''), 0x71: ('moveobject', 'Obb'), 0x72: ('writeobjectxy', 'O'),
    0x73: ('loademote', 'b'), 0x74: ('showemote', 'bOb'), 0x75: ('turnobject', 'Ob'), 0x76: ('follownotexact', 'OO'),
    0x77: ('earthquake', 'b'), 0x78: ('changemapblocks', 'X'), 0x79: ('changeblock', 'bbb'), 0x7a: ('reloadmap', ''),
    0x7b: ('refreshmap', ''), 0x7c: ('writecmdqueue', 'R'), 0x7d: ('delcmdqueue', 'b'), 0x7e: ('playmusic', 'Q'),
    0x7f: ('encountermusic', ''), 0x80: ('musicfadeout', 'Qb'), 0x81: ('playmapmusic', ''),
    0x82: ('dontrestartmapmusic', ''), 0x83: ('cry', 'C'), 0x84: ('playsound', 'Y'), 0x85: ('waitsfx', ''),
    0x86: ('warpsound', ''), 0x87: ('specialsound', ''), 0x88: ('autoinput', 'X'), 0x89: ('newloadmap', 'b'),
    0x8a: ('pause', 'b'), 0x8b: ('deactivatefacing', 'b'), 0x8c: ('sdefer', 'p'), 0x8d: ('warpcheck', ''),
    0x8e: ('stopandsjump', 'p', 'end'), 0x8f: ('endcallback', '', 'end'), 0x90: ('end', '', 'end'),
    0x91: ('reloadend', 'b', 'end'), 0x92: ('endall', '', 'end'), 0x93: ('pokemart', 'bw'), 0x94: ('elevator', 'R'),
    0x95: ('trade', 'b'), 0x96: ('askforphonenumber', 'b'), 0x97: ('phonecall', 't'), 0x98: ('hangup', ''),
    0x99: ('describedecoration', 'b'), 0x9a: ('fruittree', 'b'), 0x9b: ('specialphonecall', 'w'),
    0x9c: ('checkphonecall', ''), 0x9d: ('verbosegiveitem', 'Ib'),
    # ここから クリスタルだけ（銀の 番号は SILVER_OP）
    0x9e: ('verbosegiveitemvar', 'Ib'), 0x9f: ('swarm', 'bM'), 0xa0: ('halloffame', '', 'end'),
    0xa1: ('credits', '', 'end'), 0xa2: ('warpfacing', 'bMbb'), 0xa3: ('battletowertext', 'b'),
}
SILVER_OP = {i: i for i in range(0x9e)}
SILVER_OP.update({0x9f: 0x9e, 0xa0: 0x9f, 0xa1: 0xa0, 0xa2: 0xa1})   # swarm は 引数が ちがう（銀は マップだけ）
SIZES = {'b': 1, 'w': 2, 'p': 2, 't': 2, 'm': 2, 'F': 3, 'T': 3, 'A': 3, 'E': 2, 'G': 2, 'S': 2, 'D': 2, 'M': 2,
         'I': 1, 'K': 1, 'X': 3, 'R': 2, 'U': 2, 'O': 1, 'P': 1, 'L': 1, 'Q': 2, 'Y': 2, 'C': 2}


def decode(rom, bank, addr):
    """1つの 命令を 読む → (op, 名前, [(形, 値, ROMの位置)], 長さ, 終わりか)"""
    o = fo(bank, addr); op = rom[o]
    if op not in CMDS: raise ValueError('知らない 命令 %02X @ %02X:%04X' % (op, bank, addr))
    c = CMDS[op]; name, fmt = c[0], c[1]; end = len(c) > 2
    args = []; p = o + 1
    if fmt == 'GIVEPOKE':
        args += [('K', rom[p], p), ('b', rom[p + 1], p + 1), ('I', rom[p + 2], p + 2), ('b', rom[p + 3], p + 3)]
        trainer = rom[p + 3]; p += 4
        if trainer:
            args += [('N', r16(rom, p), p), ('N', r16(rom, p + 2), p + 2)]; p += 4
    else:
        for f in fmt:
            n = SIZES[f]
            if n == 1: v = rom[p]
            elif n == 2: v = r16(rom, p)
            else: v = (rom[p], r16(rom, p + 1))
            args.append((f, v, p)); p += n
    return op, name, args, p - o, end


def walk(rom, bank, addr, seen=None, refs=None, depth=0):
    """スクリプトを たどって、使って いる ものを すべて 集める
       refs: dict 形 → set((値, 位置, バンク))"""
    if seen is None: seen = set()
    if refs is None: refs = {}
    stack = [(bank, addr)]
    while stack:
        b, a = stack.pop()
        while True:
            if (b, a) in seen: break
            if not (0x4000 <= a < 0x8000): refs.setdefault('bad', set()).add((b, a)); break
            seen.add((b, a))
            try:
                op, name, args, ln, end = decode(rom, b, a)
            except ValueError as e:
                refs.setdefault('bad', set()).add((b, a)); break
            refs.setdefault('op', set()).add((op, fo(b, a), b))
            for f, v, p in args:
                refs.setdefault(f, set()).add((v, p, b))
                if f == 'p': stack.append((b, v))
                elif f == 'F': stack.append(v)
            a += ln
            if end: break
    return seen, refs
