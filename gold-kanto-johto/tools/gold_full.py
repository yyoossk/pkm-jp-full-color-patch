"""金に 第1〜9弾の マップを入れる（試作）"""
import sys, zlib
sys.path.insert(0, '/home/claude/work/scripts')
from c2g import *
from changed import changed_maps
VAN = open('/home/claude/roms/Pocket Monsters - Crystal Version (Japan).gbc', 'rb').read()
MOD = open('/home/claude/work/ref/crystal_kj.gbc', 'rb').read()
VAN = VAN + bytes(len(MOD) - len(VAN))
g = bytearray(open('/home/claude/work/ref/kin_late.gbc', 'rb').read())
g += bytes(0x400000 - len(g)); g[0x148] = 0x07
# 4MB：バンク $80 以降のスクリプトから もどるとき 上のビットを消さない（クリスタル版 第67弾と同じ）
o = 0x25 * 0x4000 + 0x7389 - 0x4000; assert g[o + 3:o + 5] == b'\xf6\x80'; g[o + 4] = 0x00
o = 0x25 * 0x4000 + 0x7a16 - 0x4000; assert g[o + 0x13:o + 0x15] == b'\xe6\x7f'; g[o + 0x14] = 0xff
# LoadMetatiles の 128 番より 後の ブロックが 前に もどる バグ（金の 追加機能パッチ bugfix 48 と 同じ。クリスタル版の 赤の 町が 使う）
assert g[0x1FAF:0x1FB6] == bytes.fromhex('876f2600292929'); g[0x1FAF:0x1FB6] = bytes.fromhex('6f260029292929')
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
E = Emit(g)
import gold_specials; gold_specials.register()
# ---- 第11弾の 土台：新しい タイルセット・グループ 26 の 14〜149 番
import gold_p11, gold_safari, c2g as _c2g
_l11 = []
_p11 = gold_p11.apply(g, MOD, E, _l11)
# ---- 第15弾の 土台：イベントフラグ $800〜
import gold_flags
FB = E.next_bank; E.next_bank += 1
gold_flags.apply(g, FB, 0x4000, _l11); print('\n'.join(_l11))
cm = {m['name']: m for m in maplist(MOD, CMGP, 'pokecrystal')}
gm = {m['name']: m for m in maplist(g, GMGP, 'pokegold')}
G26 = []
for n in range(gold_p11.G26_FIRST, gold_p11.G26_N + 1):
    nm = 'G26_%03d' % n; G26.append(nm)
    ch = 0x94000 + 0x4D75 - 0x4000 + 9 * (n - 1)
    cm[nm] = dict(name=nm, group=26, num=n, hdr=ch, attr=fo(MOD[ch], MOD[ch + 3] | MOD[ch + 4] << 8))
    gm[nm] = dict(name=nm, group=26, num=n, hdr=_p11['hdr0'] + 9 * (n - gold_p11.G26_FIRST), attr=0)
    _c2g.CMAP[(26, n)] = nm; _c2g.GMAP[nm] = (26, n)
KANTO = [m['name'] for m in maplist(MOD, CMGP, 'pokecrystal') if KL <= MOD[m['hdr'] + 5] <= KE and m['name'] not in JOHTO_SIDE]
KANTO += [nm for nm in G26 if KL <= MOD[cm[nm]['hdr'] + 5] <= KE]
names = sorted(set(KANTO))   # ジョウトは 金のまま（MOD だけの 変更は フェーズごとに 入れる） if len(sys.argv) < 2 else sys.argv[1].split(',')
walks = {}
for nm in names:
    W = Walk(MOD)
    try: at = W.map(cm[nm]['attr'], nm); W.run()
    except Exception as e: print('とばす', nm, e); continue
    if nm not in gm: print('金にない', nm); continue
    walks[nm] = (W, at)
# MOD が変えていない カントーのマップで、クリスタルにしかない しくみ（女の子の主人公・モバイル・スイクン など）を
# 使っているものは 金の マップのまま にする
CHG = set()   # 完成版では すべて 調べる
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
            if sem == 'opcode' and MOD[o] not in (0x9F, 0xA0, 0xA1, 0xA2): X._m('命令 %02X' % MOD[o], MOD[o], ctx)
    return X.miss
for nm in list(walks):
    if nm not in CHG:
        ms = _misses(*walks[nm], nm)
        if ms: print('金のまま:', nm, ms[0]); del walks[nm]
# 入れない マップへ つながる マップも 入れない（グループ 26 の 新しい マップは 金に かわりが ない）
# また、まだ 金に うつしていない asm（callasm など）を 指す マップも 入れない（gold_asm.PORTED に あるものは 入れる）
import gold_asm
def _unplaced(W, keys):
    out = []
    for k_, b in W.blobs.items():
        for off, t, sem, name in b['fix']:
            o_ = fo(b['bank'], b['addr']) + off
            if t == 'dw' and ('pointer' in sem or sem == 'data'):
                v = MOD[o_] | MOD[o_ + 1] << 8
                if v >= 0x4000 and v < 0x8000 and v != 0xFFFF and (b['bank'], v) not in keys: out.append((b['bank'], v))
            elif t == 'dba':
                bb, aa = MOD[o_], MOD[o_ + 1] | MOD[o_ + 2] << 8
                if aa >= 0x4000 and (bb, aa) not in keys: out.append((bb, aa))
    return out
