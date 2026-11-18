import sys; sys.path.insert(0,'/home/claude/sameboy-harness/python')
from gr import GR
from PIL import Image
T = {'Pewter': ((14,4),[(4,12),(5,12)]), 'Cerulean': ((7,6),[(4,14),(5,14)]), 'Vermilion': ((12,11),[(4,16),(5,16)]),
     'Celadon': ((21,21),[(4,16),(5,16)]), 'Saffron': ((25,4),[(8,16),(9,16)]), 'Viridian': ((23,4),[(4,16),(5,16)])}
sel = sys.argv[1:] or list(T)
g = GR('/home/claude/work/out/gold_full.gbc')
rows = []
for nm in sel:
    mid, cells = T[nm]
    for (px, py) in cells:
        g.load_state('jo0.st'); g.wait(2)
        g.poke(0xD9C6, mid[0]); g.poke(0xD9C7, mid[1]); g.poke(0xD9C9, px); g.poke(0xD9C8, py - 1)
        g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1); g.wait(300)
        g.press('D', 16, 4)
        fr = []
        def sh():
            g.shot('/tmp/tt.png'); fr.append(Image.open('/tmp/tt.png').copy())
        g.wait(20); sh()                      # びっくり
        for i in range(3): g.press('A', 4, 30)
        sh()                                  # 歩いて くる 途中
        g.wait(60); sh()                      # ついた
        for i in range(6): g.press('A', 4, 30)
        sh()                                  # はい／いいえ
        g.press('D', 4, 20); g.press('A', 4, 40); g.press('A', 4, 40); g.press('A', 4, 40); sh()
        g.wait(120); sh()                     # もどった
        rows.append(fr)
        print(nm, (px, py), g.peek(0xD9C8, 2), flush=True)
out = Image.new('RGB', (160 * 6, 144 * len(rows)))
for j, fr in enumerate(rows):
    for i, im in enumerate(fr): out.paste(im, (i * 160, j * 144))
out.save('/tmp/tts.png')
