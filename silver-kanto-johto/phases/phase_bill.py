"""第104弾の のこり（銀版）：
   ・ハナダの ショップ：上下に 歩く 男の人（赤の (3,4)）が クリスタルの 部屋では 店員に 話す 場所（3,3）で 買えない → (4,2) に。
   ・マサキの 家（クリスタル版の マップ、スクリプトは $61）：ピカチュウ版と 同じ 動き。
     ポケモンの マサキは 歩いて 電送マシンに 入って から 消える（主人公が 上に いれば よけて 回る）。
     パソコンで ピカチュウ版と 同じ 間（「チーン」は 銀に ある SFX_SHINE）、マサキが マシンから 出て 歩いて くる、主人公も 歩いて 前へ、そのまま 話が 始まる。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port, gsc, xlat
from gsc import fo, r16

BB = 0x61
BMON_END, PC_END, BHUM = 0x5456, 0x5474, 0x547E
MART = (7, 7)


def w(v): return bytes([v & 0xFF, v >> 8])


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); T = xlat.Tables()
    P = port.Port.__new__(port.Port); P.T = T
    P.CM = cmaps.CMaps(cmod); P.SM = gsc.Maps(bytes(rom[:0x100000]), gsc.PG + '/constants/map_constants.asm'); P.todo = {}
    # ---- ハナダの ショップ
    g, m = P.x_map(*MART)
    gt = fo(0x25, 0x40ED); h = fo(0x25, r16(rom, gt + 2 * (g - 1))) + 9 * (m - 1)
    ao = fo(rom[h], r16(rom, h + 3)); sb = rom[ao + 6]; p = fo(sb, r16(rom, ao + 9)) + 2
    k = rom[p]; p += 1 + 5 * k; k = rom[p]; p += 1 + 8 * k; k = rom[p]; p += 1 + 5 * k; k = rom[p]; p += 1
    spr = P.x_sprite(0x23)
    hit = [p + 13 * i for i in range(k) if rom[p + 13 * i] == spr and (rom[p + 13 * i + 2] - 4, rom[p + 13 * i + 1] - 4) == (3, 4)]
    assert len(hit) == 1, (g, m, hex(spr))
    rom[hit[0] + 1] = 2 + 4; rom[hit[0] + 2] = 4 + 4
    # ---- マサキの 家
    o1 = fo(BB, BMON_END); o2 = fo(BB, PC_END)
    assert rom[o1:o1 + 6] == bytes.fromhex('6d0233350890') and rom[o2:o2 + 10] == bytes.fromhex('841f00856e0333360890')
    sfx = lambda n: T.g_sfx['SFX_SHINE' if n == 'SFX_GLASS_TING' else n]      # 銀に GLASS_TING が ないので SHINE
    s = rom[fo(BB, 0x4000):fo(BB, 0x8000)]; base = 0x4000 + len(s.rstrip(b'\0')) + 4
    b = bytearray(); lab = {}; fix = []
    def L(n): lab[n] = base + len(b)
    def ref(n): fix.append((len(b), n)); b.extend(b'\0\0')
    L('mon'); b += bytes([0x1C, 0x09, 0x06, 0x00]); ref('around')                    # readvar VAR_FACING / ifequal DOWN
    b += bytes([0x68, 0x02]); ref('up3'); b += b'\x03'; ref('gone')
    L('around'); b += bytes([0x68, 0x02]); ref('round')
    L('gone'); b += bytes([0x6D, 0x02, 0x33]) + w(0x835) + b'\x90'
    L('up3'); b += bytes([0x0D, 0x0D, 0x0D, 0x47])
    L('round'); b += bytes([0x0F, 0x0D, 0x0D, 0x0E, 0x0D, 0x47])
    L('pc')
    for pz, sn in ((16, 'SFX_GLASS_TING'), (40, 'SFX_WARP_TO'), (24, 'SFX_GLASS_TING'), (16, 'SFX_ITEM')):
        b += bytes([0x8A, pz, 0x84]) + w(sfx(sn)) + b'\x85'
    b += bytes([0x71, 0x03, 1 + 4 - 4, 2 + 4 - 4])                                    # moveobject 3, 1, 2
    b += bytes([0x6E, 0x03, 0x33]) + w(0x836) + bytes([0x8A, 4])
    b += bytes([0x68, 0x03]); ref('out'); b += bytes([0x68, 0x00]); ref('right3')
    b += bytes([0x75, 0x03, 0x00, 0x75, 0x00, 0x01, 0x03]) + w(BHUM)
    L('out'); b += bytes([0x0C, 0x0F, 0x0F, 0x0F, 0x0C, 0x47])
    L('right3'); b += bytes([0x0F, 0x0F, 0x0F, 0x47])
    for off, n in fix: b[off:off + 2] = w(lab[n])
    assert base + len(b) <= 0x8000
    rom[fo(BB, base):fo(BB, base) + len(b)] = b
    rom[o1:o1 + 6] = b'\x03' + w(lab['mon']) + b'\x90\x90\x90'
    rom[o2:o2 + 10] = b'\x03' + w(lab['pc']) + b'\x90' * 7
    log.append('ハナダの ショップの 男の人 (4,2)・マサキの 家の 動き（$%02X:$%04X）' % (BB, base))
    return rom
