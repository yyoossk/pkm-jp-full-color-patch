# このソース（disasm.py が 書く 形）を 組み立てて、元の ROM と くらべる ための 小さい アセンブラ。
# rgbds の かわりでは ない（このソースで 使って いる 書き方だけ わかる）。rgbds が あれば、そちらで 組んでも 同じ ROM になる。
#   python3 tools/asm.py src editions/ポケットモンスター緑フルカラー.asm 出力.gbc [くらべる.gbc]
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from sm83 import OPS, CBOPS

TEMPL = []   # (正規表現, 引数の 種類, opcode bytes)
def _add(fmt, prefix):
    kinds = re.findall(r'n8|n16|e8|a16|a8|s8', fmt)
    pat = re.escape(fmt)
    for k in ('n16', 'a16', 'n8', 'e8', 'a8', 's8'):
        pat = pat.replace(k, '(.+)')
    TEMPL.append((re.compile('^' + pat + '$'), kinds, prefix, fmt))
for code, (fmt, n) in OPS.items():
    _add(fmt, bytes([code]))
for code, fmt in CBOPS.items():
    _add(fmt, bytes([0xcb, code]))
# 引数の ない 書式を 先に
TEMPL.sort(key=lambda t: len(t[1]))
EXACT = {t[3]: t[2] for t in TEMPL if not t[1]}


class Asm:
    def __init__(self, root):
        self.root = root
        self.syms = {}
        self.lines = []   # (section, text)

    def load(self, path):
        for raw in open(os.path.join(self.root, path), encoding='utf-8'):
            line = raw.split(';', 1)[0].rstrip()
            if not line.strip():
                continue
            m = re.match(r'\s*INCLUDE "(.+)"', line)
            if m:
                self.load(m.group(1)); continue
            m = re.match(r'\s*DEF (\w+) EQU \$([0-9a-fA-F]+)', line)
            if m:
                self.syms[m.group(1)] = int(m.group(2), 16); continue
            self.lines.append(line)

    def val(self, e, pc):
        e = e.strip()
        m = re.match(r'^@ \+ (-?\d+)$', e)
        if m:
            return pc + int(m.group(1))
        if e.startswith('$'):
            return int(e[1:], 16)
        if re.match(r'^-?\d+$', e):
            return int(e)
        if e in self.syms:
            return self.syms[e]
        raise KeyError(e)

    def encode(self, ins, pc, final):
        ins = ins.strip()
        if ins.startswith('db '):
            return bytes(int(x.strip()[1:], 16) for x in ins[3:].split(','))
        if ins in EXACT:
            return EXACT[ins]
        m = re.match(r'^ld hl, sp ([+-]) (\d+)$', ins)
        if m:
            v = int(m.group(2)) * (1 if m.group(1) == '+' else -1)
            return bytes([0xf8, v & 0xff])
        for rx, kinds, pre, fmt in TEMPL:
            if not kinds:
                continue
            mm = rx.match(ins)
            if not mm:
                continue
            try:
                out = bytearray(pre)
                for k, g in zip(kinds, mm.groups()):
                    if not final and not g.strip().startswith('$') and not re.match(r'^-?\d+$', g.strip()) and not g.strip().startswith('@') and g.strip() not in self.syms:
                        if not re.match(r'^[A-Za-z_]\w*$', g.strip()):
                            raise KeyError(g)
                        v = pc  # 1回目：まだ 分からない 名前
                    else:
                        v = self.val(g, pc)
                    if k in ('n16', 'a16'):
                        out += bytes([v & 0xff, v >> 8 & 0xff])
                    elif k == 'a8':
                        if not (0xff00 <= v <= 0xffff):
                            raise ValueError
                        out.append(v & 0xff)
                    elif k == 'e8':
                        d = v - (pc + 2)
                        if final and not -128 <= d <= 127:
                            raise ValueError('jr')
                        out.append(d & 0xff)
                    else:
                        out.append(v & 0xff)
                return bytes(out)
            except (KeyError, ValueError):
                continue
        raise SyntaxError(ins)

    def run(self, final, rom):
        cur = None
        pc = 0
        for line in self.lines:
            m = re.match(r'^SECTION "[^"]*", (ROM0|ROMX)\[\$([0-9a-f]+)\](?:, BANK\[\$([0-9a-f]+)\])?', line)
            if m:
                bank = int(m.group(3), 16) if m.group(3) else 0
                cur = bank * 0x4000
                pc = int(m.group(2), 16)
                continue
            m = re.match(r'^(\w+)::?$', line)
            if m:
                if not final:
                    self.syms[m.group(1)] = pc
                continue
            b = self.encode(line, pc, final)
            if final:
                rom[cur + (pc & 0x3fff):cur + (pc & 0x3fff) + len(b)] = b
            pc += len(b)


def build(root, main, size=0x100000):
    a = Asm(root)
    a.load(main)
    rom = bytearray(size)
    a.run(False, rom)
    a.run(True, rom)
    return bytes(rom)


if __name__ == '__main__':
    root, main, out = sys.argv[1:4]
    rom = build(root, main)
    open(out, 'wb').write(rom)
    import zlib
    print('%08X' % zlib.crc32(rom), out)
    if len(sys.argv) > 4:
        ref = open(sys.argv[4], 'rb').read()
        bad = [i for i in range(len(ref)) if ref[i] != rom[i]]
        print('同じ' if not bad else 'ちがう %d バイト（最初 $%x）' % (len(bad), bad[0]))
        sys.exit(1 if bad else 0)
