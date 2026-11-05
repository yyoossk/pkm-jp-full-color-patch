"""英語版 pokegold の全ラベル → 日本版 金 のアドレス表を作る。
   出力: jpsym.pkl = {name: (bank, addr)}（ROM）, ram = {name: addr}"""
import align as A, pickle, sys, re
A.load(sys.argv[1])
m, labjp, votes = pickle.load(open(sys.argv[2], 'rb'))
JP = A.JP; EN = A.EN

def okat(eb, ea, jb, ja, n=8):
    eo = A.off(eb, ea); jo = A.off(jb, ja)
    code = EN[eo:eo + n]
    pat, _ = A.mask(code)
    return all(JP[jo + k] == v for k, (v, c) in enumerate(pat) if c)

rom = {}
for n, (b, a) in labjp.items():
    pass
# labjp は ptr 形式（bank, addr）
for n, v in labjp.items(): rom[n] = v
# 並べて、前のラベルからの差で埋める
labs = sorted([(b, a, n) for n, (b, a) in A.SYM.items() if a < 0x8000], key=lambda x: (x[0] if x[1] >= 0x4000 else 0, x[1]))
bybank = {}
for b, a, n in labs:
    bb = b if a >= 0x4000 else 0
    bybank.setdefault(bb, []).append((a, n))
added = 1
while added:
    added = 0
    for bb, L in bybank.items():
        L.sort()
        last = None
        for a, n in L:
            if n in rom: last = (a, n); continue
            if last is None: continue
            la, ln = last
            jb, ja = rom[ln]
            cand = ja + (a - la)
            eb = A.SYM[n][0]
            # 次のラベルまでの長さで確かめる
            if okat(eb, a, jb, cand, 6):
                rom[n] = (jb, cand); added += 1; last = (a, n)
    # 後ろからも
    for bb, L in bybank.items():
        nxt = None
        for a, n in reversed(L):
            if n in rom: nxt = (a, n); continue
            if nxt is None: continue
            na, nn = nxt
            jb, ja = rom[nn]
            cand = ja - (na - a)
            eb = A.SYM[n][0]
            if okat(eb, a, jb, cand, 6):
                rom[n] = (jb, cand); added += 1; nxt = (a, n)
# RAM
ram = {}
for n, (b, a) in A.SYM.items():
    if 0x8000 <= a:
        if a in votes:
            j, c = votes[a].most_common(1)[0]
            tot = sum(votes[a].values())
            if c >= 2 and c * 2 > tot or (c == 1 and tot == 1 and a >= 0xff80): ram[n] = j
print('rom', len(rom), 'of', len(labs), ' ram', len(ram))
pickle.dump((rom, ram), open(sys.argv[3], 'wb'))
