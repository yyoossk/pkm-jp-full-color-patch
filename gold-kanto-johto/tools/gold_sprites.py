"""外の マップの 人の絵（金は グループごとに 11こ。クリスタルは 23こ）。
   クリスタル版の カントーの 町・道路は 金の グループの 表に ない 人の絵を 使うので、
   ・グループの 表を 新しい バンクに 写し、たりない 人の絵を 入れる（入りきらない グループは マップごとの 表も 作る）
   ・AddOutdoorSprites（05:$41A8）：今の マップの 表を wStringBuffer2 に 写して そこから 読む
   ・LoadMapObjects（05:$5560）：外の マップで、表の 人の絵が 読みこまれていなければ RefreshSprites（05:$413F）
     （つなぎめを こえた とき。金は つなぎめで 人の絵を 読みなおさないので、ちがう グループや マップごとの 表に うつる ときに 要る）
"""
import sys
sys.path.insert(0, '/home/claude/work/scripts')
from cwalk import Walk
from cmaps import maplist
from maps import GMGP
from collections import defaultdict, Counter
def fo(b, a): return b * 0x4000 + a - 0x4000
N = 11
TAB = (0x05, 0x465E)
BUF = 0xCF92                  # wStringBuffer2（11 バイト）
W_USED = 0xD04F               # wUsedSprites（12 組）
W_GROUP, W_NUM = 0xD9C6, 0xD9C7

