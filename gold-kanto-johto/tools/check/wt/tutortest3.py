import sys; sys.path.insert(0,'/home/claude/sameboy-harness/python')
from gr import GR
from PIL import Image
g = GR('/home/claude/work/out/gold_full.gbc')
fr = []
def sh(): g.shot('/tmp/tt.png'); fr.append(Image.open('/tmp/tt.png').copy())
def guide():
    for i in range(1, 13):
        q = g.peek(0xD1F2 + 0x28 * i, 0x14)
        if q[0] == 0x48: return (q[0x10] - 4, q[0x11] - 4)
# 1) バッジなし：何も おきない・案内は もとの 文
g.load_state('jo0.st'); g.wait(2); bd = g.peek(0xD570)[0]; g.poke(0xD570, bd & ~1)
g.poke(0xD9C6, 14); g.poke(0xD9C7, 4); g.poke(0xD9C9, 5); g.poke(0xD9C8, 11); g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1); g.wait(300)
g.press('D', 16, 60); sh(); print('バッジなし 入口', g.peek(0xD9C8, 2), guide())
g.press('U', 16, 30); g.press('R', 4, 30); g.press('A', 4, 60); sh(); g.press('A', 4, 60); sh()
# 2) バッジあり：よびとめ → いいえ
g.load_state('jo0.st'); g.wait(2)
g.poke(0xD9C6, 14); g.poke(0xD9C7, 4); g.poke(0xD9C9, 5); g.poke(0xD9C8, 11); g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1); g.wait(300)
g.press('D', 16, 4)
for i in range(40):
    g.press('A', 4, 20)
    g.shot('/tmp/tt.png'); im = Image.open('/tmp/tt.png').convert('RGB')
    if im.getpixel((150, 70)) != im.getpixel((150, 60)) and max(im.getpixel((126, 75))) < 60: break
sh(); g.press('B', 4, 40); sh(); g.press('A', 4, 40); g.wait(150); sh()
print('いいえ のあと 案内', guide(), 'プレイヤー', g.peek(0xD9C8, 2))
# 3) もう いちど 入口：よびとめない
g.press('U', 16, 30); g.press('D', 16, 90); sh(); print('2回め', g.peek(0xD9C8, 2), guide())
# 4) 話しかける → はい → ラプラス
g.press('U', 16, 30); g.press('R', 4, 20); g.press('A', 4, 60); sh()
for i in range(8): g.press('A', 4, 30)
sh(); g.press('A', 4, 60); sh(); g.press('D', 4, 30); g.press('A', 4, 60); sh()
for i in range(4): g.press('A', 4, 50); sh()
print('ラプラスの わざ', g.peek(0xD9F0 + 0x30 + 2, 4))
out = Image.new('RGB', (160 * 6, 144 * ((len(fr) + 5) // 6)))
for i, im in enumerate(fr): out.paste(im, ((i % 6) * 160, (i // 6) * 144))
out.save('/tmp/tts.png')
