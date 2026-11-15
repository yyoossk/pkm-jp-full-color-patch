"""第13弾：ポケモンタワーの ゆうれい戦（シルフスコープ なしで 3F〜7F の 野生は 正体の わからない「ゆうれい」）を 金に。
   クリスタル版（build_phase13）と 同じ はたらき：名前は ゆうれい、はじめに「だめだ！ ゆうれい ポケモンの しょうたいが わからない！」、
   どちらも わざを 出せない（こわがっている／タチサレ）、にげるのは かならず できる、ボールは よけられる、
   ガラガラ（6F）は スコープが あっても つかまらない、絵は ピカチュウフルカラーの ゆうれい、色は その ポケモンの（色ちがい なし）。
   金の 空きが 少ない バンクは、使われていない ルーチンの 所に 小さな 入口を 置く：
     0F：FillEnemyMovesFromMoveIndicesBuffer（$7492、60）・LoadHPExpBarGFX（$6C06、36）
     03：LoadBoxMonListing（$68BE、176）  14：BetaMonPicBanks（$7F09、24）  02：$7C10〜（第11弾の フックの うしろ）
"""
from jpchar import encode
def fo(b, a): return b * 0x4000 + a - 0x4000

# 金（日本版）の RAM・ルーチン
W_BATTLEMODE, W_BATTLETYPE, W_TURNENDED = 0xD108, 0xD10B, 0xCB86
W_TEMPENEMYSPECIES, W_CURPARTYSPECIES, W_ENEMYNICK = 0xD0DF, 0xCFFE, 0xCAF6
W_CURITEM, W_NUMITEMS, W_MAPGROUP, W_MAPNUMBER = 0xCFFC, 0xD5AA, 0xD9C6, 0xD9C7
W_PLAYERACTION, H_BATTLETURN = 0xCFDE, 0xE6
CHECKITEM, PRINTTEXT, STDBATTLETEXTBOX = 0x304B, 0x0F30, 0x3BF7
SILPH_SCOPE, MAROWAK = 0x87, 0x69
TOWER_G, TOWER_3F, TOWER_6F, TOWER_7F = 26, 16, 19, 20

class Asm:
    def __init__(s, base): s.base = base; s.b = bytearray(); s.labels = {}; s.fix = []
    def label(s, n): s.labels[n] = s.base + len(s.b)
    def db(s, *v): s.b += bytes(v)
    def raw(s, v): s.b += bytes(v)
    def dw(s, v):
        if isinstance(v, str): s.fix.append((len(s.b), v)); s.b += b'\0\0'
        else: s.b += bytes([v & 0xFF, v >> 8])
    def jr(s, op, lab): s.b += bytes([op, 0]); s.fix.append((len(s.b) - 1, ('jr', lab)))
    def farcall(s, bank, lab): s.db(0x3E, bank, 0x21); s.dw(lab); s.db(0xCF)
    def done(s, ext={}):
        L = dict(ext); L.update(s.labels)
        for off, lab in s.fix:
            if isinstance(lab, tuple):
                d = L[lab[1]] - (s.base + off + 1); assert -128 <= d < 128; s.b[off] = d & 0xFF
            else: s.b[off] = L[lab] & 0xFF; s.b[off + 1] = L[lab] >> 8
        return bytes(s.b)

