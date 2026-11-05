# ミニアイコンの 色ちがいの 色を 金銀の 色ちがいの 色に そろえる
#   python3 tools/minipals_shiny.py <pokegold の フォルダ> gfxdata/minipals.bin
# minipals.bin は 1匹 8バイト（ふつう 明・暗、色ちがい 明・暗）。0 番は タマゴ。
# Polished Crystal の 色ちがいの 色は 金銀と ちがう ものが ある（ピカチュウが 青 など）ので、
# 金銀の shiny.pal と ちがう ポケモンだけ 書きかえる。
# アイコンの ふつうの 色は Polished Crystal の もの（絵に 合わせて 明・暗が 入れかわって いる ことも ある）なので、
# アイコンの ふつうの 色 それぞれに いちばん 近い 金銀の ふつうの 色を さがし、それと 同じ 番の 色ちがいの 色を 使う。
import re, struct, sys
pg, path = sys.argv[1], sys.argv[2]
d = bytearray(open(path, 'rb').read())
src = open(f'{pg}/data/pokemon/palettes.asm').read()
names = re.findall(r'gfx/pokemon/(\w+)/shiny.pal', src)[:251]
rd = lambda p: [tuple(map(int, re.findall(r'\d+', l))) for l in open(p) if 'RGB' in l]
w = lambda c: c[0] | c[1] << 5 | c[2] << 10
c = lambda x: (x & 31, (x >> 5) & 31, x >> 10)
dist = lambda a, b: sum((x - y) ** 2 for x, y in zip(a, b))
n_fix = 0
for i, n in enumerate(names, 1):
    g = struct.unpack('<4H', open(f'{pg}/gfx/pokemon/{n}/normal.gbcpal', 'rb').read())
    gn = [c(g[1]), c(g[2])]
    s = rd(f'{pg}/gfx/pokemon/{n}/shiny.pal')
    m = struct.unpack('<4H', d[i * 8:i * 8 + 8])
    if (w(s[0]), w(s[1])) == m[2:]:
        continue
    ns = [s[min((0, 1), key=lambda j: dist(col, gn[j]))] for col in (c(m[0]), c(m[1]))]
    if ns[0] == ns[1]:
        ns = s[:2]
    struct.pack_into('<2H', d, i * 8 + 4, w(ns[0]), w(ns[1]))
    n_fix += 1
open(path, 'wb').write(d)
print(n_fix, 'ひき')
