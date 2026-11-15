"""トキワのもり（と ディグダのあな・ふたごじま）の 曲を 赤と 同じに（第102弾の 銀版）：赤フルカラーの Music_Dungeon2
   （赤の バンク$1F の 曲 $E4）を クリスタル・金銀の 音の しくみに 変えて（tools/gen1audio.py。赤の ドラム 9〜13 ＝ ドラムの 組 1 の 2〜6）
   曲 $52 に 入れ、その マップの 曲に。データは $A0 の 空き。赤フルカラーの ROM は AKAFC（ない ときは この 直しを しない）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port, gsc
from gsc import fo, r16
from gen1audio import Song

AKAFC = os.environ.get('AKAFC', '/home/claude/in/aka/akafc.gbc')
MUSIC_TABLE, MUS_ID, AUD_BANK = 0x506E, 0x52, 0xA0
RED_SFX_HEADERS, MUSIC_DUNGEON2 = 0x6EBF, 0xE4
MAPS = [(26, 84), (26, 86), (26, 110), (26, 149), (26, 63), (26, 64), (26, 65), (26, 66), (26, 67)]


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    F = open(AKAFC, 'rb').read()
    song = Song(F, 0x1F, RED_SFX_HEADERS + 3 * MUSIC_DUNGEON2, {9: 2, 10: 3, 11: 4, 12: 5, 13: 6}, 1)
    s = rom[fo(AUD_BANK, 0x4000):fo(AUD_BANK, 0x8000)]; base = 0x4000 + len(s.rstrip(b'\0')) + 16
    h, data = song.build(base)
    assert base + len(data) <= 0x8000
    rom[fo(AUD_BANK, base):fo(AUD_BANK, base) + len(data)] = data
    t = fo(0x3A, MUSIC_TABLE) + 3 * MUS_ID; rom[t:t + 3] = bytes([AUD_BANK, h & 0xFF, h >> 8])
    cmod = open(cmaps.CMOD, 'rb').read()
    P = port.Port.__new__(port.Port)
    P.CM = cmaps.CMaps(cmod); P.SM = gsc.Maps(bytes(rom[:0x100000]), gsc.PG + '/constants/map_constants.asm'); P.todo = {}
    gt = fo(0x25, 0x40ED); out = []
    for cg, cm in MAPS:
        g, m = P.x_map(cg, cm); hd = fo(0x25, r16(rom, gt + 2 * (g - 1))) + 9 * (m - 1)
        rom[hd + 6] = MUS_ID; out.append('%d-%d' % (g, m))
    log.append('トキワのもりの 曲（赤の Music_Dungeon2 → 曲 $%02X、$%02X:$%04X %dバイト）：%s' % (MUS_ID, AUD_BANK, h, len(data), ' '.join(out)))
    return rom
