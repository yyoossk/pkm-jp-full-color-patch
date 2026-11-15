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
from consts import all_tables as _at
_C = _at('pokecrystal'); KL, KE = _C['landmark']['KANTO_LANDMARK'], _C['landmark']['KANTO_LANDMARK_LAST']
JOHTO_SIDE = {'Route26', 'Route27', 'TohjoFalls', 'Route26HealHouse', 'DayOfWeekSiblingsHouse', 'Route27SandstormHouse'}
KANTO = [m['name'] for m in maplist(MOD, CMGP, 'pokecrystal') if KL <= MOD[m['hdr'] + 5] <= KE and m['name'] not in JOHTO_SIDE]
names = sorted(set([x[0] for x in changed_maps(VAN, MOD)]) | set(KANTO)) if len(sys.argv) < 2 else sys.argv[1].split(',')
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
# MOD が変えていない カントーのマップで、クリスタルにしかない しくみ（女の子の主人公・モバイル・スイクン など）を
# 使っているものは 金の マップのまま にする
CHG = set(x[0] for x in changed_maps(VAN, MOD))
def _misses(W, at, nm):
    X = Xlat(); ctx = nm
    for ob in at['objs']: X.sprite(ob[0], ctx); X.event(ob[11] | ob[12] << 8, ctx)
    for wv in at['warps']: X.mapid((wv[3], wv[4]), ctx)
    for k, b in W.blobs.items():
        for off, t, sem, name in b['fix']:
            o = fo(b['bank'], b['addr']) + off; v = MOD[o] if t == 'db' else MOD[o] | MOD[o + 1] << 8
            f = {'event_flag': X.event, 'engine_flag': X.engine, 'special': X.special, 'std': X.std, 'music_pointer': X.music,
                 'sound_pointer': X.sfx, 'sprite': X.sprite}.get(sem)
            if f: f(v, ctx)
            if t == 'map_id': X.mapid((MOD[o], MOD[o + 1]), ctx)
    return X.miss
for nm in list(walks):
    if nm not in CHG:
        ms = _misses(*walks[nm], nm)
        if ms: print('金のまま:', nm, ms[0]); del walks[nm]
allblobs = {}
for nm, (W, at) in walks.items(): allblobs.update(W.blobs)
for k, b in allblobs.items(): E.place(k, b)
for nm, (W, at) in walks.items(): emit_map(E, W, at, nm, cm[nm]['hdr'], MOD, g, gm, cm)
for k, b in allblobs.items(): E.write(k, b)
finish_maps(E, MOD, g, cm, gm)
# ---- トレーナーの手持ち：読むコード（0E:$5511-$595B）ごと 新しいバンクへ（クリスタル版 第13弾と同じ考え）
from trainers import merged
import re as _re
TB = E.next_bank; E.next_bank += 1
src = 0x0E * 0x4000 - 0x4000; dst = TB * 0x4000 - 0x4000
g[dst + 0x5511:dst + 0x595C] = g[src + 0x5511:src + 0x595C]
L = merged(VAN, MOD, bytes(g[:0x200000]))
a = 0x595C + 2 * 66; tbl = bytearray(); body = bytearray()
for cls in L:
    tbl += (a + len(body)).to_bytes(2, 'little'); body += b''.join(cls)
assert 0x595C + len(tbl) + len(body) <= 0x8000, 'トレーナーのデータが入らない'
g[dst + 0x595C:dst + 0x595C + len(tbl)] = tbl; g[dst + a:dst + a + len(body)] = body
n = 0
for m in list(_re.finditer(rb'\x21(..)\x3e\x0e\xcf', bytes(g[:0x200000]), _re.S)):
    ad = m.group(1)[0] | m.group(1)[1] << 8
    if 0x5511 <= ad < 0x595C: g[m.start() + 4] = TB; n += 1
assert n == 12, n
for o in (0x2aba9, 0x2abb1, 0x2abbd, 0x2abc7, 0x2abea, 0x2ac04):   # RandomPhoneMon の ld a, BANK(TrainerGroups)
    assert g[o:o + 3] == b'\x3e\x0e\xcd'; g[o + 1] = TB
print('トレーナー：バンク %02X、%d バイト' % (TB, len(body)))
s = (sum(g) - g[0x14E] - g[0x14F]) & 0xFFFF; g[0x14E] = s >> 8; g[0x14F] = s & 0xFF
open('/home/claude/work/out/gold_p9.gbc', 'wb').write(g)
print('maps', len(walks), 'banks', {('%02X' % k): ('%02X' % v) for k, v in E.bankmap.items()})
print('読みかえできない:', len(E.X.miss)); print('\n'.join(sorted(set(E.X.miss))[:60]))
print('ポインター:', len(E.homemiss)); print('\n'.join(sorted(set(E.homemiss))[:30]))
