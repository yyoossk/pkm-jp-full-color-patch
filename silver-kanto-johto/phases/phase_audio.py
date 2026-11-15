"""曲と 効果音（第53弾 など）：クリスタル版が 入れた 赤の 曲・効果音を 銀へ。
   クリスタル版は 曲 $52・$53（金銀の オープニング）、$5E・$5F（モバイル）、$62（クリスタルの オープニング）と
   効果音 $BE〜$C4（クリスタルの オープニング）の 場所を、バンク$20 の 空き（$5F3A〜）に 置いた 赤の 曲に かえた。
   銀：そのデータを $A0 の 同じ 場所へ。曲 $52・$53 は 銀の 表を 書きかえる。銀の 曲は $5C まで、効果音は $BB まで
   なので、$5D〜$62 と $BE〜$C4 は バンク$3A の 空き（$7FB7〜）の 足した 表から 読む（読む 所 3か所を call に）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port
from gsc import fo, r16

AB = 0x3A
MUSIC, SFX = 0x506E, 0x525E            # 銀の 表（$3A）
C_MUSIC, C_SFX = 0x506E, 0x527C        # クリスタルの 表
N_MUSIC, N_SFX = 0x5D, 0xBC            # 銀の 曲・効果音の 数
BLOCK = (0x20, 0x5F3A, 3183)           # クリスタル版の 赤の 曲の データ
FREE = 0x7FB7


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    b, a, n = BLOCK
    src = fo(b, a); dst = fo(port.cb(b), a)
    assert not any(rom[dst:dst + n]); rom[dst:dst + n] = cmod[src:src + n]

    def ent(r, base, i): o = fo(AB, base) + 3 * i; return r[o], r16(r, o + 1)
    def conv(e):
        bk, ad = e; assert bk == b and a <= ad < a + n, e; return bytes([port.cb(bk), ad & 0xff, ad >> 8])
    mus = [i for i in range(0x67) if ent(cmod, C_MUSIC, i) != ent(corig, C_MUSIC, i)]
    sfx = [i for i in range(0xCF) if ent(cmod, C_SFX, i) != ent(corig, C_SFX, i)]
    assert mus == [0x52, 0x53, 0x5E, 0x5F, 0x62] and sfx == list(range(0xBE, 0xC5)), (mus, sfx)

    for i in (0x52, 0x53):                                   # 銀にも ある 番号：表を 書きかえる
        o = fo(AB, MUSIC) + 3 * i; rom[o:o + 3] = conv(ent(cmod, C_MUSIC, i))

    assert not any(rom[fo(AB, FREE):fo(AB, 0x8000)])
    q = FREE
    def put(bs):
        nonlocal q
        o = fo(AB, q); rom[o:o + len(bs)] = bs; r = q; q += len(bs); return r
    def hook(base, first, tab):
        # ld hl, base / ld a, e / cp first / jr c, .ok / ld hl, tab - 3*first / .ok: add hl, de ×3 / ret
        t = (tab - 3 * first) & 0xFFFF
        return bytes([0x21, base & 0xff, base >> 8, 0x7B, 0xFE, first, 0x38, 0x03, 0x21, t & 0xff, t >> 8,
                      0x19, 0x19, 0x19, 0xC9])
    none = bytes(rom[fo(AB, MUSIC):fo(AB, MUSIC) + 3])         # 曲 0（MUSIC_NONE）
    mt = put(b''.join(conv(ent(cmod, C_MUSIC, i)) if i in mus else none
                      for i in range(N_MUSIC, 0x63)))       # $5D〜$62（使わない 番号は 曲 0 と 同じ）
    st = put(b''.join(conv(ent(cmod, C_SFX, i)) for i in range(0xBE, 0xC5)))
    mh = put(hook(MUSIC, N_MUSIC, mt))
    sh = put(hook(SFX, 0xBE, st))
    assert q <= 0x8000, hex(q)
    for at, h, base in ((0x4B39, mh, MUSIC), (0x4C78, sh, SFX), (0x4CB7, sh, SFX)):
        o = fo(AB, at)
        assert rom[o:o + 6] == bytes([0x21, base & 0xff, base >> 8, 0x19, 0x19, 0x19]), hex(at)
        rom[o:o + 6] = bytes([0xCD, h & 0xff, h >> 8, 0, 0, 0])
    log.append('曲・効果音：赤の 曲 %s・効果音 $BE〜$C4 を $%02X に、足した 表 $3A:$%04X〜$%04X'
               % (' '.join('$%02X' % i for i in mus), port.cb(b), FREE, q))
    return rom
