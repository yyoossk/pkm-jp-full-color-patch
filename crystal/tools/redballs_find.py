"""src/redballs.asm（戦闘・ずかんのボールの印を赤白に）の「ROM ごとにちがう所」を ROM から調べる。
   python3 tools/redballs_find.py ROM.gbc
   金・銀（日本版）は 命令の並びが同じなので そのまま出る。出た DEF を .inc にして redballs.asm より前に読みこむ
   （例：rgbasm -P src/redballs_silver.inc ... src/redballs.asm。または redballs.asm の先頭の DEF を書きかえる）。
   RB_HUD_FREE（10バイト）・RB_ADDR（約100バイト）は 空いている所を自分で決める（ほかのパッチと重ならないように）。
   クリスタルは 戦闘の色の処理（wOBPals が WRAM バンク5）と ずかんの絵の読み方がちがうので、見つからない所は
   pret/pokecrystal を見て 手で直す（README の「クリスタルに入れるとき」）。"""
import sys

def find_all(d, pat, start=0, end=None):
    """pat：16進の文字列。?? は なんでもよい"""
    toks = pat.split()
    end = len(d) if end is None else end
    out = []
    for i in range(start, end - len(toks)):
        ok = True
        for k, t in enumerate(toks):
            if t != '??' and d[i + k] != int(t, 16):
                ok = False; break
        if ok: out.append(i)
    return out

def ba(o):
    return o // 0x4000, (o % 0x4000) + (0x4000 if o >= 0x4000 else 0)

