"""ピカチュウ版フルカラーパッチ（pika.gbc）から サファリゾーンの マップ・タイルセットを取り出して
   src/safari/safari_gen.asm を作る（金 日本版用）。
   python3 tools/safari_gen.py ピカチュウ.gbc 金.gbc > src/safari/safari_gen.asm
"""
import sys, os

PK = open(sys.argv[1], 'rb').read()
GD = open(sys.argv[2], 'rb').read()

def rd16(d, o): return d[o] | d[o + 1] << 8
def off(b, a): return b * 0x4000 + a - 0x4000 if a >= 0x4000 else a

# ---- ピカチュウ版の表（tools で調べた場所）
PK_MAPPTRS = 0xfc1f2
PK_MAPBANKS = 0xfc3e4
PK_TILESETS = 0xc54b
PK_PALMAP = 0xec200      # タイルセットごと 256バイト（タイル → 色の番号）
PK_COLL_BANK = 1

def pk_header(m):
    b = PK[PK_MAPBANKS + m]; o = off(b, rd16(PK, PK_MAPPTRS + 2 * m))
    h = dict(bank=b, tileset=PK[o], h=PK[o + 1], w=PK[o + 2], blocks=rd16(PK, o + 3))
    conn = PK[o + 9]; o2 = o + 10
    for bit in range(4):
        if conn & (1 << bit): o2 += 11
    oo = off(b, rd16(PK, o2))
    h['border'] = PK[oo]
    h['data'] = PK[off(b, h['blocks']):off(b, h['blocks']) + h['h'] * h['w']]
    return h

def pk_tileset(i):
    e = PK[PK_TILESETS + 12 * i:PK_TILESETS + 12 * i + 12]
    t = dict(bank=e[0], blocks=e[1] | e[2] << 8, gfx=e[3] | e[4] << 8, coll=e[5] | e[6] << 8, grass=e[10])
    o = off(PK_COLL_BANK, t['coll']); lst = []
    while PK[o] != 0xff: lst.append(PK[o]); o += 1
    t['pass'] = lst
    return t

# ---- 金のコリジョン
FLOOR, WALL, TALL_GRASS, WATER, COUNTER = 0x00, 0x07, 0x18, 0x29, 0x90
DOOR, CARPET_DOWN, CARPET_LEFT, CARPET_UP, CARPET_RIGHT = 0x71, 0x70, 0x76, 0x78, 0x7e

# 3つのタイルセット：ピカチュウ版の番号, 金の新しい番号, 名前, マップ
TILESETS = [
    (3, 0x1d, 'SafariOut', [0xdc, 0xd9, 0xda, 0xdb]),
    (12, 0x1e, 'SafariGate', [0x9c, 0xdd, 0xdf, 0xe0, 0xe1]),
    (20, 0x1f, 'SafariLab', [0xde]),
]
# マップ：ピカチュウ版の番号, 名前, ワープ（x, y）
MAPS = {
    0x9c: ('SafariGate', [(3, 5), (4, 5), (3, 0), (4, 0)]),
    0xdc: ('SafariCenter', [(14, 25), (15, 25), (0, 10), (0, 11), (14, 0), (15, 0), (29, 10), (29, 11), (17, 19)]),
    0xd9: ('SafariEast', [(0, 4), (0, 5), (0, 22), (0, 23), (25, 9)]),
    0xda: ('SafariNorth', [(2, 35), (3, 35), (8, 35), (9, 35), (20, 35), (21, 35), (39, 30), (39, 31), (35, 3)]),
    0xdb: ('SafariWest', [(20, 0), (21, 0), (26, 0), (27, 0), (29, 22), (29, 23), (3, 3), (11, 11)]),
    0xdd: ('SafariCenterRest', [(2, 7), (3, 7)]),
    0xde: ('SafariSecret', [(2, 7), (3, 7)]),
    0xdf: ('SafariWestRest', [(2, 7), (3, 7)]),
    0xe0: ('SafariEastRest', [(2, 7), (3, 7)]),
    0xe1: ('SafariNorthRest', [(2, 7), (3, 7)]),
}

def lz_literal(data):
    """金銀の LZ（文字そのままの命令だけ）"""
    out = bytearray(); i = 0
    while i < len(data):
        n = min(1024, len(data) - i)
        if n <= 32:
            out.append(n - 1)
        else:
            out.append(0xe0 | ((n - 1) >> 8)); out.append((n - 1) & 0xff)
        out += data[i:i + n]; i += n
    out.append(0xff)
    return bytes(out)

