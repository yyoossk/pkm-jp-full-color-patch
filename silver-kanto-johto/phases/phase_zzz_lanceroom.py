"""チャンピオンの へや（ワタルの へや (16,7)）：クリスタル版の ブロックの 並びを 写したのに、タイルセットは 銀の
   チャンピオンの へや（17）で ブロックの 中身が ちがう ため、へやの 上・まわりが 文字の 点（゛）の 絵に なって いた
   （チャンピオンに 勝った あと 上へ 歩くと よく 見える）。クリスタルの タイルセットは 銀の 読みこみと 形が ちがうので、
   ブロックの 並びを 銀の もとの もの（同じ 大きさ 5×12、入口・出口・通路も 同じ）に もどす。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import gsc
from gsc import fo


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    g1 = open(os.path.join(H, 'roms', 'gin1.gbc'), 'rb').read()
    G = gsc.Maps(g1, gsc.PG + '/constants/map_constants.asm')
    S = gsc.Maps(bytes(rom), gsc.PG + '/constants/map_constants.asm')
    k = G.id['LANCES_ROOM']
    ag = G.attributes(k); a = S.attributes(k)
    assert (ag['height'], ag['width']) == (a['height'], a['width']) and S.header(k)['tileset'] == 17
    n = ag['height'] * ag['width']; src = fo(ag['blocks_bank'], ag['blocks'])
    assert rom[src:src + n] == g1[src:src + n]                  # 銀の もとの 並びが そのまま 残って いる
    o = a['off']
    rom[o + 3] = ag['blocks_bank']; rom[o + 4] = ag['blocks'] & 0xff; rom[o + 5] = ag['blocks'] >> 8
    log.append('  ワタルの へや：ブロックの 並びを 銀の もとの もの（$%02X:$%04X）に' % (ag['blocks_bank'], ag['blocks']))
    return rom
