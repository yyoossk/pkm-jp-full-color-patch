"""第11弾の 土台を 金に 入れる：
   ・クリスタル版の 新しい タイルセット（クリスタル版 33〜53 → 金 29〜49）：絵・ブロック・当たり・色の割り当て・アニメ・色
   ・マップグループ 26 の 14 番から うしろ（クリスタル版の 新しい マップ）の 見出しの 場所
   色の割り当て（パレットマップ）は 金では バンク 02 に ないと 読めないので、バンク 02 の $4000〜$4619
   （_LoadOverworldAttrmapPals・_ScrollBGMapPalettes・パレットマップ・MapGroupPalettes）を 新しい バンクの 同じ 住所へ うつし、
   ホームの 2つの homecall（$0D45・$0D51）の バンクを かえる。
   色（BG 8色×8）は _CGB_MapPals（02:$56ED）の call LoadMapPals を フックして、新しい タイルセットなら 上書き。
"""
import re
from lz_util import lzlen

def fo(b, a): return b * 0x4000 + a - 0x4000
def r16(r, o): return r[o] | r[o + 1] << 8
def w16(r, o, v): r[o] = v & 0xFF; r[o + 1] = v >> 8

G_NTS = 29                      # 金の タイルセット（0〜28）
C_FIRST, C_LAST = 33, 53        # クリスタル版の 新しい タイルセット
G26_FIRST = 14                  # クリスタル版も 金も、グループ 26 の 12・13 番の 所は 属性の データ（マップではない）
G26_N = 149                     # クリスタル版 グループ 26 の 最後の 番号
W_MAPTILESET, W_BGPALS1, FARCOPYBYTES, LOADMAPPALS = 0xD074, 0xC200, 0x0DB6, 0x75CF
ROOF_TAIL = 0x7626              # LoadMapPals の うしろ（ld a,[wEnvironment] / cp TOWN …）

GJ = {}
for l in open('/home/claude/work/goldsrc/src/jp_all.inc'):
    m = re.match(r'DEF J_(\S+) EQU \$([0-9a-f]+)', l)
    if m: GJ[m.group(1)] = int(m.group(2), 16)

def tsmap(v):
    return v - C_FIRST + G_NTS if C_FIRST <= v <= C_LAST else None

class Alloc:
    def __init__(s, g, E): s.g = g; s.E = E; s.bank = None; s.a = 0x8000
    def put(s, data):
        if s.a + len(data) > 0x8000:
            s.bank = s.E.next_bank; s.E.next_bank += 1; s.a = 0x4000
            assert not any(s.g[fo(s.bank, 0x4000):fo(s.bank + 1, 0x4000)])
        a = s.a; s.g[fo(s.bank, a):fo(s.bank, a) + len(data)] = data; s.a += len(data)
        return s.bank, a

