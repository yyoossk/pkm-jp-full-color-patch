"""src/fieldcolors.asm（フィールドのボール・回復の機械・肌の色）の「ROM ごとにちがう所」を ROM から調べる。
   python3 tools/fieldcolors_find.py ROM.gbc
   出た DEF を .inc にして fieldcolors.asm より前に読みこむ（または fieldcolors.asm の先頭の DEF を書きかえる）。
   FC_FREE（50バイト）は FC_OBJ_BANK の空きから 自分で決める（ほかのパッチと重ならないように）。
   金・銀・クリスタルで 命令の並びが同じなので そのまま出る。"""
import sys

def find_all(d, pat, start=0, end=None):
    """pat：16進の文字列。?? は なんでもよい"""
    toks = pat.split()
    end = len(d) if end is None else end
    first = int(toks[0], 16) if toks[0] != '??' else None
    out = []
    i = start
    while i < end - len(toks):
        if first is not None:
            i = d.find(bytes([first]), i, end - len(toks))
            if i < 0: break
        ok = True
        for k, t in enumerate(toks):
            if t != '??' and d[i + k] != int(t, 16):
                ok = False; break
        if ok: out.append(i)
        i += 1
    return out

def ba(o):
    return o // 0x4000, (o % 0x4000) + (0x4000 if o >= 0x4000 else 0)

def rgb(r, g, b):
    v = r | g << 5 | b << 10
    return bytes([v & 0xff, v >> 8])

# PokeBallSpriteGFX のはじめの 4枚（元の絵）
BALL = bytes.fromhex(
    '0000000003030c0f111e111e203f203f00000000c0c030f08878887804fc04fc'
    '38273f201f101f100f0c0303000000001ce4fc04f808f808f030c0c000000000')

