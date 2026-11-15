"""ジョウトの ポケモンじいさんの いえの オーキド（第48弾の ジョウトがわ）：主人公は もう 図鑑を もって いるので
   あたらしい ことば。「図鑑を もらった」の かわりに「ジョウトの ずかんに なった」。
   銀の ことば（$2C:$7C51・$7DC3・$7DDA）の 所を farwritetext・end に して writetext を scall に（$E8:$4D00 の ことば）。
   （リーグの きりかえは カントーの マップと いっしょに 移植ずみ）"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import jptext
from gsc import fo, r16

CB, CA = 0xE8, 0x4D00
Q = '“'


def T(s): return b'\x00' + jptext.enc(s) + b'\x57'


TEXTS = [
    (0x7C51, 'オーキド' + Q + 'おお　<PLAYER>！<LINE>ちゃんと　ジョウトに　ついたな！<PARA>わしも　ふるい　ともだちの<LINE>'
     '<POKEMON>じいさんを　たずねて<CONT>きておったのじゃ<PARA>ほほうっ！<LINE>めずらしい　<POKEMON>を　もってるな！<PARA>'
     'ウツギくんの　おつかいか！<PARA>そうじゃ！<LINE><PLAYER>の　ずかんに<CONT>ジョウトの　<POKEMON>も<CONT>'
     'きろく　できるように　してやろう！'),
    (0x7DC3, '<PLAYER>の　ずかんが<LINE>ジョウトの　ずかんに　なった！'),
    (0x7DDA, 'ジョウトには　カントーでは<LINE>みられない　<POKEMON>が<CONT>たくさん　いるのじゃ！<PARA>'
     'ずかんを　どんどん<LINE>うめていって　くれ！<PARA>おっと！<LINE>ながいを　した　ようじゃ！<PARA>'
     'これから　コガネシティへ　いって<LINE>いつもの　ラジオばんぐみの<CONT>しゅうろくを　せねば　ならんのだ！<PARA>'
     'それじゃ　<PLAYER>！<LINE>よろしく　たのんだぞ！'),
]


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    o = fo(0x2C, 0x7A64); assert rom[o:o + 6] == bytes([0x4C, 0x51, 0x7C, 0x54, 0x85, 0x4C])
    a = CA
    for site, s in TEXTS:
        t = T(s); assert not any(rom[fo(CB, a):fo(CB, a) + len(t)])
        rom[fo(CB, a):fo(CB, a) + len(t)] = t
        p = fo(0x2C, site); assert rom[p] == 0x00
        rom[p:p + 5] = bytes([0x4B, CB, a & 0xFF, a >> 8, 0x90])          # 文の ところを farwritetext / end に
        w = [i for i in range(fo(0x2C, 0x7A50), fo(0x2C, 0x7A90)) if rom[i:i + 3] == bytes([0x4C, site & 0xFF, site >> 8])]
        assert len(w) == 1; rom[w[0]] = 0x00                                 # writetext → scall
        a += len(t)
    log.append('ポケモンじいさんの いえの オーキドの ことば（$%02X:$%04X〜$%04X）' % (CB, CA, a))
    return rom