while True:
    keys = set(gold_asm.PORTED) | gold_safari.CALLASM
    for nm, (W, at) in walks.items(): keys |= set(W.blobs)
    drop = [(nm, '未移植の asm %02X:%04X' % _unplaced(W, keys)[0]) for nm, (W, at) in walks.items() if _unplaced(W, keys)]
    for nm, why in drop: print('金のまま（' + why + '）:', nm); del walks[nm]
    bad = set(G26) - set(walks)
    drop = []
    for nm, (W, at) in walks.items():
        tg = [(wv[3], wv[4]) for wv in at['warps']] + [(at['connections'][i], at['connections'][i + 1]) for i in range(0, len(at['connections']), 12)]
        for k_, b in W.blobs.items():
            for off, t, sem, name in b['fix']:
                if t == 'map_id': o_ = fo(b['bank'], b['addr']) + off; tg.append((MOD[o_], MOD[o_ + 1]))
        hit = [x for x in tg if _c2g.CMAP.get(x) in bad]
        if hit: drop.append((nm, _c2g.CMAP.get(hit[0])))
    if not drop:
        if not any(_unplaced(W, keys) for W, at in walks.values()): break
        continue
    for nm, why in drop: print('金のまま（入れない マップへ つながる）:', nm, why); del walks[nm]
allblobs = {}
for nm, (W, at) in walks.items(): allblobs.update(W.blobs)
for k, b in allblobs.items(): E.place(k, b)
_la = []; gold_asm.apply(E, MOD, g, _la, cm); gold_safari.apply(g, MOD, E, _la); gold_specials.apply(g, MOD, E.next_bank, _la); E.next_bank += 1; print('\n'.join(_la))
for nm, (W, at) in walks.items(): emit_map(E, W, at, nm, cm[nm]['hdr'], MOD, g, gm, cm)
for k, b in allblobs.items(): E.write(k, b)
finish_maps(E, MOD, g, cm, gm)
# ---- トレーナー：読むコード（0E:$5511-$595B）ごと 新しいバンクへ（クリスタル版 第13弾と同じ考え）。手持ちは 第10弾で 入れる
import re as _re
TB = E.next_bank; E.next_bank += 1
src = 0x0E * 0x4000 - 0x4000; dst = TB * 0x4000 - 0x4000
g[dst + 0x5511:dst + 0x595C] = g[src + 0x5511:src + 0x595C]
n = 0
for m in list(_re.finditer(rb'\x21(..)\x3e\x0e\xcf', bytes(g[:0x200000]), _re.S)):
    ad = m.group(1)[0] | m.group(1)[1] << 8
    if 0x5511 <= ad < 0x595C: g[m.start() + 4] = TB; n += 1
assert n == 12, n
for o in (0x2aba9, 0x2abb1, 0x2abbd, 0x2abc7, 0x2abea, 0x2ac04):   # RandomPhoneMon の ld a, BANK(TrainerGroups)
    assert g[o:o + 3] == b'\x3e\x0e\xcd'; g[o + 1] = TB
# ---- 第10弾：トレーナーの種類 67〜79（名前・絵・色・DV・属性・ジムリーダーの表・手持ち）
import gold_p10
NB = E.next_bank; E.next_bank += 1
_log = []
gold_p10.apply(g, VAN, MOD, TB, NB, _log)
print('トレーナー：バンク %02X、第10弾 バンク %02X' % (TB, NB)); print('\n'.join(_log))
import gold_p52
_l52 = []; gold_p52.apply(g, MOD, E.next_bank, TB, _l52); E.next_bank += 1; print('\n'.join(_l52))
# ---- 野生（第12弾〜：カントーの 表は クリスタル版の もの）
import gold_wild
import os
if not os.environ.get("NOWILD"): _lw = []; gold_wild.apply(g, MOD, E, E.X, _lw); print('\n'.join(_lw))
# ---- 第12弾ほか：大事な どうぐ
import gold_items
_li = []; gold_items.apply(g, MOD, E, _li); print('\n'.join(_li))
# ---- シーンの 変数の 表
import gold_scenes
_ls = []; gold_scenes.apply(g, MOD, VAN, E, set(walks), _ls); print('\n'.join(_ls))
# ---- 第13弾：ゆうれい戦
import gold_ghost
_lg = []; gold_ghost.apply(g, MOD, E, _lg); print('\n'.join(_lg))
import gold_engine
_le = []; gold_engine.apply(g, _le, MOD); print('\n'.join(_le))
import gold_sprites
_lsp = []; gold_sprites.apply(g, E.next_bank, _lsp); E.next_bank += 1; print('\n'.join(_lsp))
s = (sum(g) - g[0x14E] - g[0x14F]) & 0xFFFF; g[0x14E] = s >> 8; g[0x14F] = s & 0xFF
open('/home/claude/work/out/gold_full.gbc', 'wb').write(g)
print('maps', len(walks), 'banks', {('%02X' % k): ('%02X' % v) for k, v in E.bankmap.items()})
print('読みかえできない:', len(E.X.miss))
from collections import Counter
for k, v in Counter(m.split('（')[0] for m in E.X.miss).most_common(): print(v, k)
print('MISSLIST'); print('\n'.join(sorted(set(E.X.miss))))
print('ポインター:', len(E.homemiss)); print('\n'.join(sorted(set(E.homemiss))))
# どのマップの かたまりか（未配置の ポインターを 持つもの）
_own = {}
for nm, (W, at) in walks.items():
    for k in W.blobs: _own.setdefault(k, []).append(nm)
_um = {}
for m in E.homemiss:
    mm = _re.search(r'script ([0-9A-F]{2}):([0-9A-F]{4})', m)
    if mm:
        k = (int(mm.group(1), 16), int(mm.group(2), 16))
        _um.setdefault(m.split('（')[0], set()).update(_own.get(k, ['?']))
for k, v in sorted(_um.items()): print(k, sorted(v))
