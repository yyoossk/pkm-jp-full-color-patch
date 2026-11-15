"""日本版クリスタルと 日本版銀の WRAM の アドレスの 対応を、同じ 処理（スクリプトの 命令の 処理など）を
   ならべて くらべて 集める。"""
import sys
from collections import Counter, defaultdict
OPLEN = {}
for op in range(256): OPLEN[op] = 1
for op in (0x01, 0x11, 0x21, 0x31, 0x08, 0xc2, 0xc3, 0xc4, 0xca, 0xcc, 0xcd, 0xd2, 0xd4, 0xda, 0xdc, 0xea, 0xfa):
    OPLEN[op] = 3
for op in (0x06, 0x0e, 0x16, 0x1e, 0x26, 0x2e, 0x36, 0x3e, 0x18, 0x20, 0x28, 0x30, 0x38, 0xc6, 0xce, 0xd6, 0xde,
           0xe0, 0xe6, 0xe8, 0xee, 0xf0, 0xf6, 0xf8, 0xfe, 0xcb):
    OPLEN[op] = 2


def pairs(c, co, g, go, n=80):
    """2つの コードを ならべて 読み、同じ 命令で 値の ちがう WRAM の アドレスを 返す"""
    out = []
    i = j = 0
    while i < n and j < n:
        a, b = c[co + i], g[go + j]
        if a != b: break
        L = OPLEN[a]
        if L == 3 and a in (0x01, 0x11, 0x21, 0xea, 0xfa):
            va = c[co + i + 1] | c[co + i + 2] << 8; vb = g[go + j + 1] | g[go + j + 2] << 8
            if 0xC000 <= va < 0xE000 and 0xC000 <= vb < 0xE000: out.append((va, vb))
        if a in (0xe0, 0xf0):
            out.append((0xff00 + c[co + i + 1], 0xff00 + g[go + j + 1]))
        if a in (0xc9, 0xc3, 0x18) and L != 2 and a == 0xc9: break
        i += L; j += L
    return out


def build(c, g):
    def tab(r, start, n):
        o = 0x25 * 0x4000 + start - 0x4000
        return [r[o + 2 * k] | r[o + 2 * k + 1] << 8 for k in range(n)]
    ct = tab(c, 0x6cb1, 0x9e); gt = tab(g, 0x6be4, 0x9e)
    votes = defaultdict(Counter)
    for k in range(0x9e):
        for va, vb in pairs(c, 0x25 * 0x4000 + ct[k] - 0x4000, g, 0x25 * 0x4000 + gt[k] - 0x4000, 200):
            votes[va][vb] += 1
    return {a: v.most_common(1)[0][0] for a, v in votes.items()}


if __name__ == '__main__':
    c = open(sys.argv[1], 'rb').read(); g = open(sys.argv[2], 'rb').read()
    m = build(c, g)
    for a in sorted(m): print('%04X %04X' % (a, m[a]))


def build_home(c, g, Hm, extra=None):
    """ホームの 関数の 呼び出し先を ぜんぶ 集め、銀の 同じ 関数と ならべて WRAM の 対応を ふやす"""
    from collections import Counter, defaultdict
    import asmport
    targets = set()
    for o in range(0, 0x4000 * 0x60):
        if c[o] == 0xCD:
            t = c[o + 1] | c[o + 2] << 8
            if 0x100 <= t < 0x4000: targets.add(t)
    votes = defaultdict(Counter)
    for t in targets:
        s = Hm.find(t)
        if s is None: continue
        for va, vb in pairs(c, t, g, s, 300):
            votes[va][vb] += 1
    return votes


def build_all(c, g, Hm):
    from collections import Counter, defaultdict
    v1 = build(c, g)
    votes = build_home(c, g, Hm)
    for a, b in v1.items(): votes[a][b] += 5
    return {a: v.most_common(1)[0][0] for a, v in votes.items()}
