"""トレーナーの 手持ちの リスト（クラスごと）を 読む・まぜる"""
def w(b, o): return b[o] | b[o + 1] << 8
def fo(bank, a): return bank * 0x4000 + a - 0x4000

def parse(r, bank, p, end, maxn=80):
    o = fo(bank, p); L = []
    while (end is None and len(L) < maxn) or (end is not None and o < fo(bank, end)):
        if r[o] == 0xFF and end is not None: o += 1; continue
        if r[o] == 0x00: break
        s = o
        while r[o] != 0x50: o += 1
        o += 1; t = r[o]; o += 1
        sz = {0: 2, 1: 6, 2: 3, 3: 7}.get(t)
        if sz is None: break
        while r[o] != 0xFF: o += sz
        o += 1; L.append(bytes(r[s:o]))
        if end is None and r[o] in (0x00, 0xff): break
    return L

def groups(r, bank, tbl, n, stops=()):
    """tbl：ポインターの表（バンク内の 住所）。それぞれの リストの 終わりは、つぎに 大きい ポインター（か stops）"""
    ptrs = [w(r, fo(bank, tbl) + 2 * i) for i in range(n)]
    bounds = sorted(set(ptrs) | set(stops))
    out = []
    for p in ptrs:
        nx = [x for x in bounds if x > p]
        out.append(parse(r, bank, p, nx[0] if nx else None))
    return ptrs, out

# クリスタル（日本版）：0E:$59BA・67 クラス。クリスタル版（完成版）：第13弾で バンク $7E の $45B3 へ（79 クラス）
C_TG = (0x0E, 0x59BA, 67)
M_TG = (0x7E, 0x45B3, 79, (0x554B, 0x4651, 0x8000))
G_TG = (0x0E, 0x595C, 66)

def merged(c, p, g):
    """金の手持ちリスト（79 クラス）：金に ある クラスは、金の i 番目までは 金（ただし MOD が変えた所は MOD）、
       その先は MOD のものを そのまま。67〜79 は MOD のもの"""
    _, C = groups(c, *C_TG[:3]); _, M = groups(p, *M_TG[:3], stops=M_TG[3]); _, G = groups(g, *G_TG)
    out = []
    for i in range(79):
        if i >= 66:
            out.append(list(M[i])); continue
        L = []
        for j in range(len(M[i])):
            if j < len(G[i]):
                L.append(M[i][j] if (j < len(C[i]) and M[i][j] != C[i][j]) or j >= len(C[i]) else G[i][j])
            else:
                L.append(M[i][j])
        out.append(L)
    return fix_gender(out)


# MOD（第16・19・23・27・32弾など）は トレーナーの 名前を 男女 まぜた 表から じゅんばんに つけたので、
# ふなのり（男）が ユミ、ミニスカート（女）が タカシ のように なる。男女の 合わない 名前だけ かえる
FEMALE_CLS = {0x19, 0x1C, 0x1D, 0x21, 0x22, 0x27, 0x35, 0x37, 0x39, 0x3C, 0x3D, 0x3E, 0x42, 73}
TO_MALE = {'ユミ': 'ユウキ', 'アヤ': 'アキラ', 'ミキ': 'ミツル', 'サオリ': 'サトル', 'エミ': 'エイジ', 'ナナ': 'ナオト',
           'ミナミ': 'ミノル', 'アユミ': 'アユム', 'サトミ': 'サトシ', 'ユカリ': 'ユタカ', 'マユミ': 'マサル', 'ナツキ': 'ナツオ',
           'チアキ': 'チカラ', 'カオリ': 'カオル', 'ハルカ': 'ハルキ', 'リエ': 'リキ'}
TO_FEMALE = {'タカシ': 'タカコ', 'ヒロシ': 'ヒロミ', 'マコト': 'マキ', 'ユウジ': 'ユウコ', 'ケンタ': 'ケイコ', 'ショウタ': 'ショウコ',
             'ダイスケ': 'ナツミ', 'リョウ': 'リョウコ', 'ナオキ': 'ナオミ', 'カズヤ': 'カズミ'}

def fix_gender(out):
    from jpchar import encode
    for i, L in enumerate(out):
        tbl = TO_FEMALE if i + 1 in FEMALE_CLS else TO_MALE
        enc = {encode(a + '@'): encode(b + '@') for a, b in tbl.items()}
        for j, e in enumerate(L):
            k = e.index(0x50) + 1
            if bytes(e[:k]) in enc: L[j] = enc[bytes(e[:k])] + bytes(e[k:])
            elif bytes(e[:k]) == encode('ヒビキ@'): L[j] = encode('ゴールド@') + bytes(e[k:])   # シロガネやま：金の 主人公（キット 4-2）
    return out