def db_lines(data, per=16):
    return ['\tdb ' + ', '.join('$%02x' % x for x in data[i:i + per]) for i in range(0, len(data), per)]

out = []
P = out.append
P('; 自動生成（tools/safari_gen.py）：ピカチュウ版フルカラーパッチの サファリゾーンの マップ・タイルセット')
P('')
for pk_ts, gd_ts, name, maps in TILESETS:
    P(f'DEF TILESET_{name.upper()} EQU ${gd_ts:02x}')
P('')

# ---- タイルセットごと
pal_sections = []
P('SECTION "safari data", ROMX[$4000], BANK[SAFARI_DATA_BANK]')
for pk_ts, gd_ts, name, maps in TILESETS:
    t = pk_tileset(pk_ts)
    bo = off(t['bank'], t['blocks']); go = off(t['bank'], t['gfx'])
    hdrs = {m: pk_header(m) for m in maps}
    nblk = max(max(h['data']) for h in hdrs.values()) + 1
    nblk = max(nblk, max(h['border'] for h in hdrs.values()) + 1)
    blocks = [list(PK[bo + 16 * b:bo + 16 * b + 16]) for b in range(nblk)]

    def cellcoll(tid):
        if pk_ts == 3:
            if tid == t['grass']: return TALL_GRASS
            if tid in (0x14, 0x48, 0x32): return WATER
        if pk_ts == 12 and tid in (0x17, 0x32): return COUNTER
        return FLOOR if tid in t['pass'] else WALL

    def blockcoll(blk):
        return [cellcoll(blocks[blk][(cy * 2 + 1) * 4 + cx * 2]) for cy in range(2) for cx in range(2)]

    colls = [blockcoll(b) for b in range(nblk)]
    # ワープのマスは 金のワープの当たりにする（ブロックを写して 当たりだけ変える）
    variants = {}
    base_of = {}
    mapblocks = {}
    for m in maps:
        h = hdrs[m]; W, H = h['w'], h['h']; data = list(h['data'])
        mname, warps = MAPS[m]
        for (x, y) in warps:
            if y == H * 2 - 1: c = CARPET_DOWN
            elif y == 0: c = CARPET_UP
            elif x == 0: c = CARPET_LEFT
            elif x == W * 2 - 1: c = CARPET_RIGHT
            else: c = DOOR
            bi = (y // 2) * W + x // 2
            cur = data[bi]
            base = base_of.get(cur, cur)
            cl = list(colls[cur])
            cl[(y % 2) * 2 + x % 2] = c
            key = (base, tuple(cl))
            if key not in variants:
                variants[key] = len(blocks); base_of[len(blocks)] = base
                blocks.append(blocks[base]); colls.append(cl)
            data[bi] = variants[key]
        mapblocks[m] = data
    # 金は マップの ブロック 0 を「まわりの ブロック」に して しまう（LoadMetatiles）ので、
    # マップの中の ブロック 0 は 同じ中身の 新しい ブロックに する
    if any(0 in d for d in mapblocks.values()):
        z = len(blocks); blocks.append(blocks[0]); colls.append(list(colls[0]))
        for m in maps:
            mapblocks[m] = [z if b == 0 else b for b in mapblocks[m]]
    assert len(blocks) <= 256
    gfx = PK[go:go + 0x60 * 16]
    P(f'{name}GFX::')
    out.extend(db_lines(lz_literal(gfx)))
    P(f'{name}Meta::')
    for b in blocks: out.extend(db_lines(bytes(b)))
    P(f'{name}Coll::')
    for c in colls: P('\tdb ' + ', '.join('$%02x' % x for x in c))
    for m in maps:
        mname = MAPS[m][0]; h = hdrs[m]
        P(f'{mname}_Blocks::')
        out.extend(db_lines(bytes(mapblocks[m]), h['w']))
        P(f'DEF {mname.upper()}_WIDTH EQU {h["w"]}')
        P(f'DEF {mname.upper()}_HEIGHT EQU {h["h"]}')
        P(f'DEF {mname.upper()}_BORDER EQU ${h["border"]:02x}')
    P('')
    # 色の対応（バンク$02 に置く。96タイル＝48バイト ＋ 文字のタイル 16バイト）
    pm = PK[PK_PALMAP + pk_ts * 0x100:PK_PALMAP + pk_ts * 0x100 + 0x60]
    pal = bytes((pm[2 * i] & 7) | ((pm[2 * i + 1] & 7) << 4) for i in range(0x30)) + bytes([0x77] * 16)
    pal_sections.append((name, pal))

# ---- タイルセットの表（元の 29こ をそのまま写して 3つ足す）
GD_TILESETS = 5 * 0x4000 + 0x562b - 0x4000
P('SafariTilesetTable::')
for i in range(29):
    e = GD[GD_TILESETS + 15 * i:GD_TILESETS + 15 * i + 15]
    if i == 3:   # カントー：ブロックを 1つ足した表にする（セキチクの サファリの入口の ドア）
        P(f'\tdb ${e[0]:02x}, ${e[1]:02x}, ${e[2]:02x}\n\tdb BANK(SafariKantoMeta)\n\tdw SafariKantoMeta\n\tdb BANK(SafariKantoColl)\n\tdw SafariKantoColl')
        out.extend(db_lines(e[9:], 15))
    else:
        out.extend(db_lines(e, 15))
for pk_ts, gd_ts, name, maps in TILESETS:
    anim = 'SafariWaterAnim' if pk_ts == 3 else 'J_TilesetHouseAnim'
    P(f'\tdb BANK({name}GFX)\n\tdw {name}GFX\n\tdb BANK({name}Meta)\n\tdw {name}Meta\n\tdb BANK({name}Coll)\n\tdw {name}Coll\n\tdw {anim}, 0, {name}PalMap')
P('')
# カントーの ブロック（128こ）に $80 を足す：$7d（入口の建物の かべ）の 左下に $7c の ドアを入れたもの
ke = GD[GD_TILESETS + 45:GD_TILESETS + 60]
km = off(ke[3], ke[4] | ke[5] << 8); kc = off(ke[6], ke[7] | ke[8] << 8)
meta = bytearray(GD[km:km + 128 * 16]); coll = bytearray(GD[kc:kc + 128 * 4])
b7c = meta[0x7c * 16:0x7c * 16 + 16]; b7d = meta[0x7d * 16:0x7d * 16 + 16]
nb = bytearray(b7d)
for r in (2, 3):
    nb[r * 4 + 0] = b7c[r * 4 + 2]; nb[r * 4 + 1] = b7c[r * 4 + 3]
meta += nb; coll += bytes([WALL, WALL, DOOR, WALL])
P('SafariKantoMeta::'); out.extend(db_lines(bytes(meta)))
P('SafariKantoColl::'); out.extend(db_lines(bytes(coll)))
P('')
P('SECTION "safari palmaps", ROMX[SAFARI_PALMAP_ADDR], BANK[2]')
for name, pal in pal_sections:
    P(f'{name}PalMap::')
    out.extend(db_lines(pal))
P('')
print('\n'.join(out))

# ---- 文章（ピカチュウ版の バイトを そのまま写す。日本版 金銀と 同じ文字コード）
def text_bytes(a, stop_at_end=True):
    """a = 文の頭（$00 の所）。$57・$58（おわり）か $50（つづく）まで"""
    o = a + 1; out = bytearray([0])
    while True:
        c = PK[o]; out.append(c); o += 1
        if c in (0x57, 0x58): break
        if c == 0x50: break
    return bytes(out)

TEXTS = [
    # 入口
    ('SafariText_Welcome', 0x7557e),
    ('SafariText_Join', 0xf1c42),
    ('SafariText_ThatsAll1', 0xf1c7a),      # それでは……！<LINE>@
    ('SafariText_ThatsAll2', 0xf1c87),      # 円 いただきまーす！… 30こ もらった！@
    ('SafariText_ThatsAll3', 0xf1cda),      # <PARA>のこり じかんが なくなるか！…
    ('SafariText_ComeAgain', 0xf1d17),
    ('SafariText_NotEnough', 0xf1d29),
    ('SafariText_LowCost1', 0xf1e60),
    ('SafariText_LowCost2', 0xf1e75),
    ('SafariText_LowCost34', 0xf1eaf),      # <PARA>まったく… ラッキー！…（@ のあとに 音、<DONE>）
    ('SafariText_LowCost5', 0xf1ee7),
    ('SafariText_LowCost6', 0xf1eff),
    ('SafariText_LowCost7', 0xf1f11),
    ('SafariText_LowCost8', 0xf1f2a),
    ('SafariText_LeavingEarly', 0x7559b),   # もう おわりに する？@
    ('SafariText_ReturnBalls', 0x755f0),
    ('SafariText_GoodLuck', 0x7560b),
    ('SafariText_GoodHaul', 0x75616),
    ('SafariText_FirstTime', 0xf1d51),
    ('SafariText_Explain', 0xf1d68),
    ('SafariText_Regular', 0xf1de8),
    # アナウンス
    ('SafariText_TimesUp', 0x1fa13),
    ('SafariText_GameOver', 0x1fa2c),
    ('SafariText_OutOfBalls', 0x3c1c1),
    # セキチクシティの 看板（入口の となり）
    ('SafariText_FuchsiaSign', 0x1a9a5),   # めいぶつ！ サファリ ゲーム！ …… ポケモン とりほうだい！
]
def map_text(m, i):
    b = PK[PK_MAPBANKS + m]; o = off(b, rd16(PK, PK_MAPPTRS + 2 * m))
    tp = rd16(PK, o + 5)
    return off(b, rd16(PK, off(b, tp) + 2 * (i - 1)))
MAPTEXTS = [
    ('SafariCenter_RestHouseSignText', 0xdc, 2), ('SafariCenter_TipsSignText', 0xdc, 3),
    ('SafariEast_Sign5Text', 0xd9, 5), ('SafariEast_Sign6Text', 0xd9, 6), ('SafariEast_Sign7Text', 0xd9, 7),
    ('SafariNorth_Sign3Text', 0xda, 3), ('SafariNorth_Sign4Text', 0xda, 4), ('SafariNorth_Sign5Text', 0xda, 5),
    ('SafariNorth_Sign6Text', 0xda, 6), ('SafariNorth_Sign7Text', 0xda, 7),
    ('SafariWest_Sign5Text', 0xdb, 5), ('SafariWest_Sign6Text', 0xdb, 6), ('SafariWest_Sign7Text', 0xdb, 7),
    ('SafariWest_Sign8Text', 0xdb, 8),
    ('SafariCenterRest_GirlText', 0xdd, 1), ('SafariCenterRest_ScientistText', 0xdd, 2),
    ('SafariWestRest_ScientistText', 0xdf, 1), ('SafariWestRest_CooltrainerText', 0xdf, 2),
    ('SafariWestRest_SilphText', 0xdf, 3),
    ('SafariEastRest_ScientistText', 0xe0, 1), ('SafariEastRest_RockerText', 0xe0, 2),
    ('SafariEastRest_SilphText', 0xe0, 3),
    ('SafariNorthRest_ScientistText', 0xe1, 1), ('SafariNorthRest_WorkerText', 0xe1, 2),
    ('SafariNorthRest_GentlemanText', 0xe1, 3),
]
P = print
P('SECTION "safari texts", ROMX[SAFARI_TEXT_ADDR], BANK[SAFARI_SCRIPT_BANK]')
for lab, a in TEXTS:
    t = text_bytes(a)
    if t[-1] == 0x50: t += bytes([0x50])   # 文の おわり（@）のあとに 文章の おわり（text_end）
    P(f'{lab}::'); P('\n'.join(db_lines(t)))
for lab, m, i in MAPTEXTS:
    a = map_text(m, i)
    assert PK[a] == 0, (lab, hex(a))
    P(f'{lab}::'); P('\n'.join(db_lines(text_bytes(a))))
# ひみつの家：「…ふあんに なってた ところだ」まで（ひでんマシンは 渡さないので しょうひんの話は 出さない）
a = 0x4bdbf
t = text_bytes(a)
t = t[:t.rindex(0x51)] + bytes([0x57])   # 「いやー！ おめでとう！ しょうひんは…」の前で おわり
P('SafariSecret_GuruText::'); P('\n'.join(db_lines(t)))

# ---- 組み合わせる文章
def tb(a): return text_bytes(a)
DIG = [0xf6 + i for i in range(10)]   # 0〜9
pay = tb(0xf1c7a)[:-1] + bytes([DIG[5], DIG[0], DIG[0]]) + tb(0xf1c87)[1:] + bytes([0x0f]) + tb(0xf1cda)
P('SafariText_Pay::'); P('\n'.join(db_lines(pay)))
oneball = tb(0xf1eaf) + bytes([0x0f, 0x00, 0x57])
P('SafariText_OneBall::'); P('\n'.join(db_lines(oneball)))

# ---- 戦闘の文章（ピカチュウ版。RAM の 名前の場所だけ 金の場所に かえる）
RAM_MAP = {0xcfc1: 0xcaf6}   # 相手の ポケモンの 名前（wEnemyMonNick → wEnemyMonNickname）
def text_full(a):
    o = a; out = bytearray()
    while True:
        c = PK[o]; o += 1; out.append(c)
        if c == 0x00:
            while True:
                c = PK[o]; o += 1; out.append(c)
                if c in (0x50, 0x57, 0x58): break
            if c in (0x57, 0x58): return bytes(out)
        elif c == 0x01:
            r = RAM_MAP[rd16(PK, o)]; out += bytes([r & 0xff, r >> 8]); o += 2
        elif c == 0x50:
            return bytes(out)
        else:
            raise ValueError(hex(c))
BTEXTS = [
    ('SafariText_Eating', 0x4141),      # やせいの ○○は エサを たべてる！
    ('SafariText_Angry', 0x4157),       # やせいの ○○は おこってる！
    ('SafariText_ThrewBait', 0xde80),   # ○○は エサを なげた！
    ('SafariText_ThrewRock', 0xde8d),   # ○○は いしを なげた！
    ('SafariText_BallMissed', 0xd69c),  # ポケモンに うまく あたらなかった！
    ('SafariText_BallBroke', 0xd6ad),   # ざんねん！ ポケモンが ボールから でてしまった！
    ('SafariText_BallAww', 0xd6c5),     # ああ！ つかまえたと おもったのに！
    ('SafariText_BallClose', 0xd6d9),   # おしい！ あと ちょっとの ところだったのに！
    ('SafariText_Fled', 0x3c260),       # やせいの ○○は にげだした！
    ('SafariText_GotAway', 0x3cd71),    # うまく にげきれた！
    ('SafariText_BoxFull', 0xe786),     # ボックスに あずけている ポケモンが いっぱいなので つかえません！
    ('SafariText_FishNoBite', 0x708d9), # つれないなー……
    ('SafariText_FishBite', 0x708f0),   # おっ！ ひいてる ひいてる！
]
for lab, a in BTEXTS:
    P(f'{lab}::'); P('\n'.join(db_lines(text_full(a))))

# ---- セキチクの「サファリが しまっている」話を かえる 文
# ピカチュウ版の セキチクの 人・看板の 文（そのまま）
FTEXTS = [
    ('SafariText_Granddaughter2', 0x74fa3),  # サファリ ゾーンの えんちょう おとし なのに すごく げんきよ でも……
    ('SafariText_OfficeMan', 0x1a8e6),       # サファリ ゾーンは いりぐち ふきんは どうぶつえんで おくに いくと…サファリ ゲームじゃ
]
for lab, a in FTEXTS:
    P(f'{lab}::'); P('\n'.join(db_lines(text_full(a))))
# えんちょうの まごの 1つめ：金の 文の さいごの 段（「そのとき サファリゾーンを やめちゃったの！」）だけ かえる
import re as _re
_cm = {}
for _l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'charmap_jp.inc'), encoding='utf-8'):
    _m = _re.match(r'\s*charmap\s+"(.+?)",\s*\$([0-9a-fA-F]+)', _l)
    if _m: _cm.setdefault(_m.group(1), int(_m.group(2), 16))
