"""第53弾・第68弾（金）：赤の オープニングと タイトル画面（コピーライト・ゲームフリークの 流れ星・ゲンガーと ニドリーノ・
   赤の タイトル：ロゴが すべって 入り、右に 主人公、ポケモンが 入れかわる）。曲と 効果音は 赤の 音の しくみで 鳴らす。
   ・コードは クリスタル版の キット（tools/red/phase53.asm、crystal-satoshi-mod の tools/asm）を 金の 住所で 組みなおす。
   ・絵・色・地図などの データは できあがった クリスタル版（crystal_kj.gbc の 36:62F0〜、タイトルの ポケモンは 2C）から 取る
     （赤フルカラーの ROM が なくても 同じ ものに なる。クリスタル版の 住所で 組みなおして バイトが 同じか 確かめる）。
   ・赤の 音（第68弾）：クリスタル版の バンク 9D（赤の バンク 1F、音の RAM を ずらした もの）を 写して、
     RAM を 金の 音の RAM（$C001〜）に ずらす。金の _UpdateSound（3A:405C）の 頭で、$C000 = $A5 の あいだは 赤の
     Audio3_UpdateMusic を よぶ（割りこみの 中なので rst 8 を 使わず 自分で バンクを かえる）。
   ・金の IntroSequence（01:63EF）→ ここを よんで、01:6408（タイトルの あと かたづけ）へ。
"""
import os, re, subprocess, tempfile, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asmx import L, CSD, GJ, GB, HRAM

HERE = os.path.dirname(os.path.realpath(__file__))
RED = HERE + '/red'
RGBDS = os.environ.get('RGBDS', '/home/claude/rgbds-src')
def fo(b, a): return b * 0x4000 + a - 0x4000

MOD_CODE, MOD_DATA, MOD_MON = 0x5B70, 0x62F0, 0x2C
RED_AUDIO = 0x9D
MOD_SFX_ADDR, MOD_MUSIC_ADDR = 0x5C7B, 0x5C89
PALS = ['Grey', 'GF', 'Star4', 'Star5', 'Star7', 'Gengar', 'Nidorino', 'Logo', 'Copyright', 'Player']
GFX = ['GfxCopyright', 'GfxGengar', 'GfxGFIntro', 'GfxNidorino', 'GfxLogo', 'GfxPlayer']
SFX = [('SHOOTING_STAR', 0xBE), ('INTRO_LUNGE', 0xBF), ('INTRO_HIP', 0xC0), ('INTRO_HOP', 0xC1),
       ('INTRO_RAISE', 0xC2), ('INTRO_CRASH', 0xC3), ('INTRO_WHOOSH', 0xC4)]
# 金の RAM（日本版）
GOLD_RAM = {'wCurSFX': 0xC1BF, 'wShadowOAM': 0xC300, 'wBGPals2': 0xC280, 'wOBPals2': 0xC2C0, 'wLYOverrides': 0xC700,
            'wTitleScreenSelectedOption': 0xCE58, 'wMonBuffer': 0xC890}   # C890〜CBA0：マップの ブロック（タイトルでは 使わない）
TILEMAP_SHIFT = -0x100          # クリスタル wTilemap $C4A0 → 金 $C3A0（作業用の RAM）
W_MUSIC, W_AUDIO_END = 0xC000, 0xC1C0
RED_ON = 0xA5


def db(b):
    return '\n'.join('\tdb ' + ', '.join('$%02X' % x for x in b[i:i + 16]) for i in range(0, len(b), 16))


def lzlen(M, o):
    s = o
    while True:
        b = M[o]; o += 1
        if b == 0xFF: return o - s
        cmd = b >> 5
        if cmd == 7: cmd = (b >> 2) & 7; n = ((b & 3) << 8 | M[o]) + 1; o += 1
        else: n = (b & 31) + 1
        if cmd == 0: o += n
        elif cmd == 1: o += 1
        elif cmd == 2: o += 2
        elif cmd == 3: pass
        else: o += 1 if M[o] & 0x80 else 2


