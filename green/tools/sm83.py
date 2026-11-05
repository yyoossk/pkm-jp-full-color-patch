# SM83（ゲームボーイの CPU）の 命令表。逆アセンブル（disasm.py）と 組み立て（asm.py）の 両方で 使う。
# 書き方は rgbds と 同じ（ld [hli], a・ldh a, [c]・ld hl, sp + n など）。
R8 = ['b', 'c', 'd', 'e', 'h', 'l', '[hl]', 'a']
R16 = ['bc', 'de', 'hl', 'sp']
R16S = ['bc', 'de', 'hl', 'af']
CC = ['nz', 'z', 'nc', 'c']
ALU = ['add a,', 'adc a,', 'sub', 'sbc a,', 'and', 'xor', 'or', 'cp']
ROT = ['rlc', 'rrc', 'rl', 'rr', 'sla', 'sra', 'swap', 'srl']

# OPS[op] = (書式, 長さ)。書式の n8 / n16 / e8（相対）/ a16（番地）/ a8（$ff00+）
OPS = {}
def op(code, fmt, n=1):
    OPS[code] = (fmt, n)

op(0x00, 'nop'); op(0x10, 'stop', 2); op(0x76, 'halt')
op(0x07, 'rlca'); op(0x0f, 'rrca'); op(0x17, 'rla'); op(0x1f, 'rra')
op(0x27, 'daa'); op(0x2f, 'cpl'); op(0x37, 'scf'); op(0x3f, 'ccf')
op(0xf3, 'di'); op(0xfb, 'ei')
for i, r in enumerate(R16):
    op(0x01 + i * 16, f'ld {r}, n16', 3)
    op(0x03 + i * 16, f'inc {r}')
    op(0x0b + i * 16, f'dec {r}')
    op(0x09 + i * 16, f'add hl, {r}')
op(0x02, 'ld [bc], a'); op(0x12, 'ld [de], a'); op(0x22, 'ld [hli], a'); op(0x32, 'ld [hld], a')
op(0x0a, 'ld a, [bc]'); op(0x1a, 'ld a, [de]'); op(0x2a, 'ld a, [hli]'); op(0x3a, 'ld a, [hld]')
for i, r in enumerate(R8):
    op(0x04 + i * 8, f'inc {r}')
    op(0x05 + i * 8, f'dec {r}')
    op(0x06 + i * 8, f'ld {r}, n8', 2)
op(0x08, 'ld [a16], sp', 3)
op(0x18, 'jr e8', 2)
for i, c in enumerate(CC):
    op(0x20 + i * 8, f'jr {c}, e8', 2)
    op(0xc0 + i * 8, f'ret {c}')
    op(0xc2 + i * 8, f'jp {c}, a16', 3)
    op(0xc4 + i * 8, f'call {c}, a16', 3)
for d in range(8):
    for s in range(8):
        if d == 6 and s == 6:
            continue
        op(0x40 + d * 8 + s, f'ld {R8[d]}, {R8[s]}')
for i, a in enumerate(ALU):
    for s in range(8):
        op(0x80 + i * 8 + s, f'{a} {R8[s]}')
    op(0xc6 + i * 8, f'{a} n8', 2)
for i, r in enumerate(R16S):
    op(0xc1 + i * 16, f'pop {r}')
    op(0xc5 + i * 16, f'push {r}')
for i in range(8):
    op(0xc7 + i * 8, f'rst ${i * 8:02x}')
op(0xc3, 'jp a16', 3); op(0xcd, 'call a16', 3); op(0xc9, 'ret'); op(0xd9, 'reti')
op(0xe9, 'jp hl'); op(0xf9, 'ld sp, hl')
op(0xe0, 'ldh [a8], a', 2); op(0xf0, 'ldh a, [a8]', 2)
op(0xe2, 'ldh [c], a'); op(0xf2, 'ldh a, [c]')
op(0xea, 'ld [a16], a', 3); op(0xfa, 'ld a, [a16]', 3)
op(0xe8, 'add sp, s8', 2); op(0xf8, 'ld hl, sp + s8', 2)
# CB
CBOPS = {}
for i, r in enumerate(ROT):
    for s in range(8):
        CBOPS[i * 8 + s] = f'{r} {R8[s]}'
for i, name in enumerate(['bit', 'res', 'set']):
    for b in range(8):
        for s in range(8):
            CBOPS[0x40 + i * 0x40 + b * 8 + s] = f'{name} {b}, {R8[s]}'

# 流れが そこで 終わる 命令
ENDS = {0xc3, 0xc9, 0xd9, 0xe9, 0x18}


def decode(rom, off):
    """off の 命令 → (書式, 長さ, 引数の 値) か None（命令に ならない）"""
    b = rom[off]
    if b == 0xcb:
        if off + 1 >= len(rom):
            return None
        return (CBOPS[rom[off + 1]], 2, None)
    if b not in OPS:
        return None
    fmt, n = OPS[b]
    if off + n > len(rom):
        return None
    val = None
    if n == 2:
        val = rom[off + 1]
    elif n == 3:
        val = rom[off + 1] | rom[off + 2] << 8
    if b == 0x10 and rom[off + 1] != 0:
        return None
    return (fmt, n, val)
