# Polished Crystal（https://github.com/Rangi42/polishedcrystal）から
# 手持ちのミニアイコンの絵と色を取り出して gfxdata/ に書き出す。
#   python3 tools/mkminis.py <polishedcrystal のフォルダ>
# 出力：gfxdata/minis.2bpp（0=タマゴ、1〜251、1匹128バイト）
#       gfxdata/minipals.bin（0〜251、1匹8バイト：ふつう 明・暗、色ちがい 明・暗）
import re, os, sys
from PIL import Image
PC = sys.argv[1].rstrip('/') + '/'
ptr = open(PC + 'data/pokemon/mini_icon_pointers.asm').read()
names = re.findall(r'^\s*mini_icon (\w+)', ptr, re.M)[:251]
src = open(PC + 'gfx/minis_icons.asm').read()
lab = {m.group(1): m.group(2) for m in re.finditer(r'^(\w+)Mini::\s+INCBIN "gfx/minis/(\w+)\.2bpp', src, re.M)}
def tiles(path):
    px = Image.open(PC + 'gfx/minis/%s.png' % path).convert('L').load(); out = bytearray()
    for ty in range(4):
        for tx in range(2):
            for y in range(8):
                lo = hi = 0
                for x in range(8):
                    v = px[tx * 8 + x, ty * 8 + y]; c = 0 if v > 212 else 1 if v > 127 else 2 if v > 42 else 3
                    lo |= (c & 1) << (7 - x); hi |= ((c >> 1) & 1) << (7 - x)
                out += bytes([lo, hi])
    return out
def pal(d, kind):
    t = open(PC + 'gfx/pokemon/%s/%s.pal' % (d, kind)).read(); out = bytearray()
    for r, g, b in [tuple(map(int, m)) for m in re.findall(r'RGB\s*(\d+),\s*(\d+),\s*(\d+)', t)][:2]:
        v = r | (g << 5) | (b << 10); out += bytes([v & 255, v >> 8])
    return out
def pdir(f):
    for c in (f, f + '_plain', f.split('_')[0], f.split('_')[0] + '_plain'):
        if os.path.exists(PC + 'gfx/pokemon/%s/normal.pal' % c): return c
mini = bytearray(tiles('egg')); pals = bytearray(pal('egg', 'normal') * 2)
for n in names:
    f = lab.get(n) or ('unown_a' if n == 'Unown' else 'egg')
    mini += tiles(f); d = pdir(f)
    pals += pal(d, 'normal') + pal(d, 'shiny') if d else bytes(8)
# 金銀クリスタルでは 色ちがいのギャラドス = いかりのみずうみの赤いギャラドス。
# Polished Crystal は赤いギャラドスを別の姿（gyarados_red）にして 色ちがいを金色にしているので、赤いギャラドスの色を使う。
if os.path.exists(PC + 'gfx/pokemon/gyarados_red/normal.pal'):
    o = 130 * 8 + 4; pals[o:o + 4] = pal('gyarados_red', 'normal')
os.makedirs('gfxdata', exist_ok=True)
open('gfxdata/minis.2bpp', 'wb').write(mini); open('gfxdata/minipals.bin', 'wb').write(pals)
print('OK', len(mini), len(pals))