def extract(M):
    """クリスタル版の データ → phase53_data.inc の データの 部分（DEF の あと）、タイトルの ポケモン（lz の リスト）"""
    o = fo(0x36, MOD_DATA); inc = []
    def take(n):
        nonlocal o; b = M[o:o + n]; o += n; return b
    for k in PALS: inc += ['Pal%s:' % k, db(take(8))]
    s = o
    while M[o]:
        o += 2
        while M[o]: o += 1
        o += 1
    o += 1; inc += ['CopyrightLayout:', db(M[s:o])]
    for k in GFX: inc += [k + ':', db(take(lzlen(M, o)))]
    inc += ['GfxStars:', db(take(48)), 'GFLogoOAM:', db(take(64)), 'BigStarOAM:', db(take(16)), 'SmallStarOAM:', db(take(4))]
    ws = o; w = take(12); wp = [w[2 * i] | w[2 * i + 1] << 8 for i in range(6)]
    data0 = ws + 12 - fo(0x36, 0) ; base = wp[0]
    assert base == data0, (hex(base), hex(data0))
    inc += ['SmallStarWaves:', '\tdw ' + ', '.join('SmallStarData + %d' % (p - base) for p in wp), 'SmallStarData:', db(take(34))]
    for i in range(3): inc += ['GengarTilemap%d:' % (i + 1), db(take(49))]
    an = take(73); k = 0; labs = []
    while k < len(an):
        labs.append(k); k2 = k
        while an[k2] != 0x50: k2 += 2
        k = k2 + 1
    assert len(labs) == 7
    for j, a in enumerate(labs):
        inc += ['NidoAnim%d:' % (j + 1), db(an[a:labs[j + 1] if j + 1 < 7 else 73])]
    inc += ['TitleLogoMap:', db(take(120)), 'TitleMons:', db(take(16)), 'TitleMonPals:', db(take(128))]
    tp = take(32); pics = []
    for i in range(16):
        a = tp[2 * i] | tp[2 * i + 1] << 8; po = fo(MOD_MON, a); pics.append((a, M[po:po + lzlen(M, po)]))
    inc += ['TitleMonPics:', '\tdw ' + ', '.join('TitleMonPic%d' % i for i in range(16))]
    return inc, pics, o - fo(0x36, 0)


def head_inc(mon_bank):
    inc = ['DEF %s EQU $%X' % kv for kv in (('MUS_TITLE', 0x52), ('MUS_INTRO', 0x53), ('MON_BANK', mon_bank),
                                             ('LOGO_ROW', 2), ('LOGO_COL', 0), ('LOGO_W', 20), ('LOGO_H', 6))]
    inc += ['DEF SFX_%s EQU $%X' % kv for kv in SFX]
    return inc


def mons_inc(pics, mon_addr, mon_bank):
    inc = ['SECTION "Phase53Mons", ROMX[$%X], BANK[$%X]' % (mon_addr, mon_bank)]
    for i, (a, p) in enumerate(pics): inc += ['TitleMonPic%d:' % i, db(p)]
    return inc


def assemble(src, jpinc, inc, code_bank, code_addr, name='phase53'):
    with tempfile.TemporaryDirectory() as d:
        open(d + '/%s.asm' % name, 'w').write(src)
        open(d + '/jp.inc', 'w').write(jpinc)
        open(d + '/%s_data.inc' % name, 'w').write('\n'.join(inc) + '\n')
        subprocess.run([RGBDS + '/rgbasm', '-I', d, '-D', 'CODE_BANK=$%X' % code_bank, '-D', 'CODE_ADDR=$%X' % code_addr,
                        '-o', d + '/a.o', d + '/%s.asm' % name], check=True)
        subprocess.run([RGBDS + '/rgblink', '-w', '-o', d + '/a.gbc', '-n', d + '/a.sym', d + '/a.o'], check=True)
        r = open(d + '/a.gbc', 'rb').read()
        sym = {}
        for l in open(d + '/a.sym'):
            m = re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)', l)
            if m: sym[m.group(3)] = (int(m.group(1), 16), int(m.group(2), 16))
    return r, sym


def gold_source(src, jpinc, glue_bank, red_bank, cry):
    """クリスタル版の DEF → 金"""
    def hram(v): return 0xFF00 | HRAM.get(v & 0xFF, v & 0xFF) if v >= 0xFF80 else v
    def home(v, name):
        nm = CSD.get((0, v)); assert nm and nm in GJ and GB.get(nm, 0) == 0, (name, hex(v), nm); return GJ[nm]
    def fix(text, ram_ok):
        out = []
        for l in text.split('\n'):
            m = re.match(r'(DEF (\w+)\s+EQU \$)([0-9A-Fa-f]+)(.*)', l)
            if m:
                n, v = m.group(2), int(m.group(3), 16)
                if n in GOLD_RAM: v = GOLD_RAM[n]
                elif v >= 0xFF80: v = hram(v)
                elif 0xFF00 <= v: pass
                elif v < 0x4000:
                    if (0, v) in CSD and CSD[(0, v)] in GJ: v = home(v, n)
                    elif not ram_ok: raise Exception(n)
                    else: l = None
                elif 0xC4A0 <= v < 0xC600: v += TILEMAP_SHIFT
                elif 0xC000 <= v < 0xE000:
                    if ram_ok: l = None          # jp.inc の 使わない RAM は けす
                    else: raise Exception(n)
                if l is not None: l = '%s%X%s' % (m.group(1), v, m.group(4))
            if l is not None: out.append(l)
        return '\n'.join(out)
    s = fix(src, False)
    s = s.replace('[$FF9E]', '[$FF%02X]' % HRAM[0x9E]).replace('[$FF9D]', '[$FF%02X]' % HRAM[0x9D])
    j = fix(jpinc, True)
    # 第68弾：Sfx・Music → 赤の 音、タイトルの 鳴き声の 前に 金の 音へ もどす
    s, n = re.subn(r'\nSfx: [^\n]*\n(?:\t[^\n]*\n)+?\tret\n', '\nSfx:\n\tjp RedSfx\n', s); assert n == 1
    s, n = re.subn(r'\nMusic: [^\n]*\n(?:\t[^\n]*\n)+?\tret\n', '\nMusic:\n\tjp RedSfx\n', s); assert n == 1
    s, n = re.subn(r'\tcall PlayMonCry\n', '\tcall CryWrap\n', s); assert n == 1
    s = s.replace('INCLUDE "phase53_data.inc"', GLUE % dict(red=red_bank, cry=cry, music=W_MUSIC, start=W_MUSIC + 1,
                                                          end=W_AUDIO_END, on=RED_ON, init=GJ['InitSound'])
                  + '\nINCLUDE "phase53_data.inc"')
    return s, j


