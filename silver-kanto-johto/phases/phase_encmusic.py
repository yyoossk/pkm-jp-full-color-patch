"""足した トレーナーの 種類（67〜79）に 見つかった ときの 曲（第105弾の 銀版）：
   見つかった ときの 曲の 表（TrainerEncounterMusic、銀 $3A:$5027）は 1種類 1バイトで 銀の 種類（0〜66）の 分しか ない。
   67〜79 は 表の 外を 読んで いた（曲が 鳴らない・ちがう 曲）。表を $E8:$5D08 に 写して 足した 種類の 分を 足し、
   $3A:$501C の ld d,0 / ld hl,表 / add hl,de / ld e,[hl] を farcall に。
   67（ミナキ）：クリスタル版と 同じ、68〜79：してんのう・ワタル＝やまおとこ／サカキ・ムサシとコジロウ＝ロケット団／
   ガールスカウト＝ミニスカート／もうじゅうつかい＝マニア／ボーイスカウト＝たんぱんこぞう／のこり＝やまおとこ（クリスタル版の キットと 同じ）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps
from gsc import fo

B, TABLE, HOOK = 0x3A, 0x5027, 0x501C
NB, NA = 0xE8, 0x5D00
S_N = 67
NEW = [0x0A, 0x0A, 0x0A, 0x39, 0x39, 0x0B, 0x3A, 0x37, 0x0A, 0x0A, 0x0A, 0x0A]   # 68〜79


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read()
    h = fo(B, HOOK); assert rom[h:h + 7] == bytes.fromhex('16002127501 95e'.replace(' ', ''))
    tab = bytes(rom[fo(B, TABLE):fo(B, TABLE) + S_N]) + bytes([cmod[fo(B, TABLE) + 67]]) + bytes(NEW)
    code = bytes([0x16, 0x00, 0x21]) + (NA + 8).to_bytes(2, 'little') + bytes([0x19, 0x5E, 0xC9])
    o = fo(NB, NA); assert not any(rom[o:o + 8 + len(tab)])
    rom[o:o + 8] = code; rom[o + 8:o + 8 + len(tab)] = tab
    rom[h:h + 7] = bytes([0x3E, NB, 0x21, NA & 0xFF, NA >> 8, 0xCF, 0x00])
    log.append('トレーナーに 見つかった ときの 曲の 表 %d 種類（$%02X:$%04X）' % (len(tab), NB, NA + 8))
    return rom
