"""クリスタル版の しくみの 小さな 直しを 金へ（弾ごとに 足していく）。"""
def fo(b, a): return b * 0x4000 + a - 0x4000

W_WINLOSS_BANK = 0xD7A2      # クリスタル版 $DA5C（イベントフラグの あと の あき）。D7A0〜D7A3 の うち D7A1 は 殿堂入り

def free25(g, n):
    """バンク 25 の うしろの あき（追加機能パッチと 合わせる ときは 見なおす）"""
    s = g[0x25 * 0x4000:0x26 * 0x4000]; i = len(s)
    while i > 0 and s[i - 1] in (0, 0xFF): i -= 1
    a = 0x4000 + i + 2; assert a + n <= 0x7FF0
    return a

def p54_winloss(g, log):
    """第54弾：トレーナーの 負けた／勝った ときの セリフを、winlosstext を 書いた スクリプトの バンクから 読む"""
    o = fo(0x25, 0x702F); assert g[o:o + 3] == bytes([0x21, 0x5C, 0xCF])
    a = free25(g, 10)
    g[fo(0x25, a):fo(0x25, a) + 10] = bytes([0xFA, 0x52, 0xD1, 0xEA, W_WINLOSS_BANK & 0xFF, W_WINLOSS_BANK >> 8,
                                            0x21, 0x5C, 0xCF, 0xC9])           # ld a,[wScriptBank] / ld [..],a / ld hl,wWinTextPointer
    g[o:o + 3] = bytes([0xCD, a & 0xFF, a >> 8])
    o = 0x38C0
    assert bytes(g[o:o + 15]) == bytes.fromhex('fa0bd1fe011805215ccf180cfae3cf')
    W = W_WINLOSS_BANK
    code = bytes([0xFA, 0xE3, 0xCF, 0x21, 0x5C, 0xCF, 0xA7, 0x28, 0x03, 0x21, 0x5E, 0xCF, 0x2A, 0x66, 0x6F,
                  0xFA, W & 0xFF, W >> 8, 0xA7, 0x20, 0x03, 0xCD, 0xEC, 0x2C,
                  0xF5, 0xAF, 0xEA, W & 0xFF, W >> 8, 0xF1,
                  0xCD, 0x66, 0x33, 0xCD, 0xAE, 0x33, 0xCD, 0x26, 0x0A, 0xC9])
    assert bytes(g[o + 0x1B:o + 0x28]) == bytes.fromhex('cdec2ccd6633cdae33cd260ac9')
    assert len(code) == 0x28
    g[o:o + 0x28] = code
    log.append('第54弾 winlosstext：25:%04X、ホーム 38C0（バンクは %04X）' % (a, W))

def p69_ledges(g, log):
    """第69弾：赤の マップ（クリスタル タイルセット 40 → 金 36）の 段差を 赤と 同じに（手前から とびこえる・ほかは かべ）。
       金の TryStep（04:4176 の call CheckLandPerms）→ 04:7F80（あき）"""
    from gold_safari import A
    o = fo(0x04, 0x4176); assert g[o:o + 3] == bytes([0xCD, 0x9E, 0x43])
    h = 0x7F80; assert not any(g[fo(0x04, h):fo(0x04, h) + 0x40])
    a = A(h)
    a.db(0xCD, 0x9E, 0x43, 0xD8)                         # call CheckLandPerms / ret c
    a.db(0xFA, 0x74, 0xD0, 0xFE, 36); a.jr(0x20, 'walk')  # wMapTileset == 36
    a.db(0xFA, 0x5C, 0xCF, 0x5F, 0xE6, 0xF0, 0xFE, 0xA0); a.jr(0x20, 'walk')
    a.db(0x7B, 0xE6, 0x07, 0x5F, 0x16, 0x00, 0x21, 0x1E, 0x42, 0x19)
    a.db(0xFA, 0x59, 0xCF, 0xA6); a.jr(0x28, 'wall')
    a.db(0xE1, 0x11, 0x16, 0x00, 0xCD, 0x45, 0x3D)       # pop hl / ld de,SFX_JUMP_OVER_LEDGE / call PlaySFX
    a.db(0x3E, 0x03, 0xCD, 0x5F, 0x42, 0x3E, 0x07, 0x37, 0xC9)
    a.L('wall'); a.db(0x37, 0xC9)
    a.L('walk'); a.db(0xA7, 0xC9)
    b = a.fin(); g[fo(0x04, h):fo(0x04, h) + len(b)] = b
    g[o + 1] = h & 0xFF; g[o + 2] = h >> 8
    log.append('第69弾 段差：04:4176 → 04:%04X（%d バイト）' % (h, len(b)))