GLUE = '''
; ---------------------------------------------------------------- 第68弾（金）：赤の 音の しくみ
DEF RedPlayShim        EQU $43DB
DEF wChannelSoundIDs   EQU $%(start)X + $26
RedSfx:  ; a = 第53弾の 番号
	push hl
	push de
	push bc
	ld e, a
	call RedSound
	pop bc
	pop de
	pop hl
	ret

RedSound:  ; e = 第53弾の 番号
	ld a, [$%(music)X]
	cp $%(on)X
	jr z, .on
	push de
	xor a
	ld [$%(music)X], a
	call $%(init)X
	ld hl, $%(start)X
	ld bc, $%(end)X - $%(start)X
.clear
	xor a
	ld [hli], a
	dec bc
	ld a, b
	or c
	jr nz, .clear
	ld a, $%(on)X
	ld [$%(music)X], a
	ld e, $FF
	call .play
	pop de
.on
	ld hl, .table
.find
	ld a, [hli]
	and a
	ret z
	cp e
	ld a, [hli]
	ld d, a
	ld a, [hli]
	jr nz, .find
	and a
	jr z, .sfx
	xor a
	ld [wChannelSoundIDs + 4], a
	ld [wChannelSoundIDs + 5], a
	ld [wChannelSoundIDs + 6], a
	ld [wChannelSoundIDs + 7], a
.sfx
	ld e, d
.play
	ld a, $%(red)X
	ld hl, RedPlayShim
	rst $08
	ret

.table  ; 第53弾の 番号, 赤の 番号, 曲なら 1
	db MUS_TITLE, $C3, 1
	db MUS_INTRO, $DC, 1
	db SFX_SHOOTING_STAR, $C2, 0
	db SFX_INTRO_LUNGE, $B8, 0
	db SFX_INTRO_HIP, $B9, 0
	db SFX_INTRO_HOP, $BA, 0
	db SFX_INTRO_RAISE, $BB, 0
	db SFX_INTRO_CRASH, $BC, 0
	db SFX_INTRO_WHOOSH, $BD, 0
	db 0

CryWrap:  ; 金の 音に もどして 鳴き声
	push af
	xor a
	ld [$%(music)X], a
	call $%(init)X
	pop af
	jp $%(cry)X
'''


def red_audio_bank(M):
    """クリスタル版の バンク 9D（赤の 音、RAM $C101〜）→ 金（RAM $C001〜）"""
    B = bytearray(M[RED_AUDIO * 0x4000:(RED_AUDIO + 1) * 0x4000])
    pc, n = 0x4417, 0
    while pc < 0x4E2A:
        op = B[pc - 0x4000]; ln = L[op]
        if ln == 3:
            v = B[pc - 0x3FFF] | B[pc - 0x3FFE] << 8
            if 0xC101 <= v <= 0xC200:
                v -= 0x100; B[pc - 0x3FFF] = v & 0xFF; B[pc - 0x3FFE] = v >> 8; n += 1
        if op in (0xE0, 0xF0) and B[pc - 0x3FFF] >= 0x80: raise Exception('hram %04X' % pc)
        pc += ln
    assert pc == 0x4E2A and n == 223, (hex(pc), n)
    assert B[0x03DB:0x03DF] == bytes([0x7B, 0xC3, 0x8A, 0x4B])      # RedPlayShim
    return bytes(B)


