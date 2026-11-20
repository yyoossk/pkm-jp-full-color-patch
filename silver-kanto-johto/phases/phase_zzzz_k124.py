"""タイトル画面に 戻る ときの 直し（第124弾。クリスタル版 カントー＆ジョウトの キットから）。
   起きて いた こと：オープニング → 赤の タイトル → START → メニュー → B で、銀の タイトル（ルギア）が 出た。
   原因：赤の オープニング（phase_opening）は 銀の IntroSequence（$01:$63EF）の 頭 9 バイトを 書きかえて 入れたが、
         メニュー（_MainMenu）の 最後の「jp StartTitleScreen」（$01:$5A94 → $63FD）は そのまま だった。
   直し：
     1 $01:$5A94 の 行き先を、使われなく なった もとの IntroSequence の のこり（$01:$63F8〜、ほかから 飛んで こない）に して、
       ld a,1 / ld [FLAG],a / jp IntroSequence（$63EF）を 書く。
       FLAG は $D698（銀の wTradeFlags の あとの 空き ds 33 の 中。交換の しるしは $D679 まで）。
     2 赤の オープニング（$B6:$5B70〜）の「call PlayIntro」（$5CD8）を、$B6 の 空き（FIX）の 小さな 処理に 向ける：
       ld a,[FLAG] / and a / jp z,PlayIntro / xor a / ld [FLAG],a / ret
       → フラグが 立って いれば コピーライト・流れ星・ゲンガーと ニドリーノを 飛ばして すぐ 赤の タイトル（赤と 同じ）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

FLAG = 0xD698
B = 0xB6
FIX = 0x7F80
INTRO, OLD = 0x63EF, 0x63F8


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    # IntroSequence（phase_opening が 書いた もの）と、のこりの 古い バイト
    expect(rom, fo(1, INTRO), '3e b6 21 c0 7f cf c3 16 64 9f 54 3e 39 cf')
    expect(rom, fo(1, 0x5A94), 'c3 fd 63')
    code = bytes([0x3E, 0x01, 0xEA, FLAG & 0xFF, FLAG >> 8, 0xC3, INTRO & 0xFF, INTRO >> 8])
    o = fo(1, OLD); rom[o:o + len(code)] = code
    rom[fo(1, 0x5A95):fo(1, 0x5A97)] = bytes([OLD & 0xFF, OLD >> 8])
    # 赤の オープニング：call ClearSprites / call $5CC2 / call PlayIntro / call TitleScreen / ld [wTitleScreenSelectedOption],a
    st = fo(B, 0x5B70)
    seq = bytes.fromhex('cdbb30cdc25ccdd85ccde660ea58ce')
    i = rom.find(seq, st, st + 0x80); assert i > 0
    play_intro = rom[i + 7] | rom[i + 8] << 8
    fx = bytes([0xFA, FLAG & 0xFF, FLAG >> 8, 0xA7, 0xCA, play_intro & 0xFF, play_intro >> 8,
                0xAF, 0xEA, FLAG & 0xFF, FLAG >> 8, 0xC9])
    a = fo(B, FIX); assert not any(rom[a - 16:a + len(fx) + 16])
    rom[a:a + len(fx)] = fx
    rom[i + 7:i + 9] = bytes([FIX & 0xFF, FIX >> 8])
    log.append('メニューから B：赤の タイトルへ（$01:$%04X、フラグ $%04X、$%02X:$%04X）' % (OLD, FLAG, B, FIX))
    return rom
