import sys
from PIL import Image, ImageDraw
mids = [tuple(map(int, a.split(','))) for a in sys.argv[2:]]
out = Image.new('RGB', (480, 144 * len(mids)), 'white')
for i, (g, m) in enumerate(mids):
    for j, n in enumerate(['base', 'kit', 'full']):
        out.paste(Image.open('jt/%s_%02d_%03db.png' % (n, g, m)), (j * 160, i * 144))
out.save(sys.argv[1])
