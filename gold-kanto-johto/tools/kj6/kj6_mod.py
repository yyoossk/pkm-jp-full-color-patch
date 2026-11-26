"""crystal_kj6.gbc：kj5 に 第128弾の MOD 側（8 おつきみ山 B2F の 赤の 隠し道具 2つ）を 当てる。
   つきのいし (18,12) フラグ $A2C、エーテル (33,9) フラグ $A2D（BGEVENT_ITEM）。
   1F の ボール（みずでっぽう）・GivePoke は 金の 側（gold_tutor.py・gold_p128.py）。
   使いかた：MODROOT=… python3 kj6_mod.py kj5.gbc kj6.gbc"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules.setdefault("mapdb", __import__("mapdb"))
import p128_mtmoon as M
from lib import *
from portlib import Space
rom = bytearray(open(sys.argv[1], 'rb').read()); log = []
sp = Space(rom)
ITEM = load_consts(PC + '/constants/item_constants.asm')
me = M.map_events(rom, M.MTB2F); B = me.sb
f, n = bank_free_tail(rom, B); sp.set_area(B, f + 16, B * 0x4000 + 0x4000)
have = {(x, y) for y, x, t, r in me.bgs}
for (x, y), it, fl in (((18, 12), 'MOON_STONE', M.HID_MOON_STONE), ((33, 9), 'ETHER', M.HID_ETHER)):
    assert (x, y) not in have
    me.bgs.append((y, x, 7, ('data', M.w16(fl) + bytes([ITEM[it]]))))
a = Asm(sp.here(B)); a.bank = B
me.write(a, sp)
base = a.base; blob = a.done(); assert sp.put(B, blob) == base
me.install(a)
log.append('おつきみ山 B2F：隠し道具 つきのいし (18,12) %X・エーテル (33,9) %X；イベント %02X:%04X' % (M.HID_MOON_STONE, M.HID_ETHER, B, base))
fix_checksum(rom); open(sys.argv[2], 'wb').write(rom); print('\n'.join(log))
