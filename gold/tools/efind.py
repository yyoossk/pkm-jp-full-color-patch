"""英語版 pret/pokegold（pokegold.gbc・pokegold.sym）の 関数を、日本版 金の ROM から さがす 道具。
   from efind import *  →  find('GetUsedSprites')・pairs('GetUsedSprites')
   ・関数の 頭 n バイトの 命令の うち、アドレス（2バイト）の 所を 伏せて さがす。
   ・見つかったら 命令を ならべて、英語版の アドレス → 日本版の アドレス の 組を 出す（RAM・関数の 対応を 調べる）。"""
import re, sys
EN = '/home/claude/work/pokegold/pokegold.gbc'
SYM = '/home/claude/work/pokegold/pokegold.sym'
JP = '/home/claude/work/goldkit/base.gbc'
e = open(EN, 'rb').read(); j = open(JP, 'rb').read()
syms = {}; addr2sym = {}
for line in open(SYM):
    m = re.match(r'([0-9a-f]{2}):([0-9a-f]{4}) (\S+)', line)
    if m:
        b, a, n = int(m.group(1), 16), int(m.group(2), 16), m.group(3)
        syms[n] = (b, a); addr2sym.setdefault((b, a), n)

# 命令の 長さ（CB は 2）
L = [1]*256
for op in [0x06,0x0e,0x16,0x1e,0x26,0x2e,0x36,0x3e,0x18,0x20,0x28,0x30,0x38,0xc6,0xce,0xd6,0xde,0xe6,0xee,0xf6,0xfe,0xe0,0xf0,0xe8,0xf8,0xcb]: L[op] = 2
for op in [0x01,0x11,0x21,0x31,0x08,0xc2,0xc3,0xc4,0xca,0xcc,0xcd,0xd2,0xd4,0xda,0xdc,0xea,0xfa]: L[op] = 3
W16 = {0x01,0x11,0x21,0x31,0x08,0xc2,0xc3,0xc4,0xca,0xcc,0xcd,0xd2,0xd4,0xda,0xdc,0xea,0xfa}

def off(b, a): return a if b == 0 else b * 0x4000 + a - 0x4000
def ba(o): return (o // 0x4000, o % 0x4000 + (0x4000 if o >= 0x4000 else 0))

def pattern(o, n, mask_imm8=False):
    pat = []; i = o
    while i < o + n:
        op = e[i]; ln = L[op]
        pat.append(op)
        if op in W16: pat += [None, None]
        elif ln == 2:
            # ldh は アドレスが 同じ ことが 多い。jr の とびさきも 同じ はず
            pat.append(None if mask_imm8 else e[i+1])
        i += ln
    return pat

def search(pat, rom=None):
    rom = rom or j; out = []
    first = pat[0]; n = len(pat); i = 0
    while True:
        i = rom.find(bytes([first]), i)
        if i < 0 or i + n > len(rom): break
        if all(p is None or rom[i+k] == p for k, p in enumerate(pat)): out.append(i)
        i += 1
    return out

def find(name, n=24, skip=0, mask_imm8=False):
    b, a = syms[name]; o = off(b, a) + skip
    hits = search(pattern(o, n, mask_imm8))
    return [ba(h - skip) for h in hits]

def pairs(name, jaddr=None, n=64, skip=0):
    """英語版の 関数と 日本版 jaddr（(bank, addr)）を 命令ごとに ならべ、2バイトの 値の 組を かえす"""
    b, a = syms[name]; o = off(b, a)
    if jaddr is None:
        h = find(name, 24, skip)
        if len(h) != 1: return ('hits', h)
        jaddr = h[0]
    jo = off(*jaddr); out = []; i = 0
    while i < n:
        op = e[o+i]
        if j[jo+i] != op: out.append(('diff@', i)); break
        if op in W16:
            ev = e[o+i+1] | e[o+i+2] << 8; jv = j[jo+i+1] | j[jo+i+2] << 8
            nm = addr2sym.get((0, ev)) or addr2sym.get((1, ev)) or addr2sym.get((b, ev)) or ''
            out.append((hex(ev), hex(jv), nm))
        elif op in (0xe0, 0xf0):
            ev = 0xff00 | e[o+i+1]; jv = 0xff00 | j[jo+i+1]
            nm = addr2sym.get((0, ev)) or ''
            out.append((hex(ev), hex(jv), nm))
        i += L[op]
    return out

if __name__ == '__main__':
    for nm in sys.argv[1:]:
        print(nm, [f'{x:02x}:{y:04x}' for x, y in find(nm)])
