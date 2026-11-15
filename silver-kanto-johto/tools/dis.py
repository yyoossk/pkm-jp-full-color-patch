"""ゲームボーイ（SM83）の かんたんな 逆アセンブラ（しらべる ため）。
   python3 tools/dis.py ROM バンク アドレス [命令の 数]"""
import sys

R = ['b', 'c', 'd', 'e', 'h', 'l', '[hl]', 'a']
RP = ['bc', 'de', 'hl', 'sp']
RP2 = ['bc', 'de', 'hl', 'af']
CC = ['nz', 'z', 'nc', 'c']
ALU = ['add a,', 'adc a,', 'sub', 'sbc a,', 'and', 'xor', 'or', 'cp']
ROT = ['rlc', 'rrc', 'rl', 'rr', 'sla', 'sra', 'swap', 'srl']


def one(b, pc):
    """b: その 位置からの バイト列 → (文字列, 長さ)"""
    op = b[0]; n = b[1] if len(b) > 1 else 0; nn = n | (b[2] << 8 if len(b) > 2 else 0)
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    rel = lambda: '$%04X' % ((pc + 2 + (n - 256 if n > 127 else n)) & 0xFFFF)
    if op == 0xCB:
        x2, y2, z2 = n >> 6, (n >> 3) & 7, n & 7
        return ([f'{ROT[y2]} {R[z2]}', f'bit {y2},{R[z2]}', f'res {y2},{R[z2]}', f'set {y2},{R[z2]}'][x2], 2)
    T = {0x00: ('nop', 1), 0x08: (f'ld [${nn:04X}],sp', 3), 0x10: ('stop', 2), 0x18: (f'jr {rel()}', 2),
         0x76: ('halt', 1), 0xC9: ('ret', 1), 0xD9: ('reti', 1), 0xE9: ('jp hl', 1), 0xF9: ('ld sp,hl', 1),
         0xC3: (f'jp ${nn:04X}', 3), 0xCD: (f'call ${nn:04X}', 3), 0xF3: ('di', 1), 0xFB: ('ei', 1),
         0xE0: (f'ldh [$FF{n:02X}],a', 2), 0xF0: (f'ldh a,[$FF{n:02X}]', 2), 0xE2: ('ld [c],a', 1), 0xF2: ('ld a,[c]', 1),
         0xEA: (f'ld [${nn:04X}],a', 3), 0xFA: (f'ld a,[${nn:04X}]', 3), 0xE8: (f'add sp,{n}', 2), 0xF8: (f'ld hl,sp+{n}', 2),
         0x07: ('rlca', 1), 0x0F: ('rrca', 1), 0x17: ('rla', 1), 0x1F: ('rra', 1), 0x27: ('daa', 1), 0x2F: ('cpl', 1),
         0x37: ('scf', 1), 0x3F: ('ccf', 1)}
    if op in T: return T[op]
    if x == 0:
        if z == 0 and y >= 4: return (f'jr {CC[y - 4]},{rel()}', 2)
        if z == 1: return ((f'ld {RP[y >> 1]},${nn:04X}', 3) if not y & 1 else (f'add hl,{RP[y >> 1]}', 1))
        if z == 2:
            m = ['[bc]', '[de]', '[hli]', '[hld]'][y >> 1]
            return ((f'ld {m},a', 1) if not y & 1 else (f'ld a,{m}', 1))
        if z == 3: return ((f'inc {RP[y >> 1]}', 1) if not y & 1 else (f'dec {RP[y >> 1]}', 1))
        if z == 4: return (f'inc {R[y]}', 1)
        if z == 5: return (f'dec {R[y]}', 1)
        if z == 6: return (f'ld {R[y]},${n:02X}', 2)
    if x == 1: return (f'ld {R[y]},{R[z]}', 1)
    if x == 2: return (f'{ALU[y]} {R[z]}', 1)
    if z == 0 and y < 4: return (f'ret {CC[y]}', 1)
    if z == 1 and not y & 1: return (f'pop {RP2[y >> 1]}', 1)
    if z == 2 and y < 4: return (f'jp {CC[y]},${nn:04X}', 3)
    if z == 4 and y < 4: return (f'call {CC[y]},${nn:04X}', 3)
    if z == 5 and not y & 1: return (f'push {RP2[y >> 1]}', 1)
    if z == 6: return (f'{ALU[y]} ${n:02X}', 2)
    if z == 7: return (f'rst ${y * 8:02X}', 1)
    return (f'db ${op:02X}', 1)


def dis(rom, bank, addr, count=60):
    out = []; a = addr
    for i in range(count):
        o = (bank * 0x4000 + a - 0x4000) if a >= 0x4000 else a
        s, L = one(rom[o:o + 3], a)
        out.append('%02X:%04X  %-10s %s' % (bank, a, rom[o:o + L].hex(), s)); a += L
    return out


if __name__ == '__main__':
    r = open(sys.argv[1], 'rb').read()
    print('\n'.join(dis(r, int(sys.argv[2], 16), int(sys.argv[3], 16), int(sys.argv[4]) if len(sys.argv) > 4 else 60)))
