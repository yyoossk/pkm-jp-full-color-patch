"""タイルセットの 色（第44・92弾 など）：クリスタル版の 色の 処理（$6A:$74AF〜。タイルセットごとの 表、
   カントーの 町の 時間ごとの 色、暗い ほら穴）を 銀でも 使う。
   銀の LoadMapPals（$02:$75CF）の はじめで farcall し、色を 入れたら 人の 色の 所（$02:$760F）へ とぶ。
   クリスタルの wBGPals1（WRAM バンク5 の $D000〜）は 銀では $C200〜。"""
import os, sys, pickle
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, asmport, wramxl
from gsc import fo

LMP, OBJPART, FREE2 = 0xB5CF, 0x760F, 0x7F29


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    g1 = open(os.path.join(H, 'roms', 'gin1.gbc'), 'rb').read()
    Hm = asmport.Home(corig, g1)
    wm = dict(pickle.load(open(os.path.join(ctx['B'], 'wram_map.pkl'), 'rb')))
    for a in range(0xD000, 0xD100): wm[a] = 0xC200 + (a - 0xD000)        # 色の 処理の 中では パレット
    wm.update({0xD834: 0xD55B, 0xD1CA: 0xD074, 0xD1CB: 0xD075})
    TR = asmport.Translator(cmod, corig, g1, wm, Hm, log)
    TR.wm = wm; TR.nosvbk = True
    TR.routine(rom, 0x6A, 0x74AF, 'palettes')
    # 銀の フック
    assert rom[LMP:LMP + 3] == bytes([0xFA, 0x75, 0xD0]) and not any(rom[fo(2, FREE2):fo(2, FREE2) + 16])
    hk = bytes([0x3E, 0x6A, 0x21, 0xAF, 0x74, 0xCF, 0x38, 0x04, 0xFA, 0x75, 0xD0, 0xC9, 0xE1, 0xC3,
                OBJPART & 0xff, OBJPART >> 8])
    rom[fo(2, FREE2):fo(2, FREE2) + len(hk)] = hk
    rom[LMP:LMP + 3] = bytes([0xCD, FREE2 & 0xff, FREE2 >> 8])
    # タイルごとの 色の 表（palmap）：タイルセット 37〜 は $93（クリスタルの $13）から GetFarByte で 読む
    GETFARBYTE = 0x30E4
    a = FREE2 + len(hk)
    def put(code):
        nonlocal a
        o = fo(2, a); assert not any(rom[o:o + len(code)]); rom[o:o + len(code)] = code; r = a; a += len(code); return r
    def rd(tail):
        return bytes([0xFA, 0x74, 0xD0, 0xFE, 37, 0x38, 0x06 + len(tail), 0x3E, 0x93, 0xCD, GETFARBYTE & 0xff, GETFARBYTE >> 8]) + \
            tail + bytes([0xC9, 0x7E]) + tail + bytes([0xC9])
    r1 = put(rd(bytes([0xE6, 0x0F]))); r2 = put(rd(bytes([0xCB, 0x37, 0xE6, 0x0F])))
    n = 0
    for o in range(fo(2, 0x4000), fo(2, 0x8000) - 5):
        if rom[o:o + 9] == bytes([0xFA, 0xC2, 0xD0, 0xCE, 0x00, 0x67, 0x7E, 0xE6, 0x0F]):
            rom[o + 6:o + 9] = bytes([0xCD, r1 & 0xff, r1 >> 8]); n += 1
        elif rom[o:o + 11] == bytes([0xFA, 0xC2, 0xD0, 0xCE, 0x00, 0x67, 0x7E, 0xCB, 0x37, 0xE6, 0x0F]):
            rom[o + 6:o + 11] = bytes([0xCD, r2 & 0xff, r2 >> 8, 0, 0]); n += 1
    assert n == 4, n
    log.append('タイルセットの 色：$6A:$74AF を フック' + ('（TODO %s）' % TR.unres if TR.unres else ''))
    return rom


# ---- 第97弾：カントーの 町・道路（外の タイルセット）は 朝・夜で 色が かわる（クリスタル版の キットの 直しの 銀版）
DAY = [[(27, 31, 27), (21, 21, 21), (13, 13, 13), (7, 7, 7)], [(27, 31, 27), (31, 19, 24), (30, 10, 6), (7, 7, 7)],
       [(22, 31, 10), (12, 25, 1), (5, 14, 0), (7, 7, 7)], [(31, 31, 31), (8, 12, 31), (1, 4, 31), (7, 7, 7)],
       [(27, 31, 27), (31, 31, 7), (31, 16, 1), (7, 7, 7)], [(27, 31, 27), (24, 18, 7), (20, 15, 3), (7, 7, 7)],
       [(27, 31, 27), (15, 31, 31), (5, 17, 31), (7, 7, 7)]]
