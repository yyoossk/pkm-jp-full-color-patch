# 連れ歩きキットの 歩行グラフィック（png、16×96、4色の グレー）を gfxdata/follow/*.2bpp に する
#   python3 tools/follow_png2bpp.py <歩行グラフィック/png の フォルダ>
import sys, glob, os
from PIL import Image
M = {255: 0, 169: 1, 84: 2, 0: 3}
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.png'))):
    im = Image.open(f).convert('L'); w, h = im.size; px = im.load()
    out = bytearray()
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for y in range(8):
                lo = hi = 0
                for x in range(8):
                    v = px[tx + x, ty + y]
                    c = M[min(M, key=lambda k: abs(k - v))]
                    lo |= (c & 1) << (7 - x); hi |= (c >> 1) << (7 - x)
                out += bytes([lo, hi])
    open('gfxdata/follow/' + os.path.basename(f)[:-4] + '.2bpp', 'wb').write(out)
