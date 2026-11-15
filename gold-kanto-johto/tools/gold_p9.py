"""金に 第1〜9弾の マップを入れる（試作）"""
import sys, zlib
sys.path.insert(0, '/home/claude/work/scripts')
from c2g import *
from changed import changed_maps
VAN = open('/home/claude/roms/Pocket Monsters - Crystal Version (Japan).gbc', 'rb').read()
MOD = open('/home/claude/work/ref/crystal_p9.gbc', 'rb').read()
g = bytearray(open('/home/claude/work/ref/kin_late.gbc', 'rb').read())
g += bytes(0x400000 - len(g)); g[0x148] = 0x07
# 4MB：バンク $80 以降のスクリプトから もどるとき 上のビットを消さない（クリスタル版 第67弾と同じ）
o = 0x25 * 0x4000 + 0x7389 - 0x4000; assert g[o + 3:o + 5] == b'\xf6\x80'; g[o + 4] = 0x00
o = 0x25 * 0x4000 + 0x7a16 - 0x4000; assert g[o + 0x13:o + 0x15] == b'\xe6\x7f'; g[o + 0x14] = 0xff
# はじめの場所：スポーン0 を レッドの家2F に（クリスタル版 05:SpawnPoints と同じ）
o = 0x05 * 0x4000 + 0x5286 - 0x4000; assert g[o:o + 2] == b'\x18\x07'; g[o:o + 2] = b'\x0d\x04'
# シーンの表：主人公の家1F の シーンの変数を レッドの家1F で使う（クリスタル版 13:506A と同じ）
o = 0x9404c + 12; assert g[o:o + 2] == b'\x18\x06'; g[o:o + 2] = b'\x0d\x03'
# 秘伝わざのバッジをカントーのバッジに（クリスタル版 バンク03 と同じ。金のエンジンフラグの番号で）
for off, old, new in ((0xc819, 27, 35), (0xc949, 26, 34), (0xc9c3, 29, 38), (0xcab8, 29, 38), (0xcb24, 31, 36),
                      (0xce23, 28, 37), (0xcf3f, 28, 37), (0xd43c, 27, 35)):
    assert g[off - 1] == 0x11 and g[off] == old and g[off + 1] == 0, hex(off); g[off] = new
# 名前の候補：ゴールド → サトシ（クリスタル版 22:42DD と同じ）
o = 0x629d; assert g[o:o + 17] == bytes.fromhex('09e3a613509aa88650929184508f858b50'), g[o:o + 20].hex()
g[o:o + 17] = bytes.fromhex('8a938b509aa88650929184508f858b5050')
names = [x[0] for x in changed_maps(VAN, MOD)] if len(sys.argv) < 2 else sys.argv[1].split(',')
cm = {m['name']: m for m in maplist(MOD, CMGP, 'pokecrystal')}
gm = {m['name']: m for m in maplist(g, GMGP, 'pokegold')}
E = Emit(g)
walks = {}
for nm in names:
    W = Walk(MOD)
    try: at = W.map(cm[nm]['attr'], nm); W.run()
    except Exception as e: print('とばす', nm, e); continue
    if nm not in gm: print('金にない', nm); continue
    walks[nm] = (W, at)
allblobs = {}
for nm, (W, at) in walks.items(): allblobs.update(W.blobs)
for k, b in allblobs.items(): E.place(k, b)
for nm, (W, at) in walks.items(): emit_map(E, W, at, nm, cm[nm]['hdr'], MOD, g, gm, cm)
for k, b in allblobs.items(): E.write(k, b)
finish_maps(E, MOD, g, cm, gm)
s = (sum(g) - g[0x14E] - g[0x14F]) & 0xFFFF; g[0x14E] = s >> 8; g[0x14F] = s & 0xFF
open('/home/claude/work/out/gold_p9.gbc', 'wb').write(g)
print('maps', len(walks), 'banks', {('%02X' % k): ('%02X' % v) for k, v in E.bankmap.items()})
print('読みかえできない:', len(E.X.miss)); print('\n'.join(sorted(set(E.X.miss))[:60]))
print('ポインター:', len(E.homemiss)); print('\n'.join(sorted(set(E.homemiss))[:30]))
