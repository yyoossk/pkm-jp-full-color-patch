"""第54弾（金）：カントーの 殿堂入りと スタッフロールを 赤の もの（赤フルカラーの ならべ・文・色・曲）に。
   ・コードは クリスタル版の キット（tools/red/phase54.asm）を 金の 住所で 組みなおす。データは crystal_kj.gbc の 35:67A3〜。
     はじめに クリスタル版の 住所で 組みなおして 同じ バイトに なるか 確かめる。
   ・金で かえる 所：主人公の 絵（金の CAL の 絵：GetTrainerPic、後ろ姿：GetTrainerBackpic）、WRAM バンク 5 は 使わない
     （wBGPals2・wLYOverrides は 金では バンク 0）、つづきの 時の ライバルの 名前（金には 古い セーブが ないので しない）。
   ・曲：クリスタル版の バンク $20（赤の 殿堂入り・スタッフロールの 曲を クリスタルの 形に した もの）を 写して、
     金の 曲 $52・$53（GS の オープニング。第53弾で 使わなく なった）を そこへ。
   ・金の HallOfFame（21:65CF〜）の「call AnimateHallOfFame / pop af / ld b,a / farcall Credits / ret」→ ここへ
     （EVENT_BEAT_ELITE_FOUR が ある＝ジョウトの 殿堂入りは 金の まま）。
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asmx import CSD, GJ, GB, HRAM, RX, RAM_FIX
from gold_opening import db, lzlen, assemble, RED, fo

MOD_CODE, MOD_DATA = 0x6240, 0x67A3
MOD_AUDIO, MOD_HOF, MOD_CRED = 0x20, 0x5E, 0x5F
G_HOF, G_CRED = 0x52, 0x53
CAL = 0x0C
# 金の 住所（日本版）：名前 → 値（RX で 読めない もの・かえる もの）
GOLD = {'wTilemap': 0xC3A0, 'wBGPals2': 0xC280, 'wLYOverrides': 0xC700, 'wGameTimeHours': 0xD1DE,
        'wBaseType1': 0xD119, 'wBaseType2': 0xD11A, 'wPartyMon1Level': 0xD9F0 + 0x1F, 'wTrainerClass': 0xD10F, 'PrintNum': 0x31F9, 'PrintText': 0x0F30}
FAR = {(0x21, 0x6695): 'AnimateHallOfFame', (0x42, 0x58BF): (0x21, 0x6A9C),   # Credits の 2つめの 命令（b = 状態）
       (0x05, 0x4E87): 'TryLoadSaveFile',
       (0x14, 0x510D): (0x14, 0x577F),          # GetMonFrontpic（金：predef $3C の 本体）
       (0x14, 0x5202): (0x14, 0x57ED)}          # GetMonBackpic（predef $3D）


def until(M, o, term):
    e = o
    while M[e] not in term: e += 1
    return bytes(M[o:e + 1])


def extract(M):
    B = 0x35; o = fo(B, MOD_DATA); inc = []
    def take(n):
        nonlocal o; b = M[o:o + n]; o += n; return b
    def take_until(term):
        nonlocal o; b = until(M, o, term); o += len(b); return b
    def addr(): return o - fo(B, 0)
    def ptr(p): return M[p] | M[p + 1] << 8
    inc += ['MonPals:', db(take(152 * 8)), 'PalPlayer:', db(take(8))]
    for k in ('HoFText', 'HoFMonInfoText', 'HoFPlayTimeText', 'HoFMoneyText'): inc += [k + ':', db(take_until((0x50,)))]
    inc += ['DexSeenOwnedText:', db(take(0x27)), 'DexRatingText:', db(take_until((0x57,)))]
    t = take(48); rt = ['DexRatings:']
    for i in range(16): rt.append('\tdb %d\n\tdw DexRating%d' % (t[3 * i], i))
    tx = []
    for i in range(16):
        assert addr() == ptr(o - 0) if False else True
        assert t[3 * i + 1] | t[3 * i + 2] << 8 == addr(), i
        tx += ['DexRating%d:' % i, db(take_until((0x57,)))]
    inc += rt + tx
    tn = take(56); inc.append('TypeNames:\n\tdw ' + ', '.join('TypeName%d' % i for i in range(28)))
    for i in range(28):
        assert tn[2 * i] | tn[2 * i + 1] << 8 == addr(), i
        inc += ['TypeName%d:' % i, db(take_until((0x50,)))]
    pg = take(52); inc.append('CreditsPages:\n\tdw ' + ', '.join('CreditsPage%d' % i for i in range(26)))
    for i in range(26):
        assert pg[2 * i] | pg[2 * i + 1] << 8 == addr(), i
        seq = bytearray()
        while True:
            c = M[o]; o += 1; seq.append(c)
            if c >= 0xFA and c != 0xFB: break
        inc += ['CreditsPage%d:' % i, db(bytes(seq))]
    ts = addr(); first = ptr(o); nt = (first - ts) // 2; ct = take(2 * nt)
    inc.append('CreditsTexts:\n\tdw ' + ', '.join('CreditsText%d' % i for i in range(nt)))
    for i in range(nt):
        assert ct[2 * i] | ct[2 * i + 1] << 8 == addr(), i
        inc += ['CreditsText%d:' % i, db(take_until((0x50,)))]
    inc += ['CreditsXOffsets:', db(take(nt)), 'CreditsMons:', db(take(15)), 'GfxTheEnd:', db(take(160)),
            'TheEnd1:', db(take_until((0x50,))), 'TheEnd2:', db(take_until((0x50,)))]
    inc += ['GfxCopyright:', db(take(lzlen(M, o)))]
    cl = ['CopyrightLines:']
    while M[o]:
        a = ptr(o) - 0xC4A0; o += 2; row = take_until((0,))
        cl.append('\tdb LOW(wTilemap + %d), HIGH(wTilemap + %d)\n%s' % (a, a, db(row)))
    o += 1; cl.append('\tdb 0')
    inc += cl + ['DefaultRival:', db(take(6))]
    return inc, addr()


def head_inc(hof, cred):
    return ['DEF MUS_HALL_OF_FAME EQU $%X' % hof, 'DEF MUS_CREDITS EQU $%X' % cred, 'DEF NUM_CRED_PAGES EQU 26']


def to_gold(src, jpinc):
    def val(n, v, rest):
        if n in GOLD: return GOLD[n] - (eval(rest.replace('$', '0x')) if rest.strip() else 0)
        if v >= 0xFF80: return 0xFF00 | HRAM.get(v & 0xFF, v & 0xFF)
        if v >= 0xFF00 or v < 0x100: return v
        if v < 0x4000:
            nm = CSD.get((0, v)); assert nm in GJ and GB.get(nm, 0) == 0, (n, hex(v), nm); return GJ[nm]
        if 0xC000 <= v < 0xE000:
            if 0xCB00 <= v < 0xCB10 or v == 0xC800: return v           # 作業用（金でも マップの ブロックの 所）
            if v in RAM_FIX: return RAM_FIX[v]
            gv, nm = RX.x(v); assert gv is not None, (n, hex(v), nm); return gv
        raise Exception(n)
    def fix(text, drop):
        out = []
        for l in text.split('\n'):
            m = re.match(r'(DEF (\w+)\s+EQU \$)([0-9A-Fa-f]+)(.*)', l)
            if m:
                n, v, rest = m.group(2), int(m.group(3), 16), m.group(4).split(';')[0]
                try: l = '%s%X%s' % (m.group(1), val(n, v, rest), m.group(4))
                except (AssertionError, Exception):
                    if not drop: raise
                    l = None
            if l is not None: out.append(l)
        return '\n'.join(out)
    s = fix(src, False); j = fix(jpinc, True)
    # ホームの HRAM の 数字
    s = re.sub(r'\[\$FF([89A-E][0-9A-F])\]', lambda m: '[$FF%02X]' % HRAM.get(int(m.group(1), 16), int(m.group(1), 16)), s)
    # WRAM バンク 5 は 使わない
    s, n = re.subn(r'\n\tldh \[rSVBK\], a', '', s); assert n == 4, n
    # farcall
    def far(m):
        k = (int(m.group(1), 16), int(m.group(2), 16)); t = FAR[k]
        if isinstance(t, str): t = (GB[t], GJ[t])
        return 'farcall_ $%02X, $%04X' % t
    s, n = re.subn(r'farcall_ \$([0-9A-F]{2}), \$([0-9A-F]{4})', lambda m: far(m) if (int(m.group(1), 16), int(m.group(2), 16)) in FAR else m.group(0), s)
    # 主人公の 絵：金の CAL の 絵と 後ろ姿
    old = re.search(r'\tld de, \$48B2[^\n]*\n\tld hl, \$9000\n\tlb bc, \$22, 49\n\tcall Get2bpp\n\tfarcall_ \$22, \$482E[^\n]*\n', s)
    assert old
    s = s.replace(old.group(0), '\tld a, $%02X\n\tld [wTrainerClass], a\n\tld de, $9000\n\tfarcall_ $%02X, $%04X\n'
                  '\tfarcall_ $0F, $79B8                  ; GetTrainerBackpic -> tiles $31\n' % (CAL, GB['GetTrainerPic'], GJ['GetTrainerPic']))
    # 金の HallOfFame の「xor a / ld [wGameLogicPaused], a」を ここで
    s = s.replace('HallOfFameAnimAndCredits::\n', 'HallOfFameAnimAndCredits::\n\txor a\n\tld [$C1CC], a\n')
    return s, j


def verify_crystal(M, src, jpinc, data, dend):
    r, sym = assemble(src, jpinc, head_inc(MOD_HOF, MOD_CRED) + data, 0x35, MOD_CODE, 'phase54')
    a = fo(0x35, MOD_CODE); e = fo(0x35, dend)
    diff = [hex(i) for i in range(a, e) if r[i] != M[i]]
    assert not diff, diff[:10]
    assert sym['DataStart' if 'DataStart' in sym else 'MonPals'][1] == MOD_DATA


def apply(g, M, E, log):
    G0 = bytes(g)
    src = open(RED + '/phase54.asm', encoding='utf-8').read()
    jpinc = open(RED + '/jp.inc', encoding='utf-8').read()
    data, dend = extract(M)
    verify_crystal(M, src, jpinc, data, dend)
    code_bank = E.next_bank; E.next_bank += 1
    aud_bank = E.next_bank; E.next_bank += 1
    for b in (code_bank, aud_bank): assert not any(g[b * 0x4000:(b + 1) * 0x4000])
    gs, gj = to_gold(src, jpinc)
    r, sym = assemble(gs, gj, head_inc(G_HOF, G_CRED) + data, code_bank, 0x4000, 'phase54')
    g[code_bank * 0x4000:(code_bank + 1) * 0x4000] = r[code_bank * 0x4000:(code_bank + 1) * 0x4000]
    end = max(a for n, (b, a) in sym.items() if b == code_bank)
    # 曲
    g[aud_bank * 0x4000:(aud_bank + 1) * 0x4000] = M[MOD_AUDIO * 0x4000:(MOD_AUDIO + 1) * 0x4000]
    for gid, cid in ((G_HOF, MOD_HOF), (G_CRED, MOD_CRED)):
        mo = fo(0x3A, 0x506E) + 3 * cid; assert M[mo] == MOD_AUDIO
        go = fo(0x3A, 0x506E) + 3 * gid
        g[go:go + 3] = bytes([aud_bank, M[mo + 1], M[mo + 2]])
    # 金の HallOfFame の おわり（21:6600〜660A）：xor a / ld [wGameLogicPaused], a / call AnimateHallOfFame / pop af / jp Credits
    o = fo(0x21, 0x6600)
    assert G0[o:o + 11] == bytes([0xAF, 0xEA, 0xCC, 0xC1, 0xCD, GJ['AnimateHallOfFame'] & 0xFF, GJ['AnimateHallOfFame'] >> 8,
                                  0xF1, 0xC3, GJ['Credits'] & 0xFF, GJ['Credits'] >> 8])
    assert G0[fo(0x21, 0x6A9B):fo(0x21, 0x6A9E)] == bytes([0x47, 0xCB, 0x70])
    h = sym['HallOfFameAnimAndCredits'][1]
    g[o:o + 11] = bytes([0xF1, 0x47, 0x3E, code_bank, 0x21, h & 0xFF, h >> 8, 0xCF, 0xC9, 0, 0])
    log.append('第54弾：赤の 殿堂入りと スタッフロール %02X:4000〜%04X（金の 21:6600 から）、曲 $%02X・$%02X → バンク %02X'
               % (code_bank, end, G_HOF, G_CRED, aud_bank))
