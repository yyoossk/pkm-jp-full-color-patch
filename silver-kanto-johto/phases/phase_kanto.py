"""カントー：クリスタル版の カントーの マップを ぜんぶ 銀へ 写す（第1〜46弾 などの マップ・人・セリフ・トレーナー）。
   tools/port.py の 決まり（クリスタルの バンク b → 銀の b+$80、この MOD の バンク $60〜$7C は そのまま）。
   ここで やる こと
    1. ROM を 4MB に（MBC30）
    2. この MOD の バンクを 写す・MOD が 日本版クリスタルの 空きに 置いた データを b+$80 へ
    3. カントーの マップ（グループ26 に 足した 137 マップも）を 写して、銀の マップの 表に 入れる
    4. タイルセットの 表を のばす（$E1:$4000。銀 0〜28、MOD 37〜53）
    5. イベントフラグ $800〜 を 使えるように（第15弾）
"""
import os, sys, json
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import gsc, cmaps, port, xlat
from gsc import fo, r16

ROM4 = 0x400000
ATTR_BANK = 0xE0          # 銀の マップの 属性を バンク$25 から 動かす 先（グループ26 を のばす 場所を あける）
TS_BANK = 0xE1            # タイルセットの 表
EXT_FLAGS = 0xD60D        # $800〜 の フラグの もと（$D60D+$100 = $D70D〜$D7A9。$D6E5〜$D70C は 地名の 看板が 使う）
DATA_BANKS = (0x47, 0x59, 0x5A, 0x5B, 0x5D)   # MOD が 日本版クリスタルの 空きに 置いた データ


