# Crystal Crunch（joseph-bayer/crystal-for-friends）の リポジトリから、連れ歩きに 使う データを 取り出す
#   python3 tools/follow_cc_extract.py <Crystal Crunch の フォルダ>
#   → gfxdata/follow_cc/icons/*.png（手持ちの アイコン。16×32、2コマ）
#     gfxdata/follow_cc/pals.bin（0 = タマゴ、1〜251、1匹 8バイト：ふつうの 明るい・暗い、色ちがいの 明るい・暗い。
#                                 Crystal Crunch の GetArrangedMonIconColors と 同じ あて方を した あと の 色）
import sys, os, re, shutil
from PIL import Image
CC = sys.argv[1]
OUT = 'gfxdata/follow_cc/'
os.makedirs(OUT + 'icons', exist_ok=True)
for f in os.listdir(CC + '/gfx/icons'):
    if f.endswith('.png'): shutil.copy(CC + '/gfx/icons/' + f, OUT + 'icons/' + f)

def c5(v): return (v * 31 + 127) // 255
def front_middle(path):
    # rgbgfx と 同じ：明るい 順に ならべた 4色の まんなか 2色
    im = Image.open(path).convert('RGB')
    cols = [c for _, c in im.getcolors(1 << 16)]
    cols = sorted(set(cols), key=lambda c: -(0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]))
    while len(cols) < 4: cols.insert(1, cols[0])
    return [tuple(c5(x) for x in cols[1]), tuple(c5(x) for x in cols[2])]
def rgb_lines(txt):
    return [tuple(int(x) for x in m) for m in re.findall(r'RGB\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', txt)]

src = open(CC + '/data/pokemon/palettes.asm').read()
entries = []   # [(normal2, shiny2)]
cur = []
for line in src.split('\n'):
    line = line.split(';')[0].strip()
    m = re.match(r'INCBIN\s+"([^"]+)/normal\.gbcpal"', line) or re.match(r'INCBIN\s+"([^"]+)/front\.gbcpal"', line)
    if m:
        d = CC + '/' + m.group(1)
        if os.path.exists(d + '/normal.pal'):
            c = rgb_lines(open(d + '/normal.pal').read())
            cur += c[1:3] if len(c) == 4 else c[:2]
        else:
            cur += front_middle(d + '/front.png')
        continue
    m = re.match(r'INCLUDE\s+"([^"]+\.pal)"', line)
    if m:
        cur += rgb_lines(open(CC + '/' + m.group(1)).read()); continue
    if line.startswith('RGB'):
        cur += rgb_lines(line)
    if line.startswith('PokemonPalettes'):
        cur.append('MARK')
flat = cur
mark = flat.index('MARK')
pre = flat[:mark]; post = flat[mark + 1:]
# pre：-3（タマゴ）・-2・-1 の 4色ずつ
egg = pre[0:4]
mons = [post[i * 4:i * 4 + 4] for i in range(256)]   # 0〜255

od = open(CC + '/data/pokemon/icon_palette_order.asm').read()
body = od.split('IconPaletteOrders:')[1].split('IconPaletteOrderForms')[0]
orders = []
for l in body.split('\n'):
    l = l.split(';')[0].strip()
    if l.startswith('db '): orders.append(('SWAP' in l, 'OFFWHITE' in l))
WHITE = (31, 31, 31)   # PALRGB_ICON_LIGHT
def arrange(c1, c2, o):
    sw, ow = o
    light, dark = (c2, c1) if sw else (c1, c2)
    if ow: light = WHITE
    return light, dark
def w(c): return c[0] | c[1] << 5 | c[2] << 10
out = bytearray()
for i in range(252):
    if i == 0: p, o = egg, (False, False)
    else: p, o = mons[i], orders[i - 1]
    for k in (0, 2):
        l, d = arrange(p[k], p[k + 1], o)
        out += w(l).to_bytes(2, 'little') + w(d).to_bytes(2, 'little')
open(OUT + 'pals.bin', 'wb').write(out)
print('icons', len(os.listdir(OUT + 'icons')), 'pals', len(out) // 8)
