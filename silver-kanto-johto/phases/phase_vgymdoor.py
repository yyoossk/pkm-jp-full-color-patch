"""クチバジムの マチスの 前の 扉（第108弾の 銀版。赤と 同じ 2まいの 扉）：
   なぞを 解く 前、ブロック (2,2) は クリスタル版の キット（第75弾）で「壁」（銀の タイルセット 13 の ブロック $20）に して いた。
   赤の 扉（赤フルカラーの ジムの タイル $20 $21 / $30 $31）を 入れる：
   ・クチバジム だけの タイルセット 29（あき。タイルセット 13 の 写し）を 作る：クチバジムで 使わない タイル $0E $0F $22 $23
     （色は 床と 同じ パレット 1）に 赤の 扉、ブロック $40（上が 扉で 通れない、下は 床）を 足す。データは $EE。
   ・第75弾の callback（$63:$7330 changeblock 4,4,$20）を $40 に。開くと 床（$01、前と 同じ）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port, gsc
from gsc import fo, r16

AKAFC = os.environ.get('AKAFC', '/home/claude/in/aka/akafc.gbc')
RED_GYM_GFX = 0x68050
SRC_TS, NEW_TS, DB = 13, 29, 0xEE
NEW_TILES = [0x0E, 0x0F, 0x22, 0x23]
RED_DOOR = [0x20, 0x21, 0x30, 0x31]
FLOOR, WALL, DOOR = 0x01, 0x20, 0x40
CALLBACK = (0x63, 0x7330)


def unlz(r, o):
    out = bytearray()
    while True:
        b = r[o]; o += 1
        if b == 0xFF: return bytes(out)
        cmd = b >> 5
        if cmd == 7: cmd = (b >> 2) & 7; n = ((b & 3) << 8 | r[o]) + 1; o += 1
        else: n = (b & 0x1F) + 1
        if cmd == 0: out += r[o:o + n]; o += n
        elif cmd == 1: out += bytes([r[o]]) * n; o += 1
        elif cmd == 2: out += bytes([r[o], r[o + 1]] * n)[:n]; o += 2
        elif cmd == 3: out += bytes(n)
        else:
            if r[o] & 0x80: src = len(out) - (r[o] & 0x7F) - 1; o += 1
            else: src = r[o] << 8 | r[o + 1]; o += 2
            for k in range(n):
                if cmd == 4: out.append(out[src + k])
                elif cmd == 5: v = out[src + k]; out.append(int('{:08b}'.format(v)[::-1], 2))
                else: out.append(out[src - k])


def lz_literal(d):
    out = bytearray()
    for i in range(0, len(d), 32):
        ch = d[i:i + 32]; out.append(len(ch) - 1); out += ch
    return bytes(out) + b'\xff'


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    te = fo(0xE1, 0x4000); e = te + 15 * SRC_TS; ne = te + 15 * NEW_TS
    gb, ga, mb, ma, cb, ca = rom[e], r16(rom, e + 1), rom[e + 3], r16(rom, e + 4), rom[e + 6], r16(rom, e + 7)
    gfx = bytearray(unlz(rom, fo(gb, ga))); assert len(gfx) == 96 * 16
    meta = bytearray(rom[fo(mb, ma):fo(mb, ma) + 64 * 16]); coll = bytearray(rom[fo(cb, ca):fo(cb, ca) + 64 * 4])
    # クチバジムで 使わない タイル か たしかめる
    cmod = open(cmaps.CMOD, 'rb').read()
    P = port.Port.__new__(port.Port)
    P.CM = cmaps.CMaps(cmod); P.SM = gsc.Maps(bytes(rom[:0x100000]), gsc.PG + '/constants/map_constants.asm'); P.todo = {}
    g, m = P.x_map(*P.CM.id['VERMILION_GYM'])
    gt = fo(0x25, 0x40ED); h = fo(0x25, r16(rom, gt + 2 * (g - 1))) + 9 * (m - 1); assert rom[h + 1] == SRC_TS
    ao = fo(rom[h], r16(rom, h + 3)); bp = fo(rom[ao + 3], r16(rom, ao + 4)); blocks = set(rom[bp:bp + rom[ao + 1] * rom[ao + 2]])
    blocks |= {FLOOR, WALL}
    used = set(); [used.update(meta[16 * b:16 * b + 16]) for b in blocks]
    assert not used & set(NEW_TILES), [hex(t) for t in used & set(NEW_TILES)]
    F = open(AKAFC, 'rb').read()
    for t, rt in zip(NEW_TILES, RED_DOOR): gfx[16 * t:16 * t + 16] = F[RED_GYM_GFX + 16 * rt:RED_GYM_GFX + 16 * rt + 16]
    a, b, c, d = NEW_TILES; fl = meta[16 * FLOOR:16 * FLOOR + 16]
    meta += bytes([a, b, a, b, c, d, c, d]) + fl[8:16]
    wc, fc = coll[4 * WALL:4 * WALL + 4], coll[4 * FLOOR:4 * FLOOR + 4]
    coll += bytes([wc[0], wc[1], fc[2], fc[3]])
    data = lz_literal(bytes(gfx)); assert unlz(data, 0) == bytes(gfx)
    assert not any(rom[fo(DB, 0x4000):fo(DB, 0x8000)])
    g2 = 0x4000; m2 = g2 + len(data); c2 = m2 + len(meta)
    o = fo(DB, 0x4000); blob = data + bytes(meta) + bytes(coll); rom[o:o + len(blob)] = blob
    rom[ne:ne + 15] = bytes([DB]) + g2.to_bytes(2, 'little') + bytes([DB]) + m2.to_bytes(2, 'little') + bytes([DB]) + c2.to_bytes(2, 'little') + rom[e + 9:e + 15]
    rom[h + 1] = NEW_TS
    o = fo(*CALLBACK); assert rom[o:o + 5] == bytes([0x79, 4, 4, WALL, 0x8F]); rom[o + 3] = DOOR
    log.append('クチバジムの 扉：タイルセット %d（%d の 写し＋赤の 扉、$%02X）・ブロック $%02X' % (NEW_TS, SRC_TS, DB, DOOR))
    return rom
