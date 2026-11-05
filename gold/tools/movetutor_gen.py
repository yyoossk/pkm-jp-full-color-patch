"""クリスタルの 技教え（かえんほうしゃ・10まんボルト・れいとうビーム）を おぼえられる ポケモンの 表を 作る。
   pokecrystal の data/pokemon/base_stats/*.asm の tmhm を 読む（図鑑の 番号の じゅん。1ビット ＝ 1匹）。
   python3 tools/movetutor_gen.py pokecrystalの場所 > src/movetutor_compat.inc
"""
import sys, re, os
root = sys.argv[1]
order = re.findall(r'INCLUDE "data/pokemon/base_stats/(\w+)\.asm"', open(os.path.join(root, 'data/pokemon/base_stats.asm')).read())
assert len(order) == 251, len(order)
moves = ['FLAMETHROWER', 'THUNDERBOLT', 'ICE_BEAM']
names = ['かえんほうしゃ', '10まんボルト', 'れいとうビーム']
bits = {m: [0] * 32 for m in moves}
count = {m: 0 for m in moves}
for i, n in enumerate(order):
    src = open(os.path.join(root, 'data/pokemon/base_stats', n + '.asm')).read()
    tm = re.search(r'tmhm\s+(.*)', src).group(1)
    lst = [x.strip() for x in tm.split(';')[0].split(',')]
    for m in moves:
        if m in lst:
            bits[m][i // 8] |= 1 << (i % 8); count[m] += 1
print('; tools/movetutor_gen.py で 作った（pokecrystal の base_stats の tmhm から。図鑑の 番号 - 1 の ビット）')
for m, nm in zip(moves, names):
    print(f'MoveTutorCompat_{m}: ; {nm}（{count[m]}匹）')
    for k in range(0, 32, 16):
        print('\tdb ' + ', '.join('$%02x' % x for x in bits[m][k:k + 16]))
