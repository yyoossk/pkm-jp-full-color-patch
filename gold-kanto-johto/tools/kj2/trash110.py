"""第110弾 1（クチバジムの ゴミばこ の 文と 音）を crystal_kj2 に：文の はじまりを 1バイト うしろ、まちがい＝SFX_WRONG、
   2つめ＝扉の 音を 文の あと・ボタン待ちの 前に"""
import sys
sys.path.insert(0, '/home/claude/yyoossk/crystal-satoshi-mod/tools')
from lib import *
rom = bytearray(open(sys.argv[1], 'rb').read())
B = 0x63
def at(a): return fo(B, a)
can = bytes.fromhex('0e63ec7106010c730602177306031a73523a73')
i = rom.find(can, at(0x4000), at(0x8000)); assert i == at(0x72F9), hex(i)
assert rom[at(0x730C):at(0x7317)] == bytes.fromhex('474c4f738411008553499052')[:11]
assert rom[at(0x7317):at(0x731A)] == bytes.fromhex('52cc73')
assert rom[at(0x731A):at(0x7329)] == bytes.fromhex('474c9a73534979040401841f007b85')
assert rom[at(0x734F)] == 0 and rom[at(0x7350)] == 0 and rom[at(0x739A)] == 0x0F and rom[at(0x73CC)] == 0x0F
rom[at(0x730E)] = 0x50                                   # c1: writetext $7350
f, n = bank_free_tail(rom, B); f += 2
def here(): return 0x4000 + f % 0x4000
c2 = here(); blk = bytes.fromhex('474ccd73841900855349 90'.replace(' ', ''))
rom[f:f + len(blk)] = blk; f += len(blk)
c3 = here(); blk = bytes.fromhex('474c9b73841f00855349790404017b90')
rom[f:f + len(blk)] = blk; f += len(blk)
o = at(0x72F9)
rom[o + 7:o + 9] = bytes([c2 & 0xFF, c2 >> 8]); rom[o + 11:o + 13] = bytes([c3 & 0xFF, c3 >> 8])
fix_checksum(rom); open(sys.argv[2], 'wb').write(rom)
print('trash cans: c2 63:%04X c3 63:%04X' % (c2, c3))