def apply(g, SB, log):
    maps = maplist(bytes(g), GMGP, 'pokegold')
    own = {}; bygroup = defaultdict(list)
    for m in maps:
        if g[m['hdr'] + 2] not in (1, 2): continue          # ROUTE・TOWN だけ
        at = Walk(bytes(g)).map(m['attr'], m['name'])
        own[(m['group'], m['num'])] = [o[0] for o in at['objs'] if o[0]]
        bygroup[m['group']].append((m['group'], m['num'], m['name']))
    t = fo(*TAB)
    lists = []; gtab = []; mtab = []
    for gr in range(1, 27):
        lp = fo(5, g[t + 2 * (gr - 1)] | g[t + 2 * (gr - 1) + 1] << 8); L0 = list(g[lp:lp + N])
        U = []
        cnt = Counter()
        for k in bygroup.get(gr, []):
            for s in dict.fromkeys(own[k[:2]]): cnt[s] += 1
        U = [s for s, c in cnt.most_common()]
        if all(s in L0 for s in U):
            gtab.append(len(lists)); lists.append(L0); continue
        def fill(need, base):
            out = list(dict.fromkeys(need))[:N]
            for s in base:
                if len(out) >= N: break
                if s not in out and s: out.append(s)
            return out + [0] * (N - len(out))
        GL = fill(U, L0)                      # 多く 使われる 順に 11こ
        gtab.append(len(lists)); lists.append(GL)
        log.append('人の絵の 表 グループ %d：%s' % (gr, ' '.join('%02X' % s for s in GL)))
        for k in bygroup[gr]:
            o = list(dict.fromkeys(own[k[:2]]))
            if all(s in GL for s in o): continue
            assert len(o) <= N, (k, o)
            ML = fill(o, GL); mtab.append((k[0], k[1], len(lists))); lists.append(ML)
            log.append('人の絵の 表 %s：%s' % (k[2], ' '.join('%02X' % s for s in ML)))
    assert len(lists) < 256
    # ---- コード
    from gold_safari import A
    a = A(0x4000)
    # 表を BUF へ
    a.L('fill')
    a.db(0xFA); a.dw(W_GROUP); a.db(0x47); a.db(0xFA); a.dw(W_NUM); a.db(0x4F)
    a.db(0x21); a.dw('mtab')
    a.L('m_lp'); a.db(0x2A, 0xFE, 0xFF); a.jr(0x28, 'm_grp'); a.db(0xB8); a.jr(0x20, 'm_s2')
    a.db(0x2A, 0xB9); a.jr(0x20, 'm_s1'); a.db(0x7E); a.jr(0x18, 'm_idx')
    a.L('m_s2'); a.db(0x23)
    a.L('m_s1'); a.db(0x23); a.jr(0x18, 'm_lp')
    a.L('m_grp'); a.db(0x78, 0x3D, 0x5F, 0x16, 0x00, 0x21); a.dw('gtab'); a.db(0x19, 0x7E)
    a.L('m_idx')                                       # hl = lists + 11 * a
    a.db(0x6F, 0x26, 0x00, 0x54, 0x5D, 0x29, 0x29, 0x19, 0x29, 0x19, 0x11); a.dw('lists'); a.db(0x19)
    a.db(0x11); a.dw(BUF); a.db(0x0E, N)
    a.L('cp'); a.db(0x2A, 0x12, 0x13, 0x0D); a.jr(0x20, 'cp'); a.db(0xC9)
    # LoadMapObjects
    a.L('lmo')
    a.db(0xCD, 0x1F, 0x2D, 0xCD, 0x7A, 0x23); a.jr(0x20, 'go')           # GetMapEnvironment / CheckOutdoorMap
    a.db(0xCD); a.dw('fill')
    a.db(0x21); a.dw(BUF); a.db(0x0E, N)
    a.L('l_lp'); a.db(0x2A, 0xA7); a.jr(0x28, 'l_nx')
    a.db(0xE5, 0xC5, 0x47, 0x21); a.dw(W_USED); a.db(0x0E, 12)
    a.L('l_s'); a.db(0x2A, 0x23, 0xB8); a.jr(0x28, 'l_ok'); a.db(0x0D); a.jr(0x20, 'l_s')
    a.db(0xC1, 0xE1); a.jr(0x18, 'reload')
    a.L('l_ok'); a.db(0xC1, 0xE1)
    a.L('l_nx'); a.db(0x0D); a.jr(0x20, 'l_lp'); a.jr(0x18, 'go')
    a.L('reload'); a.far(0x05, 0x413F)
    KIT = bytes(g[fo(0x05, 0x5560):fo(0x05, 0x5567)]) == bytes.fromhex('3e79210640cfc9')   # 金の 追加機能パッチの 連れ歩き
    if KIT: a.L('go'); a.far(0x79, 0x4006); a.db(0xC9)            # キットの LoadMapObjects の つづき（連れ歩き こみ）
    else: a.L('go'); a.db(0x3E, 0x02, 0xCD, 0x11, 0x27); a.far(0x09, 0x4488); a.far(0x02, 0x4767); a.db(0xC9)
    a.L('mtab')
    for gr, n, i in mtab: a.db(gr, n, i)
    a.db(0xFF)
    a.L('gtab'); a.b += bytes(gtab)
    a.L('lists')
    for L_ in lists: a.b += bytes(L_)
    blob = a.fin(); assert len(blob) < 0x4000
    g[fo(SB, 0x4000):fo(SB, 0x4000) + len(blob)] = blob
    lab = a.lab
    # ---- フック
    o = fo(0x05, 0x41A8); assert g[o:o + 17] == bytes.fromhex('fac6d93d4f0600215e4609092a666f0e0b')
    g[o:o + 15] = bytes([0x3E, SB, 0x21, lab['fill'] & 0xFF, lab['fill'] >> 8, 0xCF, 0x21, BUF & 0xFF, BUF >> 8]) + bytes(6)
    o = fo(0x05, 0x5560)
    if KIT: g[o:o + 7] = bytes([0x3E, SB, 0x21, lab['lmo'] & 0xFF, lab['lmo'] >> 8, 0xCF, 0xC9])
    else:
        assert g[o:o + 18] == bytes.fromhex('3e02cd11273e09218844cf3e02216747cfc9')
        g[o:o + 18] = bytes([0x3E, SB, 0x21, lab['lmo'] & 0xFF, lab['lmo'] >> 8, 0xCF, 0xC9]) + bytes(11)
    log.append('人の絵の 表：バンク %02X（表 %d こ、マップごと %d）' % (SB, len(lists), len(mtab)))
