import sys, pickle, glob
sys.path.insert(0, '/home/claude/yyoossk/crystal-satoshi-mod/tools')
from lib import *
import portmaps as PM
from portlib import lz, Space
import akapalmap as A
OUT = __import__('os').environ.get('MODROOT', '/home/claude/yyoossk/crystal-satoshi-mod') + '/out'
paths = [OUT + '/aka_m%s.pkl' % m for m in ('80', '81', '82', '83', '8b')] + sorted(glob.glob(OUT + '/akd8[0-3b]_*.pkl'))
rom = bytearray(open(sys.argv[1], 'rb').read())
TS = PM.Tilesets(rom, Space(rom))
G26_END = None
from build_phase17 import US
G = US.get().groups()
hd = G[26 - 1] + 9 * (124 - 1)
tid = rom[hd + 1]; e = TS.entry(tid)
print('chief house tileset', tid, e.hex())
# palette copy routine: find hook in bank 12 'cp tid / jr z,+3' then farcall data_bank:cp
b12 = bytes(rom[0x12 * 0x4000:0x13 * 0x4000])
i = b12.find(bytes([0xFE, tid, 0x28, 0x03, 0xC3]))
assert i >= 0 and b12.find(bytes([0xFE, tid, 0x28, 0x03, 0xC3]), i + 1) < 0
db_, cpa = b12[i + 8], b12[i + 10] | b12[i + 11] << 8
cp = fo(db_, cpa); assert rom[cp] == 0x21
pa = fo(db_, rom[cp + 1] | rom[cp + 2] << 8)
pm = fo(0x13, e[13] | e[14] << 8)
old_pm = bytes(rom[pm:pm + 0x70])
class T: pass
t = T(); t.palmap = old_pm
A.apply(t, paths)
gfx = lz(t.gfx_raw)
go = fo(e[0], e[1] | e[2] << 8)
from gsclz import unlz
print('old gfx lz bytes at', hex(go))
# 新しい 絵：同じ バンクの あとの あきへ（なければ 末尾）
gb = e[0]; f, n = bank_free_tail(rom, gb)
if n < len(gfx) + 16:
    gb = next(b for b in range(0x40, 0x100) if bank_free_tail(rom, b)[1] > len(gfx) + 64)
    f, n = bank_free_tail(rom, gb)
f += 1
rom[f:f + len(gfx)] = gfx; ga = 0x4000 + f % 0x4000
rom[TS.tab + 15 * tid] = gb; rom[TS.tab + 15 * tid + 1] = ga & 0xFF; rom[TS.tab + 15 * tid + 2] = ga >> 8
rom[pa:pa + 64] = t.pals
rom[pm:pm + 0x70] = t.palmap
fix_checksum(rom)
open(sys.argv[2], 'wb').write(rom)
print('mansion: gfx %02X:%04X, pals %X, palmap %X' % (gb, ga, pa, pm))
