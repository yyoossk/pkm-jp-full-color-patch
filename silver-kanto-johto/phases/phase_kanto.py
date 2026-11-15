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
DATA_BANKS = (0x13, 0x47, 0x59, 0x5A, 0x5B, 0x5D)   # $13 は この MOD の タイルごとの 色の 表（palmap）   # MOD が 日本版クリスタルの 空きに 置いた データ


def w16(rom, o, v): rom[o] = v & 0xff; rom[o + 1] = v >> 8


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    rom = bytearray(rom) + bytes(ROM4 - len(rom)); rom[0x148] = 7

    # ---- 2. MOD の バンク
    rom[0x60 * 0x4000:0x7D * 0x4000] = cmod[0x60 * 0x4000:0x7D * 0x4000]
    for b in DATA_BANKS:                     # MOD が データを 置いた クリスタルの バンクは まるごと（元と 同じ バイトも 要る）
        d = port.cb(b); rom[d * 0x4000:(d + 1) * 0x4000] = cmod[b * 0x4000:(b + 1) * 0x4000]
    for b in (0x7D, 0x7E):
        d = b
        for i in range(0x4000):
            o = b * 0x4000 + i
            if cmod[o] != corig[o]: rom[d * 0x4000 + i] = cmod[o]

    P = port.Port(rom, cmod, log)

    def is_kanto(k):
        """写す マップ：カントー（ランドマーク マサラ〜セキエイ）と ふね、グループ26 に 足した マップ。
           26・27・28ばんどうろ と トージョウの たき は 銀の 物語（ジョウトの 所で 別に 入れる）"""
        if k[0] == 26 and k[1] in (12, 13): return False
        if k[0] == 26 and k[1] > cmaps.G26_JP: return True
        lm = P.CM.header(k)['landmark']
        return 0x2F <= lm <= 0x5A or lm == 0x5F
    T = P.T
    SM = P.SM; CM = P.CM

    # ---- マップの シーンの 表（第21・70弾 など）。$25:$4000 → $E1:$4400
    C_EV, C_EXT, S_EXT = 0xDA65, 0xD901, EXT_FLAGS
    free = list(range(0xD771, 0xD78D))
    def scene_tab(r, b, a):
        q = fo(b, a); out = []
        while r[q] != 0xFF: out.append((r[q], r[q + 1], r16(r, q + 2))); q += 4
        return out
    ctab_s = scene_tab(cmod, cmod[0x210F], r16(cmod, 0x2112))
    otab_s = {(g, m): a for g, m, a in scene_tab(corig, corig[0x210F], r16(corig, 0x2112))}
    assert rom[0x1F46:0x1F4A] == bytes([0x3E, 0x25, 0xD7, 0x21]) and r16(rom, 0x1F4A) == 0x4000
    stab = scene_tab(rom, 0x25, 0x4000)
    s_by_name = {SM.name[(g, m)]: a for g, m, a in stab}
    have = {(g, m) for g, m, a in stab}
    amap = {}
    def x_addr(a, name):
        if a in amap: return amap[a]
        if name in s_by_name and otab_s.get(CM.id.get(name)) == a: r = s_by_name[name]
        elif 0xDA01 <= a < C_EV: r = a - (C_EXT - S_EXT)
        elif C_EV <= a < C_EV + 0x100:
            r = free.pop(0)
            for bit in range(8): P.force[(a - C_EV) * 8 + bit] = (r - S_EXT) * 8 + bit
        else: r = free.pop(0)
        amap[a] = r; return r
    newtab = list(stab)
    for g, m, a in ctab_s:
        if not is_kanto((g, m)): continue
        sg, sm = P.x_map(g, m)
        r = x_addr(a, CM.name[(g, m)])
        newtab = [e for e in newtab if (e[0], e[1]) != (sg, sm)] + [(sg, sm, r)]
    # アセンブリだけが つかう バイト：$DACE（フラグ $348〜。78:5E9E など）、$D836（MOD の 変数。47:7E4E〜7F13）
    x_addr(0xDACE, None)
    amap[0xD836] = free.pop(0)
    blob = b''.join(bytes([g, m, a & 0xff, a >> 8]) for g, m, a in newtab) + b'\xff'
    o = fo(TS_BANK, 0x4400); rom[o:o + len(blob)] = blob
    rom[0x1F47] = TS_BANK; w16(rom, 0x1F4A, 0x4400)
    log.append('シーンの表 %d（WRAM %s）' % (len(newtab), ' '.join('%04X>%04X' % kv for kv in sorted(amap.items()))))

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
        if r16(e, 13) in cpal: w16(e, 13, cpal[r16(e, 13)])  # クリスタルの もとの palmap → 銀の もの。MOD の palmap は $93 に（読む 所を フック）
        tab[15 * i:15 * i + 15] = e
    o = fo(TS_BANK, 0x4000); rom[o:o + len(tab)] = tab
    assert rom[0x2DB8:0x2DBB] == bytes([0x21, 0x2B, 0x56]) and rom[0x2DCA:0x2DCC] == bytes([0x3E, 0x05])
    rom[0x2DB9:0x2DBB] = bytes([0x00, 0x40]); rom[0x2DCB] = TS_BANK

    def x_ts(v):
        if v >= 37: return v
        return P.x_named(T.c_ts, T.g_ts, v, 'tileset')

    # ---- 3. マップ
    keys = [k for k in sorted(CM.hdr) if is_kanto(k)]
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

    # タマムシの ポケモンセンターの ミナキ（クリスタルの スイクンの 話。銀には ない）は 出さない：
    # 人の フラグを いつも 立って いる EVENT_INITIALIZED_EVENTS に（BeastsCheck・MonCheck も 使われなく なる）
    SM.rom = rom
    ev = SM.events(SM.id['CELADON_POKECENTER_1F'])
    o = ev['end'] - 13 * len(ev['objects'])
    hid = 0
    for i, ob in enumerate(ev['objects']):
        if ob[0] == T.g_spr['SPRITE_SUPER_NERD']:
            q = o + 13 * i + 11; w16(rom, q, T.g_ev['EVENT_INITIALIZED_EVENTS']); hid += 1
    assert hid == 1, hid

    # ---- WRAM の アドレス（テキストの 数・名前、readmem など）を 銀の アドレスへ
    import wramxl
    wm = wramxl.build(corig, open(os.path.join(H, 'roms', 'gin1.gbc'), 'rb').read())
    wm.update({0xD067: 0xCF93, 0xD068: 0xCF94, 0xD21C: 0xD0C6, 0xD833: 0xD7A3, 0xDC3F: 0xD989})
    wm.update(amap)
    for a, q in P.ram_pos:
        if a in wm: w16(rom, q, wm[a])
        else: P.note('wram', '%04X' % a)

    # ---- この MOD の アセンブリ（callasm の 先）を 銀の アドレスへ
    import asmport, pickle
    g1 = open(os.path.join(H, 'roms', 'gin1.gbc'), 'rb').read()
    cache = os.path.join(ctx['B'], 'wram_map.pkl')
    Hm = asmport.Home(corig, g1)
    if os.path.exists(cache): wm2 = pickle.load(open(cache, 'rb'))
    else:
        wm2 = wramxl.build_all(corig, g1, Hm); pickle.dump(wm2, open(cache, 'wb'))
    wm2 = dict(wm2); wm2.update(wm)
    TR = asmport.Translator(cmod, corig, g1, wm2, Hm, log)
    # 殿堂入りの 画面（$59:6DCE・6E08）は クリスタルの WRAM バンク5（色・LYOverrides）を 使う → 銀の WRAM0 へ
    wm59 = dict(wm2); wm59.update(asmport.WRAM_EXTRA)
    for a in range(0xD000, 0xD100): wm59[a] = 0xC200 + (a - 0xD000)       # 色
    for a in range(0xD100, 0xD190): wm59[a] = 0xC700 + (a - 0xD100)       # wLYOverrides
    for a in range(0xD190, 0xD195): wm59[a] = free.pop(0)                 # バンク5 の 作業用
    wm59.update({0xC568: 0xC468, 0xCE95: 0xCD95})                         # タイルマップ・属性マップ（-$100）
    TR59 = asmport.Translator(cmod, corig, g1, wm59, Hm, log); TR59.wm = wm59; TR59.nosvbk = True
    for x in sorted(P.todo.get('asm', ())):
        bb, aa = [int(v, 16) for v in x.split()[1].split(':')]
        (TR59 if bb == 0x59 else TR).routine(rom, bb, aa, x.split()[1])
    TR.unres.update(TR59.unres)
    P.todo['asm'] = {'%s %s' % (k, ' '.join(v)) for k, v in TR.unres.items()}

    # ---- 5. イベントフラグ $800〜（第15弾）：EventFlagAction $2EEB → $0018（rst $18・$20 は 使われて いない）
    assert rom[0x2EEB:0x2EF2] == bytes([0x21, 0xAA, 0xD7, 0xCD, 0xF2, 0x2E, 0xC9]) and rom[0x18] == 0xFF and not any(rom[0x19:0x20]) and rom[0x20] == 0xFF and not any(rom[0x21:0x28])
    rom[0x2EEB:0x2EF2] = bytes([0xC3, 0x18, 0x00, 0, 0, 0, 0])
    rom[0x18:0x27] = bytes([0x21, 0xAA, 0xD7, 0x7A, 0xFE, 0x08, 0xDA, 0xF2, 0x2E, 0x21, EXT_FLAGS & 0xff, EXT_FLAGS >> 8, 0xC3, 0xF2, 0x2E])
    assert max([0x800] + list(P.ext_flags.values())) < 0x800 + (0xD7AA - 0xD70D) * 8
    log.append('クリスタルだけの フラグ %d を $%03X〜 に' % (len(P.ext_flags), port.EXT_FLAG_BASE + 0x400))

    # ---- 人の絵の 2つめの 表（$67〜$7A。第14弾 など）：銀の バンク5 の もとの タイルセットの 表の 所（もう 使わない）へ
    ct2 = fo(5, 0x7F34); n2 = 0x7A - 0x66
    tab2 = bytearray(cmod[ct2:ct2 + 6 * n2])
    kitn = 0
    for i in range(n2):
        e = tab2[6 * i:6 * i + 6]
        if e[3] >= 0x80:                                  # 追加機能キットの バンクに ある 絵 → $E1:$7000〜 へ
            src = fo(e[3], r16(e, 0)); size = e[2] or 0x100
            d = 0x7000 + 0x80 * kitn; kitn += 1; rom[fo(TS_BANK, d):fo(TS_BANK, d) + size] = cmod[src:src + size]
            e[3] = TS_BANK; e[0] = d & 0xff; e[1] = d >> 8
        elif e[3] < 0x60: e[3] = port.cb(e[3])
        tab2[6 * i:6 * i + 6] = e
    T2 = 0x562B; rom[fo(5, T2):fo(5, T2) + len(tab2)] = tab2
    virt = T2 - 0x66 * 6; hp = T2 + len(tab2)
    for off, d in ((0x14286, 0), (0x142EF, 4), (0x1430C, 5)):
        assert rom[off] == 0x21 and r16(rom, off + 1) == 0x47B0 + d
        code = bytes([0xFE, 0x67, 0x30, 0x04, 0x21]) + (0x47B0 + d).to_bytes(2, 'little') + bytes([0xC9, 0x21]) + \
            ((virt + d) & 0xffff).to_bytes(2, 'little') + bytes([0xC9])
        rom[fo(5, hp):fo(5, hp) + len(code)] = code
        rom[off] = 0xCD; w16(rom, off + 1, hp); hp += len(code)
    assert hp <= 0x562B + 15 * 29

    # ---- この MOD が 変えた 人の絵（主人公＝レッドの 絵・自転車・サカキ・ボール・岩の 色）を 銀の 表へ
    S_OW = 0x147B0; C_OW = 0x14727
    for i in range(1, 0x67):
        ce = bytearray(cmod[C_OW + 6 * (i - 1):C_OW + 6 * i]); oe = corig[C_OW + 6 * (i - 1):C_OW + 6 * i]
        b, a = ce[3], r16(ce, 0); size = {1: 0x180, 2: 0xC0, 3: 0x40}.get(ce[4], ce[2])   # 歩く 絵は 止まり 12 ＋ 歩き 12 タイル
        src = fo(b, a)
        gfx_changed = b < 0x80 and cmod[src:src + size] != corig[src:src + size]
        if bytes(ce) == oe and not gfx_changed: continue
        if b < 0x60:
            d = fo(port.cb(b), a); rom[d:d + size] = cmod[src:src + size]; ce[3] = port.cb(b)
        si = P.x_sprite(i)
        rom[S_OW + 6 * (si - 1):S_OW + 6 * si] = ce
        log.append('人の絵 %02X → 銀 %02X を クリスタル版の ものに' % (i, si))

    # ---- 外の マップの 人の絵の 表（銀は 1グループ 11まで）：カントーの グループは、その グループの 外の マップで 使う 絵
    OUT_TAB, OUT_N = 0x465E, 11
    from collections import Counter
    use = {}
    for k in keys:
        h = CM.header(k)
        if h['env'] not in (1, 2): continue
        sg, sm = P.x_map(*k)
        for ob in CM.events(k)['objects']:
            if ob[0] and ob[0] < 0xF0: use.setdefault(sg, Counter())[P.x_sprite(ob[0])] += 1
    lp = hp
    for g, cnt in sorted(use.items()):
        spr = [s for s, n in cnt.most_common()]
        if len(spr) > OUT_N: P.note('outdoor', 'group %d: %d 絵（%s は 入らない）' % (g, len(spr), spr[OUT_N:])); spr = spr[:OUT_N]
        blob = bytes(spr + [0] * (OUT_N - len(spr)))
        rom[fo(5, lp):fo(5, lp) + OUT_N] = blob
        w16(rom, fo(5, OUT_TAB) + 2 * (g - 1), lp); lp += OUT_N
    assert lp <= 0x562B + 15 * 29, hex(lp)

    # ---- 新しい ゲームは レッドの いえ 2F から（第1〜9弾。クリスタル版と 同じ 3,3）
    assert rom[0x15286:0x1528A] == bytes([24, 7, 3, 3])
    rom[0x15286:0x1528A] = bytes(list(SM.id['REDS_HOUSE_2F']) + [3, 3])

    ctx['kanto_trainers'] = P.trainers; ctx['amap'] = amap
    for kind, v in sorted(P.todo.items()):
        log.append('TODO %s %d: %s' % (kind, len(v), ' / '.join(sorted(v)[:12])))
    json.dump({k: sorted(v) for k, v in P.todo.items()}, open(os.path.join(ctx['B'], 'kanto_todo.json'), 'w'),
              ensure_ascii=False, indent=1)
    return rom
