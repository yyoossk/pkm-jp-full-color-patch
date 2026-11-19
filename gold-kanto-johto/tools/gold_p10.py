"""第10弾（トレーナーの種類 68〜79 を 足す）を 金に 入れる。
   データは クリスタル版 完成 ROM（A844BDEB）から 取り出す（クラス 67 なぞのせいねん も 金に ないので いっしょに 入れる）。
   ・名前・絵・DV の 表 → 新しい バンク NB（DV は GetTrainerDVs を 遠くの バンクから 読むように 書きかえ）
   ・色（4バイト×80）→ 金の バンク 02 の 空き $7EB0（追加機能パッチが 使っていない 所）
   ・属性（7バイト×79）→ トレーナーの バンク TB の $4000（コピーした コードと バンク 11 の AI から）と、
     バンク 0E の 使われなくなった 古い 手持ちの 所（バンク 0E の AI から）
   ・ジムリーダーの 表（ジョウトの うしろに 四天王 3人、カントーの うしろに サカキ）→ バンク 0F の 使われていない GetHalfHP の 所
   ・手持ち：79 クラス。表は TB:$595C のまま、中身は TB の $4229〜$5510 と $59FA〜 に
"""
import re
from trainers import merged
from jpchar import encode, decode

def fo(b, a): return b * 0x4000 + a - 0x4000
def r16(r, o): return r[o] | r[o + 1] << 8
def w16(r, o, v): r[o] = v & 0xFF; r[o + 1] = v >> 8

NEW_N = 79
G_N = 66

def lzlen(r, o):
    """第二世代の LZ の 長さ（終わりの $FF まで）"""
    s = o
    while True:
        b = r[o]
        if b == 0xFF: return o + 1 - s
        cmd = b >> 5
        if cmd == 7:
            cmd = (b >> 2) & 7; n = ((b & 3) << 8 | r[o + 1]) + 1; o += 2
        else:
            n = (b & 0x1F) + 1; o += 1
        if cmd == 0: o += n
        elif cmd == 1: o += 1
        elif cmd == 2: o += 2
        elif cmd == 3: pass
        else: o += 1 if r[o] & 0x80 else 2

def names(r, o, n):
    L = []
    for i in range(n):
        e = r.index(0x50, o); L.append(bytes(r[o:e + 1])); o = e + 1
    return L

