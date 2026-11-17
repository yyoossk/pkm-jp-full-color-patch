"""ひでんわざの バッジを 赤と 同じ カントーの バッジに（クリスタル版の MOD と 同じ）。
   銀は ジョウトの バッジ（いあいぎり＝インセクト、なみのり＝ファントム、そらをとぶ＝ストーム、かいりき＝レギュラー）なので、
   カントーで ブルーバッジを もらっても いあいぎりが 使えなかった（クチバジムの 前の 木が きれない）。
   クリスタル版の MOD：いあいぎり → ブルー、なみのり → ピンク、そらをとぶ → オレンジ、かいりき → レインボー。
   銀の エンジンフラグ：ウイング $1A … ライジング $21、グレー $22、ブルー $23、オレンジ $24、レインボー $25、ピンク $26。
   （うずしお・たきのぼりは クリスタル版でも ジョウトの まま）"""

SITES = [  # (アドレス, 銀の フラグ, 新しい フラグ, なに)
    (0x0C818, 0x1B, 0x23, 'いあいぎり（手持ちから）'),
    (0x0D43B, 0x1B, 0x23, 'いあいぎり（木に 話しかける）'),
    (0x0C9C2, 0x1D, 0x26, 'なみのり（手持ちから）'),
    (0x0CAB7, 0x1D, 0x26, 'なみのり（水に 話しかける）'),
    (0x0CB23, 0x1F, 0x24, 'そらをとぶ'),
    (0x0CE22, 0x1C, 0x25, 'かいりき（手持ちから）'),
    (0x0CF3E, 0x1C, 0x25, 'かいりき（岩に 話しかける）'),
]


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    for a, old, new, what in SITES:
        assert rom[a] == 0x11 and rom[a + 1] == old and rom[a + 2] == 0 and rom[a + 3] == 0xCD, (hex(a), rom[a:a + 6].hex())
        rom[a + 1] = new
    log.append('ひでんわざの バッジを カントーの バッジに（%d か所）' % len(SITES))
    cut_trees(rom, log)
    return rom


def cut_trees(rom, log):
    """いあいぎりの 木の ブロックの 表（$03:$48F5。タイルセットごと）に、カントーの タイルセット 40（赤の 外の 絵）を 足す。
       銀の 表には ない ので、カントーの 木は「いあいぎりで きりますか？」→ はい の あと 何も 起きなかった。
       ブロックの 組は クリスタル版の MOD（$03:$4881）と 同じ。表を 1つ ぶん のばすため、タイルセット 2 の 組と 40 の 組は $03:$7FE0〜 に 置く。"""
    B = 3 * 0x4000 - 0x4000
    TAB = 0x48F5
    assert rom[0xC87D:0xC880] == bytes([0x21, TAB & 0xff, TAB >> 8])
    ents = []; q = B + TAB
    while rom[q] != 0xFF: ents.append((rom[q], rom[q + 1] | rom[q + 2] << 8)); q += 3
    assert [t for t, a in ents] == [1, 2, 3, 22, 28], ents
    def lst(a):
        q = B + a; out = bytearray()
        while rom[q] != 0xFF: out += rom[q:q + 3]; q += 3
        return bytes(out) + b'\xff'
    L = {t: lst(a) for t, a in ents}
    end = max(B + a + len(L[t]) for t, a in ents)
    K40 = bytes.fromhex('3c3500 3f3500 3d3600 0b0a01 326d00 336c00 346f00 354c00 606e00') + b'\xff'
    FREE = 0x7FE0
    assert not any(rom[B + FREE:B + 0x8000]) and len(K40) + len(L[2]) <= 0x20
    a40, a2 = FREE, FREE + len(K40)
    rom[B + a40:B + a40 + len(K40)] = K40; rom[B + a2:B + a2 + len(L[2])] = L[2]
    new = {2: a2, 40: a40}
    order = [1, 2, 3, 22, 28, 40]
    pos = TAB + 3 * len(order) + 1
    body = bytearray()
    for t in (1, 3, 22, 28):
        new[t] = pos + len(body); body += L[t]
    tab = b''.join(bytes([t, new[t] & 0xff, new[t] >> 8]) for t in order) + b'\xff'
    blob = tab + body
    assert B + TAB + len(blob) <= end, (hex(B + TAB + len(blob)), hex(end))
    rom[B + TAB:B + TAB + len(blob)] = blob
    for i in range(B + TAB + len(blob), end): rom[i] = 0
    log.append('いあいぎりの 木：タイルセット 40 を 足した')