def main(rom):
    d = open(rom, 'rb').read()
    res = {}
    # InitSprite：xor a / bit IN_GRASS_F, e / jr z, +2 / or OAM_PRIO / ldh [hCurSpriteOAMFlags], a
    h = find_all(d, 'af cb 5b 28 02 f6 80 e0 ??')
    if len(h) == 1:
        b, a = ba(h[0])
        res['FC_OBJ_BANK'] = b; res['FC_INIT_HOOK'] = a
        res['FC_hCurSpriteOAMFlags'] = 0xff00 | d[h[0] + 8]
        # .addsprite：and $f0 / or d / ld [bc], a（同じバンク、すぐあと）
        h2 = find_all(d, 'e6 f0 b2 02', h[0], h[0] + 0x100)
        if len(h2) == 1:
            res['FC_ATTR_HOOK'] = ba(h2[0])[1]
        else:
            print('; FC_ATTR_HOOK:', len(h2), 'か所（手で確かめる）')
    else:
        print('; FC_INIT_HOOK:', len(h), 'か所（手で確かめる）', [hex(x) for x in h[:8]])
    # ボールの絵（元の絵をさがす。だめなら 少しゆるく：まん中の 32バイト）
    o = d.find(BALL)
    if o < 0:
        o2 = d.find(BALL[16:48])
        o = o2 - 16 if o2 >= 0 else -1
    if o >= 0:
        b, a = ba(o); res['FC_BALLGFX_BANK'] = b; res['FC_BALLGFX'] = a
    else:
        print('; FC_BALLGFX … 見つからない（gfx/sprites/poke_ball.2bpp と同じ並びを さがす）')
    # OverworldSprites（6バイトずつ）：道具のボールの所（dw PokeBallSpriteGFX / db 4 tiles, BANK, STILL_SPRITE, PAL_OW_RED）から 表の頭を出す
    if 'FC_BALLGFX' in res:
        pat = bytes([res['FC_BALLGFX'] & 0xff, res['FC_BALLGFX'] >> 8, 0x40, res['FC_BALLGFX_BANK'], 3, 0])
        h = []
        i = d.find(pat)
        while i >= 0:
            h.append(i); i = d.find(pat, i + 1)
        if len(h) == 1:
            t = h[0] - (0x54 - 1) * 6
            b, a = ba(t); res['FC_SPRITES_BANK'] = b; res['FC_SPRITES'] = a
            e = d[t + (0x3f - 1) * 6: t + (0x3f - 1) * 6 + 6]
            if e[2] != 0xc0 or e[4] != 2:
                print('; SPRITE_UNUSED_GUY（$3f）の表が 思っていたもの（12枚・STANDING_SPRITE）とちがう：', e.hex(), '（使われていないか 手で確かめる）')
        else:
            print('; FC_SPRITES:', len(h), 'か所（手で確かめる）')
    # ウツギ研究所の 3つのボール（object_event：スプライト $54、y+4 = 7、x+4 = 10・11・12。13バイトずつ）
    h = []
    i = d.find(bytes([0x54, 7, 10]))
    while i >= 0:
        if d[i + 13:i + 16] == bytes([0x54, 7, 11]) and d[i + 26:i + 29] == bytes([0x54, 7, 12]):
            h.append(i)
        i = d.find(bytes([0x54, 7, 10]), i + 1)
    if len(h) == 1:
        b, a = ba(h[0]); res['FC_LABOBJ_BANK'] = b; res['FC_LABOBJ'] = a
    else:
        print('; FC_LABOBJ:', len(h), 'か所（手で確かめる）', [hex(x) for x in h[:8]])
    # MapObjectPals：4つの時間 × 8パレット、はじめの 5つ（赤・青・緑・茶・ピンク）の 色1 が 肌色（31,19,10）
    skin = rgb(31, 19, 10)
    cands = []
    i = 0
    while True:
        i = d.find(skin, i)
        if i < 0: break
        o = i - 2
        if o >= 0 and all(d[o + t * 64 + p * 8 + 2: o + t * 64 + p * 8 + 4] == skin for t in range(4) for p in range(5)):
            cands.append(o)
        i += 1
    if len(cands) == 1:
        b, a = ba(cands[0]); res['FC_NPCPALS_BANK'] = b; res['FC_NPCPALS'] = a
    else:
        print('; FC_NPCPALS:', len(cands), 'か所（手で確かめる）', [hex(x) for x in cands[:8]])
    # 回復の機械：白・肌色・赤・黒
    h = find_all(d, (rgb(31, 31, 31) + skin + rgb(31, 7, 1) + b'\0\0').hex(' '))
    if len(h) == 1:
        b, a = ba(h[0]); res['FC_HEALPAL_BANK'] = b; res['FC_HEALPAL'] = a
    else:
        print('; FC_HEALPAL:', len(h), 'か所（手で確かめる）', [hex(x) for x in h[:8]])
    order = ['FC_OBJ_BANK', 'FC_INIT_HOOK', 'FC_ATTR_HOOK', 'FC_hCurSpriteOAMFlags',
             'FC_BALLGFX_BANK', 'FC_BALLGFX', 'FC_SPRITES_BANK', 'FC_SPRITES', 'FC_LABOBJ_BANK', 'FC_LABOBJ', 'FC_NPCPALS_BANK', 'FC_NPCPALS', 'FC_HEALPAL_BANK', 'FC_HEALPAL']
    for k in order:
        if k in res:
            v = res[k]
            print(f'DEF {k:<22} EQU ${v:02x}' if v < 0x100 else f'DEF {k:<22} EQU ${v:04x}')
        else:
            print(f'; DEF {k} … 見つからない')
    # 空きの候補（FC_OBJ_BANK のおわりの 0 か $ff）
    if 'FC_OBJ_BANK' in res:
        b = res['FC_OBJ_BANK']
        s = d[b * 0x4000:(b + 1) * 0x4000]
        for fill in (0, 0xff):
            n = len(s)
            while n > 0 and s[n - 1] == fill: n -= 1
            if 0x4000 - n >= 50:
                base = 0x4000 if b else 0
                print(f'; FC_FREE の候補：バンク${b:02x} ${base + n:04x}〜（{0x4000 - n}バイト、ほかのパッチが使っていないか確かめる）')
                break
        else:
            print('; FC_FREE … このバンクのおわりに 50バイトの空きがない。ほかの空きを さがす')

    print('; DEF FC_LABGFX_BANK / FC_LABGFX … 研究所のボールの絵（64バイト）を置く空きを 自分で決める（どのバンクでもよい）')

if __name__ == '__main__':
    main(sys.argv[1])
