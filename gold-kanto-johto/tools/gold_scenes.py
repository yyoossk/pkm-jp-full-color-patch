"""マップの シーンの 変数の 表（GetMapSceneID がしらべる 表）を クリスタル版に 合わせる。
   金の 表（25:$4000、4 バイトずつ：グループ・番号・変数の 住所）を 新しい バンクへ うつし、
   入れた マップの うち クリスタル版で 変数が ちがう／ない ものを 足す。ホーム $1F42 の ld a,$25 / ld hl,$4000 を 書きかえ。
   変数の 住所：クリスタル版の 足した 所 $DA5F〜$DA64 → 金 $D7A4〜（asmx.RAM_FIX）、$DA5D・$DA5E（クリスタル版は 足した フラグの 所の
   うしろを 使う）→ 金は フラグ $7F0〜$7FF の 所（金・クリスタル版とも 使っていない）$D8A8・$D8A9。
   クリスタルの 元の 変数は クリスタルの 表で 同じ 住所を 使う マップの 名前 → 金の 表の その マップの 住所。
"""
import asmx
def fo(b, a): return b * 0x4000 + a - 0x4000
asmx.RAM_FIX.update({0xDA5D: 0xD8A8, 0xDA5E: 0xD8A9})

def tab(r, o):
    L = []
    while r[o] != 0xFF: L.append((r[o], r[o + 1], r[o + 2] | r[o + 3] << 8)); o += 4
    return L

def apply(g, M, V, E, ported, log):
    import c2g
    X = E.X
    assert g[0x1F42 + 4:0x1F42 + 10] == bytes.fromhex('3e25d7210040')
    G = tab(g, fo(0x25, 0x4000)); C = tab(V, fo(0x13, 0x5012)); MM = tab(M, fo(0x62, 0x7A0A))
    cvar_map = {}                      # クリスタルの 元の 変数 → 金の 変数（同じ マップの 名前で。金の 元の 表で）
    G0 = tab(open('/home/claude/work/ref/kin_late.gbc', 'rb').read(), fo(0x25, 0x4000))
    gd0 = {(a, b): c for a, b, c in G0}
    gd = {(a, b): c for a, b, c in G}
    for a, b, c in C:
        nm = c2g.CMAP.get((a, b)); gid = c2g.GMAP.get(nm)
        if gid and gid in gd0: cvar_map[c] = gd0[gid]
    out = dict(gd); added = []
    for a, b, c in MM:
        nm = c2g.CMAP.get((a, b))
        if nm not in ported: continue
        gid = X.mapid((a, b), 'scene')
        if c in asmx.RAM_FIX: gv = asmx.RAM_FIX[c]
        elif c in cvar_map: gv = cvar_map[c]
        elif 0xDA65 <= c < 0xDA65 + 0x100: gv = 0xD7AA + (c - 0xDA65)      # イベントフラグの 所
        else: raise AssertionError('シーンの 変数 %04X（%s）' % (c, nm))
        if out.get(gid) != gv: out[gid] = gv; added.append('%s→%04X' % (nm, gv))
    blob = b''.join(bytes([a, b, v & 0xFF, v >> 8]) for (a, b), v in out.items()) + b'\xff'
    nb = E.next_bank; E.next_bank += 1
    g[fo(nb, 0x4000):fo(nb, 0x4000) + len(blob)] = blob
    g[0x1F42 + 5] = nb
    log.append('シーンの 表：%d こ（%02X:4000）、足した／かえた %d：%s' % (len(out), nb, len(added), ' '.join(added)))
