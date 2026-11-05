"""ピカチュウフルカラー（ピカチュウ版 日本版）の ROM から カントー御三家を くれる 3人の 文と ジュンサーの 絵を 取り出す
   python3 tools/starters_gen.py ピカチュウ.gbc
   → src/starters_texts.inc（文。日本版 金銀と 同じ 文字コードなので そのまま）・src/starters_jenny.inc（ジュンサーの 絵 24タイル）"""
import sys, os
PK = open(sys.argv[1], 'rb').read()
def off(b, a): return b * 0x4000 + a - 0x4000
def text(b, a, end):
    """$00 で はじまる 文。$57・$58（おわり）か $50 まで。$50 で おわる ものは end（$57/$58）に かえる"""
    o = off(b, a); assert PK[o] == 0, hex(a)
    out = bytearray([0]); o += 1
    while True:
        c = PK[o]; o += 1
        if c == 0x50: out.append(end); break
        out.append(c)
        if c in (0x57, 0x58): break
    return bytes(out)
T = [
    # フシギダネ（ハナダシティの 女の人。バンク$07）
    ('StarterText_Bulbasaur1', 0x07, 0x5b7c, 0x58),  # わたしは ここで きずついた ポケモンたちの せわを しています……
    ('StarterText_Bulbasaur2', 0x07, 0x5bd0, 0x57),  # そうだ！ あなた この フシギダネの めんどうを みてくださらない？
    ('StarterText_Bulbasaur3', 0x07, 0x5bf4, 0x57),  # それじゃ おねがいします！
    ('StarterText_Bulbasaur4', 0x07, 0x5c05, 0x57),  # フシギダネ がんばってます？
    ('StarterText_Bulbasaur5', 0x07, 0x5c17, 0x57),  # そう… ざんねん です…
    # ヒトカゲ（24ばんどうろの 男の人。バンク$14）
    ('StarterText_Charmander1', 0x14, 0x5e2d, 0x57), # おれ… ポケモン そだてるの へた なんだ……きみに あげるけど？
    ('StarterText_Charmander2', 0x14, 0x5e88, 0x57), # それじゃ おねがい するよ！
    ('StarterText_Charmander3', 0x14, 0x5e9a, 0x57), # そうか… じゃ どこに にがそうかな…
    ('StarterText_Charmander4', 0x14, 0x5eaf, 0x57), # あのときの ヒトカゲ そだってる？
    # ゼニガメ（クチバシティの ジュンサー。バンク$3c）
    ('StarterText_Squirtle1', 0x3c, 0x4c4a, 0x57),   # さいきん いたずら ばかりする ゼニガメを つかまえたの！……
    ('StarterText_Squirtle2', 0x3c, 0x4c8a, 0x57),   # その オレンジバッジ！……あなた ひきとって くれない？
    ('StarterText_Squirtle3', 0x3c, 0x4cdb, 0x57),   # まかせたわ！ だいじに そだてて あげてね！
    ('StarterText_Squirtle4', 0x3c, 0x4cf5, 0x57),   # どうしようかしら… こまったわ
    ('StarterText_Squirtle5', 0x3c, 0x4d06, 0x57),   # ゼニガメ げんきで やっている？
]
def dblines(b):
    return '\n'.join('\tdb ' + ', '.join('$%02x' % x for x in b[i:i + 16]) for i in range(0, len(b), 16))
here = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
with open(os.path.join(here, 'starters_texts.inc'), 'w') as f:
    f.write('; tools/starters_gen.py が ピカチュウフルカラーの ROM から 作った（ピカチュウ版の 文 そのまま）\n')
    for lab, b, a, e in T:
        f.write(f'{lab}:\n{dblines(text(b, a, e))}\n')
# ジュンサーの 絵：SpriteSheetPointerTable（$142ca。4バイトずつ：dw 絵, db 大きさ, db バンク）の SPRITE_OFFICER_JENNY（$3e）
SPT = 0x142ca; JENNY = 0x3e
e = SPT + 4 * (JENNY - 1)
p = PK[e] | PK[e + 1] << 8; size = PK[e + 2]; bank = PK[e + 3]
gfx = PK[off(bank, p):off(bank, p) + size * 2]      # 止まって いる 12タイル ＋ 歩く 12タイル
with open(os.path.join(here, 'starters_jenny.inc'), 'w') as f:
    f.write('; tools/starters_gen.py が ピカチュウフルカラーの ROM から 取り出した ジュンサーの 絵（24タイル）\n')
    f.write(dblines(gfx) + '\n')
print('ok', len(gfx))
