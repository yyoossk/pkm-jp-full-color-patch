"""つり（第57弾：151匹そろう版の カントーの つり、第28弾：サファリの つりざお）：
   クリスタル版の つりの 処理（$47:$7174。カントーの 31 マップは キットの ポケモン、ほかは $6E:$5034 → サファリ、
   それ以外は もとの Fish）を 銀でも 使う。$47 は 銀の $C7（まるごと 写して ある）。
     ・銀の つりの 所（$03:$524D の farcall Fish $24:$68C9）→ farcall $C7:$7174。
     ・処理の WRAM・ホームの 関数は asmport で、マップの 表（$47:$71DB：グループ, 番号, つりの 組）は 銀の マップの 番号に。"""
import os, sys, pickle
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port, gsc, asmport
from gsc import fo, r16

SITE = 0x524D
FISH = (0x24, 0x68C9)
MAPS = 0x71DB


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    g1 = open(os.path.join(H, 'roms', 'gin1.gbc'), 'rb').read()
    P = port.Port.__new__(port.Port)
    P.CM = cmaps.CMaps(cmod); P.SM = gsc.Maps(bytes(rom[:0x100000]), gsc.PG + '/constants/map_constants.asm'); P.todo = {}
    B = port.cb(0x47)
    o = fo(B, MAPS); n = 0
    while rom[o] != 0xFF:
        g, m = P.x_map(cmod[fo(0x47, MAPS) + 3 * n], cmod[fo(0x47, MAPS) + 3 * n + 1])
        rom[o] = g; rom[o + 1] = m; o += 3; n += 1
    asmport.FAR_EXTRA[(0x24, 0x6975)] = FISH
    wm = dict(pickle.load(open(os.path.join(ctx['B'], 'wram_map.pkl'), 'rb'))); wm.update(asmport.WRAM_EXTRA)
    TR = asmport.Translator(cmod, corig, g1, wm, asmport.Home(corig, g1), log); TR.wm = wm
    TR.routine(rom, 0x47, 0x7174, '47:7174'); TR.routine(rom, 0x6E, 0x5034, '6E:5034')
    assert not TR.unres, TR.unres
    o = fo(B, 0x7193); assert rom[o:o + 6] == bytes([0x3E, 0x6E, 0x21, 0x34, 0x50, 0xCF])
    o = fo(3, SITE); assert rom[o:o + 6] == bytes([0x3E, FISH[0], 0x21, FISH[1] & 0xff, FISH[1] >> 8, 0xCF])
    rom[o:o + 6] = bytes([0x3E, B, 0x21, 0x74, 0x71, 0xCF])
    if P.todo: log.append('TODO %s' % P.todo)
    log.append('つり：クリスタル版の 処理（$%02X:$7174、カントーの %d マップ）' % (B, n))
    return rom