def apply(g, MOD, E, log):
    from near import load, near
    CS = load('/home/claude/work/ref/crystal_jp.sym')
    M = MOD
    # ---------- パレットマップの バンク
    PM = E.next_bank; E.next_bank += 1
    g[fo(PM, 0x4000):fo(PM, 0x461A)] = g[fo(2, 0x4000):fo(2, 0x461A)]
    for o in (0x0D45, 0x0D51):
        assert g[o - 1:o + 1] == b'\x3e\x02'; g[o] = PM
    pm_a = 0x4620
    # ---------- タイルセットの 表（金 05:$562B を 新しい バンクへ。LoadTilesetHeader $2DB8）
    o = 0x2DB8; assert g[o:o + 3] == b'\x21\x2b\x56' and g[o + 18:o + 20] == b'\x3e\x05'
    old = bytes(g[fo(5, 0x562B):fo(5, 0x562B) + 15 * G_NTS])
    A = Alloc(g, E)
    T = fo(0x6A, 0x4000)
    pal_tab = []
    tab = bytearray(old)
    for ci in range(C_FIRST, C_LAST + 1):
        e = M[T + 15 * ci:T + 15 * ci + 15]
        gb, ga, mb, ma, cb, ca = e[0], r16(e, 1), e[3], r16(e, 4), e[6], r16(e, 7)
        assert mb == cb and ca > ma
        gfx = M[fo(gb, ga):fo(gb, ga) + lzlen(M, fo(gb, ga))]
        meta = M[fo(mb, ma):fo(mb, ca)]; coll = M[fo(cb, ca):fo(cb, ca) + len(meta) // 4]
        b1, a1 = A.put(gfx); b2, a2 = A.put(meta); b3, a3 = A.put(coll)
        # 当たり（ブロックの 4つ）は 同じ バンクに ないと いけないか？ → 金は バンクごとに 読む（dba）ので 別々で よい
        anim_c = r16(e, 9); nm = near(CS, 0x3F, anim_c)
        anim = GJ.get(nm[0]) if nm and nm[1] == 0 else None
        if anim is None: anim = GJ['TilesetHouseAnim']; log.append('タイルセット %d：アニメ %s → 金 なし（House）' % (ci, nm))
        pmc = r16(e, 13)
        pmap = M[fo(0x13, pmc):fo(0x13, pmc) + 0x30]
        pa = pm_a; g[fo(PM, pa):fo(PM, pa) + 0x30] = pmap; pm_a += 0x30
        tab += bytes([b1, a1 & 0xFF, a1 >> 8, b2, a2 & 0xFF, a2 >> 8, b3, a3 & 0xFF, a3 >> 8,
                      anim & 0xFF, anim >> 8, 0, 0, pa & 0xFF, pa >> 8])
        mx = max(meta)
        if mx >= 0x60: log.append('タイルセット %d：ブロックに タイル $%02X（$60 以上は 金では 出ない）' % (ci, mx))
    tb, ta = A.put(bytes(tab))
    w16(g, o + 1, ta); g[o + 19] = tb
    log.append('タイルセット：表 %02X:%04X（%d こ）、パレットマップ バンク %02X（$%04X まで）' % (tb, ta, len(tab) // 15, PM, pm_a))
    # ---------- 色：クリスタル版の 表（6A:6EE9 の うしろ。[番号, ポインター]…$FF、64 バイトずつ）
    ho = fo(0x6A, 0x6EE9); assert M[ho:ho + 5] == bytes.fromhex('facad14721')
    t = fo(0x6A, r16(M, ho + 5)); pals = {}
    while M[t] != 0xFF:
        pals[M[t]] = M[fo(0x6A, r16(M, t + 1)):fo(0x6A, r16(M, t + 1)) + 64]; t += 3
    assert sorted(pals) == list(range(C_FIRST, C_LAST + 1)), sorted(pals)
    pb, pa0 = A.put(b''.join(pals[i] for i in range(C_FIRST, C_LAST + 1)))
    # フック（バンク 02 の 空き $7BE0。金の 追加機能パッチは $7BC0〜$7BD8 と $7C60〜 を 使う）
    hk = 0x7BE0; ho = fo(2, hk); assert not any(g[ho:ho + 0x30])
    assert g[fo(2, ROOF_TAIL):fo(2, ROOF_TAIL) + 10] == bytes.fromhex('fa75d0fe012803fe02c0')
    code = bytes([0xCD, LOADMAPPALS & 0xFF, LOADMAPPALS >> 8,          # call LoadMapPals
                  0xFA, W_MAPTILESET & 0xFF, W_MAPTILESET >> 8,        # ld a,[wMapTileset]
                  0xD6, G_NTS, 0xD8,                                   # sub 29 ; ret c
                  0x6F, 0x26, 0x00, 0x29, 0x29, 0x29, 0x29, 0x29, 0x29,  # hl = a*64
                  0x11, pa0 & 0xFF, pa0 >> 8, 0x19,                    # ld de,pals ; add hl,de
                  0x11, W_BGPALS1 & 0xFF, W_BGPALS1 >> 8,              # ld de,wBGPals1
                  0x01, 0x40, 0x00, 0x3E, pb,                          # ld bc,64 ; ld a,bank
                  0xCD, FARCOPYBYTES & 0xFF, FARCOPYBYTES >> 8,        # call FarCopyBytes
                  0xC3, ROOF_TAIL & 0xFF, ROOF_TAIL >> 8])             # jp LoadMapPals の 屋根の 色（町・道路）
    g[ho:ho + len(code)] = code
    o = fo(2, 0x56ED); assert g[o:o + 3] == b'\xcd\xcf\x75'; w16(g, o + 1, hk)
    # ---------- グループ 26：14〜149 番の 見出しの 場所（金 25:$4DAE + 13×9 から）。重なる 属性は よそへ
    from maps import w as _w, GMGP
    G = [r16(g, GMGP + 2 * i) for i in range(26)]
    assert G[25] == 0x4DAE
    lo = fo(0x25, 0x4DAE + 9 * (G26_FIRST - 1)); hi = lo + 9 * (G26_N - G26_FIRST + 1)
    cover = bytearray(hi - lo); moved = 0
    hdrs = []
    for gi in range(26):
        n = (G[gi + 1] - G[gi]) // 9 if gi < 25 else 11
        for k in range(n): hdrs.append(fo(0x25, G[gi]) + 9 * k)
    for h in hdrs:
        ao = fo(g[h], r16(g, h + 3)); nconn = bin(g[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
        if ao < hi and ao + size > lo:
            nb, na = A.put(bytes(g[ao:ao + size])); g[h] = nb; w16(g, h + 3, na); moved += 1
            for i in range(max(ao, lo), min(ao + size, hi)): cover[i - lo] = 1
    # 12・13 番の 所の 属性（金は グループ 26 の 11 こ の うしろ）も 同じ あつかい
    assert all(cover), [hex(lo + i) for i, c in enumerate(cover) if not c][:8]
    g[lo:hi] = bytes(hi - lo)
    log.append('グループ 26：見出し %d こ ぶん（25:%04X〜%04X）、よそへ 移した 属性 %d こ' %
               (G26_N - G26_FIRST + 1, lo % 0x4000 + 0x4000, hi % 0x4000 + 0x4000, moved))
    # ---------- 人の絵：クリスタル版 $67〜$7A（20こ）→ 金 $60〜$73
    # クリスタル版は 05:$7DE9 の 小さな ルーチンで 表を 分けている（$67 から 05:$7CD0 の 表）。金も 同じ 形で、
    # 使われなくなった 古い タイルセットの 表（05:$562B〜、435 バイト）に ルーチンと 表を 置く
    OS = 0x47B0; NSP = 0x7A - 0x67 + 1; GS0 = 0x60
    base = 0x562B; tab = base + 36
    ents = bytearray()
    for v in list(range(0x67, 0x7B)) + [0x3F]:      # 0x3F：クリスタル版は 使っていない 人の 所に サカキ（第13弾）→ 金 $74
        e = M[fo(5, 0x7CD0) + (v - 1) * 6:fo(5, 0x7CD0) + (v - 1) * 6 + 6] if v >= 0x67 else M[0x14727 + 6 * (v - 1):0x14727 + 6 * v]
        n = e[2]; src = fo(e[3], r16(e, 0)); sb, sa = A.put(M[src:src + n * 1])
        ents += bytes([sa & 0xFF, sa >> 8, n, sb, e[4], e[5]])
    code = bytearray()
    for f in (0, 4, 5):
        nb = tab - (GS0 - 1) * 6 + f
        code += bytes([0xFE, GS0, 0x30, 0x04, 0x21, (OS + f) & 0xFF, (OS + f) >> 8, 0xC9, 0x21, nb & 0xFF, nb >> 8, 0xC9])
    blob = bytes(code) + bytes(ents); assert len(blob) <= 435
    g[fo(5, base):fo(5, base) + len(blob)] = blob
    for ad, k, f, i in ((0x4281, 5, 0, 0), (0x42E9, 6, 4, 1), (0x4306, 6, 5, 2)):
        o = fo(5, ad + k); assert g[o:o + 3] == bytes([0x21, (OS + f) & 0xFF, (OS + f) >> 8]), hex(ad)
        h = base + 12 * i; g[o:o + 3] = bytes([0xCD, h & 0xFF, h >> 8])
    log.append('人の絵：クリスタル版 $67〜$7A → 金 $60〜$73、$3F（サカキ）→ $74（表 05:%04X）' % tab)
    return dict(hdr0=lo)
