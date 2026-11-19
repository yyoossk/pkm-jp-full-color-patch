"""ジョウトは 第二世代だけ（第60弾）：銀の ジョウトの データ・スクリプトの 第一世代の ポケモンを クリスタル版と 同じ
   置きかえ（同じ なかまの 第二世代、同じ レベル）に。草むら・水（phase_wild で クリスタル版の 表）の ほかに：
   ・むれ（草 $0A:$7F02・水 $0A:$7FBF）、つり（FishGroups $24:$6946 の 13 組と 時間の 組 $24:$6B2D）、
     ずつき・いわくだき（TreeMons $2E:$6470）、むしとり大会（$25:$7BDC）
   ・人から もらう・止まって いる ポケモン（銀の ジョウトの スクリプトの givepoke・giveegg・loadwildmon。
     いかりのみずうみの 赤い ギャラドスは そのまま）
   ・交換（クリスタル版の 表 15 こ を 銀の $3F:$7D00 へ。ジョウトの 4 つは 第二世代どうし、カントーは クリスタル版の 番号）
   ・コガネの ゲームコーナーの 景品（スクリプトの ほか メニューの 名前も）"""
TRADE_AT = 0x7D00
import os, sys, re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, gsc, cscript, jptext
from gsc import fo, r16

MAP = {
    'CATERPIE': 'LEDYBA', 'METAPOD': 'LEDYBA', 'BUTTERFREE': 'LEDIAN', 'WEEDLE': 'SPINARAK', 'KAKUNA': 'SPINARAK',
    'BEEDRILL': 'ARIADOS', 'PIDGEY': 'HOOTHOOT', 'PIDGEOTTO': 'NOCTOWL', 'PIDGEOT': 'NOCTOWL',
    'RATTATA': 'SENTRET', 'RATICATE': 'FURRET', 'SPEAROW': 'MURKROW', 'FEAROW': 'MURKROW',
    'EKANS': 'DUNSPARCE', 'ARBOK': 'DUNSPARCE', 'SANDSHREW': 'PHANPY', 'SANDSLASH': 'DONPHAN',
    'NIDORAN_F': 'SNUBBULL', 'NIDORINA': 'GRANBULL', 'NIDORAN_M': 'TEDDIURSA', 'NIDORINO': 'URSARING',
    'JIGGLYPUFF': 'SNUBBULL', 'WIGGLYTUFF': 'GRANBULL', 'ZUBAT': 'GLIGAR', 'GOLBAT': 'GLIGAR',
    'ODDISH': 'SUNKERN', 'GLOOM': 'SUNFLORA', 'VILEPLUME': 'SUNFLORA', 'PARAS': 'PINECO', 'PARASECT': 'FORRETRESS',
    'VENONAT': 'YANMA', 'VENOMOTH': 'YANMA', 'DIGLETT': 'PHANPY', 'DUGTRIO': 'DONPHAN', 'MEOWTH': 'AIPOM',
    'PERSIAN': 'AIPOM', 'PSYDUCK': 'MARILL', 'GOLDUCK': 'AZUMARILL', 'MANKEY': 'TEDDIURSA', 'PRIMEAPE': 'URSARING',
    'GROWLITHE': 'HOUNDOUR', 'ARCANINE': 'HOUNDOOM', 'POLIWAG': 'WOOPER', 'POLIWHIRL': 'QUAGSIRE',
    'POLIWRATH': 'QUAGSIRE', 'ABRA': 'NATU', 'KADABRA': 'XATU', 'MACHOP': 'TEDDIURSA', 'MACHOKE': 'URSARING',
    'BELLSPROUT': 'MAREEP', 'WEEPINBELL': 'FLAAFFY', 'TENTACOOL': 'CHINCHOU', 'TENTACRUEL': 'LANTURN',
    'GEODUDE': 'SLUGMA', 'GRAVELER': 'MAGCARGO', 'PONYTA': 'HOUNDOUR', 'RAPIDASH': 'HOUNDOOM',
    'SLOWPOKE': 'WOOPER', 'SLOWBRO': 'QUAGSIRE', 'MAGNEMITE': 'MAREEP', 'MAGNETON': 'FLAAFFY',
    'FARFETCH_D': 'NATU', 'DODUO': 'GIRAFARIG', 'DODRIO': 'GIRAFARIG', 'SEEL': 'DELIBIRD', 'DEWGONG': 'PILOSWINE',
    'SHELLDER': 'CORSOLA', 'CLOYSTER': 'CORSOLA', 'GASTLY': 'MISDREAVUS', 'HAUNTER': 'MISDREAVUS', 'ONIX': 'SHUCKLE',
    'DROWZEE': 'GIRAFARIG', 'HYPNO': 'GIRAFARIG', 'KRABBY': 'CORSOLA', 'KINGLER': 'CORSOLA',
    'VOLTORB': 'PINECO', 'ELECTRODE': 'FORRETRESS', 'EXEGGCUTE': 'HOPPIP', 'EXEGGUTOR': 'JUMPLUFF',
    'CUBONE': 'PHANPY', 'MAROWAK': 'DONPHAN', 'LICKITUNG': 'STANTLER', 'KOFFING': 'HOUNDOUR', 'WEEZING': 'HOUNDOOM',
    'RHYHORN': 'PHANPY', 'RHYDON': 'DONPHAN', 'CHANSEY': 'MILTANK', 'TANGELA': 'SUNKERN', 'HORSEA': 'REMORAID',
    'SEADRA': 'OCTILLERY', 'GOLDEEN': 'QWILFISH', 'SEAKING': 'QWILFISH', 'STARYU': 'CORSOLA', 'STARMIE': 'CORSOLA',
    'SCYTHER': 'HERACROSS', 'PINSIR': 'HERACROSS', 'JYNX': 'SNEASEL', 'ELECTABUZZ': 'FLAAFFY', 'MAGMAR': 'MAGCARGO',
    'TAUROS': 'MILTANK', 'MAGIKARP': 'REMORAID', 'GYARADOS': 'OCTILLERY', 'LAPRAS': 'MANTINE', 'DITTO': 'SMEARGLE',
    'EEVEE': 'SNEASEL', 'DRATINI': 'MANTINE', 'DRAGONAIR': 'MANTINE', 'DRAGONITE': 'MANTINE', 'GRIMER': 'SLUGMA',
    'MUK': 'MAGCARGO', 'VULPIX': 'HOUNDOUR', 'NINETALES': 'HOUNDOOM', 'PIKACHU': 'MAREEP', 'RAICHU': 'AMPHAROS',
    'CLEFAIRY': 'SNUBBULL', 'CLEFABLE': 'GRANBULL', 'KANGASKHAN': 'URSARING', 'AERODACTYL': 'SKARMORY'}