def p27_cut(g, M, log):
    """第27弾：赤の タイルセット（クリスタル 40 → 金 36）でも いあいぎり（赤の 木 $3C/$3F/$3D と、草など は タイルセット 3 と 同じ）。
       金の CutTreeBlockPointers（03:48F5、ld hl は 03:487D）を 03 の うしろへ 移して 36 を 足す"""
    o = fo(0x03, 0x487D); assert g[o:o + 3] == bytes([0x21, 0xF5, 0x48])
    t = fo(0x03, 0x48F5); old = []
    while g[t] != 0xFF: old.append((g[t], g[t + 1] | g[t + 2] << 8)); t += 3
    ml = fo(0x03, 0x4881); lst = b''
    while M[ml] != 0xFF: lst += M[ml:ml + 3]; ml += 3
    lst += b'\xff'
    s_ = g[0x03 * 0x4000:0x04 * 0x4000]; i = len(s_)
    while s_[i - 1] in (0, 0xFF): i -= 1
    base = 0x4000 + i + 2; tab = base; la = tab + 3 * (len(old) + 1) + 1
    data = b''.join(bytes([ts, p & 0xFF, p >> 8]) for ts, p in old) + bytes([36, la & 0xFF, la >> 8, 0xFF]) + lst
    assert base + len(data) <= 0x8000
    g[fo(0x03, base):fo(0x03, base) + len(data)] = data
    g[o + 1] = tab & 0xFF; g[o + 2] = tab >> 8
    log.append('第27弾 いあいぎり：表 03:%04X（タイルセット 36 を 足す）' % tab)

def p32_spawns(g, M, log):
    """赤の 町の 飛ぶ所・負けた ときに もどる 所（SpawnPoints。クリスタル版 05:5346 → 金 05:5286、番号は 同じ）と、
       第32弾：もどる 所が ない ときは マサラ（スポーン 2）。クリスタル 04:63E8 → 金 04:6795（04:7FC0 へ）"""
    import sys; sys.path.insert(0, '/home/claude/work/scripts')
    import c2g
    cm = fo(0x05, 0x5346); gm = fo(0x05, 0x5286); n = 0
    for i in range(14):                 # カントー（0〜13）だけ。ジョウトは 金の 町の まま
        c = M[cm + 4 * i:cm + 4 * i + 4]
        nm = c2g.CMAP.get((c[0], c[1])); nm = c2g.MAPALIAS.get(nm, nm)
        if nm not in c2g.GMAP or nm in ('RedsHouse2F',): continue
        gg, gn = c2g.GMAP[nm]; new = bytes([gg, gn, c[2], c[3]])
        if bytes(g[gm + 4 * i:gm + 4 * i + 4]) != new: g[gm + 4 * i:gm + 4 * i + 4] = new; n += 1
    o = fo(0x04, 0x6795); assert bytes(g[o:o + 8]) == bytes.fromhex('793801afea20cfc9')
    h = 0x7FC0; assert not any(g[fo(0x04, h):fo(0x04, h) + 10])
    g[fo(0x04, h):fo(0x04, h) + 9] = bytes.fromhex('793802' '3e02' 'ea20cf' 'c9')
    g[o:o + 3] = bytes([0xC3, h & 0xFF, h >> 8])
    log.append('スポーン：%d こ 赤の 位置に、負けた ときの もどる 所 04:%04X' % (n, h))

