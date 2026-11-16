"""GSC (pokecrystal) LZ decompressor"""
def unlz(r, o):
    out = bytearray(); start = o
    while True:
        c = r[o]; o += 1
        if c == 0xFF: break
        cmd = c >> 5
        if cmd == 7:
            cmd = (c >> 2) & 7; n = ((c & 3) << 8 | r[o]) + 1; o += 1
        else: n = (c & 0x1F) + 1
        if cmd == 0: out += r[o:o + n]; o += n
        elif cmd == 1: out += bytes([r[o]]) * n; o += 1
        elif cmd == 2:
            a, b = r[o], r[o + 1]; o += 2
            for i in range(n): out.append(a if i % 2 == 0 else b)
        elif cmd == 3: out += bytes(n)
        else:
            x = r[o]; o += 1
            if x & 0x80: p = len(out) - (x & 0x7F) - 1
            else: p = x << 8 | r[o]; o += 1
            if cmd == 4:
                for i in range(n): out.append(out[p + i])
            elif cmd == 5:
                for i in range(n):
                    b = out[p + i]; out.append(int('{:08b}'.format(b)[::-1], 2))
            elif cmd == 6:
                for i in range(n): out.append(out[p - i])
    return bytes(out), o - start
