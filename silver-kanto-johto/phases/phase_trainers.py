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
    for b in (0x0E, TB): rom[fo(b, NA):fo(b, NA) + len(tab)] = tab
    for off, d in ((0x3956A, 0), (0x38023, 5), (0x38110, 5), (0x4413C, 3)):
        assert rom[off] == 0x21 and r16(rom, off + 1) == S_ATTR + d, hex(off)
        rom[off + 1:off + 3] = w(NA + d)
        if fo(0x0E, S_CODE) <= off < fo(0x0E, S_TAB):
            e2 = off - fo(0x0E, 0x4000) + fo(TB, 0x4000); rom[e2 + 1:e2 + 3] = w(NA + d)
    # DV（2 バイト）：$E2:$7E40 に 79 クラス分、バンク9 の 読む 所は 終わりの 14 バイトへ（GetFarHalfword）
    S_DVS = 0x75E1; ND = 0x7E40
    dv = bytes(rom[fo(9, S_DVS):fo(9, S_DVS) + 2 * N0]) + bytes(cmod[fo(9, 0x7DD8) + 2 * N0:fo(9, 0x7DD8) + 2 * N])
    rom[fo(TB, ND):fo(TB, ND) + len(dv)] = dv
    o = 0x275D7; assert rom[o:o + 10] == bytes([0x21, 0xE1, 0x75, 0x09, 0x09, 0x2A, 0x47, 0x4E, 0xE1, 0xC9])
    tr = bytes([0x21]) + w(ND) + bytes([0x09, 0x09, 0x3E, TB, 0xCD, 0xF8, 0x30, 0x45, 0x4C, 0xE1, 0xC9])
    assert not any(rom[fo(9, 0x7FF2):fo(9, 0x8000)]); rom[fo(9, 0x7FF2):fo(9, 0x8000)] = tr
    rom[o:o + 10] = bytes([0xC3, 0xF2, 0x7F]) + bytes(7)
    # 色（4 バイト）：67〜79 は バンク2 の 空きへ。0x9B75 "ld bc,$74C3 ; add hl,bc ; ret" を 分ける
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
    rom[fo(PB, 0x4000):fo(PB, 0x4000) + len(pic)] = pic
    g = 0x5188A; assert rom[g:g + 8] == bytes([0xFA, 0x0F, 0xD1, 0xA7, 0xC8, 0xFE, 0x43, 0xD0]); rom[g + 6] = N + 1
    n = 0
    for o in range(g, g + 80):
        if rom[o:o + 5] == bytes([0x3E, 0x20, 0xCD, 0xE4, 0x30]): rom[o + 1] = PB; n += 1
    assert n == 3, n
    log.append('クラス 67〜79：アイテム・AI・DV・色・絵')
