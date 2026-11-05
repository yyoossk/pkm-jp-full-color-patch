"""src/hmfield.asm の「ROM ごとにちがう所」を ROM から調べる（金・銀・クリスタル、日本版・海外版）。
   python3 tools/hmfield_find.py ROM.gbc
   CheckPartyMove の命令の並びで探して、その中のアドレスを読む。
   最後に、空いていそうな所（0 か $ff が続く所）も出す。ほかのパッチで使っていないか確かめてから選ぶ。"""
import sys
d = open(sys.argv[1], 'rb').read()
# ld e,0 / xor a / ld [wCurPartyMon],a / ld c,e / ld b,0 / ld hl,wPartySpecies / add hl,bc / ld a,[hl] /
# and a / jr z / cp -1 / jr z / cp EGG / jr z / ld bc,$30 / ld hl,wPartyMon1Moves / ld a,e / call AddNTimes / ld b,4
pat = [0x1e, 0x00, 0xaf, 0xea, None, None, 0x4b, 0x06, 0x00, 0x21, None, None, 0x09, 0x7e, 0xa7, 0x28, None,
       0xfe, 0xff, 0x28, None, 0xfe, 0xfd, 0x28, None, 0x01, 0x30, 0x00, 0x21, None, None, 0x7b, 0xcd, None, None,
       0x06, 0x04]
hits = []
i = d.find(bytes(pat[:4]))
while i != -1:
    if all(v is None or d[i + k] == v for k, v in enumerate(pat)): hits.append(i)
    i = d.find(bytes(pat[:4]), i + 1)
if len(hits) != 1:
    sys.exit('CheckPartyMove が %d か所見つかった（1か所のはず）' % len(hits))
o = hits[0]
w = lambda k: d[o + k] | d[o + k + 1] << 8
bank, addr = o // 0x4000, o % 0x4000 + (0x4000 if o >= 0x4000 else 0)
print('DEF HMFIELD_CheckPartyMove      EQU $%04x' % addr)
print('DEF HMFIELD_CheckPartyMove_BANK EQU $%02x' % bank)
print('DEF HMFIELD_wCurPartyMon        EQU $%04x' % w(4))
print('DEF HMFIELD_wPartySpecies       EQU $%04x' % w(10))
print('DEF HMFIELD_wPartyMon1Moves     EQU $%04x' % w(29))
print('DEF HMFIELD_AddNTimes           EQU $%04x' % w(33))
print('; 空いていそうな所（128バイト以上。ほかのパッチで使っていないか確かめる）')
for b in range(len(d) // 0x4000 - 1, 0, -1):
    s = d[b * 0x4000:(b + 1) * 0x4000]
    i = 0
    while i < 0x4000:
        if s[i] in (0, 0xff):
            j = i
            while j < 0x4000 and s[j] == s[i]: j += 1
            if j - i >= 128: print(';   バンク $%02x  $%04x〜（$%x バイト）' % (b, 0x4000 + i, j - i))
            i = j
        else: i += 1