def apply(g, VAN, MOD, TB, NB, log):
    M = MOD
    L = merged(VAN, M, bytes(g[:0x200000]))       # 金の 0E を 書きかえる 前に
    # ---- NB：名前・絵・DV
    assert not any(g[fo(NB, 0x4000):fo(NB + 1, 0x4000)])
    cur = [0x4000]
    def put(data):
        a = cur[0]; g[fo(NB, a):fo(NB, a) + len(data)] = data; cur[0] += len(data); assert cur[0] <= 0x8000; return a
    # 名前（金 0B:$52D6 66こ。ホーム $3562 が 指す）
    assert g[0x3562:0x3565] == bytes([0x0B, 0xD6, 0x52])
    gn = names(g, fo(0x0B, 0x52D6), G_N)
    mn = names(M, fo(0x7C, 0x49BC), NEW_N)
    assert decode(gn[63]) == 'ジムりーダー@' and decode(mn[63]) == 'ライバル@'
    gn[63] = mn[63]
    na = put(b''.join(gn + mn[G_N:]))
    g[0x3562] = NB; w16(g, 0x3563, na)
    # 絵：クリスタル版の 表（7C:$48CF、3バイト）。バンクは FixPicBank の 表（14:$526A、番号 - $12）で 決まる
    gp = fo(0x14, 0x588A)
    assert g[gp:gp + 8] == bytes.fromhex('fa0fd1a7c8fe43d0')
    seg = bytes(g[gp:gp + 0x50]); k = seg.index(b'\x21\x00\x40')
    ks = [m.start() for m in re.finditer(b'\x3e\x20\xcd', seg)]; assert len(ks) == 3, ks
    old = bytes(g[fo(0x20, 0x4000):fo(0x20, 0x4000) + 3 * G_N])
    ents = bytearray(old)
    for c in range(G_N + 1, NEW_N + 1):
        if c == 70:                                  # してんのう ワタル：クリスタル版は クリスタルの ワタル（チャンピオン）の絵 → 金の ワタルの絵
            ents += old[15 * 3:16 * 3]; continue
        e = fo(0x7C, 0x48CF) + 3 * (c - 1)
        bank = M[0x5126A + M[e] - 0x12]; a = r16(M, e + 1)
        src = fo(bank, a); n = lzlen(M, src)
        p = put(M[src:src + n]); ents += bytes([NB, p & 0xFF, p >> 8])
        log.append('絵 %d：%d バイト（クリスタル版 %02X:%04X）' % (c, n, bank, a))
    pt = put(bytes(ents))
    g[gp + 6] = NEW_N + 1
    w16(g, gp + k + 1, pt)
    for x in ks: g[gp + x + 1] = NB
    # DV：GetTrainerDVs（09:$75CF）を 遠くの 表を 読む形に
    dv = bytearray(g[fo(9, 0x75E1):fo(9, 0x75E1) + 2 * G_N]) + M[fo(9, 0x7DD8) + 2 * G_N:fo(9, 0x7DD8) + 2 * NEW_N]
    dt = put(bytes(dv))
    o = fo(9, 0x75CF)
    assert g[o:o + 18] == bytes.fromhex('e5fa0ad13d4f060021e17509092a474ee1c9')
    GETFARBYTE = 0x30E4                      # 金（日本版）GetFarByte
    code = bytes([0xE5, 0xFA, 0x0A, 0xD1, 0x3D, 0x4F, 0x06, 0x00, 0x21, dt & 0xFF, dt >> 8, 0x09, 0x09,
                  0x3E, NB, 0xCD, GETFARBYTE & 0xFF, GETFARBYTE >> 8, 0x47, 0x23,
                  0x3E, NB, 0xCD, GETFARBYTE & 0xFF, GETFARBYTE >> 8, 0x4F, 0xE1, 0xC9])
    g[o:o + len(code)] = code
    # ---- 色（バンク 02）
    pal = bytearray(g[fo(2, 0x74C3):fo(2, 0x74C3) + 4 * (G_N + 1)]) + M[fo(2, 0x77E3) + 4 * (G_N + 1):fo(2, 0x77E3) + 4 * (NEW_N + 1)]
    pal[70 * 4:71 * 4] = pal[16 * 4:17 * 4]        # ワタル：金の チャンピオンの 色
    pa = 0x7EB0; po = fo(2, pa)
    assert not any(g[po:po + len(pal)]) or all(x == 0xFF for x in g[po:po + len(pal)])
    g[po:po + len(pal)] = pal
    o = fo(2, 0x5B70); assert g[o:o + 10] == bytes.fromhex('6f2600292901c37409c9'); w16(g, o + 6, pa)
    # ---- 属性
    attr = bytes(g[fo(0x0E, 0x5580):fo(0x0E, 0x5580) + 7 * G_N]) + M[fo(0x0E, 0x7DD7) + 7 * G_N:fo(0x0E, 0x7DD7) + 7 * NEW_N]
    # TB：$4000
    g[fo(TB, 0x4000):fo(TB, 0x4000) + len(attr)] = attr
    o = fo(TB, 0x556A); assert g[o:o + 3] == b'\x21\x80\x55'; w16(g, o + 1, 0x4000)
    o = fo(0x11, 0x413C); assert g[o:o + 3] == b'\x21\x83\x55'; w16(g, o + 1, 0x4003)
    seg = g[o:o + 0x30]; d = [i for i in range(len(seg) - 1) if seg[i] == 0x16 and seg[i + 1] == 0x0E]
    assert len(d) == 1, d; g[o + d[0] + 1] = TB
    # バンク 0E：古い 手持ちの データの 終わりに（0E の 手持ちは もう 読まれない）
    from trainers import groups, G_TG
    ptrs, GG = groups(bytes(g[:0x200000]), *G_TG)
    end = r16(g, fo(0x0E, 0x595C) + 2 * 65) - 0x4000 + 0x38000 + len(b''.join(GG[65]))
    ea = end - len(attr)
    g[ea:end] = attr
    for o in (0x38023, 0x38110):
        assert g[o:o + 3] == b'\x21\x85\x55'; w16(g, o + 1, 0x4000 + ea % 0x4000 + 5)
    log.append('属性：TB:4000、0E:%04X' % (0x4000 + ea % 0x4000))
    # ---- ジムリーダー（バンク 0F）：GetHalfHP（使われていない 28 バイト）の 所へ
    o = fo(0x0F, 0x5071)
    assert g[o:o + 8] == bytes.fromhex('2193501803218550')
    old = bytes(g[fo(0x0F, 0x5085):fo(0x0F, 0x5085) + 23]); assert old[-1] == 0xFF
    nl = old[:14] + bytes([68, 69, 70]) + old[14:22] + bytes([71, 0xFF])
    ho = fo(0x0F, 0x4C66); assert g[ho:ho + 2] == b'\x21\x12'
    g[ho:ho + 28] = nl + bytes(28 - len(nl))
    w16(g, o + 1, 0x4C66 + 17); w16(g, o + 6, 0x4C66)
    # ---- 手持ち（TB）
    TBL = 0x595C
    cur = {'A': 0x4000 + len(attr), 'B': TBL + 2 * NEW_N}; lim = {'A': 0x5511, 'B': 0x8000}
    def alloc(n):
        for k in ('B', 'A'):
            if cur[k] + n <= lim[k]:
                a = cur[k]; cur[k] += n; return a
        raise AssertionError('トレーナーの データが 入らない')
    tot = 0
    for i, cls in enumerate(L):
        bl = b''.join(cls); a = alloc(len(bl)); tot += len(bl)
        g[fo(TB, a):fo(TB, a) + len(bl)] = bl; w16(g, fo(TB, TBL) + 2 * i, a)
    log.append('手持ち：%d バイト（のこり A %d・B %d）' % (tot, lim['A'] - cur['A'], lim['B'] - cur['B']))
    # バンク 0E の GetTrainerName（電話の 相手の 名前 など。0E:$595C の 古い 表を 読んでいた → 表が こわれて いて
    # 電話番号を とうろく すると 止まって リセット）：TB に ある 同じ コード（TB:$5939、表は TB:$595C）を farcall で 呼ぶ
    o = fo(0x0E, 0x5939); code = bytes(g[o:o + 35])
    assert code[:7] == bytes.fromhex('0dc50600215c59') and bytes(g[fo(TB, 0x5939):fo(TB, 0x5939) + 35]) == code
    g[o:o + 7] = bytes([0x3E, TB, 0x21, 0x39, 0x59, 0xCF, 0xC9])
    log.append('GetTrainerName（0E:5939）→ TB:5939')
    log.append('NB %02X：$%04X まで' % (NB, cur[0]) if False else 'NB %02X 使用' % NB)
