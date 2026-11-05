"""src/sigmove.asm（ルギア・ホウオウの 専用わざ）の「ROM ごとにちがう所」を ROM から調べる。
   python3 tools/sigmove_find.py ROM.gbc
   ・ルギア・ホウオウの EvosAttacks（進化なし＋レベルアップで覚える わざ）を 元の並びで さがし、
     同じバンクの EvosAttacksPointers の中の その2つの ポインタの場所を出す。
   ・表の中身が sigmove.asm と ちがうときは 知らせる（そのときは sigmove.asm の表を 直す）。
   ・ルギア・ホウオウが 出てくるときの loadwildmon の レベルの所（SIG_LUGIA_WILD・SIG_HOOH_WILD）も出す。
   ・SIG_FREE（48バイト）の候補として バンクの おわりの空きを出す（ほかのパッチが使っていないか map で確かめる）。
   パッチを入れる前の ROM で調べる。"""
import sys

LUGIA = bytes([0, 1, 0xb1, 11, 0xdb, 22, 0x10, 33, 0x69, 44, 0x38, 55, 0xf0, 66, 0x81, 77, 0x12, 88, 0xf6, 99, 0xf8, 0])
HOOH  = bytes([0, 1, 0xdd, 11, 0xdb, 22, 0x10, 33, 0x69, 44, 0x7e, 55, 0xf1, 66, 0x81, 77, 0x12, 88, 0xf6, 99, 0xf8, 0])

def ba(o):
    return o // 0x4000, (o % 0x4000) + (0x4000 if o >= 0x4000 else 0)

def find(d, head, full, name):
    hits = []
    i = d.find(head)
    while i >= 0:
        hits.append(i); i = d.find(head, i + 1)
    if len(hits) != 1:
        print(f'; {name} の表：{len(hits)} か所（手で確かめる）', [hex(h) for h in hits[:6]])
        return None
    o = hits[0]
    if d[o:o + len(full)] != full:
        print(f'; {name} の表が 思っていたものと ちがう：', d[o:o + 24].hex(' '), '（sigmove.asm の表を直す）')
    return o

def main(rom):
    d = open(rom, 'rb').read()
    ol = find(d, LUGIA[:8], LUGIA, 'ルギア')
    oh = find(d, HOOH[:8], HOOH, 'ホウオウ')
    if ol is None or oh is None:
        return
    b, al = ba(ol); b2, ah = ba(oh)
    if b != b2:
        print('; ルギアと ホウオウの 表の バンクが ちがう（手で確かめる）')
        return
    s = d[b * 0x4000:(b + 1) * 0x4000]
    pl = s.find(bytes([al & 0xff, al >> 8]) + bytes([ah & 0xff, ah >> 8]))
    if pl < 0:
        print('; EvosAttacksPointers の ルギア・ホウオウ（つづいた 2つの ポインタ）が 見つからない')
        return
    print(f'DEF SIG_BANK           EQU ${b:02x}')
    print(f'DEF SIG_PTR_LUGIA      EQU ${0x4000 + pl:04x}')
    print(f'DEF SIG_PTR_HOOH       EQU ${0x4000 + pl + 2:04x}')
    n = len(s)
    while n > 0 and s[n - 1] == 0: n -= 1
    # 出てくるときの レベル：loadwildmon（cmd）ルギア・ホウオウ, レベル / startbattle（cmd + 2）
    cands = {}
    for cmd in range(0x50, 0x62):
        for sp in (0xf9, 0xfa):
            i = d.find(bytes([cmd, sp]))
            while i >= 0:
                if d[i + 3] == cmd + 2 and 1 <= d[i + 2] <= 100:
                    cands.setdefault(cmd, {}).setdefault(sp, []).append(i)
                i = d.find(bytes([cmd, sp]), i + 1)
    both = [c for c in cands if len(cands[c].get(0xf9, [])) == 1 and len(cands[c].get(0xfa, [])) == 1]
    if len(both) == 1:
        c = both[0]
        for sp, nm in ((0xf9, 'LUGIA'), (0xfa, 'HOOH')):
            o = cands[c][sp][0] + 2; b3, a3 = ba(o)
            print(f'DEF SIG_{nm}_WILD_BANK EQU ${b3:02x}')
            print(f'DEF SIG_{nm}_WILD     EQU ${a3:04x}   ; 元の レベル {d[o]}')
    else:
        print('; 出てくるときの レベルの所が 1つに しぼれない（手で確かめる）。候補：')
        for c in cands:
            for sp in cands[c]:
                for o in cands[c][sp]:
                    b3, a3 = ba(o + 2); print(f';   命令 ${c:02x}  種類 ${sp:02x}  バンク${b3:02x}:${a3:04x}  レベル {d[o + 2]}')
    print(f'; SIG_FREE の候補：バンク${b:02x} ${0x4000 + n:04x}〜（{0x4000 - n}バイト。48バイト いる。ほかのパッチが使っていないか確かめる）')

if __name__ == '__main__':
    main(sys.argv[1])
