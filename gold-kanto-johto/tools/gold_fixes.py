"""クリスタル版の 追加の 直し（第95〜110弾の キット）の うち、データの 写しでは 入らない 所を 金に 入れる。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cwalk import fo, Walk
from gsclz import unlz
from gold_player import lz_literal

POKERED = '/home/claude/work/mod/ref/pokered'
def r16(b, o): return b[o] | b[o + 1] << 8


def ts_table(g):
    o = 0x2DB8; assert g[o] == 0x21 and g[o + 18] == 0x3E
    return g[o + 19], r16(g, o + 1)


def add_tileset(g, E, entry):
    """タイルセットの 表を 1つ ふやして（新しい 所へ 写す）その 番号を かえす"""
    tb, ta = ts_table(g); t = fo(tb, ta)
    n = E.ts_n; E.ts_n += 1
    nb = E.next_bank; E.next_bank += 1; assert not any(g[fo(nb, 0x4000):fo(nb + 1, 0x4000)])
    new = bytes(g[t:t + 15 * n]) + bytes(entry)
    g[fo(nb, 0x4000):fo(nb, 0x4000) + len(new)] = new
    g[0x2DB9] = 0x00; g[0x2DBA] = 0x40; g[0x2DCB] = nb
    E.fix_bank = [nb, 0x4000 + len(new) + 0x10]
    return n


def put(g, E, data):
    b, a = E.fix_bank; assert a + len(data) <= 0x8000
    g[fo(b, a):fo(b, a) + len(data)] = data; E.fix_bank[1] = a + len(data); return b, a


def fix108(g, E, M, log, gmap):
    """第108弾：クチバジムの マチスの 前の 2まいの 扉（赤の ジムの タイル $20 $21 / $30 $31）。
       金の タイルセット 13 は あいて いる タイルが ない ので、クチバジム だけの 写し（新しい 番号）を 作り、
       ジムで 使わない タイルを 4つ 扉に、ブロック $40（上：扉・下：床。当たりは 上が 壁）を 足す。"""
    hdr = gmap['VermilionGym']['hdr']; old_id = g[hdr + 1]
    tb, ta = ts_table(g); e = bytearray(g[fo(tb, ta) + 15 * old_id:fo(tb, ta) + 15 * old_id + 15])
    gfx, _ = unlz(g, fo(e[0], r16(e, 1))); gfx = bytearray(gfx)
    meta = bytearray(g[fo(e[3], r16(e, 4)):fo(e[6], r16(e, 7))]); nb = len(meta) // 16
    coll = bytearray(g[fo(e[6], r16(e, 7)):fo(e[6], r16(e, 7)) + 4 * nb])
    assert nb == 0x40, nb
    at = Walk(g).map(gmap['VermilionGym']['attr'], 'VermilionGym')
    blk = g[fo(at['blkbank'], at['blk']):fo(at['blkbank'], at['blk']) + at['w'] * at['h']]
    used = set(blk) | {0x20, 0x01, at['border']}
    tiles = set()
    for b in used: tiles |= set(meta[16 * b:16 * b + 16])
    free = [t for t in range(1, 0x60) if t not in tiles][:4]; assert len(free) == 4
    red = open(POKERED + '/gfx/tilesets/gym.2bpp', 'rb').read()
    for t, rt in zip(free, (0x20, 0x21, 0x30, 0x31)): gfx[16 * t:16 * t + 16] = red[16 * rt:16 * rt + 16]
    a_, b_, c_, d_ = free; fl = meta[16:32]
    meta += bytes([a_, b_, a_, b_, c_, d_, c_, d_]) + fl[8:16]
    coll += bytes([coll[0x80], coll[0x81], coll[6], coll[7]])
    # パレットマップ：扉は 床の タイルの 色
    pmb = E.ts_pm[0]; pmo = fo(pmb, r16(e, 13)); pm = bytearray(g[pmo:pmo + 0x30])
    def pal(t): return pm[t // 2] >> (4 * (t & 1)) & 0x0F
    fp = pal(fl[8])
    for t in free:
        pm[t // 2] = (pm[t // 2] & (0x0F if t & 1 else 0xF0)) | (fp << (4 * (t & 1)))
    pa = E.ts_pm[1]; g[fo(pmb, pa):fo(pmb, pa) + 0x30] = pm; E.ts_pm[1] += 0x30
    new_id = add_tileset(g, E, bytes(15))
    gb, ga = put(g, E, lz_literal(bytes(gfx))); mb, ma = put(g, E, bytes(meta)); cb, ca = put(g, E, bytes(coll))
    assert mb == cb
    ne = bytes([gb, ga & 0xFF, ga >> 8, mb, ma & 0xFF, ma >> 8, cb, ca & 0xFF, ca >> 8]) + bytes(e[9:13]) + bytes([pa & 0xFF, pa >> 8])
    tb, ta = ts_table(g); g[fo(tb, ta) + 15 * new_id:fo(tb, ta) + 15 * new_id + 15] = ne
    g[hdr + 1] = new_id
    log.append('第108弾：クチバジムの 扉（タイルセット %d の 写し → %d、タイル %s、ブロック $40）' % (old_id, new_id, ' '.join('%02X' % t for t in free)))


def fix97(g, E, M, log):
    """第97弾：カントーの 町・道路の 色を 朝・昼・夜で かえる。クリスタル版の 朝・夜の 色の 組（6A の 表）を 写し、
       gold_p11 の 色の フック（02:7BE0、MOD の タイルセットの 昼の 色を 読んだ あと）から HFI で よぶ。"""
    import gold_hfi
    o = fo(0x6A, 0x74AF); assert M[o] == 0xCD
    ra = M[o + 1] | M[o + 2] << 8
    if ra == 0x6EE9: return                                  # クリスタル版に 第97弾が ない
    r = fo(0x6A, ra); k = M.find(bytes([0xFA, 0xCA, 0xD1, 0x47, 0x21]), r, r + 0x60); assert k > 0
    t = fo(0x6A, r16(M, k + 5)); ents = []
    while M[t] != 0xFF: ents.append((M[t], r16(M, t + 1), r16(M, t + 3))); t += 5
    tab = bytearray()
    for ci, am, an in ents:
        assert 33 <= ci <= 53
        b1, a1 = put(g, E, M[fo(0x6A, am):fo(0x6A, am) + 56]); b2, a2 = put(g, E, M[fo(0x6A, an):fo(0x6A, an) + 56])
        tab += bytes([ci - 4, a1 & 0xFF, a1 >> 8, a2 & 0xFF, a2 >> 8])
    tab += b'\xff'
    DB = E.fix_bank[0]
    W_ENV, W_TS, W_TOD, BGP1, FCB = 0xD075, 0xD074, 0xD55B, 0xC200, 0x0DB6
    # 町・道路 でない（家の 中など）ときは 8つめの 色（MOD の タイルセットの 表の 8つめ）を 字の 色に する。
    # クリスタル版は 中では 8つめが 字の 色（白・$7268・$40A5・黒）。写した ままだと 字の 黒が うすく なっていた
    tpb, tpa = put(g, E, bytes.fromhex('ff7f6872a5400000'))
    outs = [ci - 4 for ci, _, _ in ents]          # 外の タイルセット（朝・夜の 色が ある もの）
    pre = bytearray([0xFA, W_TS & 0xFF, W_TS >> 8])
    for t in outs: pre += bytes([0xFE, t, 0x28, 0])  # cp t ; jr z,外
    ind = bytes([0x21, tpa & 0xFF, tpa >> 8, 0x11, (BGP1 + 0x38) & 0xFF, (BGP1 + 0x38) >> 8,
                 0x01, 0x08, 0x00, 0x3E, tpb, 0xC3, FCB & 0xFF, FCB >> 8])
    for i in range(len(outs)): pre[3 + 4 * i + 3] = len(pre) - (3 + 4 * i + 4) + len(ind)
    pre += ind
    code = bytearray(pre) + bytearray([0xFA, W_ENV & 0xFF, W_ENV >> 8, 0x3D, 0xFE, 0x02, 0xD0,              # 町・道路 だけ
                      0xFA, W_TOD & 0xFF, W_TOD >> 8, 0xE6, 0x03, 0x1E, 0x01, 0xA7, 0x28, 0x05, # 朝：e=1
                      0x1E, 0x03, 0xFE, 0x02, 0xC0,                                           # 夜：e=3（昼は そのまま）
                      0xFA, W_TS & 0xFF, W_TS >> 8, 0x47, 0x21, 0, 0,                         # ld hl,表
                      0x7E, 0xFE, 0xFF, 0xC8, 0xB8, 0x28, 0x07, 0x23, 0x23, 0x23, 0x23, 0x23, 0x18, 0xF2,
                      0x16, 0x00, 0x19, 0x2A, 0x66, 0x6F,
                      0x11, BGP1 & 0xFF, BGP1 >> 8, 0x01, 0x38, 0x00, 0x3E, DB, 0xCD, FCB & 0xFF, FCB >> 8, 0xC9])
    base = gold_hfi.here(); ta = base + len(code)
    code[27 + len(pre)] = ta & 0xFF; code[28 + len(pre)] = ta >> 8
    assert gold_hfi.put(g, bytes(code) + bytes(tab)) == base
    hk = fo(2, 0x7BE0); end = hk + bytes(g[hk:hk + 0x30]).find(bytes([0xC3, 0x26, 0x76]))
    assert end > hk and not any(g[end + 3:end + 8])
    g[end:end + 8] = bytes([0xCD, gold_hfi.HFI & 0xFF, gold_hfi.HFI >> 8, base & 0xFF, base >> 8, 0xC3, 0x26, 0x76])
    log.append('第97弾：カントーの 町・道路の 朝・夜の 色（%d タイルセット、7E:%04X）' % (len(ents), base))


def fix96(g, log):
    """第96弾：ドア・ワープの 色の フェードの 1段の 待ちを 2 → 1 フレーム（ConvertTimePalsIncHL / DecHL）"""
    for a in (0x4287, 0x4296):
        o = fo(0x23, a); assert g[o + 6:o + 11] == bytes([0x0E, 0x02, 0xCD, 0x3C, 0x03]), hex(a)
        g[o + 7] = 1
    log.append('第96弾：ドアの 出入りの フェード 1段 1フレーム')


def fix99(g, log):
    """第99弾：シゲル（SPRITE_BLUE）の 歩く 絵の 色を 青（PAL_OW_BLUE）に"""
    o = fo(0x05, 0x47B0) + 6 * 6; assert g[o:o + 5] == bytes.fromhex('4048c03001'), g[o:o + 6].hex()
    g[o + 5] = 1
    log.append('第99弾：シゲルの 色 PAL_OW_BLUE')


def fix105(g, M, log):
    """第105弾：足した トレーナーの 種類（67〜79）に 見つかった ときの 曲。金の 表（3A:5027、67こ）の うしろを 読んで いた。
       表を 80こに して 7E に 置き、PlayTrainerEncounterMusic の 読む 所を HFI に。"""
    import gold_hfi, c2g
    o = fo(0x3A, 0x501C); assert g[o:o + 11] == bytes.fromhex('160021275019 5ecdb93cc9'.replace(' ', ''))
    k = M.find(bytes.fromhex('1600 21'.replace(' ', '')), fo(0x3A, 0x501C), fo(0x3A, 0x501C) + 4)
    mo = fo(0x3A, 0x501C)
    if M[mo:mo + 3] == bytes.fromhex('3e4021') or M[mo] != 0x16:   # クリスタル版 第105弾：farcall で 表を 読む
        q = M.find(bytes.fromhex('1600'), fo(0x40, 0x7F00), fo(0x40, 0x8000))
    tab = bytearray(g[fo(0x3A, 0x5027):fo(0x3A, 0x5027) + 67])
    # クリスタル版の 新しい 表（第105弾）：40:7F00〜 の 80 バイト（はじめの 67 は もとの 表と 同じ）
    orig = bytes(M[fo(0x3A, 0x5027):fo(0x3A, 0x5027) + 67])
    b40 = bytes(M[fo(0x40, 0x4000):fo(0x40, 0x8000)])
    i = b40.find(orig[:40]); assert i >= 0
    mt = b40[i:i + 80]
    X = c2g.Xlat()
    for c in range(67, 80): tab.append(X.music(mt[c], 'encounter %d' % c))
    body = bytes([0x16, 0x00, 0x21, 0, 0, 0x19, 0x6E, 0x26, 0x00, 0xC9])
    base = gold_hfi.here(); ta = base + len(body)
    body = bytearray(body); body[3] = ta & 0xFF; body[4] = ta >> 8
    assert gold_hfi.put(g, bytes(body) + bytes(tab)) == base
    g[o:o + 11] = bytes([0xCD, gold_hfi.HFI & 0xFF, gold_hfi.HFI >> 8, base & 0xFF, base >> 8, 0x54, 0x5D, 0xCD, 0xB9, 0x3C, 0xC9])
    log.append('第105弾：見つかった ときの 曲の 表 80こ（7E:%04X）：%s' % (ta, ' '.join('%02X' % v for v in tab[67:])))


def fix109(g, log):
    """第109弾：ポケギアの カントーの 地図で ↓を 押し続けても ジョウトの 地名に 入らない（いつも マサラ〜28ばんどうろ）"""
    o = fo(0x24, 0x5046); assert g[o:o + 17] == bytes.fromhex('fa64d5cb772805165d1e2ec9165d1e57c9')
    g[o + 15] = 0x2E
    log.append('第109弾：カントーの 地図の カーソル いつも $2E〜$5D')


def fix110_poison(g, log):
    """第110弾 3：どくで 歩いた ときの 点滅を 赤と 同じに（背景の 8つの パレットの 色0 に 色2。紫 一色に しない）"""
    import gold_hfi
    o = fo(0x32, 0x7C2F); assert g[o:o + 14] == bytes.fromhex('2180c20e203ebc223e7e220d20f7')
    body = bytes([0x21, 0x80, 0xC2, 0x0E, 0x08, 0x23, 0x23, 0x23, 0x23, 0x2A, 0x46, 0x11, 0xFB, 0xFF, 0x19, 0x22, 0x70,
                  0x11, 0x07, 0x00, 0x19, 0x0D, 0x20, 0xED, 0xC9])
    t = gold_hfi.put(g, body)
    g[o:o + 14] = bytes([0xCD, gold_hfi.HFI & 0xFF, gold_hfi.HFI >> 8, t & 0xFF, t >> 8]) + bytes(9)
    log.append('第110弾 3：どくの 点滅（7E:%04X）' % t)


def fix110_boxfull(g, log):
    """第110弾 4：ボックスが いっぱいに なっても マサキから 電話が こない（.SendToPC で BATTLERESULT_BOX_FULL を 立てない）"""
    o = fo(0x03, 0x6EAE); seg = bytes(g[o:o + 0x30])
    i = seg.find(bytes.fromhex('cbfe')); 
    k = seg.find(bytes.fromhex('fe1e2005'))
    assert k >= 0, seg.hex()
    j = seg.find(bytes.fromhex('cbfe'), k); assert j > k and j - k < 12, seg.hex()
    g[o + j:o + j + 2] = b'\x00\x00'
    log.append('第110弾 4：ボックスが いっぱいの 電話なし（03:%04X）' % (0x6EAE + j))


def fix110_follow(g, log):
    """第110弾 5：連れ歩きの 移動の 列（wFollowMovementQueue $D1EB、5バイト、長さ $D1EA）が あふれて 主人公の
       オブジェクトを こわさない ように、いっぱいなら 足さない（01:5476 → HFI）"""
    import gold_hfi
    o = fo(0x01, 0x5476); assert g[o:o + 15] == bytes.fromhex('f521ead1345e160021ebd119f177c9')
    body = bytes.fromhex('f521ead17e3cfe05300777c6eb6ff177c9f1c9')
    t = gold_hfi.put(g, body)
    g[o:o + 15] = bytes([0xCD, gold_hfi.HFI & 0xFF, gold_hfi.HFI >> 8, t & 0xFF, t >> 8, 0xC9]) + bytes(9)
    log.append('第110弾 5：連れ歩きの 列に 上限（7E:%04X）' % t)


def fix100(g, log):
    """第100弾：ずかんの ぶんぷ（Pokedex_GetArea 24:5DA5）。主人公の いる 地方の 地図を 出す、カントーは いつでも、
       ジョウトは 着いて から（EV $34C）。追加機能パッチの ぶんぷの 時間帯（START、45:5800）は 作りなおした あと
       見て いた 地方に もどす（1 カントー・2 ジョウト）。新しい ゲームの ずかんの ならびは 番号順。"""
    B = 0x24
    def at(a): return fo(B, a)
    def w(v): return bytes([v & 0xFF, v >> 8])
    LRI, LEFT, BLINK, GETNEST, CLR = 0x5E2F, 0x5E3A, 0x5E61, 0x5EC0, 0x30BB
    assert g[at(LRI):at(LRI) + 11] == bytes.fromhex('7ee620200 67ee6102012c9'.replace(' ', ''))
    assert g[at(LEFT):at(LEFT) + 0x11] == bytes.fromhex('f0d4fe90c8cdbb303e90e0d4afcdc05ec9')
    assert g[at(0x5E4B):at(0x5E4B) + 6] == bytes.fromhex('fa64d5cb77c8')
    EVB, EVM = 0xD7AA + 0x34C // 8, 1 << (0x34C % 8)
    left = (b'\xfa' + w(EVB) + bytes([0xE6, EVM, 0xC8]) + bytes.fromhex('f0d4fe90c8') + b'\xcd' + w(CLR)
            + bytes.fromhex('3e90e0d4afc3') + w(GETNEST))
    right_at = LEFT + len(left)
    right = bytes.fromhex('f0d4a7c8') + b'\xcd' + w(CLR) + bytes.fromhex('afe0d43e01c3') + w(GETNEST)
    blk = left + right; assert LEFT + len(blk) <= BLINK
    g[at(LEFT):at(BLINK)] = blk + bytes(BLINK - LEFT - len(blk))
    g[at(LRI) + 9] = right_at - (LRI + 10)
    # はじめ：主人公が カントー（$2E〜$5D）なら カントー
    o = at(0x5DFE); assert g[o:o + 4] == bytes.fromhex('afcdc05e')
    ia = 0x7F40; assert not any(g[at(ia):at(ia) + 16])
    init = b'\xfa' + w(0xCF21) + bytes([0xFE, 0x2E, 0x38, 0x07, 0xFE, 0x5E, 0x30, 0x03, 0xC3]) + w(right_at + 4) + b'\xaf\xc3' + w(GETNEST)
    g[at(ia):at(ia) + len(init)] = init
    g[o:o + 4] = b'\xcd' + w(ia) + b'\x00'
    # ぶんぷの 時間帯（追加機能パッチ 45:5800）→ 新しい NestTime_Input（45:7E10）
    q = fo(0x24, 0x7F1F); assert g[q:q + 6] == bytes.fromhex('3e45210058cf')
    na = 0x7E10; assert not any(g[fo(0x45, na):fo(0x45, na) + 0x40])
    nt = bytes.fromhex('faf5dea72812f5afeaf5def13d21') + w(right_at) + bytes.fromhex('280321') + w(LEFT) + bytes.fromhex('3e24cf')
    nt += bytes.fromhex('f0a9e608c8faf4de3ce603eaf4def0d4a73e0128013ceaf5decdbb3037c9')
    g[fo(0x45, na):fo(0x45, na) + len(nt)] = nt
    g[q + 3:q + 5] = w(na)
    # 新しい ゲーム：wLastDexMode（$D671）= 1（番号順）。gold_p52 の OakSpeech（01:5FB3）の 頭で
    o = fo(0x01, 0x5FB3); assert g[o] == 0x3E and g[o + 2:o + 7] == bytes.fromhex('216758cfc9')
    pb = g[o + 1]
    g[o:o + 12] = bytes.fromhex('3e01ea71d63e') + bytes([pb]) + bytes.fromhex('216758cfc9')
    log.append('第100弾：ぶんぷ（はじめ 24:%04X、.right 24:%04X、時間帯 45:%04X）、ずかんの ならび 番号順' % (ia, right_at, na))


GOLD_BLOCKS = ['LancesRoom', 'CeladonDeptStore1F', 'CeladonDeptStore2F', 'CeladonDeptStore3F', 'CeladonDeptStore6F',
               'CeladonMansionRoof']


def fix_gold_blocks(g, log, gmap):
    """クリスタル版で ブロックが 金と ちがう マップ（MOD は クリスタルの まま）を、MOD の スクリプトの まま 金の ブロックに。
       クリスタルの ブロックは VRAM バンク1 の タイルを 使う ので、金の タイルセットでは くずれて いた
       （チャンピオンの へや・タマムシデパート・タマムシマンションの 屋上）。チャンピオンの へやの 上の 入口は 金の y=0。"""
    from cmaps import maplist; from maps import GMGP
    B = open(os.environ.get('GBASE', '/home/claude/work/ref/kin64.gbc'), 'rb').read()
    bm = {m['name']: m for m in maplist(B, GMGP, 'pokegold')}
    done = []
    for n in GOLD_BLOCKS:
        a = Walk(g).map(gmap[n]['attr'], n); b = Walk(B).map(bm[n]['attr'], n)
        assert (a['w'], a['h']) == (b['w'], b['h']), n
        sz = a['w'] * a['h']; o = fo(a['blkbank'], a['blk'])
        g[o:o + sz] = B[fo(b['blkbank'], b['blk']):fo(b['blkbank'], b['blk']) + sz]
        if n == 'LancesRoom':
            ev = fo(a['scbank'], a['events']); assert g[ev:ev + 2] == b'\x00\x00' and g[ev + 2] == 4
            for i in (2, 3):
                w = ev + 3 + 5 * i; assert g[w] == 1 and B[fo(b['scbank'], b['events']) + 3 + 5 * i] == 0
                g[w] = 0
        done.append(n)
    log.append('金の ブロックに もどした マップ：%s' % ' '.join(done))


def fix_fishnest(g, log):
    """追加機能パッチの「ぶんぷ」の 釣りの マーク（3F:7900〜）の 表を この 移植版の データで 作りなおす。
       ジョウト（と 26〜28番道路・トージョウのたき）：マップの 釣りの グループ（金の FishGroups）・水の ある マップ。
       カントー：第57弾の マップごとの 表（kmaps：つりざおの グループ → krod）。サファリの 足しは 使わない（本物の サファリが ある）"""
    B = 0x3F
    def r(a): return r16(g, fo(B, a))
    assert g[fo(B, 0x794D)] == 0x21 and r(0x794E) == 0x7A2B
    assert bytes(g[fo(B, 0x79E9):fo(B, 0x79EB)]) == bytes([0xFE, 13]) and g[fo(B, 0x79F0)] == 0x21 and r(0x79F1) == 0x7AA2
    assert g[fo(B, 0x7994)] == 0x7B
    gm = [r(0x7AA2 + 2 * i) for i in range(13)]
    mons = []
    for p in gm:
        o = fo(B, p); l = []
        while g[o]: l.append(g[o]); o += 1
        mons.append(l)
    end = fo(B, 0x7AA2) + 26 + sum(len(l) + 1 for l in mons)
    # 第57弾の カントーの つり（03:524D の farcall の 先）
    o = fo(0x03, 0x524D); SB = g[o + 1]; kf = r16(g, o + 3)
    km = r16(g, fo(SB, kf + 9)); kr = r16(g, fo(SB, kf + 0x4B))
    kmaps = []; o = fo(SB, km)
    while g[o] != 0xFF: kmaps.append(tuple(g[o:o + 3])); o += 3
    # マップの 見出し
    mg = fo(0x25, 0x40ED); gp = []; o = mg
    while not gp or o < fo(0x25, min(gp)): gp.append(r16(g, o)); o += 2
    tb, ta = ts_table(g); TS = fo(tb, ta); CP = fo(0x3E, 0x734A)
    def hdr(gi, mi): return fo(0x25, gp[gi - 1]) + 9 * (mi - 1)
    def water(h):
        ao = fo(g[h], r16(g, h + 3)); H, W = g[ao + 1], g[ao + 2]; bo = fo(g[ao + 3], r16(g, ao + 4))
        t = TS + g[h + 1] * 15; co = fo(g[t + 6], r16(g, t + 7))
        return any(g[CP + c] & 0x0F == 1 for b in set(g[bo:bo + W * H]) for c in g[co + b * 4:co + b * 4 + 4])
    srt = sorted(set(gp)); pairs = []
    kset = {(a, b) for a, b, _ in kmaps}
    for gi in range(1, 26):
        p = gp[gi - 1]; e = [q for q in srt if q > p][0]
        for mi in range(1, (fo(0x25, e) - fo(0x25, p)) // 9 + 1):
            h = hdr(gi, mi); lm, fg = g[h + 5], g[h + 8]
            if (gi, mi) in kset or not lm or not fg or fg > 13 or 0x2E <= lm < 0x5A or lm > 0x5E: continue
            if (gi, mi) == (3, 81): continue                       # SafariZoneBeta（行けない）
            if water(h) and (lm, fg) not in pairs: pairs.append((lm, fg))
    nj = len(pairs)
    # カントー：グループ 14〜（つりざおの グループ sg → 14 + sg、データの ない 所（$FF）→ ボロ・いいつりざおだけ）
    ks = sorted({s for _, _, s in kmaps if s != 0xFF}); kid = {s: 14 + i for i, s in enumerate(ks)}
    kid[0xFF] = 14 + len(ks)
    for s in ks:
        l = [0x81, 0x76, 0x3C]
        for i in range(4):
            sp = g[fo(SB, kr) + s * 8 + i * 2]
            if sp and sp not in l: l.append(sp)
        mons.append(l)
    mons.append([0x81, 0x76, 0x3C])
    for a, b, s in kmaps:
        lm = g[hdr(a, b) + 5]
        if (lm, kid[s]) not in pairs: pairs.append((lm, kid[s]))
    out = bytearray()
    for lm, fg in pairs: out += bytes([lm, fg])
    out.append(0)
    gp_at = 0x7A2B + len(out); out += bytes(2 * len(mons)); la = 0x7A2B + len(out)
    for i, l in enumerate(mons):
        out[gp_at - 0x7A2B + 2 * i] = la & 0xFF; out[gp_at - 0x7A2B + 2 * i + 1] = la >> 8
        out += bytes(l) + b'\0'; la += len(l) + 1
    lim = end
    while g[lim] == 0 and lim < fo(B, 0x8000): lim += 1
    assert fo(B, 0x7A2B) + len(out) <= lim - 16, (hex(len(out)), hex(lim))
    g[fo(B, 0x7A2B):end] = bytes(end - fo(B, 0x7A2B))
    g[fo(B, 0x7A2B):fo(B, 0x7A2B) + len(out)] = out
    g[fo(B, 0x79EA)] = len(mons); g[fo(B, 0x79F1)] = gp_at & 0xFF; g[fo(B, 0x79F2)] = gp_at >> 8
    g[fo(B, 0x7994)] = 0xC9                                         # FishNest_Extra（キットの サファリ）を 使わない
    log.append('つりの ぶんぷ：ジョウト %d・カントー %d か所、グループ %d（3F:7A2B〜%04X）' %
               (nj, len(pairs) - nj, len(mons), 0x7A2B + len(out)))



def fix_twin_doors(g, log):
    """c2g.EXTRA_WARPS で 足した 入口の マスに、となりの 入口と 同じ 当たりを つける（その ブロックが ほかで 使われない ときだけ）"""
    from c2g import EXTRA_WARPS, GMAP
    mg = fo(0x25, 0x40ED); tb, ta = ts_table(g); TS = fo(tb, ta)
    for name, L in EXTRA_WARPS.items():
        gi, mi = GMAP[name]; h = fo(0x25, r16(g, mg + 2 * (gi - 1))) + 9 * (mi - 1)
        ao = fo(g[h], r16(g, h + 3)); H, W = g[ao + 1], g[ao + 2]; bo = fo(g[ao + 3], r16(g, ao + 4))
        t = TS + 15 * g[h + 1]; co = fo(g[t + 6], r16(g, t + 7))
        for y, x, _ in L:
            b = g[bo + (y // 2) * W + x // 2]; q = (y % 2) * 2 + x % 2; qn = (y % 2) * 2 + (x - 1) % 2
            assert x % 2 == 1 and g[bo:bo + W * H].count(b) == 1, (name, hex(b))
            g[co + 4 * b + q] = g[co + 4 * b + qn]
            log.append('2マスの 入口：%s (%d,%d) ブロック %02X → %02X' % (name, x, y, b, g[co + 4 * b + q]))



# タイルセットの 当たりの なおし：(金の タイルセット番号, ブロック, 4分の1, いまの 値, なおす 値, 説明)
QUAD_FIX = [(34, 0x3D, 3, 0x90, 0x00, 'ハナダの バッジの家・セキチクの つりざおの家：上の かべの 下の マス（1,1）（5,1）（7,1）が カウンターで 歩けない（赤・黄では 歩ける）')]

def fix_quads(g, log):
    tb, ta = ts_table(g); TS = fo(tb, ta)
    for ts, b, q, old, new, what in QUAD_FIX:
        t = TS + 15 * ts; co = fo(g[t + 6], r16(g, t + 7))
        assert g[co + 4 * b + q] == old, (ts, hex(b), hex(g[co + 4 * b + q]))
        g[co + 4 * b + q] = new; log.append('当たり：' + what)



def fix_follow_tiles(g, log):
    """連れ歩き（追加機能パッチ）：人の 絵を 読みなおした（LoadUsedSpritesGFX）あと、出て いる 人の タイルの 番号も なおす。
       研究所で はじめての ポケモンを もらうと、連れ歩きの 絵（タイル $0C〜）が 読まれるのに オーキドの タイルが $0C の まま で、
       オーキドが 連れ歩きの 絵に、ライバルが オーキドの 絵に なっていた（クリスタル版は ReloadSpriteIndex で なおる）。"""
    B = 0x79; o = fo(B, 0x401D + 0x1B)
    assert bytes(g[o:o + 3]) == bytes([0xC3, 0x29, 0x48]) and g[fo(B, 0x4574)] == 0x3E
    at = 0x7D60; assert not any(g[fo(B, at):fo(B, at) + 16])
    g[fo(B, at):fo(B, at) + 6] = bytes([0xCD, 0x29, 0x48, 0xC3, 0x74, 0x45])     # call Fw_ReloadMask / jp Fw_RefreshTiles
    g[o + 1] = at & 0xFF; g[o + 2] = at >> 8
    log.append('連れ歩き：人の 絵を 読みなおした あと 人の タイルも なおす（79:%04X）' % at)



def fix_waitsfx(g, log):
    """赤の 音の しくみ（第98弾 シゲルの 曲・第68弾）が 鳴って いる 間（$C000 ≥ $A5）は 金の 効果音が すすまないのに、
       WaitSFX（00:3D77）は 金の チャンネル5〜8の フラグ（赤の 音の RAM と 重なる）を 待ちつづけて 止まっていた
       （オーキド研究所で 図鑑を もらった ところで 止まる）。赤の 音の 間は 待たない。
       バンクを かえずに ホームだけで 書く（3D77〜3D95 と HFI の うしろの あき 3FD5〜3FDF）。
       バンクを かえる 書きかた（HFI・rst $08）では hROMBank が ずれた 所で よばれた とき（トキワの もりで
       むしとりに 勝った あと）に もどる バンクが ちがい、止まった。"""
    o = 0x3D77
    assert bytes(g[o:o + 0x1F]) == bytes.fromhex('e521ccc0cb4620f921fec0cb4620f22130c1cb4620eb2162c1cb4620e4e1c9')
    assert not any(g[0x3FD5:0x3FE0])
    A = bytes([0xE5,                               # 3D77 push hl
               0x21, 0x00, 0xC0, 0xCB, 0x7E, 0x20, 0x15,   # 3D78 .wait: ld hl,$C000 / bit 7,[hl] / jr nz,.done（3D94）
               0x2E, 0xCC, 0xCB, 0x46, 0x20, 0xF3,         # 3D7F ld l,$CC / bit 0,[hl] / jr nz,.wait
               0x2E, 0xFE, 0xCB, 0x46, 0x20, 0xED,         # 3D85 ld l,$FE / bit 0,[hl] / jr nz,.wait
               0xC3, 0xD5, 0x3F,                           # 3D8B jp 3FD5
               0x2E, 0x62, 0xCB, 0x46, 0x20, 0xE4,         # 3D8E ld l,$62 / bit 0,[hl] / jr nz,.wait
               0xE1, 0xC9])                                # 3D94 .done: pop hl / ret
    assert len(A) == 0x1F
    B = bytes([0x24, 0x2E, 0x30, 0xCB, 0x46, 0xC2, 0x78, 0x3D, 0xC3, 0x8E, 0x3D])   # inc h / ld l,$30 / bit 0 / jp nz,.wait / jp 3D8E
    g[o:o + 0x1F] = A; g[0x3FD5:0x3FE0] = B
    log.append('WaitSFX：赤の 音の 間は 待たない（ホーム 3D77・3FD5）')


def fix_sidewalls(g, log):
    """横の かべ（コリジョン b0〜b7）：金の GetMovementPermissions は となりの マスの かべを 見ても いつも「下」を ふさぐ（金の バグ）。
    クリスタル版と 同じく 下・上・右・左 を ふさぐ ように（set 3 → 3/2/0/1）。
    これが ないと おつきみやま 1F の かべの すきまに 横から 入れて、出られなく なる"""
    for a, bit in ((0x2A4C, 3), (0x2A66, 2), (0x2A80, 0), (0x2A9A, 1)):
        assert g[a + 3:a + 6] == b'\xcb\xde\xc9' and g[a] == 0x21, hex(a)
        g[a + 4] = 0xC6 | bit << 3
    log.append('sidewalls')

def fix_statuscolor_item(g, log):
    """追加機能パッチの 状態異常の 色（49:StatusColor_BattleLayout）：戦いで どうぐを 使うと、画面の 色わけを 作る 時に
    まだ 自分の HP の わくが 消えて いて（$7f）、状態異常の 文字の ますが ふつうの 色・バンク0 に もどる
    → わくが もどった あと「どく」などが べつの 絵（Ⅱ など）に なる。
    ますが 空白（$7f）でも 自分の ポケモンが 状態異常なら 色1 の 文字（バンク1・6本目）に する（バンク1 の $7f は 空白）"""
    a, F = fo(0x49, 0x4150), fo(0x49, 0x7F00)
    assert g[a:a + 11] == bytes.fromhex('fa50c4fe7c3e0e28023e03'), g[a:a + 11].hex()
    assert not any(g[F:F + 24])
    g[a:a + 11] = bytes([0xCD, 0x00, 0x7F]) + bytes(8)
    g[F:F + 24] = bytes([0xFA, 0x50, 0xC4,      # ld a,[ます]
                         0xFE, 0x7C, 0x28, 0x0C,  # cp $7c / jr z,.b1
                         0xFE, 0x7F, 0x20, 0x0B,  # cp $7f / jr nz,.plain
                         0xFA, 0x10, 0xCB,      # ld a,[wBattleMonStatus]
                         0xA7, 0x28, 0x05,      # and a / jr z,.plain
                         0x00, 0x00,
                         0x3E, 0x0E, 0xC9,      # .b1: ld a,$0e / ret
                         0x3E, 0x03]) + b''     # .plain: ld a,$03
    g[F + 24] = 0xC9
    log.append('statuscolor_item')

def apply(g, E, M, log):
    from maps import GMGP
    from cmaps import maplist
    gmap = {m['name']: m for m in maplist(g, GMGP, 'pokegold')}
    for k in gmap: gmap[k]['hdr'] = int(gmap[k]['hdr'])
    fix108(g, E, M, log, gmap)
    fix_gold_blocks(g, log, gmap)
    fix97(g, E, M, log)
    fix96(g, log); fix99(g, log); fix105(g, M, log); fix109(g, log); fix110_poison(g, log); fix110_boxfull(g, log); fix110_follow(g, log); fix100(g, log); fix_fishnest(g, log); fix_twin_doors(g, log); fix_quads(g, log); fix_follow_tiles(g, log); fix_waitsfx(g, log); fix_sidewalls(g, log); fix_statuscolor_item(g, log)