def apply(g, M, E, log):
    HB = E.next_bank; E.next_bank += 1
    tiles = M[fo(0x78, 0x5EB1):fo(0x78, 0x5EB1) + 49 * 16]
    assert M[fo(0x14, 0x79C5) + 0x18:fo(0x14, 0x79C5) + 0x1B] == bytes([0x11, 0xB1, 0x5E])
    a = Asm(0x4000)
    a.label('pic'); a.raw(tiles)
    def wbk1(lab, core):
        a.label(lab); a.db(0xC5, 0xF0, 0x70, 0x47, 0x3E, 0x01, 0xE0, 0x70, 0xCD); a.dw(core); a.db(0x78, 0xE0, 0x70, 0xC1, 0xC9)
    wbk1('isghost', 'c_isghost'); wbk1('isgm', 'c_isgm')
    a.label('c_isghost')
    a.db(0xFA); a.dw(W_BATTLEMODE); a.db(0x3D); a.jr(0x20, 'no')
    a.db(0xFA); a.dw(W_MAPGROUP); a.db(0xFE, TOWER_G); a.jr(0x20, 'no')
    a.db(0xFA); a.dw(W_MAPNUMBER); a.db(0xD6, TOWER_3F, 0xFE, TOWER_7F - TOWER_3F + 1); a.jr(0x30, 'no')
    a.db(0xC5, 0xD5, 0xE5, 0xFA); a.dw(W_CURITEM); a.db(0xF5, 0x3E, SILPH_SCOPE, 0xEA); a.dw(W_CURITEM)
    a.db(0x21); a.dw(W_NUMITEMS); a.db(0xCD); a.dw(CHECKITEM)
    a.db(0x9F, 0x47, 0xF1, 0xEA); a.dw(W_CURITEM); a.db(0x78, 0xE1, 0xD1, 0xC1, 0xFE, 0x01, 0xC9)
    a.label('no'); a.db(0xA7, 0xC9)
    a.label('c_isgm')
    a.db(0xCD); a.dw('c_isghost'); a.db(0xD8)
    a.db(0xFA); a.dw(W_BATTLEMODE); a.db(0xFE, 0x01); a.jr(0x20, 'no')
    a.db(0xFA); a.dw(W_MAPGROUP); a.db(0xFE, TOWER_G); a.jr(0x20, 'no')
    a.db(0xFA); a.dw(W_MAPNUMBER); a.db(0xFE, TOWER_6F); a.jr(0x20, 'no')
    a.db(0xFA); a.dw(W_TEMPENEMYSPECIES); a.db(0xFE, MAROWAK, 0x37, 0xC8, 0xA7, 0xC9)
    # 名前
    a.label('gname'); a.db(0xCD); a.dw('isghost'); a.db(0xD0)
    nm = encode('ゆうれい@'); nm = nm + b'\x50' * (6 - len(nm))
    for i, c in enumerate(nm): a.db(0x3E, c, 0xEA); a.dw(W_ENEMYNICK + i)
    a.db(0xC9)
    # はじめの セリフ
    a.label('gintro'); a.db(0xCD); a.dw('isghost'); a.db(0xD0, 0x21); a.dw('t_cantid'); a.db(0xCD); a.dw(PRINTTEXT); a.db(0xC9)
    # 主人公の 番：わざを えらんだ ときだけ「こわがっている」で おわり（carry）
    a.label('gturnp'); a.db(0xCD); a.dw('isghost'); a.db(0xD0)
    a.db(0xFA); a.dw(W_PLAYERACTION); a.db(0xA7); a.jr(0x20, 'no')
    a.db(0xAF, 0xE0, H_BATTLETURN, 0x21); a.dw('t_scared'); a.db(0xCD); a.dw(PRINTTEXT); a.db(0x37, 0xC9)
    a.label('gturne'); a.db(0xCD); a.dw('isghost'); a.db(0xD0)
    a.db(0x3E, 0x01, 0xE0, H_BATTLETURN, 0x21); a.dw('t_getout'); a.db(0xCD); a.dw(PRINTTEXT); a.db(0x37, 0xC9)
    # 絵：ゆうれい戦の 敵の 絵なら SRAM $A000（PadFrontpic の 出口）を ゆうれいに
    a.label('gpic'); a.db(0xCD); a.dw('isghost'); a.db(0xD0)
    a.db(0xFA); a.dw(W_CURPARTYSPECIES); a.db(0x47, 0xFA); a.dw(W_TEMPENEMYSPECIES); a.db(0xB8, 0xC0)
    a.db(0xC5, 0xD5, 0xE5, 0x21); a.dw('pic'); a.db(0x11, 0x00, 0xA0, 0x01, (49 * 16) & 0xFF, (49 * 16) >> 8)
    a.label('cp'); a.db(0x2A, 0x12, 0x13, 0x0B, 0x78, 0xB1); a.jr(0x20, 'cp'); a.db(0xE1, 0xD1, 0xC1, 0xC9)
    a.label('t_cantid'); a.raw(encode('{00}だめだ！　ゆうれい　<POKEMON>の<LINE>しょうたいが　わからない！<PROMPT>'))
    a.label('t_scared'); a.raw(encode('{00}<USER>は　こわがっている！<LINE>わざを　だすことが　できない！<PROMPT>'))
    a.label('t_getout'); a.raw(encode('{00}ゆうれい{72}タチサレ<……>タチサレ<……><PROMPT>'))
    blob = a.done(); L = a.labels
    g[fo(HB, 0x4000):fo(HB, 0x4000) + len(blob)] = blob

    def site(bank, addr, old, new):
        o = fo(bank, addr); assert g[o:o + len(old)] == old, (hex(bank), hex(addr), g[o:o + len(old)].hex())
        g[o:o + len(new)] = new
    def put(bank, addr, size, asm):
        b = asm.done(L); o = fo(bank, addr); assert len(b) <= size, (hex(bank), len(b)); g[o:o + size] = b + bytes(size - len(b))
    call = lambda x: bytes([0xCD, x & 0xFF, x >> 8])
    # ---- 0F（$7492）
    a = Asm(0x7492)
    a.label('name'); a.db(0xCD); a.dw(0x676B); a.farcall(HB, 'gname'); a.db(0xC9)
    a.label('intro'); a.db(0xCD); a.dw(STDBATTLETEXTBOX); a.farcall(HB, 'gintro'); a.db(0xC9)
    a.label('run'); a.farcall(HB, 'isghost'); a.db(0x3E, 0x02, 0xD8, 0xFA); a.dw(W_BATTLETYPE); a.db(0xC9)
    a.label('gender'); a.farcall(HB, 'isghost'); a.db(0xD8, 0x21, 0x05, 0x53, 0x3E, 0x14, 0xCF, 0xC9)
    b = a.done(L); l0f = dict(a.labels); put(0x0F, 0x7492, 60, a)
    site(0x0F, 0x743D + 5, call(0x676B), call(l0f['name']))
    i = g.find(bytes.fromhex('e1cdf73bc9'), fo(0x0F, 0x7CFB), fo(0x0F, 0x7CFB) + 0x80); assert i > 0
    g[i + 1:i + 4] = call(l0f['intro'])
    site(0x0F, 0x5746, bytes([0xFA, 0x0B, 0xD1]), call(l0f['run']))
    site(0x0F, 0x5EF6, bytes.fromhex('2105533e14cf'), call(l0f['gender']) + bytes(3))
    # ---- 0F（$6C06）：わざの 番
    a = Asm(0x6C06)
    a.label('tp'); a.farcall(HB, 'gturnp'); a.db(0xD8, 0x3E, 0x0D, 0x21, 0x00, 0x40, 0xCF, 0xC9)
    a.label('te'); a.farcall(HB, 'gturne'); a.db(0xD8, 0x3E, 0x0D, 0x21, 0x19, 0x40, 0xCF, 0xC9)
    b = a.done(L); lt = dict(a.labels); put(0x0F, 0x6C06, 36, a)
    site(0x0F, 0x467D, bytes.fromhex('2100403e0dcf'), call(lt['tp']) + bytes(3))
    site(0x0F, 0x468C, bytes.fromhex('2119403e0dcf'), call(lt['te']) + bytes(3))
    # ---- 03：ボールは よけられる
    PB = 0x6C29; ub = bytes(g[fo(3, 0x7C60):fo(3, 0x7C60) + 28]); assert ub[23:28] == bytes.fromhex('3e37cd052e')
    pb = bytes(g[fo(3, PB):fo(3, PB) + 7]); assert pb == bytes.fromhex('fa08d13dc2607c')
    a = Asm(0x68BE)
    a.farcall(HB, 'isgm'); a.jr(0x38, 'dodge'); a.raw(pb); a.db(0xC3); a.dw(PB + 7)
    a.label('dodge'); a.raw(ub); a.db(0x21); a.dw('t'); a.db(0xCD); a.dw(PRINTTEXT); a.db(0xC3); a.dw(0x7C55)
    a.label('t'); a.raw(encode('{00}よけられた！<LINE>こいつは　つかまりそうにないぞ！<PROMPT>'))
    put(3, 0x68BE, 176, a)
    site(3, PB, pb[:3], bytes([0xC3, 0xBE, 0x68]))
    # ---- 14：絵（GetFrontpic の ld de,$A000 の 前に）
    a = Asm(0x7F09)
    a.farcall(HB, 'gpic'); a.db(0x11, 0x00, 0xA0, 0xC9)
    put(0x14, 0x7F09, 24, a)
    i = g.find(bytes.fromhex('cd30591100a00e31e1'), fo(0x14, 0x577F), fo(0x14, 0x577F) + 0x80); assert i > 0
    g[i + 3:i + 6] = call(0x7F09)
    # ---- 02：色（色ちがい なし）
    a = Asm(0x7C10)
    a.farcall(HB, 'isghost'); a.jr(0x30, 'n'); a.db(0x01); a.dw('dv0'); a.label('n'); a.db(0xFA); a.dw(W_TEMPENEMYSPECIES); a.db(0xC9)
    a.label('dv0'); a.db(0, 0)
    o = fo(2, 0x7C10); assert not any(g[o:o + 0x18]); put(2, 0x7C10, 0x18, a)
    site(2, 0x5B50 + 9, bytes([0xFA, 0xDF, 0xD0]), call(0x7C10))
    log.append('ゆうれい戦：バンク %02X、入口 0F:7492/6C06・03:68BE・14:7F09・02:7C10' % HB)
