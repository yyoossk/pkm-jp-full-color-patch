"""第64弾：金の 追加機能パッチと あわせると 元の バンクの あきが ほとんど ない。
   ホームに 小さな「どこからでも 呼べる farcall（a・hl・フラグを 受けわたす）」HFI を 置き、
   ルーチンの 本体は バンク $7E（金・キットで 使っていない）に 置く。元の バンクには 5バイトの
   「call HFI / dw 本体」だけ。RAM：$D7A5〜$D7A9（a・hl・あて先）。
   ・call HFI / dw 本体 の つぎの 命令へ もどる（その場でも 使える）。
   ・本体は 入口で 呼び出し元の a・hl を そのまま 受け、出口の a・hl・フラグが 呼び出し元へ もどる。bc・de も そのまま。
   ・本体の 中で スタックを さわる（pop で 呼び出し元へ もどる など）ことは できない。"""
def fo(b, a): return b * 0x4000 + a - 0x4000
HFI = 0x3FA0
EB = 0x7E
WA, WL, WT = 0xDEEA, 0xDEEB, 0xDEED       # 使われていない WRAM（キットは $DEE8・$DEE9・$DEF0〜 を 使う）
_cur = {}
# キットの マップ（kin64.map）で 見た、うしろ以外の あき：バンク → (はじめ, おわり)
FREE = {0x0F: (0x7F96, 0x7FC8), 0x02: (0x7C60, 0x7E40), 0x04: (0x7FEB, 0x8000)}


def install(g):
    from gold_safari import A
    assert not any(g[HFI:HFI + 0x40]), g[HFI:HFI + 0x40].hex()
    lo = lambda v: v & 255; hi = lambda v: v >> 8
    D = put(g, bytes(64))                     # 7E の 中の 手順（下で 書く）
    a = A(HFI)
    a.db(0xEA, lo(WA), hi(WA), 0x7D, 0xEA, lo(WL), hi(WL), 0x7C, 0xEA, lo(WL + 1), hi(WL + 1))   # a・hl を とっておく
    a.db(0xE1, 0x2A, 0xEA, lo(WT), hi(WT), 0x2A, 0xEA, lo(WT + 1), hi(WT + 1), 0xE5)   # pop hl / あて先（よび出し元の バンクで 読む）/ dw の つぎへ もどる
    a.db(0xF0, 0x9F, 0xF5, 0x3E, EB, 0xD7, 0xC3, lo(D), hi(D))      # push 今の バンク / バンク 7E へ / jp D
    a.L('back')
    a.db(0xF5, 0x7D, 0xEA, lo(WL), hi(WL), 0x7C, 0xEA, lo(WL + 1), hi(WL + 1))   # 出口の af・hl
    a.db(0xE1, 0xF1, 0xE5, 0xD7)                                       # pop hl(af) / pop af(バンク) / push hl / rst $10
    a.db(0xFA, lo(WL), hi(WL), 0x6F, 0xFA, lo(WL + 1), hi(WL + 1), 0x67, 0xF1, 0xC9)
    code = a.fin(); assert len(code) <= 0x40, len(code)
    g[HFI:HFI + len(code)] = code
    back = a.lab['back']
    d = A(D)
    d.db(0x21, lo(back), hi(back), 0xE5)                                # push back（その 下に もとの バンク）
    d.db(0xFA, lo(WT), hi(WT), 0x6F, 0xFA, lo(WT + 1), hi(WT + 1), 0x67, 0xE5)   # push あて先
    d.db(0xFA, lo(WL), hi(WL), 0x6F, 0xFA, lo(WL + 1), hi(WL + 1), 0x67, 0xFA, lo(WA), hi(WA), 0xC9)
    dc = d.fin(); g[fo(EB, D):fo(EB, D) + len(dc)] = dc
    return len(code)


def put(g, data):
    """バンク $7E に 置く → 住所"""
    c = _cur.setdefault(EB, 0x4000); assert c + len(data) <= 0x8000
    g[fo(EB, c):fo(EB, c) + len(data)] = data; _cur[EB] = c + len(data); return c


def here(): return _cur.setdefault(EB, 0x4000)


def local(g, bank, n):
    """元の バンクの うしろの あき（キットの あと）から n バイト"""
    hi = 0x8000
    if bank in FREE: hi = FREE[bank][1]
    if bank not in _cur:
        if bank in FREE: _cur[bank] = FREE[bank][0]
        else:
            s = g[fo(bank, 0x4000):fo(bank + 1, 0x4000)]; e = len(s)
            while e and s[e - 1] in (0, 0xFF): e -= 1
            _cur[bank] = 0x4000 + e + 1
    c = _cur[bank]; assert c + n <= hi, ('あきが ない', hex(bank), n)
    if any(g[fo(bank, c):fo(bank, c) + n]):
        import freesp; raise Exception(('つかわれている', hex(bank), hex(c), [(hex(a), m) for a, m in freesp.runs(g, bank, 24)][-8:]))
    _cur[bank] = c + n; return c


def stub(g, bank, target):
    """元の バンクに call HFI / dw target / ret を 置いて その 住所を かえす"""
    a = local(g, bank, 6)
    g[fo(bank, a):fo(bank, a) + 6] = bytes([0xCD, HFI & 255, HFI >> 8, target & 255, target >> 8, 0xC9])
    return a
