"""バンクの あき（0 か FF が つづく 所）を さがす"""
def fo(b, a): return b * 0x4000 + a - 0x4000
def runs(g, bank, minlen=16):
    s = g[fo(bank, 0x4000):fo(bank + 1, 0x4000)]; out = []; i = 0
    while i < 0x4000:
        if s[i] in (0, 0xFF):
            j = i
            while j < 0x4000 and s[j] == s[i]: j += 1
            if j - i >= minlen: out.append((0x4000 + i, j - i))
            i = j
        else: i += 1
    return out
def tail(g, bank):
    s = g[fo(bank, 0x4000):fo(bank + 1, 0x4000)]; e = len(s)
    while e and s[e - 1] in (0, 0xFF): e -= 1
    return 0x4000 + e
if __name__ == '__main__':
    import sys
    g = open(sys.argv[1], 'rb').read()
    for b in [int(x, 16) for x in sys.argv[2:]]: print(hex(b), 'tail %04X' % tail(g, b), [(hex(a), n) for a, n in runs(g, b, 24)][-6:])