def main(rom):
    d = open(rom, 'rb').read()
    res = {}
    def one(name, hits, fmt):
        if len(hits) != 1:
            print(f'; {name}: {len(hits)} か所（1か所でないので 手で確かめる）', [hex(h) for h in hits[:8]])
            return None
        return fmt(hits[0])
    # 手持ちの数のボールの絵（元気のボール。金銀クリスタルで同じ絵）
    h = find_all(d, '00 00 1c 1c 22 3e 51 6f 41 7f 7f 41 3e 22 1c 1c')
    if one('RB_BALLGFX', h, lambda o: None) is None and len(h) != 1:
        pass
    else:
        b, a = ba(h[0]); res['RB_BALLGFX_BANK'] = b; res['RB_BALLGFX'] = a
    # LoadTrainerHudOAM の ld a, PAL_BATTLE_OB_YELLOW / ld [hli], a
    h = find_all(d, '1a 22 3e 03 22')
    if len(h) == 1:
        res['RB_HUD_ATTR'] = ba(h[0] + 2)[1]
        if 'RB_BALLGFX_BANK' in res and ba(h[0])[0] != res['RB_BALLGFX_BANK']:
            print('; ボールの絵と LoadTrainerHudOAM のバンクがちがう（RB_HUD_FREE は LoadTrainerHudOAM のバンクに置く）')
    else:
        one('RB_HUD_ATTR', h, None)
    # つかまえた印（ExpBarGFX の 9枚目）
    h = find_all(d, '00 00 78 78 dc dc fc fc 84 84 84 84 78 78 00 00')
    if len(h) == 1:
        b, a = ba(h[0]); res['RB_CAUGHT_BANK'] = b; res['RB_CAUGHT_GFX'] = a
    else:
        one('RB_CAUGHT_GFX', h, None)
    # _CGB_FinishBattleScreenLayout のおわり（金銀：wOBPals1 palette 2 = $c250）
    h = find_all(d, '21 ?? ?? 11 50 c2 01 30 00 cd ?? ?? cd ?? ?? c9')
    if len(h) == 1:
        o = h[0]; b, a = ba(o)
        res['RB_BATTLEPAL_BANK'] = b; res['RB_BATTLEPAL_HOOK'] = a
        res['RB_BattleObjectPals'] = d[o + 1] | d[o + 2] << 8
        res['RB_ApplyAttrmap'] = d[o + 13] | d[o + 14] << 8
    else:
        # クリスタル：ld hl, BattleObjectPals / ld de, wOBPals1 palette 2 ($d050) / ld bc, 6 palettes / ld a, 5 / call FarCopyWRAM / call ApplyAttrmap / ret
        hc = find_all(d, '21 ?? ?? 11 50 d0 01 30 00 3e 05 cd ?? ?? cd ?? ?? c9')
        if len(hc) == 1:
            o = hc[0]; b, a = ba(o)
            res['RB_BATTLEPAL_BANK'] = b; res['RB_BATTLEPAL_HOOK'] = a
            res['RB_BattleObjectPals'] = d[o + 1] | d[o + 2] << 8
            res['RB_ApplyAttrmap'] = d[o + 15] | d[o + 16] << 8
            res['crystal'] = True
        else:
            one('RB_BATTLEPAL_HOOK', h, None)
    # ずかんの絵（vTiles2 tile $31 = $9310 に PokedexLZ を読む 2か所）
    h1 = find_all(d, '21 ?? ?? 11 10 93 01 ?? ?? cd ?? ?? c9')
    h2 = find_all(d, '21 ?? ?? 11 10 93 cd ?? ??')
    lz = lambda o: d[o + 1] | d[o + 2] << 8
    # 同じバンクで 同じ PokedexLZ を読んでいる 2か所の組
    pairs = [(x, y) for x in h1 for y in h2 if ba(x)[0] == ba(y)[0] and lz(x) == lz(y) and d[x + 8] == ba(x)[0]]
    if len(pairs) > 1:
        print('; ずかんの絵を読む所が', len(pairs), '組ある。いちばん前の組（ふつうの ずかん）を使う：', [(hex(x), hex(y)) for x, y in pairs[:4]])
    if pairs:
        o, o2 = pairs[0]; b, a = ba(o)
        res['RB_DEX_BANK'] = b; res['RB_DEX_LOAD1'] = a; res['RB_DEX_LOAD2'] = ba(o2)[1]
        res['RB_PokedexLZ'] = lz(o); res['RB_DEX_TILES'] = d[o + 7]
    else:
        print('; ずかんの絵を読む所が見つからない')
    # WRAM（金銀の _CGB_FinishBattleScreenLayout の hlcoord 0, 0, wAttrmap）
    if 'RB_BATTLEPAL_HOOK' in res:
        o = res['RB_BATTLEPAL_BANK'] * 0x4000 + res['RB_BATTLEPAL_HOOK'] - 0x4000
        h = find_all(d, '21 ?? ?? 01 68 01 3e 02 cd', o - 0x80, o)
        if h: res['RB_wAttrmap'] = d[h[-1] + 1] | d[h[-1] + 2] << 8
        if res.get('crystal'):
            res['RB_wOBPals1'] = 0xd040; res['RB_wBGPals1'] = 0xd000
            res['RB_PALS_WRAMBANK'] = 5; res['RB_BATTLEPAL_LEN'] = 18
        else:
            res['RB_wOBPals1'] = 0xc240; res['RB_wBGPals1'] = 0xc200
    order = ['RB_BALLGFX_BANK', 'RB_BALLGFX', 'RB_HUD_ATTR', 'RB_CAUGHT_BANK', 'RB_CAUGHT_GFX',
             'RB_BATTLEPAL_BANK', 'RB_BATTLEPAL_HOOK', 'RB_BattleObjectPals', 'RB_ApplyAttrmap',
             'RB_DEX_BANK', 'RB_DEX_LOAD1', 'RB_DEX_LOAD2', 'RB_PokedexLZ', 'RB_DEX_TILES',
             'RB_wOBPals1', 'RB_wBGPals1', 'RB_wAttrmap', 'RB_PALS_WRAMBANK', 'RB_BATTLEPAL_LEN']
    for k in order:
        if k in res:
            v = res[k]
            print(f'DEF {k:<22} EQU {v}' if k in ('RB_DEX_TILES', 'RB_PALS_WRAMBANK', 'RB_BATTLEPAL_LEN') else f'DEF {k:<22} EQU ${v:02x}' if v < 0x100 else f'DEF {k:<22} EQU ${v:04x}')
        elif k not in ('RB_PALS_WRAMBANK', 'RB_BATTLEPAL_LEN'):
            print(f'; DEF {k} … 見つからない')
    print('; DEF RB_HUD_FREE … RB_HUD_ATTR と同じバンクの空き（10バイト）を決める')
    print('; DEF RB_BANK / RB_ADDR … 新しい処理（約100バイト）を置く空きを決める')

if __name__ == '__main__':
    main(sys.argv[1])
