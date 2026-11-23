"""第126弾（報告の 直し）キットの 金版：エンジンの 所。
   2 ゲートの グレーバッジ は MOD 側（kj4/make_kj4.sh → crystal_kj4.gbc）から c2g で 入る。
   3 26番道路の エリートトレーナー は 金の 元の 文が 使われる ので、ここで 金の 文を 直す（route26）。
   ここは 金の ROM に 直接：
    1 たいあたりの 演出：金には 当てはまらない（入れない）。金で ニドラン♂ と ポッポで たいあたりを 使う・使われる を
      録画して 見ると、元の ROM でも 動くのは 使った 側だけ（相手の 足もと・こちらの 頭の 行は 動かない）。
      キットの 直しを 金の 住所で 入れても 録画は 1コマも かわらなかった。
    4 人に ついて 行く 場面：「follow 人, PLAYER / applymovement 人 / stopfollow」を その 人と 主人公の 交代の 1歩ずつに
      （キットの follow() と 同じ。callasm の 住所は 金：GetMapObject $171C・GetObjectStruct $192F・wPlayerMapX $D200・wScriptVar $D165）。
      はじめの オーキド（まだ ポケモンが いない）の 2つは そのまま。金の ちがい 2つ：
      ・スクリプトの 人 N は wMapObjects の N（金は 1 が 空き。キットの N-1 だと 空きを 見て 1歩目が いつも 上に なった）。
      ・applymovement の あいだに wScriptVar が 書きかわる（CheckSwarmFlag 03:458B）ので、向きで 先に 分けてから
        その 人の 1歩目 → 主人公の 1歩目（キットは その 人の 1歩目 → 向きで 分ける。研究所で 主人公が ななめに ずれた）。
    5 マサキに 会う 前は「だれかの パソコン」：パソコンの メニューの 表（05:5830）を wStringBuffer2（$CF92）に、
      .ChooseWhichPCListToUse（05:5874）の 頭で HFI → 7E の 本体：イベント $835 を 見て 名前を 入れてから 元と 同じ 処理。
      「マサキの パソコンと つないだ！」（05:5D13）も text_ram で 同じ 名前。
    6 ニビの ニドランの 家：nidoran() の 説明を 見る（人の絵 $E3 ＝ 連れ歩きの ニドラン♂の 絵）。
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE + '/kj4')
from lib import Asm
from jpchar import encode
import gold_hfi

def fo(b, a): return b * 0x4000 + a - 0x4000
def w16(v): return bytes([v & 0xFF, v >> 8])


def expect(g, o, h):
    b = bytes.fromhex(h.replace(' ', '')); assert bytes(g[o:o + len(b)]) == b, (hex(o), g[o:o + len(b)].hex(' '), h); return b


def tail(g, b, margin=2):
    B = g[b * 0x4000:(b + 1) * 0x4000]; e = len(B)
    while e and B[e - 1] == 0: e -= 1
    return 0x4000 + e + margin


# ---- 4 人に ついて 行く
GET_MAP_OBJECT, GET_OBJECT_STRUCT = 0x171C, 0x192F
W_PLAYER_X, W_PLAYER_Y, W_SCRIPT_VAR = 0xD200, 0xD201, 0xD165
# はじめの オーキド（ポケモンが まだ いない）：MOD 71:4C4E・71:4CA6 と 同じ 人・道すじ
SKIP_PATHS = {(2, '0c0c0c0c0c0e0c0c0c0c0c0f0f0f0d'), (2, '0e0c0c0c0c0c0e0c0c0c0c0c0f0f0f0d')}


class Free:
    def __init__(s, g, bank): s.g, s.bank, s.a = g, bank, 0x4000
    def addr(s): return s.a
    def put(s, data):
        assert s.a + len(data) <= 0x8000; o = fo(s.bank, s.a); s.g[o:o + len(data)] = data; a = s.a; s.a += len(data); return a


def follow(g, log, FB):
    assert not any(g[fo(FB, 0x4000):fo(FB + 1, 0x4000)])
    f = Free(g, FB); mv = {}
    def movement(c):
        if c not in mv: mv[c] = f.put(bytes([c, 0x47]))
        return mv[c]
    for c in (0x0C, 0x0D, 0x0E, 0x0F): movement(c)
    common = f.put(bytes([0xCD]) + w16(GET_MAP_OBJECT) + bytes([0x0A, 0xCD]) + w16(GET_OBJECT_STRUCT) + bytes([
        0x21, 0x10, 0x00, 0x09, 0x56, 0x23, 0x5E,
        0xFA]) + w16(W_PLAYER_X) + bytes([0xBA, 0x38, 0x10, 0x20, 0x12,
        0xFA]) + w16(W_PLAYER_Y) + bytes([0xBB, 0x38, 0x04,
        0x3E, 0x0D, 0x18, 0x0A, 0x3E, 0x0C, 0x18, 0x06, 0x3E, 0x0F, 0x18, 0x02, 0x3E, 0x0E,
        0xEA]) + w16(W_SCRIPT_VAR) + bytes([0xC9]))
    entry = {}; n = 0; skipped = 0
    for m in list(re.finditer(rb'\x6f(.)\x00\x68(.)(..)\x70', bytes(g), re.S)):
        if m.group(1) != m.group(2): continue
        at = m.start(); b = at // 0x4000; a_ = at % 0x4000 + 0x4000
        obj = m.group(1)[0]
        p = fo(b, int.from_bytes(m.group(3), 'little')); path = []
        while g[p] != 0x47:
            path.append(g[p]); p += 1; assert len(path) < 64
        if (obj, bytes(path).hex()) in SKIP_PATHS: skipped += 1; continue
        if obj not in entry: entry[obj] = f.put(bytes([0x3E, obj, 0xC3]) + w16(common))   # 金：スクリプトの 人 N ＝ wMapObjects の N（1 は 空き。キットの クリスタルは N-1）
        for c in path: movement(c)
        a = Asm(f.addr()); a.bank = FB
        a.callasm(FB, entry[obj])
        prev = None
        for c in path:
            if prev is None and 0x08 <= c < 0x20:
                # 金：applymovement の あいだに wScriptVar が 書きかわる（CheckSwarmFlag 03:458B など）ので、
                # 先に 向きで 分けてから、分かれた 先で その 人の 1歩目 → 主人公の 1歩目
                for d in (0x0C, 0x0D, 0x0E): a.ifequal(d, 'p%d' % d)
                a.applymovement(obj, movement(c)); a.applymovement(0, mv[0x0F]); a.sjump('j')
                for d in (0x0C, 0x0D, 0x0E): a.label('p%d' % d); a.applymovement(obj, movement(c)); a.applymovement(0, mv[d]); a.sjump('j')
                a.label('j')
                prev = c; continue
            a.applymovement(obj, movement(c))
            if not (0x08 <= c < 0x20): continue
            a.applymovement(0, movement(prev))
            prev = c
        a.farsjump(b, a_ + 8)
        blob = a.done(); new = f.put(blob); assert new == a.base
        g[at:at + 4] = bytes([0x04, FB]) + w16(new); g[at + 4:at + 8] = bytes([0x90] * 4)
        n += 1
        log.append('第126弾 4 ついて 行く %02X:%04X 人 %d（%d 歩）→ %02X:%04X' % (b, a_, obj, len(path), FB, new))
    assert n >= 10 and skipped == 2, (n, skipped)
    return f


# ---- 5 パソコンの 名前
EVENT_MET_BILL = 0x0835
W_SB2 = 0xCF92
EFA, CHECK_DEX, W_HOF = 0x2EEB, 0x2F29, 0xD676


def bills_pc(g, log):
    expect(g, fo(5, 0x582E), 'bb 58 43 58')
    masaki = encode('マサキの　').rstrip(b'\x50'); dareka = encode('だれかの　').rstrip(b'\x50')
    expect(g, fo(5, 0x5843), (masaki + b'\x5b\x50').hex())
    g[fo(5, 0x5830):fo(5, 0x5830) + 2] = w16(W_SB2)
    # .ChooseWhichPCListToUse（05:5874）：call CheckReceivedDex / jr nz / ld a, 0 / ret / ld a, [wHallOfFameCount] …
    o = fo(5, 0x5874); expect(g, o, 'cd 29 2f 20 03 3e 00 c9 fa 76 d6 a7 3e 01 c8 3e 02 c9')
    sm = gold_hfi.put(g, masaki + b'\x5b\x50' + masaki + b'\x50')
    sd = gold_hfi.put(g, dareka + b'\x5b\x50' + dareka + b'\x50')
    body = bytes([0xC5, 0xD5,
                  0x11]) + w16(EVENT_MET_BILL) + bytes([0x06, 0x02, 0xCD]) + w16(EFA) + bytes([
                  0x79, 0xA7, 0x21]) + w16(sm) + bytes([0x20, 0x03, 0x21]) + w16(sd) + bytes([
                  0x11]) + w16(W_SB2) + bytes([0x0E, 13, 0x2A, 0x12, 0x13, 0x0D, 0x20, 0xFA,
                  0xD1, 0xC1,
                  0xCD]) + w16(CHECK_DEX) + bytes([0x20, 0x03, 0x3E, 0x00, 0xC9,
                  0xFA]) + w16(W_HOF) + bytes([0xA7, 0x3E, 0x01, 0xC8, 0x3E, 0x02, 0xC9])
    ba = gold_hfi.put(g, body)
    g[o:o + 18] = bytes([0xCD]) + w16(gold_hfi.HFI) + w16(ba) + bytes([0xC9]) + bytes(12)
    # 「マサキの　{PC}と　つないだ！」（05:5D13）
    t0 = fo(5, 0x5D13); expect(g, t0, '00' + (masaki + b'\x5b').hex())
    g[t0:t0 + 7] = bytes([0x01]) + w16(W_SB2 + 7) + bytes([0x00, 0x50, 0x00, 0x5B])
    log.append('第126弾 5 だれかの パソコン：7E:%04X（05:5874 から HFI）' % ba)


# ---- 6 ニビの ニドランの 家
#  金の 連れ歩き（キット）は 人の絵 $E2 が 連れ歩き：GetMonSprite（05:429D）の「cp $E0」の 所 → 05:4000
#  （cp $E2 → farcall 79:43C9 Fw_GetSprite / cp $E0 → 42BF / ほかは 42A5）。バンク 5 に あきが ないので、
#  05:4000 を「call HFI / dw 本体 / ret c / cp $E0 / jp z 42BF / jp 42A5」に して、本体（7E）で $E2 と 新しい $E3 を 見る。
#  $E3 ＝ 連れ歩きの ニドラン♂の 絵（キットの 絵の 番号 31：バンク $60、384 バイト）の 色1・色2 を 色2 に した 写し（人の 色 9）。
FW_PIC_BANK, NIDO_IDX = 0x60, 31
NIDO_REMAP = [0, 2, 2, 3]
NIDO_PAL, NIDO_MOVE = 9, 6          # PAL_NPC_BLUE（クリスタル版の キットと 同じ）、SPRITEMOVEDATA_STANDING_DOWN


def nidoran(g, log, f):
    o = fo(5, 0x4000)
    expect(g, o, 'fe e2 28 08 fe e0 ca bf 42 c3 a5 42 e5 3e 79 21 c9 43 cf e1 c9 cd ad 30 c9')
    expect(g, fo(5, 0x42A1), 'c3 00 40 00 fe e1')
    src = fo(FW_PIC_BANK, 0x4000 + NIDO_IDX * 384); pic = bytearray(g[src:src + 384])
    for i in range(0, 384, 2):
        lo, hi = pic[i], pic[i + 1]; nlo = nhi = 0
        for x in range(8):
            v = NIDO_REMAP[((lo >> x) & 1) | (((hi >> x) & 1) << 1)]
            nlo |= (v & 1) << x; nhi |= (v >> 1) << x
        pic[i], pic[i + 1] = nlo, nhi
    pa = f.put(bytes(pic))
    gfx = f.put(bytes([0x06, f.bank, 0x11]) + w16(pa) + bytes([0x0E, 0x0C, 0x37, 0xC9]))   # b / de / c = 12 / scf
    body = bytes([0xFE, 0xE2, 0x20, 0x09,
                  0xE5, 0x3E, 0x79, 0x21, 0xC9, 0x43, 0xCF, 0xE1, 0xC9,                 # 連れ歩き（元と 同じ）
                  0xFE, 0xE3, 0x28, 0x02, 0xA7, 0xC9,                                   # ほか：a そのまま・キャリーなし
                  0xE5, 0x3E, f.bank, 0x21]) + w16(gfx) + bytes([0xCF, 0xE1, 0xC9])     # $E3
    ba = gold_hfi.put(g, body)
    hook = bytes([0xCD]) + w16(gold_hfi.HFI) + w16(ba) + bytes([0xD8, 0xFE, 0xE0, 0xCA, 0xBF, 0x42, 0xC3, 0xA5, 0x42])
    g[o:o + 21] = hook + bytes(21 - len(hook))
    # 家の ニドラン（金の 人の絵 $82）
    sys.path.insert(0, '/home/claude/work/scripts')
    from cwalk import Walk
    from cmaps import maplist
    from maps import GMGP
    m = [m for m in maplist(bytes(g), GMGP, 'pokegold') if m['name'] == 'PewterNidoranSpeechHouse']; assert len(m) == 1
    at = Walk(bytes(g)).map(m[0]['attr'], m[0]['name'])
    objs = [ob for ob in at['objs'] if ob[0] == 0x82]; assert len(objs) == 1
    pat = bytes(objs[0][:13]); assert len(pat) == 13; G_ = bytes(g); hits = [m_.start() for m_ in re.finditer(re.escape(pat), G_)]; assert len(hits) == 1, hits
    off = hits[0]; assert g[off + 7] == 0x90
    g[off] = 0xE3; g[off + 3] = NIDO_MOVE; g[off + 7] = NIDO_PAL << 4
    log.append('第126弾 6 ニドランの 家：人の絵 $E3（%02X:%04X、本体 7E:%04X）、人 %X' % (f.bank, gfx, ba, off))


# ---- 3 26番道路の エリートトレーナー♀：金の 文（金の 元の 文を 使う。MOD 側の 直しは 入らない）の <RIVAL> → <GREEN>
def route26(g, log):
    pat = bytes.fromhex('5700537f1eb2b34f5d1dcfb9c0c9')            # <DONE> {00}<RIVAL>　っていう<LINE>{5D}に　まけたの
    G_ = bytes(g); hits = [m_.start() for m_ in re.finditer(re.escape(pat), G_)]; assert len(hits) == 1, hits
    g[hits[0] + 2] = 0x39
    log.append('第126弾 3 26番道路の エリートトレーナー：<RIVAL> → <GREEN>（%X）' % (hits[0] + 2))


def apply(g, log, FB):
    route26(g, log)
    f = follow(g, log, FB)
    bills_pc(g, log)
    nidoran(g, log, f)