def pokepic_color(g, log):
    """pokepic の 窓の ポケモンを 色つきに（クリスタル版 02:7F9D と 同じ。金 _CGB_Pokepic 02:5966 → 02:7C30）"""
    o = fo(0x02, 0x5966); assert bytes(g[o:o + 5]) == bytes.fromhex('3e00cd875a')
    h = 0x7C30; assert not any(g[fo(0x02, h):fo(0x02, h) + 0x22])   # 02:7C28〜7C5F（金の 追加機能パッチは 7C60〜）
    code = bytes.fromhex('e5c5' 'fafecf' 'cd7a5b' 'e5' '1138c2' 'cd715a' 'e1' '11b8c2' 'cd715a'
                         '3e01e0e7' 'c1e1' '3e07' 'c3875a')
    g[fo(0x02, h):fo(0x02, h) + len(code)] = code
    g[o:o + 5] = bytes([0xCD, h & 0xFF, h >> 8, 0, 0])
    log.append('pokepic の 色：02:%04X（%d バイト）' % (h, len(code)))

def p75_copyobject(g, log):
    """第75弾：appear で 画面に いる 人を 2人に しない（CopyObjectStruct：すでに 人の 入れものが あれば もどる）。
       金 02:46D7 → 02:7C54"""
    o = fo(0x02, 0x46D7); assert bytes(g[o:o + 5]) == bytes.fromhex('cde627a7c0')
    h = 0x7C54; assert not any(g[fo(0x02, h):fo(0x02, h) + 10])
    g[fo(0x02, h):fo(0x02, h) + 10] = bytes([0x0A, 0xFE, 0xFF, 0xC0, 0xCD, 0xE6, 0x27, 0xC3, 0xDA, 0x46])
    g[o:o + 3] = bytes([0xC3, h & 0xFF, h >> 8])
    log.append('第75弾 CopyObjectStruct：02:%04X' % h)

def p75_marts(g, M, log):
    """MOD のカントーのショップの品ぞろえ（赤の品ぞろえ）。金の 05:66C7-6755 に詰めなおす"""
    CT, GT = fo(5, 0x64C3), fo(5, 0x65EA)
    assert g[GT + 36] == 0xC7 and g[GT + 37] == 0x66
    out = bytearray(); ptr = []
    for k in range(18, 34):
        p = M[CT + 2 * k] | M[CT + 2 * k + 1] << 8; o = fo(5, p); n = M[o]
        ptr.append(0x66C7 + len(out)); out += bytes([n]) + M[o + 1:o + 1 + n] + b'\xff'
    assert len(out) <= 0x6756 - 0x66C7
    g[fo(5, 0x66C7):fo(5, 0x66C7) + len(out)] = out
    for i, a in enumerate(ptr):
        g[GT + 2 * (18 + i)] = a & 255; g[GT + 2 * (18 + i) + 1] = a >> 8
    log.append('第75弾 ショップ：カントー16か所の品ぞろえ（%d バイト）' % len(out))


def p55_koga(g, TB, log):
    """第55弾：セキチクジムの キョウ（KOGA の 2ばん）は 「ジムリーダー」の 名前・カントーの ジムリーダーの 曲。
       ホーム $3F80／$3F95（クリスタル版と 同じ 住所。金では あき）"""
    CLS, OID = 0xD10A, 0xD10D
    assert not any(g[0x3F80:0x3FB0])
    a = bytes([0x79, 0xFE, 0x0F, 0x20, 0x0A, 0xFA, OID & 255, OID >> 8, 0xFE, 0x02, 0x79, 0x20, 0x02, 0x3E, 0x11,
               0x21, 0xC1, 0xD1, 0xFE, 0x09, 0xC9])
    b = bytes([0xFA, CLS & 255, CLS >> 8, 0xFE, 0x0F, 0x20, 0x09, 0xFA, OID & 255, OID >> 8, 0xFE, 0x02, 0x20, 0x02,
               0x37, 0xC9, 0x21, 0x77, 0x4C, 0xC3, 0x79, 0x50])
    g[0x3F80:0x3F80 + len(a)] = a; assert len(a) <= 0x15
    g[0x3F95:0x3F95 + len(b)] = b
    for bk, ad in ((0x0E, 0x5511), (TB, 0x5511), (0x0E, 0x553D), (TB, 0x553D)):   # GetTrainerClassName・GetOTName
        o = fo(bk, ad); assert g[o:o + 6] == bytes.fromhex('21c1d179fe09'), (hex(bk), g[o:o + 6].hex())
        g[o:o + 6] = bytes.fromhex('cd803f000000')
    o = fo(0x0F, 0x5071); assert g[o:o + 3] == bytes.fromhex('21774c'); g[o:o + 3] = bytes.fromhex('c3953f')
    log.append('第55弾 キョウ：ホーム 3F80／3F95、0E・%02X:5511／553D、0F:5071' % TB)