def enc(t):
    out = bytearray(); i = 0
    ctl = {'<LINE>': 0x4f, '<PARA>': 0x51, '<CONT>': 0x55, '<DONE>': 0x57}
    while i < len(t):
        for k, v in ctl.items():
            if t.startswith(k, i): out.append(v); i += len(k); break
        else:
            for n in (2, 1):
                if t[i:i + n] in _cm: out.append(_cm[t[i:i + n]]); i += n; break
            else: raise ValueError(t[i])
    return bytes(out)
GD_GRANDDAUGHTER1 = off(0x2d, 0x63d3)
g1 = GD[GD_GRANDDAUGHTER1:GD.index(0x57, GD_GRANDDAUGHTER1) + 1]
SAFARI_KANA = bytes([0x8a, 0x9b, 0xe9, 0xd8, 0x0e, 0xe3, 0xab])      # サファリゾーン（金の 文の まま）
cut = g1.rindex(0x51)                                                # さいごの 段
g1 = g1[:cut] + bytes([0x51]) + SAFARI_KANA + enc('は<LINE>かかりの　ひとたちが<CONT>ちゃんと　あけて　くれてるわ！<DONE>')
P('SafariText_Granddaughter1::'); P('\n'.join(db_lines(g1)))
# 戦闘の メニュー（「サファリボール×   エサをなげる／いしをなげる     にげる」）
MENU = 0x7754
m = PK[MENU:PK.index(0x50, MENU)]
name = m[:m.index(0xf1)]                       # サファリボール
row1, row2 = m.split(bytes([0x4e]))
items = [row1[:row1.index(0xf1) + 1], row1[row1.index(0xf1) + 1:].strip(b'\x7f'), row2.split(b'\x7f')[0], row2.strip(b'\x7f').split(b'\x7f')[-1]]
P('SafariMenuItems::')
for it in items: P('\n'.join(db_lines(it + b'\x50')))
# ○○は サファリボールを つかった！（ピカチュウ版は 道具の名前を RAM から出す。ここでは 名前を そのまま入れる）
use = bytes([0x00, 0x52, 0xca, 0x50, 0x05, 0x00]) + name + bytes([0x50]) + PK[0xe7bd:0xe7c6]
P('SafariText_UseBall::'); P('\n'.join(db_lines(use)))

