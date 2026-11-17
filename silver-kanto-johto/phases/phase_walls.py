"""かべの 向きの ある タイル（$B0〜$B7）で、下へ 歩けなく なる 所を 直す（GetMovementPermissions $00:$29C1）。
   銀は 上・右・左の かべを しらべた とき も、ぜんぶ「下へ 行けない」ビット（set 3,[hl]）を 立てて いた。
   クリスタルでは 上 → ビット2、右 → ビット0、左 → ビット1。カントーの マップ（クリスタル版の MOD から 写した もの）は
   この タイルを よく 使うので、たとえば イワヤマトンネルで 左に かべの ある 所から 下へ 歩けなかった。"""

SITES = [(0x2A69, 0xD6, '上'), (0x2A83, 0xC6, '右'), (0x2A9D, 0xCE, '左')]


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    assert rom[0x2A4F:0x2A51] == bytes([0xCB, 0xDE])          # 下 は そのまま
    for a, op, what in SITES:
        assert rom[a:a + 2] == bytes([0xCB, 0xDE]), hex(a)
        rom[a + 1] = op
    log.append('かべの タイル：上・右・左の かべで 下へ 行けなく なって いたのを 直した（$00:$2A69・$2A83・$2A9D）')
    return rom