def verify_crystal(M, src, jpinc, data, pics, dend):
    """クリスタル版の 住所で 組みなおして、できあがった クリスタル版と 同じか（第68弾で かえた 所は のぞく）"""
    r, sym = assemble(src, jpinc, head_inc(MOD_MON) + data + mons_inc(pics, pics[0][0], MOD_MON), 0x36, MOD_CODE)
    a, e = fo(0x36, MOD_CODE), fo(0x36, MOD_DATA)
    skip = set(range(fo(0x36, MOD_SFX_ADDR), fo(0x36, MOD_SFX_ADDR) + 14)) | set(range(fo(0x36, MOD_MUSIC_ADDR), fo(0x36, MOD_MUSIC_ADDR) + 9))
    diff = [hex(i) for i in range(a, fo(0x36, dend)) if i not in skip and r[i] != M[i]]
    assert len(diff) <= 3, diff      # 鳴き声の call（第68弾）
    for a_, p in pics: assert r[fo(MOD_MON, a_):fo(MOD_MON, a_) + len(p)] == p


def apply(g, M, E, log):
    G0 = bytes(g)
    src = open(RED + '/phase53.asm', encoding='utf-8').read()
    jpinc = open(RED + '/jp.inc', encoding='utf-8').read()
    data, pics, dend = extract(M)
    verify_crystal(M, src, jpinc, data, pics, dend)
    code_bank = E.next_bank; E.next_bank += 1
    red_bank = E.next_bank; E.next_bank += 1
    assert not any(g[code_bank * 0x4000:(code_bank + 1) * 0x4000]) and not any(g[red_bank * 0x4000:(red_bank + 1) * 0x4000])
    gs, gj = gold_source(src, jpinc, code_bank, red_bank, GJ['PlayMonCry'])
    mon_bank = E.next_bank; E.next_bank += 1
    assert not any(g[mon_bank * 0x4000:(mon_bank + 1) * 0x4000])
    r, sym = assemble(gs, gj, head_inc(mon_bank) + data + mons_inc(pics, 0x4000, mon_bank), code_bank, 0x4000)
    end = max(a for n, (b, a) in sym.items() if b == code_bank)
    for b in (code_bank, mon_bank): g[b * 0x4000:(b + 1) * 0x4000] = r[b * 0x4000:(b + 1) * 0x4000]
    mon_addr, tot = 0x4000, 0x4000 + sum(len(p) for a, p in pics)
    g[red_bank * 0x4000:(red_bank + 1) * 0x4000] = red_audio_bank(M)
    # 金の _UpdateSound の 頭
    o = fo(0x3A, 0x405C); assert G0[o:o + 5] == bytes([0xFA, 0x00, 0xC0, 0xA7, 0xC8])
    # 割りこみの 中：rst 8（hTempBank・wFarCallBC）を 使わず、ホームの Bankswitch（$0010）と「pop af / rst $10 / ret」で 行き来する
    pop_sw = bytes(g[:0x4000]).find(bytes([0xF1, 0xD7, 0xC9]))
    t = 0x8000 - 0x48
    back = t + 12 + 4 + 4 + 3 + 4 + 4 + 5
    hook = bytes([0xFA, 0x00, 0xC0, 0xFE, RED_ON, 0x28, 0x05, 0xA7, 0xC8, 0xC3, 0x61, 0x40,
                  0x3E, 0x77, 0xE0, 0x24,
                  0x21, back & 0xFF, back >> 8, 0xE5, 0x3E, 0x3A, 0xF5,
                  0x21, pop_sw & 0xFF, pop_sw >> 8, 0xE5, 0x21, 0x17, 0x44, 0xE5,
                  0x3E, red_bank, 0xC3, 0x10, 0x00, 0xC9])
    assert len(hook) == back - t + 1 and g[0x10:0x16] == bytes.fromhex('e09fea0020c9')
    ho = fo(0x3A, t); assert not any(g[ho - 1:ho + len(hook)]), 'bank 3A'
    g[ho:ho + len(hook)] = hook
    g[o:o + 5] = bytes([0xC3, t & 0xFF, t >> 8, 0x00, 0x00])
    # 金の IntroSequence → 赤の オープニング → 01:6408
    o = fo(0x01, 0x63EF); assert G0[o:o + 9] == bytes.fromhex('2110533e39cf380621')
    ro = sym['RedOpening'][1]
    hk = bytes([0x3E, code_bank, 0x21, ro & 0xFF, ro >> 8, 0xCF,
                         0xAF, 0xE0, 0xD8, 0x3E, 0x98, 0xE0, 0xD9,      # hBGMapAddress = $9800（金の タイトルの あとと 同じ）
                         0xC3, 0x08, 0x64])
    g[o:o + len(hk)] = hk
    log.append('第53・68弾：赤の オープニング %02X:%04X〜%04X、タイトルの ポケモン %02X:%04X〜%04X、赤の 音 バンク %02X'
               % (code_bank, ro, end, mon_bank, mon_addr, tot, red_bank))
