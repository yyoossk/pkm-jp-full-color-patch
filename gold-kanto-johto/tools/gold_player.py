"""第71弾（金）：主人公を 赤の 見た目に（クリスタル版の 第71弾と 同じ もの。絵は できあがった クリスタル版から 取る）。
   ・歩く 絵：金の 絵 1番（ゴールド）→ 金に ある 赤の 絵（SPRITE_RED、30:46C0）。名前の 画面の アイコンも（24:5F6D）。
   ・自転車：pokered の 赤の 自転車の 絵（red_bike.png）。クリスタル版の 第71弾の 絵は ライバルの 歩く 絵だった。
   ・後ろ姿：クリスタル版の もの（LZ、6x6）。金の GetTrainerBackpic（0F:79B8）と 金の 殿堂入り（21:69C0）が 読む。
     ダイ（つかまえかたの 手本）の 後ろ姿も 同じ バンクへ 写す（ld b, バンク を 2つで 使うので）。
   ・前の 絵：クリスタル版の ChrisPic（22:48B2、7x7、たての 並び）を LZ に して トレーナーの 種類 CAL の 絵に
     （金では オーキドの 話・殿堂入り・つうしんの 主人公の 絵が CAL の 絵）。
   ・トレーナーカード：前の 絵の まんなかの 5列（金の ChrisPicAndTrainerCardGFX、09:5490 の はじめの 35タイル）。
   ・色：主人公の 色（トレーナーの 色の 表の はじめ。第10弾で 02:7EB0 へ うつした）→ 赤フルカラーの 赤。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gold_opening import lzlen, fo

RED_PAL = bytes.fromhex('5c46f620')
POKERED = '/home/claude/work/mod/ref/pokered'


def png2bpp(path):
    from PIL import Image
    im = Image.open(path).convert('L'); W, H = im.size; out = bytearray()
    for ty in range(H // 8):
        for tx in range(W // 8):
            for y in range(8):
                lo = hi = 0
                for x in range(8):
                    v = 3 - im.getpixel((tx * 8 + x, ty * 8 + y)) // 85
                    lo |= (v & 1) << (7 - x); hi |= (v >> 1) << (7 - x)
                out += bytes([lo, hi])
    return bytes(out)
CAL = 0x0C


def bike_head(bike, walk):
    """16x16 の コマ（タイル 左上・右上・左下・右下）× 6 の 上 9段を、walk の 立ちの コマ（f % 3）の 上 9段に"""
    def px(b, o):
        P = [[0] * 16 for _ in range(16)]
        for t, (dx, dy) in enumerate(((0, 0), (8, 0), (0, 8), (8, 8))):
            d = b[o + t * 16:o + t * 16 + 16]
            for y in range(8):
                for x in range(8): P[dy + y][dx + x] = ((d[2 * y] >> (7 - x)) & 1) | (((d[2 * y + 1] >> (7 - x)) & 1) << 1)
        return P
    out = bytearray()
    for f in range(6):
        s_, k = px(walk, (f % 3) * 64), px(bike, f * 64)
        P = [s_[y] if y < 9 else k[y] for y in range(16)]
        for dx, dy in ((0, 0), (8, 0), (0, 8), (8, 8)):
            for y in range(8):
                lo = hi = 0
                for x in range(8):
                    v = P[dy + y][dx + x]; lo |= (v & 1) << (7 - x); hi |= (v >> 1) << (7 - x)
                out += bytes([lo, hi])
    return bytes(out)


def lz_literal(data):
    out = bytearray(); i = 0
    while i < len(data):
        n = min(1024, len(data) - i)
        out += bytes([0xE0 | ((n - 1) >> 8), (n - 1) & 0xFF]) + data[i:i + n]; i += n
    return bytes(out + b'\xff')


def apply(g, M, E, log):
    G0 = bytes(g)
    nb = E.next_bank; E.next_bank += 1
    assert not any(g[nb * 0x4000:(nb + 1) * 0x4000])
    put_at = [0x4000]
    def put(b):
        a = put_at[0]; g[fo(nb, a):fo(nb, a) + len(b)] = b; put_at[0] += len(b); return a
    # 歩く 絵・アイコン
    t = fo(0x05, 0x47B0)
    chris, bike, red = G0[t:t + 6], G0[t + 6:t + 12], G0[t + 30:t + 36]
    assert chris == bytes.fromhex('0040c0300100') and bike == bytes.fromhex('8041c0300100') and red == bytes.fromhex('c046c0300100')
    g[t:t + 2] = red[:2]; g[t + 3] = red[3]
    o = fo(0x24, 0x5F6D); assert G0[o:o + 5] == bytes([0x11, 0x00, 0x40, 0x06, 0x30])
    g[o + 1:o + 3] = red[:2]; g[o + 4] = red[3]
    # 自転車
    # クリスタル版（第71弾）の 自転車の 絵は 赤フルカラーの 絵の 表の 2番め＝ライバルの 歩く 絵だったので、
    # pokered の red_bike.png（16x96、6コマ。タイルは 左上・右上・左下・右下）を 2bpp に して 使う
    bk = png2bpp(os.path.join(POKERED, 'gfx/sprites/red_bike.png'))
    # 第127弾：自転車の 6コマの 上 9段を、歩く 絵（サトシ）の 立ちの 絵（下・上・横）の 上 9段に（赤の 頭の ままだった）
    bk = bike_head(bk, G0[fo(0x30, 0x46C0):fo(0x30, 0x46C0) + 3 * 64])
    a = put(bk)
    g[t + 6] = a & 0xFF; g[t + 7] = a >> 8; g[t + 9] = nb
    # 後ろ姿（クリスタル版：ld b, bank / ld hl, pic）
    assert M[0x3FC38] == 0x06 and M[0x3FC3A] == 0x21
    mbk, mad = M[0x3FC39], M[0x3FC3B] | M[0x3FC3C] << 8
    bp = M[fo(mbk, mad):fo(mbk, mad) + lzlen(M, fo(mbk, mad))]
    ba = put(bp)
    dude = G0[fo(0x0F, 0x7BBB):fo(0x0F, 0x7BBB) + lzlen(G0, fo(0x0F, 0x7BBB))]
    da = put(dude)
    o = fo(0x0F, 0x79B8)
    assert G0[o:o + 18] == bytes.fromhex('212b7afa0bd1fe03200321bb7b111093060f')
    g[o + 1] = ba & 0xFF; g[o + 2] = ba >> 8; g[o + 11] = da & 0xFF; g[o + 12] = da >> 8; g[o + 17] = nb
    o = fo(0x21, 0x69C0); assert G0[o:o + 8] == bytes.fromhex('212b7a111093060f')
    g[o + 1] = ba & 0xFF; g[o + 2] = ba >> 8; g[o + 7] = nb
    # 前の 絵
    raw = M[fo(0x22, 0x48B2):fo(0x22, 0x48B2) + 49 * 16]
    fa = put(lz_literal(raw))
    # トレーナーの 絵の 表（第10弾で NB へ。NB は ビルドで かわるので GetTrainerPic 14:588A の ld hl・ld a,NB から 読む）
    gp = fo(0x14, 0x588A); code = bytes(g[gp:gp + 48])
    i = code.index(bytes([0xD5, 0x21])); tbl = code[i + 2] | code[i + 3] << 8
    j = code.index(bytes([0xCD, 0xE4, 0x30])); tb_bank = code[j - 1]; assert code[j - 2] == 0x3E
    pt = fo(tb_bank, tbl) + 3 * (CAL - 1)
    assert bytes(g[pt:pt + 3]) == bytes.fromhex('1a9069'), g[pt:pt + 3].hex()   # 金の 主人公の 絵（1A:6990）
    fix = G0[fo(0x14, 0x5862):fo(0x14, 0x5862) + 64]
    assert nb not in fix[:fix.index(0xFF):2]
    g[pt:pt + 3] = bytes([nb, fa & 0xFF, fa >> 8])
    # トレーナーカード（たての 並びの 1〜5列）
    # 金の カードの 絵は 横の 並び（5x7）。右上の タイルは カードの 角の 折りめ（赤の 絵が そこで 空なら 金の まま）
    o = fo(0x09, 0x5490); card = bytearray(G0[o:o + 35 * 16])
    for y in range(7):
        for x in range(5):
            t = raw[((x + 1) * 7 + y) * 16:((x + 1) * 7 + y) * 16 + 16]
            if (y, x) == (0, 4) and not any(t): continue
            card[(y * 5 + x) * 16:(y * 5 + x) * 16 + 16] = t
    g[o:o + len(card)] = card
    # 色
    for pa in (0x7EB0, 0x74C3):
        o = fo(0x02, pa); assert G0[o:o + 4] == bytes.fromhex('59323615'), hex(pa); g[o:o + 4] = RED_PAL
    assert put_at[0] < 0x8000
    log.append('第71弾：主人公を 赤の 見た目に（歩く 絵・アイコン・自転車・後ろ姿・前の 絵・カード・色）バンク %02X' % nb)