GIFT = {'EEVEE': 'SNEASEL', 'DRATINI': 'LARVITAR', 'SPEAROW': 'MURKROW', 'LAPRAS': 'MANTINE', 'ELECTRODE': 'FORRETRESS'}


def mons():
    N = {}; v = 0
    for l in open(os.path.join(gsc.PG, 'constants', 'pokemon_constants.asm'), encoding='utf-8'):
        m = re.match(r'\s*const_def\s*(\d*)', l)
        if m: v = int(m.group(1) or 0); continue
        m = re.match(r'\s*const (\w+)', l)
        if m and m.group(1) not in N: N[m.group(1)] = v; v += 1; continue
        if re.match(r'\s*const_skip', l): v += 1
    return N


TEXTS = [  # マサキの イーブイ、ロケットだんの マルマイン、ケンヤの オニスズメ
    (0x13, 0x4A00, 'イーブイ', 'ニューラ'), (0x13, 0x4A9E, 'イーブイ', 'ニューラ'),
    (0x13, 0x4AAD, 'イーブイ', 'ニューラ'), (0x28, 0x4F94, 'マルマイン', 'フォレトス'),
    (0x26, 0x7740, 'オニスズメ', 'ヤミカラス'),
]


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    N = mons(); M = {N[k]: N[v] for k, v in MAP.items()}
    n = [0]
    def put(o):
        if 0 < rom[o] <= 151:
            assert rom[o] in M, (hex(o), rom[o])
            rom[o] = M[rom[o]]; n[0] += 1
    # むれ
    o = fo(0x0A, 0x7F02); assert rom[o:o + 5] == bytes.fromhex('0a02191919')
    while rom[o] != 0xFF:
        for i in range(21): put(o + 5 + 2 * i + 1)
        o += 47
    o = fo(0x0A, 0x7FBF)
    while rom[o] != 0xFF:
        for i in range(3): put(o + 3 + 2 * i + 1)
        o += 9
    # つり
    tabs = set()
    for gi in range(13):
        r = fo(0x24, 0x6946) + 7 * gi
        for k in range(3): tabs.add(r16(rom, r + 1 + 2 * k))
    for t in sorted(tabs):
        o = fo(0x24, t)
        while True:
            if rom[o + 1]: put(o + 1)
            if rom[o] == 0xFF: break
            o += 3
    for o in range(fo(0x24, 0x6B2D), fo(0x24, 0x6B2D) + 0x58, 2): put(o)
    # ずつき・いわくだき
    sets = [r16(rom, fo(0x2E, 0x6470) + 2 * i) for i in range(6)]
    for i, st in sorted(set((min(j for j in range(6) if sets[j] == x), x) for x in sets)):   # TreeMons（いわくだき は 1 つ、ほか 2 つ）
        o = fo(0x2E, st)
        for k in range(1 if i == 3 else 2):
            while rom[o] != 0xFF: put(o + 1); o += 3
            o += 1
    # むしとり大会
    o = 0x97BDC
    while True:
        put(o + 1)
        if rom[o] == 0xFF: break
        o += 4
    log.append('ジョウトの 野生（むれ・つり・ずつき・むしとり）%d' % n[0])
    # スクリプト：銀の ジョウトの マップ（カントーは クリスタル版の スクリプトに なって いる）
    SM = gsc.Maps(bytes(rom), gsc.PG + '/constants/map_constants.asm')
    seen = set(); refs = {}
    for k in SM.hdr:
        try:
            a = SM.attributes(k)
        except Exception: continue
        b = a['scripts_bank']
        if b >= 0x60: continue
        ev = SM.events(k); o = ev['off']
        starts = []
        for ob in ev['objects']: starts.append(r16(bytes(ob), 9))
        for bg in ev['bgs']: starts.append(r16(bytes(bg), 3))
        for co in ev['coords']: starts.append(r16(bytes(co), 5))
        so = fo(b, a['scripts'])
        for st in starts:
            if 0x4000 <= st < 0x8000:
                try: cscript.walk(rom, b, st, seen, refs)
                except Exception: pass
    gifts = 0
    for op, p, bk in refs.get('op', ()):
        if fo(0x13, 0x5D80) <= p < fo(0x13, 0x5F40): continue        # 景品は 下で（ほかの 置きかえと 同じ）
        if rom[p] in (0x2D, 0x2E, 0x5C):
            s = rom[p + 1]; nm = [x for x, v in N.items() if v == s]
            if nm and nm[0] in GIFT:
                rom[p + 1] = N[GIFT[nm[0]]]; gifts += 1
    log.append('もらう・止まって いる ポケモン %d' % gifts)
    # コガネの ゲームコーナーの 景品（銀 $13:$5D80〜$5F40 の getmonname・givepoke と 2つの メニューの 名前）
    PRIZE = {'ABRA': ('ケーシィ', 'ネイティ'), 'EKANS': ('アーボ', 'ノコッチ'), 'SANDSHREW': ('サンド', 'ゴマゾウ'),
             'DRATINI': ('ミニリュウ', 'マンタイン')}
    k = 0
    for o in range(fo(0x13, 0x5D80), fo(0x13, 0x5F40)):
        if rom[o] in (0x40, 0x2D) and rom[o + 1] in [N[x] for x in PRIZE] and rom[o + 2] in (0x00, 0x0A):
            rom[o + 1] = M[rom[o + 1]]; k += 1
    for nm, (a, b) in PRIZE.items():
        ea, eb = jptext.enc(a), jptext.enc(b); i = fo(0x13, 0x5D80)
        while True:
            i = rom.find(ea + b'\x7f', i, fo(0x13, 0x5F40))
            if i < 0: break
            j = i + len(ea)
            while rom[j] == 0x7F: j += 1
            pad = j - i - len(eb); assert pad >= 1, nm
            rom[i:j] = eb + b'\x7f' * pad; k += 1; i = j
    log.append('ゲームコーナーの 景品 %d' % k)
    # 交換
    cmod = open(cmaps.CMOD, 'rb').read()
    o = fo(0x3F, 0x4B9B); assert rom[o:o + 3] == bytes([0x21, 0x23, 0x4C])
    # クリスタル版の 表は 15 こ（0〜6 ジョウト、7〜14 カントー）。16 バイトずつ ＝ 240 バイト。
    # 前は 8 こ だけ 写して いて、8〜14 の 交換が ？？？？？ に なったり 止まったり して いた（12 からは バンクの 外）。
    t = fo(0x3F, TRADE_AT); assert not any(rom[t - 16:t + 240 + 16])
    src = cmod[fo(0x3F, 0x7A53):fo(0x3F, 0x7A53) + 256]
    assert src[240:] == bytes(16) and all(src[16 * i + 1] for i in range(15))
    rom[t:t + 240] = src[:240]
    rom[o + 1] = TRADE_AT & 0xFF; rom[o + 2] = TRADE_AT >> 8
    log.append('交換：クリスタル版の 表 15（$3F:$%04X）' % TRADE_AT)
    # 交換の 話は クリスタルが 4 しゅるい（0〜3）、銀は 3 しゅるい（$3F:$4CA1、5 つの 場面 × 3）。
    # 表の 3 番（女の子の 話：とりかえて くれない？）を 使う 交換（ジョウト 2 つ・カントー）で ほかの 文が 出て いたので、
    # クリスタルの 3 番の 文（RAM の 名前の 場所を 銀に 読みかえ）を 写し、5 × 4 の 表に する。
    a = fo(0x3F, 0x4C8B)
    assert rom[a:a + 22] == bytes.fromhex('21a14c191919191919fa58ce5f19192a666fcd300fc9'), rom[a:a + 22].hex()
    RAMX = {0xD046: 0xCF72, 0xD05B: 0xCF87, 0xD066: 0xCF92}
    def ctext(addr):
        o = fo(0x3F, addr); out = bytearray()
        while True:
            b = cmod[o]
            if b == 0x01:
                v = cmod[o + 1] | cmod[o + 2] << 8; v = RAMX[v]; out += bytes([1, v & 0xFF, v >> 8]); o += 3; continue
            out.append(b); o += 1
            if b in (0x57, 0x58): return bytes(out)
    ct = fo(0x3F, 0x4EE2); old_t = fo(0x3F, 0x4CA1)
    TXT_AT, TAB_AT = 0x7B10, 0x7C60
    tx = fo(0x3F, TXT_AT); tb = fo(0x3F, TAB_AT)
    assert not any(rom[tx - 16:tx + 200]) and not any(rom[tb - 16:tb + 40 + 16])
    q = tx; tab = bytearray()
    for part in range(5):
        for d in range(3):
            tab += rom[old_t + 6 * part + 2 * d:old_t + 6 * part + 2 * d + 2]
        t = ctext(cmod[ct + 8 * part + 6] | cmod[ct + 8 * part + 7] << 8)
        rom[q:q + len(t)] = t; ad = 0x4000 + (q - fo(0x3F, 0x4000)); tab += bytes([ad & 0xFF, ad >> 8]); q += len(t)
    assert q < tx + 200
    rom[tb:tb + 40] = tab
    rom[a:a + 22] = bytes([0x21, TAB_AT & 0xFF, TAB_AT >> 8]) + bytes.fromhex('cb23cb23cb2319fa58ce5f19192a666fc3300f')   # e×8 ＋ 話×2
    log.append('交換の 話：4 しゅるいに（文 $3F:$%04X、表 $3F:$%04X）' % (TXT_AT, TAB_AT))
    # 文の 名前（同じ 長さで 入れかえ。名前の 表と 図鑑は さわらない）
    k = 0
    for bk, ad, a, b in TEXTS:
        o = fo(bk, ad); ea = jptext.enc(a)
        assert rom[o:o + len(ea)] == ea, (a, hex(bk), hex(ad))
        rom[o:o + len(ea)] = jptext.enc(b); k += 1
    log.append('文の 名前 %d' % k)
    return rom
