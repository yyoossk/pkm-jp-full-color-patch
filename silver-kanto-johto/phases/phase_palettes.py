"""タイルセットの 色（第44・92弾 など）：クリスタル版の 色の 処理（$6A:$74AF〜。タイルセットごとの 表、
   カントーの 町の 時間ごとの 色、暗い ほら穴）を 銀でも 使う。
   銀の LoadMapPals（$02:$75CF）の はじめで farcall し、色を 入れたら 人の 色の 所（$02:$760F）へ とぶ。
   クリスタルの wBGPals1（WRAM バンク5 の $D000〜）は 銀では $C200〜。"""
import os, sys, pickle
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, asmport, wramxl
from gsc import fo

LMP, OBJPART, FREE2 = 0xB5CF, 0x760F, 0x7F29


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    g1 = open(os.path.join(H, 'roms', 'gin1.gbc'), 'rb').read()
    Hm = asmport.Home(corig, g1)
    wm = dict(pickle.load(open(os.path.join(ctx['B'], 'wram_map.pkl'), 'rb')))
    for a in range(0xD000, 0xD100): wm[a] = 0xC200 + (a - 0xD000)        # 色の 処理の 中では パレット
    wm.update({0xD834: 0xD55B, 0xD1CA: 0xD074, 0xD1CB: 0xD075})
    TR = asmport.Translator(cmod, corig, g1, wm, Hm, log)
    TR.wm = wm; TR.nosvbk = True
    TR.routine(rom, 0x6A, 0x74AF, 'palettes')
    # 銀の フック
    assert rom[LMP:LMP + 3] == bytes([0xFA, 0x75, 0xD0]) and not any(rom[fo(2, FREE2):fo(2, FREE2) + 16])
    hk = bytes([0x3E, 0x6A, 0x21, 0xAF, 0x74, 0xCF, 0x38, 0x04, 0xFA, 0x75, 0xD0, 0xC9, 0xE1, 0xC3,
                OBJPART & 0xff, OBJPART >> 8])
    rom[fo(2, FREE2):fo(2, FREE2) + len(hk)] = hk
    rom[LMP:LMP + 3] = bytes([0xCD, FREE2 & 0xff, FREE2 >> 8])
    # タイルごとの 色の 表（palmap）：タイルセット 37〜 は $93（クリスタルの $13）から GetFarByte で 読む
    GETFARBYTE = 0x30E4
    a = FREE2 + len(hk)
    def put(code):
        nonlocal a
        o = fo(2, a); assert not any(rom[o:o + len(code)]); rom[o:o + len(code)] = code; r = a; a += len(code); return r
    def rd(tail):
        return bytes([0xFA, 0x74, 0xD0, 0xFE, 37, 0x38, 0x06 + len(tail), 0x3E, 0x93, 0xCD, GETFARBYTE & 0xff, GETFARBYTE >> 8]) + \
            tail + bytes([0xC9, 0x7E]) + tail + bytes([0xC9])
    r1 = put(rd(bytes([0xE6, 0x0F]))); r2 = put(rd(bytes([0xCB, 0x37, 0xE6, 0x0F])))
    n = 0
    for o in range(fo(2, 0x4000), fo(2, 0x8000) - 5):
        if rom[o:o + 9] == bytes([0xFA, 0xC2, 0xD0, 0xCE, 0x00, 0x67, 0x7E, 0xE6, 0x0F]):
            rom[o + 6:o + 9] = bytes([0xCD, r1 & 0xff, r1 >> 8]); n += 1
        elif rom[o:o + 11] == bytes([0xFA, 0xC2, 0xD0, 0xCE, 0x00, 0x67, 0x7E, 0xCB, 0x37, 0xE6, 0x0F]):
            rom[o + 6:o + 11] = bytes([0xCD, r2 & 0xff, r2 >> 8, 0, 0]); n += 1
    assert n == 4, n
    log.append('タイルセットの 色：$6A:$74AF を フック' + ('（TODO %s）' % TR.unres if TR.unres else ''))
    return rom
