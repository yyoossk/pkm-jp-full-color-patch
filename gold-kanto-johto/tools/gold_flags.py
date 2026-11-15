"""第15弾の 土台：イベントフラグ $800〜$A17 を 金で 使えるように する。
   クリスタル版は wEventFlags の 前の 空き（$DA01〜）に 置いた。金の wEventFlags（$D7AA）の 前の 空きは
   追加機能パッチが 一部 使うので、空いている 2つ に 分けて 置く：
     $800〜$997 → $D70D〜$D73F（51 バイト）、$998〜$A17 → $D790〜$D79F（16 バイト）
   EventFlagAction（ホーム $2EEB：ld hl,wEventFlags / call FlagAction / ret）を farcall に かえる。
"""
def fo(b, a): return b * 0x4000 + a - 0x4000
EFA, FLAGACTION, W_EVENTFLAGS = 0x2EEB, 0x2EF2, 0xD7AA
AREA_A, AREA_B, SPLIT = 0xD70D, 0xD790, 51 * 8
LAST = 0x800 + SPLIT + 16 * 8 - 1          # $A17

def apply(g, bank, addr, log):
    assert g[EFA:EFA + 7] == bytes([0x21, 0xAA, 0xD7, 0xCD, 0xF2, 0x2E, 0xC9])
    fa = [FLAGACTION & 0xFF, FLAGACTION >> 8]
    c = bytearray()
    c += bytes([0x7A, 0xFE, 0x08, 0x38, 0x00])                # ld a,d / cp 8 / jr c,.old
    j_old = len(c) - 1
    c += bytes([0xD6, 0x08, 0x57])                            # sub 8 / ld d,a
    c += bytes([0xFE, 0x01, 0x38, 0x00])                      # cp 1 / jr c,.a
    j_a = len(c) - 1
    c += bytes([0x20, 0x00])                                  # jr nz,.b
    j_b1 = len(c) - 1
    c += bytes([0x7B, 0xFE, SPLIT & 0xFF, 0x30, 0x00])        # ld a,e / cp $98 / jr nc,.b
    j_b2 = len(c) - 1
    a_lab = len(c)
    c += bytes([0x21, AREA_A & 0xFF, AREA_A >> 8, 0xC3] + fa)
    b_lab = len(c)
    c += bytes([0x7B, 0xD6, SPLIT & 0xFF, 0x5F, 0x7A, 0xDE, SPLIT >> 8, 0x57])   # de -= $198
    c += bytes([0x21, AREA_B & 0xFF, AREA_B >> 8, 0xC3] + fa)
    old_lab = len(c)
    c += bytes([0x21, W_EVENTFLAGS & 0xFF, W_EVENTFLAGS >> 8, 0xC3] + fa)
    for j, t in ((j_old, old_lab), (j_a, a_lab), (j_b1, b_lab), (j_b2, b_lab)):
        c[j] = (t - (j + 1)) & 0xFF
    o = fo(bank, addr); assert not any(g[o:o + len(c)])
    g[o:o + len(c)] = c
    g[EFA:EFA + 7] = bytes([0x3E, bank, 0x21, addr & 0xFF, addr >> 8, 0xCF, 0xC9])
    log.append('イベントフラグ $800〜$%03X：%02X:%04X（%d バイト）' % (LAST, bank, addr, len(c)))
    return len(c)
