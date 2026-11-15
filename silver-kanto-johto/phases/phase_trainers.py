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
    tab = S_TAB; free = [(0x4000, S_CODE), (S_TAB + 2 * NCLASS, 0x7FE0)]
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
    log.append('トレーナー：処理と 表を $%02X へ（farcall %d）、%d クラス、カントーの 手持ち %d、入れた 所 %04X' % (TB, nfar, NCLASS - 1, nk, addr))
    if P.todo: log.append('TODO ' + str(P.todo))
    return rom
