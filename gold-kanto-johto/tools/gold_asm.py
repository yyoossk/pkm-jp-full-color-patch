"""クリスタル版の マップの スクリプトが よぶ 小さな asm（callasm など）を、金の 形に 書きなおして 置く。
   E.loc[(クリスタルの バンク, 住所)] に 登録すると、スクリプトの ポインターが そこへ 読みかえられる。
   ・AUTO：asmx.xlat で 機械的に 読みかえられる もの（RAM・ホームの ルーチン・farcall を 名前で）
     'warps'：マップの 入口の 表を 指す もの（入口の 数×5 バイトを うつし、マップ番号を 読みかえる）
"""
import asmx
def fo(b, a): return b * 0x4000 + a - 0x4000
def r16(r, o): return r[o] | r[o + 1] << 8

AUTO = {
    (0x78, 0x5E9E): {'warps': 'LavenderTown'},           # 第12弾：殿堂入りの あと シオンの 入口 → ラジオ塔
    (0x78, 0x6320): {'warps': 'VermilionPortPassage'},
    (0x78, 0x6345): {'warps': 'Route4'},
    (0x78, 0x6358): {'warps': 'Route25'},
    (0x63, 0x76EB): {'warps': 'SaffronCity'},
    (0x63, 0x71EC): {'size': 0x72AE - 0x71EC, 'code': 0x7263 - 0x71EC, 'also': [0x724D]},   # クチバジムの ゴミばこ（第53弾ほか）
    (0x63, 0x6551): {'size': 0x65A5 + 8 - 0x6551, 'code': 0x65A5 - 0x6551},   # チャンピオンロードの スイッチの 上の 岩（表 4こ）
    (0x68, 0x510F): {'data': [(0x5107, 8), (0x4DF7, 49 * 16)], 'bank_ops': [0x2C]},   # かがくはくぶつかんの カセキ（カブトプス）
    (0x68, 0x4DA8): {'data': [(0x4DA0, 8), (0x4A90, 49 * 16)], 'bank_ops': [0x2C]},   # （プテラ）
    (0x65, 0x6A1C): {}, (0x67, 0x7496): {},             # ずかんに のせて 見せる（かくとう道場・セキチク）
    (0x74, 0x6F52): {}, (0x74, 0x6F5B): {}, (0x74, 0x6F69): {},   # 5ばんどうろの そだてや
    (0x2E, 0x61FA): {'size': 0x620F - 0x61FA, 'code': 10},       # （あずけられない ポケモンの 表：IsInArray）
    (0x74, 0x6F77): {'size': 128, 'code': 123},                  # （あずける ポケモンを えらぶ）
    (0x74, 0x6FF7): {}, (0x74, 0x700B): {}, (0x74, 0x7054): {}, (0x74, 0x7069): {}, (0x74, 0x7076): {}, (0x74, 0x7012): {'also': [0x7019]},
    (0x67, 0x74B0): {}, (0x67, 0x74B9): {},             # ずかんの つかまえた しらべ（カセキ など）
    (0x47, 0x736C): {}, (0x47, 0x75FC): {},             # wScriptVar の 0/1
    (0x63, 0x4D2B): {},                                   # ミュウを つかまえたか
    (0x69, 0x4048): {}, (0x73, 0x54DB): {}, (0x68, 0x67C5): {},   # つかまえた 数
    (0x73, 0x54F5): {}, (0x5B, 0x5827): {},             # カビゴンを つかまえたか
    # サファリ（6E:507D など）は 第28弾の サファリの しくみと いっしょに
}
PORTED = set(AUTO) | {(cb, x) for (cb, ca), o in AUTO.items() for x in o.get('also', [])}

def _put(E, g, cb, data):
    gb = E.gbank(cb); a = E.fill[gb]; assert a + len(data) <= 0x8000
    g[fo(gb, a):fo(gb, a) + len(data)] = data; E.fill[gb] = a + len(data)
    return gb, a

def _nwarps(M, name, cm):
    from cwalk import Walk
    return len(Walk(M).map(cm[name]['attr'], name)['warps'])

def apply(E, M, g, log, cm):
    for (cb, ca), opt in AUTO.items():
        notes = []
        size = opt.get('size') or asmx.extent(M, cb, ca)
        gb = E.gbank(cb); na = E.fill[gb]
        data_fix = {}
        if 'warps' in opt:
            # 入口の 表（asm の 中の ld hl,xxxx）
            # 入口の 表は マップの スクリプトの バンクに ある（wCurMapWarpsPointer は その バンクで 読まれる）
            from cwalk import Walk
            o = fo(cb, ca); seg = M[o:o + size]; k = seg.index(0x21)
            at_ = Walk(M).map(cm[opt['warps']]['attr'], opt['warps']); sb = at_['scbank']
            tab = r16(seg, k + 1); nw = len(at_['warps'])
            alt = bytearray(M[fo(sb, tab):fo(sb, tab) + 5 * nw])
            for i in range(nw):
                gg, nn = E.X.mapid((alt[5 * i + 3], alt[5 * i + 4]), opt['warps'] + ' alt'); alt[5 * i + 3] = gg; alt[5 * i + 4] = nn
            tb_, ta_ = _put(E, g, sb, bytes(alt)); na = E.fill[gb]
            data_fix = {k: ta_}
        # いっしょに うつす データ（メニューの 見出し・絵 など）：先に 同じ バンクへ
        dmap = {}
        for da, dn in opt.get('data', []):
            db_, dd = _put(E, g, cb, M[fo(cb, da):fo(cb, da) + dn]); dmap[da] = dd
        na = E.fill[gb]
        out, prob = asmx.xlat(M, cb, ca, na, notes, size, opt.get('code'))
        out = bytearray(out)
        for i in range(len(out) - 2):
            if out[i] in (0x21, 0x11, 0x01):
                v = M[fo(cb, ca) + i + 1] | M[fo(cb, ca) + i + 2] << 8
                if v in dmap: out[i + 1] = dmap[v] & 0xFF; out[i + 2] = dmap[v] >> 8; prob = [p for p in prob if p != 'データ? %02X:%04X' % (cb, v)]
        for i in opt.get('bank_ops', []):           # ld b,バンク など（データの バンク）
            assert out[i] == cb; out[i] = gb
        for k, v in data_fix.items():
            out[k + 1] = v & 0xFF; out[k + 2] = v >> 8
            prob = [p for p in prob if not p.startswith('データ?')]
        assert not prob, ('%02X:%04X' % (cb, ca), prob)
        b_, a_ = _put(E, g, cb, bytes(out))
        E.loc[(cb, ca)] = (b_, a_); asmx.FARMAP[(cb, ca)] = (b_, a_)
        for x in opt.get('also', []): E.loc[(cb, x)] = (b_, a_ + x - ca)
        log.append('asm %02X:%04X → %02X:%04X（%s）' % (cb, ca, b_, a_, '、'.join(n for n in notes if not n.startswith('RAM')) or '-'))
