"""src/picpal.asm（ずかん・パソコンの ポケモンの絵を カラフルに）の「ROM ごとにちがう所」を ROM から調べる。
   python3 tools/picpal_find.py ROM.gbc
   金・銀（日本版）は 命令の並びが同じなので そのまま出る。出た DEF を .inc にして picpal.asm より前に読みこむ。
   PP_CGB_FREE（約90バイト。PP_CGB_BANK の空き）・PP_HOME_DEX（26バイト）・PP_HOME_PC（11バイト）・
   PP_wDexPicSpecies・PP_wPCPicSpecies（使われていない WRAM 2バイト）は 自分で決める（ほかのパッチと重ならないように）。
   クリスタルは 色が WRAM バンク5 にあるので PP_PALS_WRAMBANK EQU 5 を足し、見つからない所は pret/pokecrystal で確かめる。"""
import sys

def find_all(d, pat, start=0, end=None):
    toks = pat.split(); end = len(d) if end is None else end
    first = int(toks[0], 16) if toks[0] != '??' else None
    out = []; i = start
    while i < end - len(toks):
        if first is not None:
            i = d.find(bytes([first]), i, end - len(toks))
            if i < 0: break
        if all(t == '??' or d[i + k] == int(t, 16) for k, t in enumerate(toks)): out.append(i)
        i += 1
    return out

def ba(o): return o // 0x4000, (o % 0x4000) + (0x4000 if o >= 0x4000 else 0)
w = lambda d, o: d[o] | d[o + 1] << 8

def main(rom):
    d = open(rom, 'rb').read(); res = {}
    def only(name, h):
        if len(h) != 1: print(f'; {name}: {len(h)} か所（1か所でないので 手で確かめる）', [hex(x) for x in h[:6]])
        return h[0] if len(h) == 1 else None
    # ずかん：Pokedex_LoadSelectedMonTiles
    o = only('PP_DEX_HOOK', find_all(d, 'cd ?? ?? cd ?? ?? 28 ?? fa ?? ?? ea ?? ?? fa ?? ?? ea ?? ?? cd ?? ?? 11 00 90 3e ?? cd ?? ?? c9'))
    if o is not None:
        b, a = ba(o); res.update(PP_DEX_BANK=b, PP_DEX_HOOK=a, PP_Pokedex_GetSelectedMon=w(d, o + 1),
                                 PP_Pokedex_CheckSeen=w(d, o + 4), PP_wTempSpecies=w(d, o + 15), PP_wCurPartySpecies=w(d, o + 18))
    # パソコン：PCMonInfo の predef GetMonFrontpic のつぎ
    o = only('PP_PC_HOOK', find_all(d, '21 ?? ?? 3e ?? cd ?? ?? cd ?? ?? 11 00 90 3e ?? cd ?? ?? af ea ?? ??'))
    if o is not None:
        b, a = ba(o + 19); res.update(PP_PC_BANK=b, PP_PC_HOOK=a, PP_wBillsPC_MonHasMail=w(d, o + 21))
    # 色：_CGB_Pokedex_Init と _CGB_BillsPC の「$ff なら 決まった色」
    o = only('PP_DEX_FF', find_all(d, 'fa ?? ?? fe ff 20 08 21 ?? ?? cd ?? ?? 18 06 cd ?? ?? cd ?? ??'))
    if o is not None:
        b, a = ba(o + 7); res.update(PP_CGB_BANK=b, PP_DEX_FF=a, PP_PokedexQuestionMarkPalette=w(d, o + 8),
                                     PP_LoadHLPaletteIntoDE=w(d, o + 11), PP_GetMonPalettePointer=w(d, o + 16),
                                     PP_LoadPalette_White_Col1_Col2_Black=w(d, o + 19))
        h = find_all(d, '11 ?? ?? 3e ?? cd ?? ?? cd ?? ??', o - 24, o + 12)
        if h:
            res['PP_wBGPals1'] = w(d, h[-1] + 1); res['PP_wBGPals2'] = res['PP_wBGPals1'] + 0x80
            if res['PP_wBGPals1'] >= 0xd000: res['PP_PALS_WRAMBANK'] = 5   # クリスタル（WRAM バンク5）
    o = only('PP_PC_FF', find_all(d, 'fa ?? ?? fe ff 20 08 21 ?? ?? cd ?? ?? 18 09 01 ?? ?? cd ?? ?? cd ?? ??'))
    if o is not None:
        res.update(PP_PC_FF=ba(o + 7)[1], PP_BillsPCOrangePalette=w(d, o + 8), PP_wTempMonDVs=w(d, o + 16),
                   PP_GetPlayerOrMonPalettePointer=w(d, o + 19))
    for k in ['PP_DEX_BANK', 'PP_DEX_HOOK', 'PP_Pokedex_GetSelectedMon', 'PP_Pokedex_CheckSeen', 'PP_PC_BANK', 'PP_PC_HOOK',
              'PP_wBillsPC_MonHasMail', 'PP_CGB_BANK', 'PP_DEX_FF', 'PP_PC_FF', 'PP_PokedexQuestionMarkPalette',
              'PP_BillsPCOrangePalette', 'PP_LoadHLPaletteIntoDE', 'PP_LoadPalette_White_Col1_Col2_Black',
              'PP_GetMonPalettePointer', 'PP_GetPlayerOrMonPalettePointer', 'PP_wTempSpecies', 'PP_wCurPartySpecies',
              'PP_wTempMonDVs', 'PP_wBGPals1', 'PP_wBGPals2', 'PP_PALS_WRAMBANK']:
        if k in res: v = res[k]; print(f'DEF {k:<38} EQU {v}' if k == 'PP_PALS_WRAMBANK' else f'DEF {k:<38} EQU ${v:02x}' if v < 0x100 else f'DEF {k:<38} EQU ${v:04x}')
        elif k == 'PP_PALS_WRAMBANK': pass
        else: print(f'; DEF {k} … 見つからない')
    print('DEF PP_hCGBPalUpdate                       EQU $ffe7   ; 金銀（クリスタルは $ffe5）')
    print('; DEF PP_CGB_FREE（PP_CGB_BANK の空き 約90バイト）・PP_HOME_DEX（ホーム 26バイト）・PP_HOME_PC（ホーム 11バイト）')
    print('; DEF PP_wDexPicSpecies・PP_wPCPicSpecies（使われていない WRAM）… 自分で決める')

if __name__ == '__main__':
    main(sys.argv[1])
