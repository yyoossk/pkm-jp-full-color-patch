"""第123弾（追加の直し）キットの 金版：エンジンの 直し。
   MOD（クリスタル版）の スクリプト・マップ・文の 直し（3 シゲル・4 オーキドの 向き・5 トキワジムの 扉・7 研究所の 助手・
   2 はみ出す 行）は crystal_kj3.gbc（kj2 に キットの build_phase123.py を かけた もの）から c2g で そのまま 入る。
   ここは 金の エンジンの 所：
    1 さいしょから：赤の 部屋の ゲーム機の 前（3,6。スポーンの 表は gold_engine.p32_spawns で MOD から）で 上向き、
      パソコンに キズぐすり 1こ（金 NewGame 01:5C2A → 79:7E40）
    6 段差の あとの 連れ歩き：止まって いる（wPlayerStepDirection $FF）ときは 主人公の マスで 待つ（79:4ADA）
    9 野生の ポケモンの もちもの（タイムカプセルでしか 手に 入らなかった 道具。金の 道具の 番号は クリスタルと 同じ）
   10 カントーで そらをとぶ：マサラの とびさきで カントーの 地図、カーソルの はじめは マサラ（24:5D5B）
   11 つよさの 画面の なつき度の ハートを 9行めへ（2つめの タイプが かくれていた。45:6B00）
   8 つかまえかたの おじいさんの 絵：金は ダンの 絵の まま（赤の 絵を 使っていない）ので 直す 所なし。
"""
def fo(b, a): return b * 0x4000 + a - 0x4000
def w16(v): return bytes([v & 0xFF, v >> 8])


def expect(g, o, h):
    b = bytes.fromhex(h.replace(' ', '')); assert bytes(g[o:o + len(b)]) == b, (hex(o), g[o:o + len(b)].hex(' '), h); return b


def apply(g, log):
    B = 0x79; at = 0x7E40; assert not any(g[fo(B, at):fo(B, 0x7F00)])
    # 1 new game
    o = fo(1, 0x5C2A); expect(g, o, '3e 00 ea 20 cf 3e f1 e0 a1 c3 7a 5e')
    code = bytes([0xAF, 0xEA, 0x20, 0xCF,               # xor a / ld [wDefaultSpawnpoint], a
                  0x3E, 0x21, 0xEA, 0x74, 0xD1,         # ld a, CUSTOM_FACING | UP / ld [wPlayerSpriteSetupFlags], a
                  0x21, 0x09, 0xD6,                     # ld hl, wNumPCItems
                  0x3E, 1, 0x22, 0x3E, 0x12, 0x22, 0x3E, 1, 0x22, 0x3E, 0xFF, 0x77,   # 1 / POTION, 1 / -1
                  0x3E, 0xF1, 0xE0, 0xA1, 0xC9])        # ld a, MAPSETUP_WARP / ldh [hMapEntryMethod], a / ret
    g[fo(B, at):fo(B, at) + len(code)] = code
    g[o:o + 9] = bytes([0x3E, B, 0x21]) + w16(at) + bytes([0xCF, 0, 0, 0])
    log.append('第123弾 1 さいしょから 上向き・パソコンに キズぐすり（%02X:%04X）' % (B, at)); at += len(code)
    # 6 follower after a ledge
    o = fo(B, 0x4ADA)
    expect(g, o, 'fa 7a ce a7 20 03 25 18 0d 3d 20 03 24 18 07 3d 20 03 2c 18 01 2d e5 7a cd 1c 17')
    place = o + 22 + 17; expect(g, place, 'fa f7 d1 3c c0 7a cd 1c 17')
    new = bytes([0xFA, 0x7A, 0xCE, 0x3C, 0x28, place - (o + 6),
                 0x25, 0x3D, 0x28, 22 - 10,
                 0x24, 0x24, 0x3D, 0x28, 22 - 15,
                 0x25, 0x2C, 0x3D, 0x28, 22 - 20,
                 0x2D, 0x2D])
    assert len(new) == 22; g[o:o + 22] = new
    log.append('第123弾 6 段差の あとの 連れ歩き（79:4ADA）')
    # 9 wild held items
    BASE = fo(0x14, 0x5AA9); assert bytes(g[BASE:BASE + 7]) == bytes([1, 45, 49, 49, 45, 65, 65])
    LIGHT_BALL, TWISTEDSPOON, METAL_POWDER, LUCKY_PUNCH, POLKADOT_BOW, BRICK_PIECE, GOLD_LEAF, SILVER_LEAF, BRIGHTPOWDER = \
        0xA3, 0x60, 0x23, 0x1E, 0xAA, 0xB4, 0x4B, 0x3C, 0x03
    HELD = {25: (None, LIGHT_BALL, (0, 0xAD)), 63: (None, TWISTEDSPOON, (0, 0)), 64: (None, TWISTEDSPOON, (0, 0)),
            132: (None, METAL_POWDER, (0, 0)), 113: (LUCKY_PUNCH, None, (0, 0x7E)), 39: (None, POLKADOT_BOW, (0, 0)),
            66: (None, BRICK_PIECE, (0, 0)), 43: (None, GOLD_LEAF, (0, 0)), 69: (None, SILVER_LEAF, (0, 0)),
            144: (BRIGHTPOWDER, None, (0, 0)), 145: (BRIGHTPOWDER, None, (0, 0)), 146: (BRIGHTPOWDER, None, (0, 0)),
            150: (BRIGHTPOWDER, None, (0, 0x98))}
    for dex, (i1, i2, was) in HELD.items():
        o = BASE + 32 * (dex - 1); assert g[o] == dex and (g[o + 11], g[o + 12]) == was, (dex, g[o + 11:o + 13].hex())
        if i1 is not None: g[o + 11] = i1
        if i2 is not None: g[o + 12] = i2
    log.append('第123弾 9 野生の もちもの %d しゅるい' % len(HELD))
    # 10 fly map
    o = fo(0x24, 0x5D5B); expect(g, o, 'f5 0e 0d cd e4 5c a7 28 18 3e 0c ea 24 cf 3e 17 ea 25 cf ea 21 cf')
    g[o + 2] = 0x02
    g[o + 9:o + 22] = bytes.fromhex('3e0cea24cfea21cf3e17ea25cf')
    # 11 hearts row 9
    h = fo(0x45, 0x6B00)
    expect(g, h + 0x3D, '21 0e 99'); expect(g, h + 0x5B, '21 49 c4'); expect(g, h + 0x80, '21 4e c4')
    g[h + 0x3E] = 0x2E; g[h + 0x5C] = 0x5D; g[h + 0x81] = 0x62
    log.append('第123弾 10 カントーの そらをとぶ（24:5D5B）・11 ハートを 9行め（45:6B00）')
