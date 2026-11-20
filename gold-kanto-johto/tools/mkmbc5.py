"""MBC5 版：MBC30（MBC3 の 4MB）の ROM を MBC5 で 動く ように する。
   python3 mkmbc5.py 入力.gbc 出力.gbc
   ・ROM の バンクは $2000 だけに 書く（$3000〜$3FFF には 書かない ことを ためして 確かめた）ので、MBC5 でも そのまま。
   ・SRAM（32KB、バンク 0〜3）も そのまま。
   ・MBC5 には 時計（RTC）が ない。時計を 読む GetClock を「プレイ時間」から 作る ように する
     （時・分・秒 ＝ プレイ時間、日 ＝ プレイ時間の 時 ÷ 24）。金の 時刻は「RTC ＋ 時計あわせの ずれ」なので、
     電源を 切って いる 間と タイトル画面の 間は 時計が 止まり、遊んで いる 間だけ 進む。プレイ時間は セーブに 入るので、
     つづきから はじめると 時計も つづきから。
   ・時計に 書く 所（SetClock・StartRTC・SaveRTC の RTC の 所）は 何も しない（MBC5 では RAM の バンク 8〜12 を 書いて
     しまい、セーブが こわれる）。"""
import sys, zlib

g = bytearray(open(sys.argv[1], 'rb').read())


def expect(o, h):
    b = bytes.fromhex(h.replace(' ', '')); assert bytes(g[o:o + len(b)]) == b, (hex(o), g[o:o + len(b)].hex(' '))


assert g[0x147] == 0x10 and g[0x148] == 0x07
# GetClock（$0477、49 バイト）
expect(0x0477, '3e 0a ea 00 00 cd 5c 04 21 00 40 11 00 a0 36 08 1a e6 3f e0 93 36 09 1a e6 3f e0 92 36 0a 1a e6 1f e0 91 36 0b 1a e0 90 36 0c 1a e0 8f cd ad 30 c9')
code = bytes.fromhex(
    'c5'            # push bc
    'fae1d1 e093'   # ld a,[wGameTimeSeconds] / ldh [hRTCSeconds],a
    'fae0d1 e092'   # ld a,[wGameTimeMinutes] / ldh [hRTCMinutes],a
    'faded1 67'     # ld a,[wGameTimeHours]   / ld h,a   （上の バイト）
    'fadfd1 6f'     # ld a,[wGameTimeHours+1] / ld l,a
    '01e8ff 1e00'   # ld bc,-24 / ld e,0
    '09 3003 1c 18fa'   # .loop: add hl,bc / jr nc,.done / inc e / jr .loop
    '7d c618 e091'  # .done: ld a,l / add 24 / ldh [hRTCHours],a
    '7b e090'       # ld a,e / ldh [hRTCDayLo],a
    'af e08f'       # xor a / ldh [hRTCDayHi],a（止まって いない・くり上がり なし）
    'c1 c9')        # pop bc / ret
assert len(code) <= 49
g[0x0477:0x0477 + 49] = code + bytes(49 - len(code))
# SetClock（$0551）→ ret
expect(0x0551, '3e 0a ea 00 00 cd 5c 04 21 00 40 11 00 a0 36 0c')
g[0x0551] = 0xC9
# StartRTC（05:4019）→ ret
o = 0x05 * 0x4000 + 0x4019 - 0x4000
expect(o, '3e 0a ea 00 00 cd 5c 04 3e 0c ea 00 40 fa 00 a0 cb b7 ea 00 a0 cd ad 30 c9')
g[o] = 0xC9
# SaveRTC（05:406A）：RTC の くり上がりを 消す 所を とばし、sRTCStatusFlags を 0 に する 所は のこす
o = 0x05 * 0x4000 + 0x406A - 0x4000
expect(o, '3e 0a ea 00 00 cd 5c 04 21 00 a0 3e 0c ea 00 40 cb be 3e 00 ea 00 40 af ea 00 b0 cd ad 30 c9')
g[o + 5:o + 18] = bytes(13)
# TryLoadSaveData（05:4E8C）：メニューの 時刻の 表示の ため、セーブの wStartDay〜（8 バイト）に つづけて
# プレイ時間（wGameTimeCap〜wGameTimeFrames）も 読む（14 バイト。sPlayerData は wPlayerData と 同じ ならび）
o = 0x05 * 0x4000 + 0x4E8C - 0x4000
expect(o + 0x12, '21 2b a0 11 d5 d1 01 08 00'); expect(o + 0x30, '21 2b b2 11 d5 d1 01 08 00')
g[o + 0x19] = 0x0E; g[o + 0x37] = 0x0E
# ヘッダー：MBC5＋RAM＋電池
g[0x147] = 0x1B
c = 0
for i in range(0x134, 0x14D): c = (c - g[i] - 1) & 0xFF
g[0x14D] = c
s = (sum(g) - g[0x14E] - g[0x14F]) & 0xFFFF; g[0x14E] = s >> 8; g[0x14F] = s & 0xFF
open(sys.argv[2], 'wb').write(g)
print(sys.argv[2], '%08X' % zlib.crc32(g))
