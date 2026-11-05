"""IPS パッチを作る。元のROMを何本でも渡せて、どれに当てても同じ結果（target）になるようにする。
   python3 mkips.py target.gbc out.ips base1.gbc [base2.gbc ...]"""
import sys, zlib
def ips(bases, b):
    n = len(b)
    diff = [any(i >= len(a) or a[i] != b[i] for a in bases) for i in range(n)]
    out = bytearray(b'PATCH'); i = 0
    while i < n:
        if not diff[i]: i += 1; continue
        j = i
        # 6バイト以下のすき間はつなげる
        while j < n and j - i < 0xfff0:
            if diff[j]: j += 1; continue
            k = j
            while k < n and not diff[k] and k - j < 6: k += 1
            if k < n and diff[k] and k - j < 6: j = k
            else: break
        s = i
        if s == 0x454f46: s -= 1
        # 同じバイトが続く所（のばした ROM の 0 の所など）は RLE でちぢめる
        k = s
        while k < j:
            r = k
            while r < j and r - k < 0xffff and b[r] == b[k]: r += 1
            if r - k >= 16 and k != 0x454f46:
                out += k.to_bytes(3, 'big') + b'\0\0' + (r - k).to_bytes(2, 'big') + bytes([b[k]]); k = r
            else:
                e = k
                while e < j and e - k < 0xffff:
                    r = e
                    while r < j and b[r] == b[e] and r - e < 16: r += 1
                    if r - e >= 16: break
                    e = r
                if k == 0x454f46: k -= 1
                out += k.to_bytes(3, 'big') + (e - k).to_bytes(2, 'big') + b[k:e]; k = e
        i = j
    out += b'EOF'; return bytes(out)
def apply(a, p):
    a = bytearray(a); i = 5
    def grow(n):
        if len(a) < n: a.extend(bytes(n - len(a)))
    while p[i:i+3] != b'EOF':
        o = int.from_bytes(p[i:i+3], 'big'); l = int.from_bytes(p[i+3:i+5], 'big'); i += 5
        if l == 0:
            rl = int.from_bytes(p[i:i+2], 'big'); grow(o + rl); a[o:o+rl] = bytes([p[i+2]]) * rl; i += 3
        else: grow(o + l); a[o:o+l] = p[i:i+l]; i += l
    return bytes(a)
if __name__ == '__main__':
    b = open(sys.argv[1], 'rb').read()
    bases = [open(f, 'rb').read() for f in sys.argv[3:]]
    p = ips(bases, b)
    for f, a in zip(sys.argv[3:], bases):
        r = apply(a, p); r = r + bytes(len(b) - len(r)) if len(r) < len(b) else r
        assert r == b, f
    open(sys.argv[2], 'wb').write(p)
    print(sys.argv[2], len(p), 'bytes; result CRC32 %08X' % zlib.crc32(b))
