"""クリスタル版の マップの スクリプトが よぶ 小さな asm（callasm など）を、金の 形に 書きなおして 置く。
   E.loc[(クリスタルの バンク, 住所)] に 登録すると、スクリプトの ポインターが そこへ 読みかえられる。
"""
def fo(b, a): return b * 0x4000 + a - 0x4000
def r16(r, o): return r[o] | r[o + 1] << 8

G_EVENTFLAGS = 0xD7AA
G_WARPS_PTR = 0xD90C          # wCurMapWarpsPointer（クリスタル $DBC2）

def _put(E, g, cb, data):
    gb = E.gbank(cb); a = E.fill[gb]; assert a + len(data) <= 0x8000
    g[fo(gb, a):fo(gb, a) + len(data)] = data; E.fill[gb] = a + len(data)
    return gb, a

def lavender_hof_warps(E, M, g, log):
    """第12弾：カントーの 殿堂入りの あと、シオンタウンの 入口の 1つを ラジオ塔へ（78:$5E9E）
       ld a,[wEventFlags+$69] / bit 2,a / ret z / ld hl,alt / wCurMapWarpsPointer = hl / ret"""
    o = fo(0x78, 0x5E9E)
    assert M[o:o + 18] == bytes.fromhex('facedacb57c82174787deac2db7ceac3dbc9'), M[o:o + 18].hex()
    alt_c = r16(M, o + 7)
    nw = 6
    alt = bytearray(M[fo(0x78, alt_c):fo(0x78, alt_c) + 5 * nw])
    for i in range(nw):
        gg, nn = E.X.mapid((alt[5 * i + 3], alt[5 * i + 4]), 'Lavender alt warps'); alt[5 * i + 3] = gg; alt[5 * i + 4] = nn
    gb, aa = _put(E, g, 0x78, bytes(alt))
    fb = G_EVENTFLAGS + (0x34A >> 3)
    code = bytes([0xFA, fb & 0xFF, fb >> 8, 0xCB, 0x57, 0xC8, 0x21, aa & 0xFF, aa >> 8,
                  0x7D, 0xEA, G_WARPS_PTR & 0xFF, G_WARPS_PTR >> 8, 0x7C, 0xEA, (G_WARPS_PTR + 1) & 0xFF, (G_WARPS_PTR + 1) >> 8, 0xC9])
    cb_, ca_ = _put(E, g, 0x78, code)
    E.loc[(0x78, 0x5E9E)] = (cb_, ca_)
    log.append('asm 78:5E9E（シオンの 入口 → ラジオ塔）→ %02X:%04X' % (cb_, ca_))

PORTS = [lavender_hof_warps]
PORTED = {(0x78, 0x5E9E)}          # 金に うつした asm（クリスタル版の バンク・住所）

def apply(E, M, g, log):
    for f in PORTS: f(E, M, g, log)
