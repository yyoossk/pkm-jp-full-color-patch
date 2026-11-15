"""クリスタル版の しくみの 小さな 直しを 金へ（弾ごとに 足していく）。"""
def fo(b, a): return b * 0x4000 + a - 0x4000

W_WINLOSS_BANK = 0xD7A2      # クリスタル版 $DA5C（イベントフラグの あと の あき）。D7A0〜D7A3 の うち D7A1 は 殿堂入り

def free25(g, n):
    """バンク 25 の うしろの あき（追加機能パッチと 合わせる ときは 見なおす）"""
    s = g[0x25 * 0x4000:0x26 * 0x4000]; i = len(s)
    while i > 0 and s[i - 1] in (0, 0xFF): i -= 1
    a = 0x4000 + i + 2; assert a + n <= 0x7FF0
    return a

def p54_winloss(g, log):
    """第54弾：トレーナーの 負けた／勝った ときの セリフを、winlosstext を 書いた スクリプトの バンクから 読む"""
    o = fo(0x25, 0x702F); assert g[o:o + 3] == bytes([0x21, 0x5C, 0xCF])
    a = free25(g, 10)
    g[fo(0x25, a):fo(0x25, a) + 10] = bytes([0xFA, 0x52, 0xD1, 0xEA, W_WINLOSS_BANK & 0xFF, W_WINLOSS_BANK >> 8,
                                            0x21, 0x5C, 0xCF, 0xC9])           # ld a,[wScriptBank] / ld [..],a / ld hl,wWinTextPointer
    g[o:o + 3] = bytes([0xCD, a & 0xFF, a >> 8])
    o = 0x38C0
    assert bytes(g[o:o + 15]) == bytes.fromhex('fa0bd1fe011805215ccf180cfae3cf')
    W = W_WINLOSS_BANK
    code = bytes([0xFA, 0xE3, 0xCF, 0x21, 0x5C, 0xCF, 0xA7, 0x28, 0x03, 0x21, 0x5E, 0xCF, 0x2A, 0x66, 0x6F,
                  0xFA, W & 0xFF, W >> 8, 0xA7, 0x20, 0x03, 0xCD, 0xEC, 0x2C,
                  0xF5, 0xAF, 0xEA, W & 0xFF, W >> 8, 0xF1,
                  0xCD, 0x66, 0x33, 0xCD, 0xAE, 0x33, 0xCD, 0x26, 0x0A, 0xC9])
    assert bytes(g[o + 0x1B:o + 0x28]) == bytes.fromhex('cdec2ccd6633cdae33cd260ac9')
    assert len(code) == 0x28
    g[o:o + 0x28] = code
    log.append('第54弾 winlosstext：25:%04X、ホーム 38C0（バンクは %04X）' % (a, W))

def p69_ledges(g, log):
    """第69弾：赤の マップ（クリスタル タイルセット 40 → 金 36）の 段差を 赤と 同じに（手前から とびこえる・ほかは かべ）。
       金の TryStep（04:4176 の call CheckLandPerms）→ 04:7F80（あき）"""
    from gold_safari import A
    o = fo(0x04, 0x4176); assert g[o:o + 3] == bytes([0xCD, 0x9E, 0x43])
    h = 0x7F80; assert not any(g[fo(0x04, h):fo(0x04, h) + 0x40])
    a = A(h)
    a.db(0xCD, 0x9E, 0x43, 0xD8)                         # call CheckLandPerms / ret c
    a.db(0xFA, 0x74, 0xD0, 0xFE, 36); a.jr(0x20, 'walk')  # wMapTileset == 36
    a.db(0xFA, 0x5C, 0xCF, 0x5F, 0xE6, 0xF0, 0xFE, 0xA0); a.jr(0x20, 'walk')
    a.db(0x7B, 0xE6, 0x07, 0x5F, 0x16, 0x00, 0x21, 0x1E, 0x42, 0x19)
    a.db(0xFA, 0x59, 0xCF, 0xA6); a.jr(0x28, 'wall')
    a.db(0xE1, 0x11, 0x16, 0x00, 0xCD, 0x45, 0x3D)       # pop hl / ld de,SFX_JUMP_OVER_LEDGE / call PlaySFX
    a.db(0x3E, 0x03, 0xCD, 0x5F, 0x42, 0x3E, 0x07, 0x37, 0xC9)
    a.L('wall'); a.db(0x37, 0xC9)
    a.L('walk'); a.db(0xA7, 0xC9)
    b = a.fin(); g[fo(0x04, h):fo(0x04, h) + len(b)] = b
    g[o + 1] = h & 0xFF; g[o + 2] = h >> 8
    log.append('第69弾 段差：04:4176 → 04:%04X（%d バイト）' % (h, len(b)))

def apply(g, log):
    p69_ledges(g, log)
    p54_winloss(g, log)
