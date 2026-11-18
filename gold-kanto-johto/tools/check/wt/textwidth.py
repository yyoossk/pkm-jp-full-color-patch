"""ROM の 中の 文（text_start 00 〜 終わり）を さがして、1行が 18文字を こえる ものを 出す。
   python3 textwidth.py ROM [比べる ROM]"""
import sys; sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools')
import jpchar
W = {0x1D:2,0x1E:2,0x1F:2,0x22:2,0x23:4,0x24:2,0x25:2,0x35:6,0x36:3,0x37:3,0x4A:2,
     0x52:5,0x53:5,0x54:4,0x56:2,0x59:7,0x5A:7}
CHAR = set(jpchar.DEC) - {0x4F,0x51,0x55,0x57,0x58,0x50,0x4C,0x4E,0x00,0x49,0x4B,0x4D,0x5B,0x5C,0x5D,0x5E,0x5F,0x60}
CHAR |= {0x72}   # 『
def scan(R):
    out = {}
    n = len(R); i = 0
    while i < n - 8:
        if R[i] != 0: i += 1; continue
        j = i + 1; lines = [0]; ok = True; seen_ctrl = False
        while j < n and j - i < 600:
            b = R[j]
            if b in (0x57, 0x58, 0x50): break
            if b in (0x4F, 0x51, 0x55, 0x4E): lines.append(0); seen_ctrl = True
            elif b in CHAR or b in W: lines[-1] += W.get(b, 1)
            else: ok = False; break
            j += 1
        if ok and j < n and R[j] in (0x57, 0x58, 0x50) and j - i >= 8 and (seen_ctrl or R[j] != 0x50):
            if max(lines) > 18:
                out[bytes(R[i:j+1])] = (i, max(lines))
            i = j + 1
        else: i += 1
    return out
a = scan(open(sys.argv[1],'rb').read())
b = scan(open(sys.argv[2],'rb').read()) if len(sys.argv) > 2 else {}
for t,(off,m) in sorted(a.items(), key=lambda x:x[1][0]):
    if t in b: continue
    print('%02X:%04X %d %s' % (off//0x4000, off%0x4000 + (0x4000 if off >= 0x4000 else 0), m, jpchar.decode(t[1:])))