# ---- 野生のポケモン（ピカチュウ版の 10こ。レベル, 図鑑の番号＝金の番号）
PK_WILD = 0xcb88; PK_DEXORDER = 0x42833
def wild(m):
    a = rd16(PK, PK_WILD + 2 * m); o = 3 * 0x4000 + a - 0x4000
    r = PK[o]; o += 1
    mons = [(PK[o + 2 * k], PK[PK_DEXORDER + PK[o + 2 * k + 1] - 1]) for k in range(10)]
    return r, mons
P('SECTION "safari wild", ROMX[SAFARI_WILD_ADDR], BANK[SAFARI_SCRIPT_BANK]')
for m, name in ((0xdc, 'SafariCenter'), (0xd9, 'SafariEast'), (0xda, 'SafariNorth'), (0xdb, 'SafariWest')):
    r, mons = wild(m)
    P(f'{name}_WildMons::')
    P(f'\tdb {r} ; くさむらで 出る確率（/256）')
    for lv, sp in mons: P(f'\tdb {lv}, {sp}')

# ---- 金の 文の 場所に そのまま 書く（日本版 金には text_far が ないので、元より 短い 文だけ）
INPLACE = [
    ('FuchsiaTeacherText', 0x1a8ba, 0x36, 0x70e1),  # サファリゾーンは おやすみちゅう… → サファリ ゲーム もう やった？…
    ('SafariOfficeSignText', 0x1a9d8, 0x36, 0x7155),# じむきょくは きゅうぎょうちゅう → いろんな ポケモン いっぱい！ サファリ ゾーンに ようこそ！
    ('FuchsiaMartFisherText', 0x1e869, 0x2d, 0x5d48),# おみやげ…きゅうぎょうちゅう → ペナントは ないのかね？…
]
for lab, a, b, ga in INPLACE:
    t = text_full(a); go = off(b, ga); n = GD.index(0x57, go) - go + 1
    assert len(t) <= n, lab
    P(f'SECTION "safari {lab}", ROMX[${ga:04x}], BANK[${b:02x}]')
    P('\n'.join(db_lines(t)))

# ---- ずかんの「ぶんぷをみる」用（src/fishnest.asm が 読む。3つめの 引数が あれば そのファイルに 書く）
#   草むら：4つの マップの 表に 出る ポケモン。つり：ボロ・いい・すごい（サファリの中）で つれる ポケモン
if len(sys.argv) > 3:
    grass = []
    for m in (0xdc, 0xd9, 0xda, 0xdb):
        for lv, sp in wild(m)[1]:
            if sp not in grass: grass.append(sp)
    fish = [129, 118, 60, 147, 148]   # コイキング・トサキント・ニョロモ・ミニリュウ・ハクリュー（safari.asm の SafariFish）
    with open(sys.argv[3], 'w') as f:
        f.write('; tools/safari_gen.py で 作った（サファリゾーンで 出る ポケモン。図鑑の 番号）\n')
        f.write('FishNestExtraGrass:\n\tdb ' + ', '.join(str(x) for x in grass) + ', 0\n')
        f.write('FishNestExtraFish:\n\tdb ' + ', '.join(str(x) for x in fish) + ', 0\n')
