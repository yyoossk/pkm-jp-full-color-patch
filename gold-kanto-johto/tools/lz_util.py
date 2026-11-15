def lzlen(r, o):
    """第二世代の LZ の 長さ（終わりの $FF まで）"""
    s = o
    while True:
        b = r[o]
        if b == 0xFF: return o + 1 - s
        cmd = b >> 5
        if cmd == 7:
            cmd = (b >> 2) & 7; n = ((b & 3) << 8 | r[o + 1]) + 1; o += 2
        else:
            n = (b & 0x1F) + 1; o += 1
        if cmd == 0: o += n
        elif cmd == 1: o += 1
        elif cmd == 2: o += 2
        elif cmd == 3: pass
        else: o += 1 if r[o] & 0x80 else 2
