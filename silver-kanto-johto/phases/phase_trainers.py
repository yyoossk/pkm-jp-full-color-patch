"""トレーナーの 手持ち（第2〜9・13弾 など）：
   銀の トレーナーの 処理（$0E:$5511〜）を $E2 に 写し、手持ちの 表を 80 クラスに のばす。
   カントーで 使う (クラス, 番号) は クリスタル版の 手持ち、それ以外は 銀の 手持ち（ジョウトは 銀の 物語）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, xlat, port
from gsc import fo, r16

TB = 0xE2
S_CODE, S_TAB, S_N = 0x5511, 0x595C, 66          # 銀：GetTrainerClassName … TrainerGroups（66 クラス）
C_TAB, C_N = 0x45B3, 79                          # クリスタル版：$7E:$45B3（79 クラス）
NCLASS = 80


def parties(rom, bank, ptrs, k, ends):
    """クラス k の 手持ちを ぜんぶ 読む → [bytes]"""
    p = fo(bank, ptrs[k]); out = []
    end = min([fo(bank, e) for e in ends if fo(bank, e) > p] + [fo(bank, 0x8000)])
    while p < end:
        q = p
        while rom[q] != 0x50: q += 1
        q += 1; typ = rom[q]; q += 1
        if typ > 3: break
        n = {0: 2, 1: 6, 2: 3, 3: 7}[typ]
        while rom[q] != 0xFF: q += n
        q += 1
        out.append(bytes(rom[p:q])); p = q
        if len(out) > 60: break
    return out


def fix_items(T, party, P):
    """手持ちの どうぐを 銀の 番号へ"""
    b = bytearray(party); q = b.index(0x50) + 1; typ = b[q]; q += 1
    n = {0: 2, 1: 6, 2: 3, 3: 7}[typ]
    while b[q] != 0xFF:
        if typ in (2, 3): b[q + 2] = P.x_item(b[q + 2])
        q += n
    return bytes(b)


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read()
    T = xlat.Tables()
    P = port.Port.__new__(port.Port); P.T = T; P.todo = {}
    used = ctx.get('kanto_trainers', set())

    # 銀の 処理を $E2 へ（同じ アドレス）
    rom[fo(TB, S_CODE):fo(TB, S_TAB)] = rom[fo(0x0E, S_CODE):fo(0x0E, S_TAB)]
    rom[fo(TB, 0x7FE0):fo(TB, 0x8000)] = rom[fo(0x0E, 0x7FE0):fo(0x0E, 0x8000)]   # 追加機能の フック（$5764 から 呼ぶ）
    sp = [r16(rom, fo(0x0E, S_TAB) + 2 * i) for i in range(S_N)]
    cp = [r16(cmod, fo(0x7E, C_TAB) + 2 * i) for i in range(C_N)]
    cinv = xlat.inv(T.c_tc); ginv = xlat.inv(T.g_tc)
    out = {}
    nk = 0
    for gi in range(1, NCLASS):
        name = ginv.get(gi)
        ci = T.c_tc.get(name) if name else (gi if gi >= 0x44 else None)
        slist = parties(rom, 0x0E, sp, gi - 1, sp) if gi <= S_N else []
        clist = parties(cmod, 0x7E, cp, ci - 1, cp) if ci and ci <= C_N else []
        res = []
        for i in range(max(len(slist), len(clist))):
            if ci and (ci, i + 1) in used and i < len(clist): res.append(fix_items(T, clist[i], P)); nk += 1
            elif i < len(slist): res.append(slist[i])
            elif i < len(clist): res.append(fix_items(T, clist[i], P)); nk += 1
        out[gi] = res
    # クリスタル版が 足した 赤の トレーナーの 名前は、男・女を 見ずに つけて あった（ふなのりが「ユミ」、ミニスカートが
    # 「ヒロシ」など）。クラスの 男・女と 名前が 合わない ものを 合う 名前に かえる
    import jptext
    MALE_C = {20, 22, 23, 24, 27, 30, 32, 36, 37, 38, 40, 41, 43, 44, 45, 47, 48, 49, 50, 52, 54, 56, 59, 65, 74, 75, 76, 77, 78, 79}
    FEMALE_C = {25, 28, 29, 33, 34, 39, 53, 57, 60, 62, 73}
    FEM = set('ユキ ナナ マイ カナ ミホ ノゾミ ユミ アヤ エミ サキ りナ サオり ユり アイ エり イズミ ミユキ ミキ ハルカ マユミ ナツキ '
              'ミナミ サトミ ミスズ カオり ミズホ チサト ユミコ チアキ アユミ'.split())
    MAS = set('ショウタ ヒロシ ケンジ ユウジ タケシ カズオ ヨシオ ノボル ミツル タカシ ゴロウ ジョウジ ケンタ ダイスケ カズヤ タロウ '
              'アキラ ナオキ りョウ ジロウ サブロウ ユウタ タクヤ ツヨシ ケント ナオト マイク カズマ マコト タダシ マサオ'.split())
    POOL_M = 'ゴロウ ノボル ヒデキ マサル ススム ケイゴ トオル ヨシキ カツミ テツオ イサオ シゲオ ミノル ヤスオ リキヤ'.split()
    POOL_F = 'ミドリ アキコ ヨシエ トモミ クミ ハルミ シズカ ミサキ レイコ エりコ ヒロミ マキ ナオミ ノりコ ユカ サヤカ りエ'.split()
    KINV = {}
    for kk, v in jptext.CM.items():
        if len(kk) == 1 and ord(kk) > 0x3000: KINV.setdefault(v, kk)
    kdec = lambda bb: ''.join(KINV.get(x, '?') for x in bb)
    nren = 0
    for c in MALE_C | FEMALE_C:
        bad, pool = (FEM, POOL_M) if c in MALE_C else (MAS, POOL_F)
        names = [kdec(b[:b.index(0x50)]) for b in out.get(c, [])]
        k = 0
        for i, b in enumerate(out.get(c, [])):
            j = b.index(0x50); nm = names[i]
            if nm not in bad: continue
            while pool[k % len(pool)].replace('リ', 'り') in names: k += 1
            nn = pool[k % len(pool)].replace('リ', 'り'); k += 1
            names[i] = nn; out[c][i] = jptext.enc(nn) + b[j:]; nren += 1
    log.append('トレーナーの 名前：クラスの 男・女と 合わない %d 人を かえた' % nren)
    # クラス 63（レッド）は ゴールド（第47弾：シロガネやま。手持ちは クリスタル版の ヒビキと 同じ）
    mv = lambda lv, sp_, *ms: bytes([lv, sp_, *ms])
    import jptext
    out[63][0] = jptext.enc('ゴールド@') + b'\x01' + mv(81, 0xB8, 0x39, 0x3A, 0x26, 0xCD) + mv(73, 0xC4, 0xBD, 0x73, 0x81, 0x5E) + \
        mv(75, 0x8F, 0x85, 0xAD, 0x9C, 0x22) + mv(77, 0x9A, 0x73, 0x22, 0xEB, 0x4C) + mv(77, 0x9D, 0x35, 0x59, 0x81, 0x62) + \
        mv(77, 0xA0, 0x39, 0xF2, 0xA3, 0x08) + b'\xff'
    # 置く：$4000〜$5511 と 表の 後ろ
    tab = S_TAB; free = [(0x4000, S_CODE), (S_TAB + 2 * NCLASS, 0x7C00)]   # $7C00〜 は クラスの 表
    cur = 0; addr = free[0][0]
    for gi in range(1, NCLASS):
        blob = b''.join(out[gi])
        if addr + len(blob) > free[cur][1]:
            cur += 1; addr = free[cur][0]
            assert addr + len(blob) <= free[cur][1], 'トレーナーの 手持ちが 入りきらない'
        rom[fo(TB, addr):fo(TB, addr) + len(blob)] = blob
        rom[fo(TB, tab) + 2 * (gi - 1):fo(TB, tab) + 2 * (gi - 1) + 2] = addr.to_bytes(2, 'little')
        addr += len(blob)
    # 呼び出しを $E2 へ
    import re
    nfar = 0
    for m in list(re.finditer(rb'\x3e\x0e\x21(..)\xcf', bytes(rom[:0x200000]), re.S)) + \
            list(re.finditer(rb'\x21(..)\x3e\x0e\xcf', bytes(rom[:0x200000]), re.S)):
        v = r16(m.group(1), 0)
        if S_CODE <= v < S_TAB:
            o = m.start() + (1 if rom[m.start()] == 0x3E else 4); assert rom[o] == 0x0E; rom[o] = TB; nfar += 1
    for o in (0x2ABA9, 0x2ABB1, 0x2ABBD, 0x2ABC7, 0x2ABEA, 0x2AC04, 0x8FCC8, 0x8FCD4, 0x8FCE0, 0x8FCEB):
        assert rom[o:o + 2] == bytes([0x3E, 0x0E]), hex(o); rom[o + 1] = TB
    classes(rom, cmod, P, log)

    # クラス $40（カントーの ライバル）の トレーナーの 名前は wGreensName（第52弾）。GetTrainerName（$E2:$5939）を フック
    o = fo(TB, 0x5939); assert rom[o:o + 4] == bytes([0x0D, 0xC5, 0x06, 0x00])
    hk = 0x7EF0; GREENS = 0xD1CD
    rom[fo(TB, hk):fo(TB, hk) + 16] = bytes([0x79, 0xFE, 0x40, 0x21, GREENS & 0xff, GREENS >> 8, 0xCA, 0x50, 0x59,
                                             0x0D, 0xC5, 0x06, 0x00, 0xC3, 0x3D, 0x59])
    rom[o:o + 4] = bytes([0xC3, hk & 0xff, hk >> 8, 0x00])
    # wGreensName の はじめの 名前「シゲル」（銀は グリーン）
    import jptext
    o = 0x5D82; assert rom[o:o + 5] == jptext.enc('グリーン@'); rom[o:o + 5] = jptext.enc('シゲル@@')

    # トレーナーの 種類の 名前：クリスタル版の 表（$7C:$49BC、79 クラス。1〜66 は 銀と 同じ 並び、64 は「ライバル」）
    assert rom[0x3562:0x3565] == bytes([0x0B, 0xD6, 0x52])
    rom[0x3562:0x3565] = bytes([0x7C, 0xBC, 0x49])
    log.append('トレーナー：処理と 表を $%02X へ（farcall %d）、%d クラス、カントーの 手持ち %d、入れた 所 %04X' % (TB, nfar, NCLASS - 1, nk, addr))
    if P.todo: log.append('TODO ' + str(P.todo))
    return rom


def classes(rom, cmod, P, log):
    """クラス 67〜79（クリスタルの ミナキと この MOD の 12 クラス）の 表：アイテム・AI、DV、色、絵（第10弾）"""
    def w(v): return bytes([v & 0xff, v >> 8])
    N0, N = 66, 79
    # アイテム・AI（7 バイト）：$0E と $E2 の $7C00 に 79 クラス分
    S_ATTR = 0x5580; C_ATTR = fo(0x0E, 0x7DD7); NA = 0x7C00
    tab = bytearray(rom[fo(0x0E, S_ATTR):fo(0x0E, S_ATTR) + 7 * N0])
    for i in range(N0, N):
        e = bytearray(cmod[C_ATTR + 7 * i:C_ATTR + 7 * i + 7]); e[0] = P.x_item(e[0]); e[1] = P.x_item(e[1]); tab += e
    # 表は $E2:$7C00 だけに 置く（$0E:$7C00〜 は 銀の 戦いの ことば。前は ここに 書いて いて、ことばが こわれ、
    # 「○○は ×× を つかった」の あとなどで 文の 命令で ない 所を 読んで とまった）。
    # $0E・$11 の 読む 所は、その クラスの 7 バイトを WRAM の BUF に 写す 小さな 処理を よんで、hl ＝ BUF + d に する。
    rom[fo(TB, NA):fo(TB, NA) + len(tab)] = tab
    BUF, HELP, STUB = 0xD77B, 0x7F00, 0x7FF0             # BUF：セーブの すき間の あき（phase_kanto の free の 後ろ）
    help_ = (bytes([0xC5, 0x7B, 0x21]) + w(NA) + bytes([0x01, 7, 0, 0xCD, 0x5F, 0x31, 0x11]) + w(BUF) +
             bytes([0x06, 7, 0x2A, 0x12, 0x13, 0x05, 0x20, 0xFA, 0xC1, 0x21]) + w(BUF) + bytes([0x06, 0, 0x09, 0x01, 7, 0, 0xC9]))
    assert not any(rom[fo(TB, HELP):fo(TB, HELP) + len(help_)]); rom[fo(TB, HELP):fo(TB, HELP) + len(help_)] = help_
    stub = bytes([0xD5, 0x5F, 0x3E, TB, 0x21]) + w(HELP) + bytes([0xCF, 0xD1, 0xC9])   # push de / ld e,a / farcall / pop de / ret
    for b in (0x0E, 0x11):
        assert not any(rom[fo(b, STUB):fo(b, STUB) + len(stub)]); rom[fo(b, STUB):fo(b, STUB) + len(stub)] = stub
    for off, d in ((0x3956A, 0), (0x38023, 5), (0x38110, 5)):    # ld hl,表+d / ld bc,7 / call AddNTimes → ld c,d / call STUB
        assert rom[off:off + 9] == bytes([0x21]) + w(S_ATTR + d) + bytes([0x01, 7, 0, 0xCD, 0x5F, 0x31]), hex(off)
        rom[off:off + 9] = bytes([0x0E, d, 0xCD]) + w(STUB) + bytes(4)
        if fo(0x0E, S_CODE) <= off < fo(0x0E, S_TAB):
            e2 = off - fo(0x0E, 0x4000) + fo(TB, 0x4000); rom[e2 + 1:e2 + 3] = w(NA + d)
    off = 0x4413C                                             # バンク11：ld hl,表+3 / ld a,[$D10F] / dec a / ld bc,7 / call AddNTimes
    assert rom[off:off + 13] == bytes([0x21]) + w(S_ATTR + 3) + bytes([0xFA, 0x0F, 0xD1, 0x3D, 0x01, 7, 0, 0xCD, 0x5F, 0x31])
    rom[off:off + 13] = bytes([0xFA, 0x0F, 0xD1, 0x3D, 0x0E, 3, 0xCD]) + w(STUB) + bytes(4)
    # DV（2 バイト）：$E2:$7E40 に 79 クラス分、バンク9 の 読む 所は 終わりの 14 バイトへ（GetFarHalfword）
    S_DVS = 0x75E1; ND = 0x7E40
    dv = bytes(rom[fo(9, S_DVS):fo(9, S_DVS) + 2 * N0]) + bytes(cmod[fo(9, 0x7DD8) + 2 * N0:fo(9, 0x7DD8) + 2 * N])
    rom[fo(TB, ND):fo(TB, ND) + len(dv)] = dv
    o = 0x275D7; assert rom[o:o + 10] == bytes([0x21, 0xE1, 0x75, 0x09, 0x09, 0x2A, 0x47, 0x4E, 0xE1, 0xC9])
    tr = bytes([0x21]) + w(ND) + bytes([0x09, 0x09, 0x3E, TB, 0xCD, 0xF8, 0x30, 0x45, 0x4C, 0xE1, 0xC9])
    assert not any(rom[fo(9, 0x7FF2):fo(9, 0x8000)]); rom[fo(9, 0x7FF2):fo(9, 0x8000)] = tr
    rom[o:o + 10] = bytes([0xC3, 0xF2, 0x7F]) + bytes(7)
    # 色（4 バイト）：67〜79 は バンク2 の 空きへ。0x9B75 "ld bc,$74C3 ; add hl,bc ; ret" を 分ける
    # 0〜66：クリスタル版で 銀と ちがう 色（主人公＝レッドの 色、レッドは もとの 主人公の 色）を 銀の 表へ
    for i in range(N0):
        cp = cmod[fo(2, 0x77E3) + 4 * i:fo(2, 0x77E3) + 4 * i + 4]; so = fo(2, 0x74C3) + 4 * i
        if rom[so:so + 4] != cp: rom[so:so + 4] = cp; log.append('トレーナーの 色 %d を クリスタル版の ものに' % i)
    pal = bytes(cmod[fo(2, 0x77E3) + 4 * N0:fo(2, 0x77E3) + 4 * N])
    a = 0x7F63
    while any(rom[fo(2, a):fo(2, a) + 4]): a += 1
    pa = a + 20
    code = bytes([0x7C, 0xA7, 0x28, 0x0A, 0x7D, 0xFE, 0x08, 0x38, 0x05, 0x01]) + w((pa - 4 * N0) & 0xffff) + \
        bytes([0x09, 0xC9, 0x01, 0xC3, 0x74, 0x09, 0xC9])
    assert len(code) <= 20 and not any(rom[fo(2, a):fo(2, a) + 20 + len(pal)])
    rom[fo(2, a):fo(2, a) + len(code)] = code; rom[fo(2, pa):fo(2, pa) + len(pal)] = pal
    o = 0x9B75; assert rom[o:o + 5] == bytes([0x01, 0xC3, 0x74, 0x09, 0xC9]); rom[o:o + 5] = bytes([0xC3]) + w(a) + bytes(2)
    # 絵（3 バイト）：$E4:$4000 に 79 クラス分、GetTrainerPic（$14:$588D）を 79 まで・表の バンクを $E4 へ
    PB = 0xE4
    pic = bytearray(rom[fo(0x20, 0x4000):fo(0x20, 0x4000) + 3 * N0])
    cfix = cmod[0x5126A:0x5126A + 26]; ct = fo(0x7C, 0x48CF)
    for i in range(N0, N):
        e = bytearray(cmod[ct + 3 * i:ct + 3 * i + 3]); real = cfix[e[0] - 0x12]
        if real < 0x60:
            src = fo(real, r16(e, 1)); n = min(0x500, fo(real + 1, 0x4000) - src)
            rom[fo(port.cb(real), r16(e, 1)):fo(port.cb(real), r16(e, 1)) + n] = cmod[src:src + n]; real = port.cb(real)
        e[0] = real; pic += e
    pic[3 * 62:3 * 63] = pic[3 * 11:3 * 12]                 # クラス 63（ゴールド）の 絵 = クラス 12（ゴールドの 絵）
    rom[fo(PB, 0x4000):fo(PB, 0x4000) + len(pic)] = pic
    rom[fo(2, 0x74C3) + 4 * 63:fo(2, 0x74C3) + 4 * 64] = rom[fo(2, 0x74C3) + 4 * 12:fo(2, 0x74C3) + 4 * 13]
    g = 0x5188A; assert rom[g:g + 8] == bytes([0xFA, 0x0F, 0xD1, 0xA7, 0xC8, 0xFE, 0x43, 0xD0]); rom[g + 6] = N + 1
    n = 0
    for o in range(g, g + 80):
        if rom[o:o + 5] == bytes([0x3E, 0x20, 0xCD, 0xE4, 0x30]): rom[o + 1] = PB; n += 1
    assert n == 3, n
    log.append('クラス 67〜79：アイテム・AI・DV・色・絵')