NITE = [[(15, 14, 24), (11, 11, 19), (7, 7, 12), (0, 0, 0)], [(15, 14, 24), (14, 7, 17), (13, 0, 8), (0, 0, 0)],
        [(15, 14, 24), (8, 13, 19), (0, 11, 13), (0, 0, 0)], [(15, 14, 24), (5, 5, 17), (3, 3, 10), (0, 0, 0)],
        [(30, 30, 11), (16, 14, 18), (16, 14, 10), (0, 0, 0)], [(15, 14, 24), (12, 9, 15), (8, 4, 5), (0, 0, 0)],
        [(15, 14, 24), (13, 12, 23), (11, 9, 20), (0, 0, 0)]]
FIT = ((0.32, 0.209, 0.102, -1.722), (-0.146, 0.567, -0.021, 0.541), (-0.086, 0.679, 0.192, 1.121))


def _night(pi, ci, col):
    if col == (7, 7, 7) and ci == 3: return (0, 0, 0)
    if pi < 7 and DAY[pi][ci] == col: return NITE[pi][ci]
    if ci == 0 and col == (27, 31, 27): return (15, 14, 24)
    return tuple(max(0, min(31, round(a * col[0] + b * col[1] + c * col[2] + d))) for a, b, c, d in FIT)


def _morning(pi, ci, col): return (28, 31, 16) if col == (27, 31, 27) else col


def timeofday(rom, log):
    PB, ROUTINE, TABLE, CALL = 0x6A, 0x6EE9, 0x6F2B, 0x74AF
    W_TILESET, W_ENV, W_TOD, COPYBYTES, BGPALS = 0xD074, 0xD075, 0xD55B, 0x30D6, 0xC200
    cmod = open(cmaps.CMOD, 'rb').read(); M = cmaps.CMaps(cmod)
    out = {cmod[h + 1] for h in M.hdr.values() if cmod[h + 2] in (1, 2)}
    o = fo(PB, CALL); assert rom[o:o + 4] == bytes([0xCD, ROUTINE & 0xFF, ROUTINE >> 8, 0xD0])
    t = fo(PB, TABLE); ents = []
    while rom[t] != 0xFF: ents.append((rom[t], rom[t + 1] | rom[t + 2] << 8)); t += 3
    ents = [(i, p) for i, p in ents if i in out]; assert ents
    s = rom[fo(PB, 0x4000):fo(PB, 0x8000)]; base = 0x4000 + len(s.rstrip(b'\0')) + 16
    unpack = lambda c: (c & 31, (c >> 5) & 31, c >> 10); pack = lambda t: t[0] | t[1] << 5 | t[2] << 10
    w = lambda v: bytes([v & 0xFF, v >> 8])
    dat0 = base + 0x60; data = b''; tab = b''
    for i, p in ents:
        q = fo(PB, p); cols = [unpack(rom[q + 2 * j] | rom[q + 2 * j + 1] << 8) for j in range(28)]
        am = dat0 + len(data); data += b''.join(pack(_morning(j // 4, j % 4, c)).to_bytes(2, 'little') for j, c in enumerate(cols))
        an = dat0 + len(data); data += b''.join(pack(_night(j // 4, j % 4, c)).to_bytes(2, 'little') for j, c in enumerate(cols))
        tab += bytes([i]) + w(am) + w(an)
    tab += b'\xff'; taba = dat0 + len(data); data += tab
    c = bytearray(b'\xcd' + w(ROUTINE) + b'\xd0' + b'\xfa' + w(W_ENV) + b'\x3d\xfe\x02')
    c += b'\x30\x00'; j1 = len(c) - 1
    c += b'\xfa' + w(W_TOD) + b'\xe6\x03' + b'\x1e\x01\xa7\x28\x00'; j2 = len(c) - 1
    c += b'\x1e\x03\xfe\x02\x20\x00'; j3 = len(c) - 1
    look = len(c); c += b'\xfa' + w(W_TILESET) + b'\x47\x21' + w(taba)
    loop = len(c); c += b'\x7e\xfe\xff\x28\x00'; j4 = len(c) - 1
    c += b'\xb8\x28\x07\x23\x23\x23\x23\x23\x18\x00'; j5 = len(c) - 1
    c += b'\x16\x00\x19\x2a\x66\x6f' + b'\x11' + w(BGPALS) + b'\x01\x38\x00\xcd' + w(COPYBYTES)
    ok = len(c); c += b'\x37\xc9'
    def rel(at, to): c[at] = (to - (at + 1)) & 0xFF
    rel(j1, ok); rel(j2, look); rel(j3, ok); rel(j4, ok); rel(j5, loop)
    assert len(c) <= 0x60 and dat0 + len(data) <= 0x8000
    rom[fo(PB, base):fo(PB, base) + len(c)] = c; rom[fo(PB, dat0):fo(PB, dat0) + len(data)] = data
    rom[o + 1:o + 3] = w(base)
    log.append('第97弾：カントーの 外の 色を 朝・夜で（タイルセット %s、$6A:$%04X）' % (','.join(str(i) for i, p in ents), base))


_apply0 = apply
def apply(rom, ctx):
    rom = _apply0(rom, ctx)
    timeofday(rom, ctx.setdefault('log', []))
    return rom
