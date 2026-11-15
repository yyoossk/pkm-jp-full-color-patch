"""SM83 の 小さな 逆アセンブラ（調べる 用）。 python3 dis.py ROM BANK ADDR [N]"""
import sys
R = ['b', 'c', 'd', 'e', 'h', 'l', '[hl]', 'a']
RP = ['bc', 'de', 'hl', 'sp']; RP2 = ['bc', 'de', 'hl', 'af']
CC = ['nz', 'z', 'nc', 'c']
ALU = ['add a,', 'adc a,', 'sub ', 'sbc a,', 'and ', 'xor ', 'or ', 'cp ']
ROT = ['rlc', 'rrc', 'rl', 'rr', 'sla', 'sra', 'swap', 'srl']

def one(m, o, pc):
    """→ (長さ, 文字列)"""
    op = m[o]; n8 = m[o + 1] if o + 1 < len(m) else 0
    n16 = n8 | (m[o + 2] << 8 if o + 2 < len(m) else 0)
    rel = pc + 2 + (n8 - 256 if n8 > 127 else n8)
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    if op == 0xCB:
        x2, y2, z2 = n8 >> 6, (n8 >> 3) & 7, n8 & 7
        return 2, (ROT[y2] + ' ' + R[z2]) if x2 == 0 else ['', 'bit', 'res', 'set'][x2] + ' %d,%s' % (y2, R[z2])
    if x == 1: return 1, 'halt' if op == 0x76 else 'ld %s,%s' % (R[y], R[z])
    if x == 2: return 1, ALU[y] + R[z]
    T = {0x00: (1, 'nop'), 0x08: (3, 'ld [$%04x],sp' % n16), 0x10: (2, 'stop'), 0x18: (2, 'jr $%04x' % rel),
         0x07: (1, 'rlca'), 0x0F: (1, 'rrca'), 0x17: (1, 'rla'), 0x1F: (1, 'rra'), 0x27: (1, 'daa'), 0x2F: (1, 'cpl'),
         0x37: (1, 'scf'), 0x3F: (1, 'ccf'), 0x02: (1, 'ld [bc],a'), 0x12: (1, 'ld [de],a'), 0x22: (1, 'ld [hli],a'),
         0x32: (1, 'ld [hld],a'), 0x0A: (1, 'ld a,[bc]'), 0x1A: (1, 'ld a,[de]'), 0x2A: (1, 'ld a,[hli]'), 0x3A: (1, 'ld a,[hld]'),
         0xC9: (1, 'ret'), 0xD9: (1, 'reti'), 0xE9: (1, 'jp hl'), 0xF9: (1, 'ld sp,hl'), 0xC3: (3, 'jp $%04x' % n16),
         0xCD: (3, 'call $%04x' % n16), 0xF3: (1, 'di'), 0xFB: (1, 'ei'), 0xE0: (2, 'ldh [$ff%02x],a' % n8),
         0xF0: (2, 'ldh a,[$ff%02x]' % n8), 0xE2: (1, 'ldh [c],a'), 0xF2: (1, 'ldh a,[c]'), 0xEA: (3, 'ld [$%04x],a' % n16),
         0xFA: (3, 'ld a,[$%04x]' % n16), 0xE8: (2, 'add sp,%d' % (n8 - 256 if n8 > 127 else n8)),
         0xF8: (2, 'ld hl,sp+%d' % (n8 - 256 if n8 > 127 else n8))}
    if op in T: return T[op]
    if x == 0:
        if z == 0: return 2, 'jr %s,$%04x' % (CC[y - 4], rel)
        if z == 1: return (3, 'ld %s,$%04x' % (RP[y >> 1], n16)) if y % 2 == 0 else (1, 'add hl,' + RP[y >> 1])
        if z == 3: return 1, ('inc ' if y % 2 == 0 else 'dec ') + RP[y >> 1]
        if z == 4: return 1, 'inc ' + R[y]
        if z == 5: return 1, 'dec ' + R[y]
        if z == 6: return 2, 'ld %s,$%02x' % (R[y], n8)
    if x == 3:
        if z == 0 and y < 4: return 1, 'ret ' + CC[y]
        if z == 1: return 1, 'pop ' + RP2[y >> 1]
        if z == 2 and y < 4: return 3, 'jp %s,$%04x' % (CC[y], n16)
        if z == 4 and y < 4: return 3, 'call %s,$%04x' % (CC[y], n16)
        if z == 5: return 1, 'push ' + RP2[y >> 1]
        if z == 6: return 2, ALU[y] + '$%02x' % n8
        if z == 7: return 1, 'rst $%02x' % (y * 8)
    return 1, 'db $%02x' % op

def dis(m, bank, a, n=40, sym=None):
    o = (bank * 0x4000 + a - 0x4000) if a >= 0x4000 else a; pc = a; out = []
    for _ in range(n):
        ln, s = one(m, o, pc)
        lab = sym(bank, pc) if sym else ''
        out.append('%02X:%04X  %-9s %s%s' % (bank, pc, m[o:o + ln].hex(), s, ('  ; ' + lab) if lab else ''))
        o += ln; pc += ln
    return '\n'.join(out)

if __name__ == '__main__':
    m = open(sys.argv[1], 'rb').read()
    print(dis(m, int(sys.argv[2], 16), int(sys.argv[3], 16), int(sys.argv[4]) if len(sys.argv) > 4 else 40))
