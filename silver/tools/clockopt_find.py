"""src/clockopt_gold.asm（せっていの「とけい」）で 新しく使う所を ROM から調べる。
   python3 tools/clockopt_find.py ROM.gbc
   ・RestartClock_Bank / RestartClock_SetFromPad … 元の RestartClock の「ld hl, wOptions」から（はじめの PrintText をとばす）
   ・JoyTextDelay / GetJoypad / DelayFrame / WaitBGMap / hJoyDown … ホームの処理
   金・銀・クリスタルで 命令の並びが同じなので そのまま出る。wClockSub（1バイト）は 使われていない WRAM を自分で決める。"""
import sys

def find_all(d, pat, start=0, end=None):
    toks = pat.split()
    end = len(d) if end is None else end
    first = int(toks[0], 16)
    out = []
    i = d.find(bytes([first]), start, end)
    while 0 <= i < end - len(toks):
        if all(t == '??' or d[i + k] == int(t, 16) for k, t in enumerate(toks)):
            out.append(i)
        i = d.find(bytes([first]), i + 1, end)
    return out

def ba(o):
    return o // 0x4000, (o % 0x4000) + (0x4000 if o >= 0x4000 else 0)

def main(rom):
    d = open(rom, 'rb').read()
    # RestartClock：ld hl, text / call PrintText / ld hl, wOptions / ld a, [hl] / push af / set NO_TEXT_SCROLL, [hl] /
    #               call LoadStandardMenuHeader / call ClearTilemap / ld hl, text / call PrintText / call .SetClock / call ExitMenu
    h = find_all(d, '21 ?? ?? cd ?? ?? 21 ?? ?? 7e f5 cb e6 cd ?? ?? cd ?? ?? 21 ?? ?? cd ?? ?? cd ?? ?? cd ?? ??')
    h = [o for o in h if d[o + 4:o + 6] == d[o + 23:o + 25]]   # 2つの PrintText が同じ
    if len(h) == 1:
        b, a = ba(h[0] + 6)
        print(f'DEF RestartClock_Bank EQU ${b:02x}')
        print(f'DEF RestartClock_SetFromPad EQU ${a:04x}')
        home = d[h[0] + 4] | d[h[0] + 5] << 8
        print(f'; （PrintText = ${home:04x}）')
    else:
        print('; RestartClock:', len(h), 'か所（手で確かめる）', [hex(x) for x in h[:8]])
    # JoyTextDelay：call GetJoypad / ldh a, [hInMenu] / and a / ldh a, [hJoyPressed] / jr z, +2 / ldh a, [hJoyDown] / ldh [hJoyLast], a
    h = find_all(d, 'cd ?? ?? f0 ?? a7 f0 ?? 28 02 f0 ?? e0 ??', 0, 0x4000)
    if len(h) == 1:
        o = h[0]
        print(f'DEF JoyTextDelay EQU ${o:04x}')
        print(f'DEF GetJoypad EQU ${d[o + 1] | d[o + 2] << 8:04x}')
        print(f'DEF hJoyDown EQU $ff{d[o + 11]:02x}')
        print(f'; （hJoyPressed = $ff{d[o + 7]:02x}、hInMenu = $ff{d[o + 4]:02x}）')
    else:
        print('; JoyTextDelay:', len(h), 'か所（手で確かめる）', [hex(x) for x in h[:8]])
    # WaitBGMap：ld a, 1 / ldh [hBGMapMode], a / ld c, 4 / call DelayFrames / ret
    h = find_all(d, '3e 01 e0 ?? 0e 04 cd ?? ?? c9', 0, 0x4000)
    if len(h) >= 1:
        print(f'DEF WaitBGMap EQU ${h[0]:04x}' + ('' if len(h) == 1 else f'   ; {len(h)} か所。いちばん前を出した'))
    else:
        print('; WaitBGMap … 見つからない')
    # DelayFrame：ld a, 1 / ld [hVBlank? ]… 版でちがうので DelayFrames（ld c,?? 前の call）から：call DelayFrame / dec c / jr nz / ret
    h = find_all(d, 'cd ?? ?? 0d 20 fa c9', 0, 0x4000)
    if h:
        o = h[0]
        print(f'DEF DelayFrame EQU ${d[o + 1] | d[o + 2] << 8:04x}' + ('' if len(h) == 1 else f'   ; {len(h)} か所。いちばん前を出した'))
    else:
        print('; DelayFrame … 見つからない')
    print('; DEF wClockSub … 使われていない WRAM 1バイトを 自分で決める')

if __name__ == '__main__':
    main(sys.argv[1])