def w16(rom, o, v): rom[o] = v & 0xff; rom[o + 1] = v >> 8


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    rom = bytearray(rom) + bytes(ROM4 - len(rom)); rom[0x148] = 7

    # ---- 2. MOD の バンク
    rom[0x60 * 0x4000:0x7D * 0x4000] = cmod[0x60 * 0x4000:0x7D * 0x4000]
    for b in (0x7D, 0x7E) + DATA_BANKS:
        d = port.cb(b) if b < 0x60 else b
        for i in range(0x4000):
            o = b * 0x4000 + i
            if cmod[o] != corig[o]: rom[d * 0x4000 + i] = cmod[o]

    P = port.Port(rom, cmod, log)
    T = P.T
    SM = P.SM; CM = P.CM

    # ---- 4. タイルセット
    ts_old = 0x1562B
    tab = bytearray(15 * 65)
    tab[0:15 * 29] = rom[ts_old:ts_old + 15 * 29]
    for i in range(29, 37): tab[15 * i:15 * i + 15] = tab[15:30]
    corig_ts = 0x4D405 - 15                                  # 日本版クリスタルの 表（$13:$53F6、0 から）
    canim = {}; cpal = {}
    for n, ci in T.c_ts.items():
        if n in T.g_ts:
            gi = T.g_ts[n]; co = corig_ts + 15 * ci; go = ts_old + 15 * gi
            canim[r16(corig, co + 9)] = r16(rom, go + 9); cpal[r16(corig, co + 13)] = r16(rom, go + 13)
    ctab = 0x6A * 0x4000
    kanto_pal = r16(rom, ts_old + 15 * T.g_ts['TILESET_KANTO'] + 13)
    for i in range(37, 54):
        e = bytearray(cmod[ctab + 15 * i:ctab + 15 * i + 15])
        for f in (0, 3, 6): e[f] = port.cb(e[f])
        a = r16(e, 9); w16(e, 9, canim.get(a, canim.get(0x42E7, a)))
        if r16(e, 9) == a and a not in canim: P.note('tileset', 'anim %d %04X' % (i, a))
        w16(e, 13, cpal.get(r16(e, 13), kanto_pal))          # MOD の パレットの 表は あとで（第44弾）
        tab[15 * i:15 * i + 15] = e
    o = fo(TS_BANK, 0x4000); rom[o:o + len(tab)] = tab
    assert rom[0x2DB8:0x2DBB] == bytes([0x21, 0x2B, 0x56]) and rom[0x2DCA:0x2DCC] == bytes([0x3E, 0x05])
    rom[0x2DB9:0x2DBB] = bytes([0x00, 0x40]); rom[0x2DCB] = TS_BANK

    def x_ts(v):
        if v >= 37: return v
        return P.x_named(T.c_ts, T.g_ts, v, 'tileset')

    # ---- 3. マップ
    keys = [k for k in sorted(CM.hdr) if not (k[0] == 26 and k[1] in (12, 13)) and
            ((k[0] == 26 and k[1] > cmaps.G26_JP) or CM.header(k)['landmark'] >= 0x2F)]
    headers = {}
    for k in keys:
        h = bytearray(P.map(k))
        h[1] = x_ts(h[1])
        h[5] = P.x_named(T.c_lm, T.g_lm, h[5], 'landmark')
        h[6] = P.x_named(T.c_mus, T.g_mus, h[6], 'music')
        headers[k] = h
    # 銀の 属性を バンク$25 から $E0 へ（グループ26 を のばす ため）
    dst = fo(ATTR_BANK, 0x4000); moved = 0
    for k in sorted(SM.hdr):
        ho = SM.hdr[k]
        if rom[ho] != 0x25: continue
        ao = fo(0x25, r16(rom, ho + 3)); n = 12 + 12 * bin(rom[ao + 11] & 0xF).count('1')
        rom[dst:dst + n] = rom[ao:ao + n]
        rom[ho] = ATTR_BANK; w16(rom, ho + 3, 0x4000 + dst - fo(ATTR_BANK, 0x4000)); dst += n; moved += 1
    assert dst < fo(ATTR_BANK + 1, 0x4000)
    # グループ26：もとの 11 ＋ 足す マップ を バンク$25 の 空いた 所へ
    g26n = len(SM.groups[25][1]); new = [k for k in keys if k[0] == 26 and k[1] > cmaps.G26_JP]
    gp = SM.table + 2 * 25; old26 = fo(0x25, r16(rom, gp))
    blk = bytearray(rom[old26:old26 + 9 * g26n])
    for k in new: blk += headers[k]
    # 置く 場所：グループ26 の もとの 場所から（後ろの 属性は もう 動かした）
    end_used = old26 + 9 * g26n
    lo = old26
    # バンク$25 の なかで 属性が あった 所は もう 使わない。グループの 表の 後ろから 置く
    rom[lo:lo + len(blk)] = blk
    assert lo + len(blk) <= fo(0x25, 0x7FE1), hex(lo + len(blk))
    for k, h in headers.items():
        if k[0] == 26 and k[1] > cmaps.G26_JP: continue
        n = CM.name[k]
        if n not in SM.id: P.note('map', 'no silver map ' + n); continue
        ho = SM.hdr[SM.id[n]]; rom[ho:ho + 9] = h
    log.append('マップ %d（グループ26 に %d 足した）、銀の 属性 %d を $%02X へ' % (len(keys), len(new), moved, ATTR_BANK))

    # ---- 5. イベントフラグ $800〜（第15弾）：EventFlagAction $2EEB → $0018（rst $18・$20 は 使われて いない）
    assert rom[0x2EEB:0x2EF2] == bytes([0x21, 0xAA, 0xD7, 0xCD, 0xF2, 0x2E, 0xC9]) and rom[0x18] == 0xFF and not any(rom[0x19:0x20]) and rom[0x20] == 0xFF and not any(rom[0x21:0x28])
    rom[0x2EEB:0x2EF2] = bytes([0xC3, 0x18, 0x00, 0, 0, 0, 0])
    rom[0x18:0x27] = bytes([0x21, 0xAA, 0xD7, 0x7A, 0xFE, 0x08, 0xDA, 0xF2, 0x2E, 0x21, EXT_FLAGS & 0xff, EXT_FLAGS >> 8, 0xC3, 0xF2, 0x2E])
    assert max([0x800] + list(P.ext_flags.values())) < 0x800 + (0xD7AA - 0xD70D) * 8
    log.append('クリスタルだけの フラグ %d を $%03X〜 に' % (len(P.ext_flags), port.EXT_FLAG_BASE + 0x400))

    # ---- 新しい ゲームは レッドの いえ 2F から（第1〜9弾。クリスタル版と 同じ 3,3）
    assert rom[0x15286:0x1528A] == bytes([24, 7, 3, 3])
    rom[0x15286:0x1528A] = bytes(list(SM.id['REDS_HOUSE_2F']) + [3, 3])

    for kind, v in sorted(P.todo.items()):
        log.append('TODO %s %d: %s' % (kind, len(v), ' / '.join(sorted(v)[:12])))
    json.dump({k: sorted(v) for k, v in P.todo.items()}, open(os.path.join(ctx['B'], 'kanto_todo.json'), 'w'),
              ensure_ascii=False, indent=1)
    return rom