def p57_evos(g, M, log):
    """第57弾：つうしん進化を Lv37 に（MOD の 進化の 表を そのまま。長さは 同じ）"""
    def tab(R, first):
        return R.find(bytes([first & 255, first >> 8]), fo(0x10, 0x4000), fo(0x11, 0x4000))
    mt = tab(M, 0x6949)
    import asmx as RX
    gt = tab(g, RX.GJ['BulbasaurEvosAttacks'])
    def part(R, t, i):
        p = R[t + 2 * i] | R[t + 2 * i + 1] << 8; o = fo(0x10, p); e = o
        while R[e]: e += 4 if R[e] == 5 else 3
        return o, e
    n = 0
    for i in range(251):
        mo, me = part(M, mt, i); go, ge = part(g, gt, i)
        if M[mo:me] != g[go:ge]:
            assert me - mo == ge - go, i
            g[go:ge] = M[mo:me]; n += 1
    log.append('第57弾 進化：%d しゅるい' % n)


def p57_hm_lugia(g, M, log):
    """MOD：どの ポケモンも ひでんマシン 1〜7 を おぼえられる（基礎データの わざマシンの 印）。
       ルギア・ホウオウは Lv60 で エアロブラスト／せいなるほのお（MOD の 覚える技）"""
    import asmx as RX
    mo = fo(0x14, 0x54BA); go = fo(0x14, RX.GJ['BaseData'])
    for i in range(251):
        m30, m31 = M[mo + 32 * i + 30], M[mo + 32 * i + 31]
        g[go + 32 * i + 30] |= m30 & 0xFC; g[go + 32 * i + 31] |= m31 & 0x01
    gt = g.find(bytes([RX.GJ['BulbasaurEvosAttacks'] & 255, RX.GJ['BulbasaurEvosAttacks'] >> 8]), fo(0x10, 0x4000), fo(0x11, 0x4000))
    mt = M.find(bytes([0x49, 0x69]), fo(0x10, 0x4000), fo(0x11, 0x4000))
    def ent(R, t, i):
        p = R[t + 2 * i] | R[t + 2 * i + 1] << 8; o = fo(0x10, p); s = o
        while R[o]: o += 4 if R[o] == 5 else 3
        o += 1
        while R[o]: o += 2
        return p, bytes(R[s:o + 1])
    p249 = ent(g, gt, 248)[0]
    blob = ent(M, mt, 248)[1] + ent(M, mt, 249)[1] + ent(g, gt, 250)[1]
    end = p249 + len(blob); assert end <= 0x8000
    tail = g[fo(0x10, ent(g, gt, 250)[0]) + len(ent(g, gt, 250)[1]):fo(0x11, 0x4000)]
    assert not any(b not in (0, 0xFF) for b in tail)
    g[fo(0x10, p249):fo(0x10, p249) + len(blob)] = blob
    a = p249
    for k, i in enumerate((248, 249, 250)):
        g[gt + 2 * i] = a & 255; g[gt + 2 * i + 1] = a >> 8
        a += len((ent(M, mt, 248)[1], ent(M, mt, 249)[1], b'')[k]) if k < 2 else 0
    log.append('第57弾 ひでんマシン：251 しゅるい、ルギア・ホウオウの 覚える技（〜10:%04X）' % end)


def apply(g, log, M=None, TB=None):
    if TB is not None: p55_koga(g, TB, log)
    p75_copyobject(g, log)
    pokepic_color(g, log)
    if M is not None: p32_spawns(g, M, log)
    if M is not None: p27_cut(g, M, log)
    p69_ledges(g, log)
    p54_winloss(g, log)
    if M is not None: p75_marts(g, M, log)
    if M is not None: p57_evos(g, M, log)
    if M is not None: p57_hm_lugia(g, M, log)
