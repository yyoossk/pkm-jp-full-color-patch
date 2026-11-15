"""金に ない スクリプトの special を 足す（金の 使われない special の 番号を 使う）。
   BeastsCheck・MonCheck（タマムシの ポケモンセンター1F の ミナキ）：クリスタル 12:66D0〜681B
   （CheckOwnMonAnywhere・CheckOwnMon・ボックスの 表・UpdateOTPointer）を 新しい バンクの 同じ 住所へ うつして 読みかえる。
   SRAM の ボックスの 住所は 金も 同じ（表 12:67F8 が 金にも ある）。
"""
import sys
sys.path.insert(0, '/home/claude/work/scripts')
from asmx import L, RX, RAM_FIX
import c2g
def fo(b, a): return b * 0x4000 + a - 0x4000

NEW = {'BeastsCheck': ('UnusedDummySpecial', 0x66D0), 'MonCheck': ('UnusedMemoryGame', 0x66F9)}
SRC = (0x12, 0x66D0, 0x6813 + 9)
DATA = (0x67F8, 0x6813)                       # ボックスの 表（9 こ × 3）
HOME = {0x2F9D: 0x309D, 0x2FAD: 0x30AD}
CHECK = {0xC2DD: 'wScriptVar', 0xDC9D: 'wPokemonData', 0xDCA5: 'wPartyMons', 0xDDC5: 'wPartyMonOTs',
         0xD48C: 'wPlayerID', 0xD48D: 'wPlayerID', 0xD48E: 'wPlayerName', 0xDB65: 'wCurBox'}
SPECIALS = 0x4239                             # 金 SpecialsPointers（03:422B の ld hl）

def register():
    """c2g が 名前で 読みかえられるように"""
    for n, (gold, _) in NEW.items(): c2g.G['special'][n] = c2g.G['special'][gold]

def apply(g, M, SB, log):
    b, lo, hi = SRC
    g[fo(SB, lo):fo(SB, hi)] = M[fo(b, lo):fo(b, hi)]
    p = lo
    while p < hi:
        if DATA[0] <= p < DATA[1]: p += 1; continue
        o = fo(b, p); op = M[o]; ln = L[op]
        if ln == 3 and op != 0x31:
            v = M[o + 1] | M[o + 2] << 8; nv = v
            if op in (0xCD, 0xC3, 0xCA, 0xC2, 0xDA, 0xD2, 0xC4, 0xCC, 0xD4, 0xDC):
                nv = HOME[v] if v < 0x4000 else v
                assert v < 0x4000 or lo <= v < hi, hex(v)
            elif 0xC000 <= v < 0xE000:
                if v in RAM_FIX: nv = RAM_FIX[v]
                else:
                    nv, nm = RX.x(v); assert nm.split('+')[0] == CHECK[v], (hex(v), nm)
            elif 0x4000 <= v < 0x8000: assert lo <= v < hi, hex(v)
            g[fo(SB, p) + 1] = nv & 0xFF; g[fo(SB, p) + 2] = nv >> 8
        p += ln
    assert bytes(g[fo(0x03, 0x422B):fo(0x03, 0x422E)]) == bytes([0x21, SPECIALS & 0xFF, SPECIALS >> 8])
    for n, (gold, adr) in NEW.items():
        i = c2g.G['special'][gold]; t = fo(0x03, SPECIALS) + 3 * i
        g[t] = SB; g[t + 1] = adr & 0xFF; g[t + 2] = adr >> 8
        log.append('special %s → %d（%02X:%04X）' % (n, i, SB, adr))
