"""報告の 直し（第126弾。クリスタル版 カントー＆ジョウトの キットから。銀の アドレスで）
 1 たいあたり の 演出（$32:$4E1E）：背の 高い ポケモンだと 相手の 絵も ずれた → src/tackle_split_silver.asm（$32:$7E20）。
 2 22番道路の ゲート（$72:$5071 / $5077。グレーバッジ＝フラグ $22）：バッジなしで 南に 押し出されて もどれない／
   見張りに 話すと カウンターに めりこむ → 来た 向きに 押しもどす・話すだけ では 押さない（$72 の 空き）。
 3 26番道路の エリートトレーナー♀（$34:$4BED）：<RIVAL>（$53）→ <GREEN>（$39、シゲル）。
 4 人に ついて行く 場面（follow 人, PLAYER / applymovement / stopfollow）で 連れ歩きが 置いていかれる →
   その人と 主人公を 1歩ずつ 交代で 歩かせる（バンク $49）。はじめの オーキド（$71:$4C4E・$4CA6）は そのまま。
   銀の スクリプトの 人の 番号 N は マップの 人 N（wMapObjects の 1 は 空き）。
 5 マサキに 会う 前は「だれかの パソコン」（イベント $0835 ＝ マサキが 転送マシンに 入った。フラグは $D713 の bit5）：
   パソコンの メニューの「マサキの パソコン」（表 $05:$5830 → $05:$5843）を WRAM $D680（銀の あき）に して、
   メニューを 出す たび（$05:$57F7 の「xor a / ldh [$D6],a / call $5874」を バンク $49 への farcall に）名前を 入れる。
   「マサキの パソコンと つないだ！」（$05:$5D13）は text_ram で 同じ 名前を 出す（銀の 日本版は text_far が ない）。
 6 ニビの 民家の ニドラン（14,3）：ガーディの 絵 → 使って いない ポケモンの 人の絵 $83（SpriteMons $05:$463B の 3 ばんめ、
   もとは ビードル）を しるし $FE に して、LoadOverworldMonIcon（$23:$6596）で 連れ歩きの ニドラン♂の 絵を わたす。
   立って 下を 向く。"""
import os, re, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo
import asmpatch, jptext

FB = 0x49                     # 新しい スクリプト・文の バンク（空き）
SKIP_FOLLOW = {(0x71, 0x4C4E), (0x71, 0x4CA6)}
W_SCRIPT_VAR = 0xD165
W_PLAYER_X, W_PLAYER_Y = 0xD200, 0xD201
GET_MAP_OBJECT, GET_OBJECT_STRUCT = 0x171C, 0x192F
ENGINE_BOULDER = 0x22
BILL_FLAG_BYTE, BILL_FLAG_BIT = 0xD713, 5          # イベント $0835
PC_NAME_BUF = 0xD680
COPY_C = 0x2898                                      # ld a,[hli] / ld [de],a / inc de / dec c / jr nz / ret
NIDORAN_M = 0x20
NIDO_SPRITE = 0x83
NIDO_PAL = int(os.environ.get('NIDO_PAL', '9'))    # 人の 色（9 ＝ 青。もとの まま。銀の 人の 色で 紫に いちばん 近い）
NIDO_MARK = 0xFE                 # SpriteMons の しるし（ポケモンの 番号に ない 値）


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)


def w16(v): return bytes([v & 0xFF, v >> 8])


class Free:
    def __init__(s, rom, bank, start=None):
        s.rom, s.bank = rom, bank
        if start is None:
            b = rom[fo(bank, 0x4000):fo(bank, 0x8000)]; i = 0x3FFF
            while i >= 0 and b[i] == 0: i -= 1
            start = 0x4000 + i + 3
        s.a = start
    def put(s, data):
        o = fo(s.bank, s.a); assert s.a + len(data) <= 0x8000 and not any(s.rom[o:o + len(data)]), (hex(s.bank), hex(s.a))
        s.rom[o:o + len(data)] = data; a = s.a; s.a += len(data); return a


class Script:
    """2回 組む：1回目で ラベルの 場所を 知る"""
    def __init__(s, base): s.base, s.b, s.lab, s.fix = base, bytearray(), {}, []
    def db(s, *v): s.b += bytes(v)
    def ref(s, l): s.fix.append((len(s.b), l)); s.b += b'\0\0'
    def label(s, l): s.lab[l] = s.base + len(s.b)
    def done(s):
        for at, l in s.fix:
            v = l if isinstance(l, int) else s.lab[l]
            s.b[at:at + 2] = w16(v)
        return bytes(s.b)


def tackle(rom, log):
    expect(rom, fo(0x32, 0x4E1E), 'e0 c8 cd 63 4f 20 05 11 36 00 18 03 11 5e 2f 7a e0 c9 7b e0 ca c9')
    assert not any(rom[fo(0x32, 0x7E20):fo(0x32, 0x7F00)])
    asmpatch.overlay(rom, open(os.path.join(H, 'src', 'tackle_split_silver.asm'), encoding='utf-8').read())
    o = fo(0x32, 0x4E1E)
    rom[o:o + 22] = bytes([0xC3, 0x20, 0x7E]) + bytes(19)       # jp TS_Customs1
    log.append('第126弾 1：たいあたり の 演出 $32:$4E1E → $32:$7E20')


def gate(rom, log):
    expect(rom, fo(0x71, 0x7E00), '04 72 71 50 04 72 77 50')
    expect(rom, fo(0x72, 0x5071), '75 00 02 03 78 50 6a 47 34 22 00 09 89 50 4c 93 50 53 49 68 00 91 50 90 '
                                  '4c cc 50 53 49 14 01 90 0c 47')
    GNO, GYES = 0x5093, 0x50CC
    f = Free(rom, 0x72)
    s = Script(f.a)
    def body(push):
        s.db(0x75, 0, 2); s.db(0x47); s.db(0x34); s.ref(ENGINE_BOULDER); s.db(0x09); s.ref('gy')
        s.db(0x4C); s.ref(GNO); s.db(0x53, 0x49)
        if push: s.db(0x68, 0); s.ref(push)
        s.db(0x90)
    s.label('gc'); s.db(0x1C, 0x09); s.db(0x06, 1); s.ref('gc_up')   # readvar VAR_FACING ; 上向き＝南から 来た
    body('mv_up')                                                    # 下向き（北から 来た）→ 北へ もどす
    s.label('gc_up'); body('mv_down')
    s.label('gt'); s.db(0x6A, 0x47); s.db(0x34); s.ref(ENGINE_BOULDER); s.db(0x09); s.ref('gy')
    s.db(0x4C); s.ref(GNO); s.db(0x53, 0x49, 0x90)
    s.label('gy'); s.db(0x4C); s.ref(GYES); s.db(0x53, 0x49, 0x14, 0x01, 0x90)
    s.label('mv_up'); s.db(0x0D, 0x47)
    s.label('mv_down'); s.db(0x0C, 0x47)
    blob = s.done(); assert f.put(blob) == s.base
    o = fo(0x71, 0x7E00)
    rom[o + 2:o + 4] = w16(s.lab['gc']); rom[o + 6:o + 8] = w16(s.lab['gt'])
    log.append('第126弾 2：ゲート 座標 $72:%04X・見張り $72:%04X' % (s.lab['gc'], s.lab['gt']))


def route26(rom, log):
    o = fo(0x34, 0x4BED)
    expect(rom, o - 2, '57 00 53 7f 1e b2 b3 4f')
    rom[o] = 0x39
    log.append('第126弾 3：26番道路 $34:$4BED <RIVAL> → <GREEN>')


def follow(rom, log, f):
    mv = {}
    def movement(c):
        if c not in mv: mv[c] = f.put(bytes([c, 0x47]))
        return mv[c]
    for c in (0x0C, 0x0D, 0x0E, 0x0F): movement(c)
    # wScriptVar = 主人公 から マップの 人 a への 向き（$0C 下・$0D 上・$0E 左・$0F 右）
    common = f.put(bytes([0xCD]) + w16(GET_MAP_OBJECT) + bytes([
        0x0A, 0xCD]) + w16(GET_OBJECT_STRUCT) + bytes([
        0x21, 0x10, 0x00, 0x09, 0x56, 0x23, 0x5E,
        0xFA]) + w16(W_PLAYER_X) + bytes([0xBA, 0x38, 0x10, 0x20, 0x12,
        0xFA]) + w16(W_PLAYER_Y) + bytes([0xBB, 0x38, 0x04,
        0x3E, 0x0D, 0x18, 0x0A, 0x3E, 0x0C, 0x18, 0x06, 0x3E, 0x0F, 0x18, 0x02, 0x3E, 0x0E,
        0xEA]) + w16(W_SCRIPT_VAR) + bytes([0xC9]))
    entry = {}; n = 0
    for m in list(re.finditer(rb'\x6f(.)\x00\x68(.)(..)\x70', bytes(rom), re.S)):
        at = m.start(); b = at // 0x4000; a_ = at % 0x4000 + 0x4000
        if b == 0 or (b, a_) in SKIP_FOLLOW: continue
        obj = m.group(1)[0]; assert m.group(2)[0] == obj
        if obj not in entry: entry[obj] = f.put(bytes([0x3E, obj, 0xC3]) + w16(common))   # 銀：人 N ＝ マップの 人 N
        p = fo(b, int.from_bytes(m.group(3), 'little')); path = []
        while rom[p] != 0x47:
            path.append(rom[p]); p += 1; assert len(path) < 64
        for c in path: movement(c)
        def build(base, lab):
            s = Script(base); s.lab = dict(lab)
            s.db(0x0E, FB); s.b += w16(entry[obj])
            prev = None
            for c in path:
                s.db(0x68, obj); s.ref(movement(c))
                if not (0x08 <= c < 0x20): continue
                if prev is None:
                    for d in (0x0C, 0x0D, 0x0E):
                        s.db(0x06, d); s.ref('p%d' % d)
                    s.db(0x68, 0); s.ref(mv[0x0F]); s.db(0x03); s.ref('j')
                    for d in (0x0C, 0x0D, 0x0E):
                        s.label('p%d' % d); s.db(0x68, 0); s.ref(mv[d]); s.db(0x03); s.ref('j')
                    s.label('j')
                else:
                    s.db(0x68, 0); s.ref(movement(prev))
                prev = c
            s.db(0x04, b); s.b += w16(a_ + 8)                      # stopfollow の あとへ もどる
            return s
        blob = build(f.a, {}).done()
        new = f.put(blob)
        rom[at:at + 4] = bytes([0x04, FB]) + w16(new)
        rom[at + 4:at + 8] = bytes([0x90] * 4)
        n += 1
        log.append('第126弾 4：follow %02X:%04X 人 %d（%d 歩）→ %02X:%04X' % (b, a_, obj, len(path), FB, new))
    assert n == 10, n


def bills_pc(rom, log, f):
    masaki = bytes(jptext.enc('マサキの　')).rstrip(b'\x50'); dareka = bytes(jptext.enc('だれかの　')).rstrip(b'\x50')
    assert len(masaki) == len(dareka) == 5
    expect(rom, fo(5, 0x582A), 'cc 58 3e 58 bb 58 43 58')
    expect(rom, fo(5, 0x5843), (masaki + b'\x5b\x50').hex())
    expect(rom, fo(5, 0x57F7), 'af e0 d6 cd 74 58 ea e1 ce')
    expect(rom, fo(5, 0x5874), 'cd 29 2f 20 03 3e 00 c9 fa 76 d6 a7 3e 01 c8 3e 02 c9')   # ChooseWhichPCListToUse
    expect(rom, fo(5, 0x580E), '30 e7')                                                      # jr nc, $57F7（くりかえし）
    expect(rom, fo(5, 0x58BE), '21 13 5d cd e2 5c')
    expect(rom, COPY_C, '2a 12 13 0d 20 fa c9')
    # 銀の 日本版の 文の 命令は $00〜$15 だけ（text_far が ない）→ 文は バンク5 の まま text_ram に する
    t0 = fo(5, 0x5D13)
    expect(rom, t0, '00' + (masaki + b'\x5b').hex())
    end = rom.index(0x58, t0); assert end - t0 == 36                     # <PROMPT> で おわる 37 バイト
    rest = bytes(rom[t0 + 7:end + 1])                                    # 「と　つないだ！…」
    txt = bytes([0x01]) + w16(PC_NAME_BUF) + bytes([0x00]) + rest       # text_ram 名前 / text_start …
    rom[t0:end + 1] = txt + bytes(37 - len(txt))
    # $05:$57F7「xor a / ldh [$D6],a / call $5874」（6 バイト）→ farcall $49：名前を 入れて、同じ ことを して c に かえす
    sm = f.put(masaki + b'\x5b\x50'); sd = f.put(dareka + b'\x5b\x50')
    code = bytes([0xFA]) + w16(BILL_FLAG_BYTE) + bytes([0x21]) + w16(sm) + \
        bytes([0xCB, 0x47 | (BILL_FLAG_BIT << 3), 0x20, 0x03, 0x21]) + w16(sd) + bytes([0x11]) + w16(PC_NAME_BUF) + \
        bytes([0x0E, 0x07, 0xCD]) + w16(COPY_C) + \
        bytes([0xAF, 0xE0, 0xD6,                                      # xor a / ldh [$D6], a
               0xCD, 0x29, 0x2F, 0x20, 0x03, 0x0E, 0x00, 0xC9,           # call $2F29 / jr nz / ld c, 0 / ret
               0xFA, 0x76, 0xD6, 0xA7, 0x0E, 0x01, 0xC8, 0x0E, 0x02, 0xC9])  # ld a,[$D676] / and a / c = 1 か 2
    hook = f.put(code)
    rom[fo(5, 0x57F7):fo(5, 0x57F7) + 6] = bytes([0x3E, FB, 0x21]) + w16(hook) + bytes([0xCF])   # farcall（a ＝ c で もどる）
    rom[fo(5, 0x5830):fo(5, 0x5830) + 2] = w16(PC_NAME_BUF)             # 表の「マサキの パソコン」→ WRAM
    log.append('第126弾 5：パソコンの 名前 %02X:%04X（$05:$57F7 から farcall）' % (FB, hook))


def nidoran(rom, log, f):
    """手持ちの アイコン（＝連れ歩きの 正面）は この MOD の ポケモンごとの 絵なので、人の絵の LoadOverworldMonIcon
    （$23:$6596。金銀の 共通の アイコン）では 同じに ならない → しるしの 種類 $FE の ときだけ、連れ歩きの 絵
    （絵 31 ＝ ニドラン♂：止まり 下 4 タイル ＋ 歩き 下 4 タイル）を 人の 色で 見える ように した 写しを わたす。"""
    sm = fo(5, 0x463B)
    expect(rom, sm, 'c9 4a 3a 0d 5a 2b 5e 29')
    expect(rom, fo(0x23, 0x6596), '7b cd 6f 67 6f 26 00 29 11 7b 68 19 2a 5f 56 06 23 0e 08 c9')
    pic = 31; src = fo(0x50 + pic // 42, 0x4000 + (pic % 42) * 384)
    gfx = bytearray(rom[src:src + 64] + rom[src + 12 * 16:src + 16 * 16])
    remap = [0, 2, 2, 3]                                                 # 色1・色2 → 色2（人の パレット）
    for i in range(0, len(gfx), 2):
        lo, hi = gfx[i], gfx[i + 1]; nlo = nhi = 0
        for x in range(8):
            v = remap[((lo >> x) & 1) | (((hi >> x) & 1) << 1)]
            nlo |= (v & 1) << x; nhi |= (v >> 1) << x
        gfx[i], gfx[i + 1] = nlo, nhi
    ga = f.put(bytes(gfx))
    h = Free(rom, 0x23)
    hook = h.put(bytes([0x7B, 0xFE, NIDO_MARK, 0x28, 0x06, 0xCD, 0x6F, 0x67, 0xC3, 0x9A, 0x65,
                        0x11]) + w16(ga) + bytes([0x06, FB, 0x0E, 0x08, 0xC9]))
    o = fo(0x23, 0x6596); rom[o:o + 3] = bytes([0xC3]) + w16(hook)
    rom[sm + NIDO_SPRITE - 0x80] = NIDO_MARK
    # ニビの 民家（14,3）の 2ばんめの 人（$82 ガーディ）
    gt = fo(0x25, 0x40ED); g, m = 14, 3
    hp = fo(0x25, int.from_bytes(rom[gt + 2 * (g - 1):gt + 2 * g], 'little')) + 9 * (m - 1)
    hh = rom[hp:hp + 9]; ao = fo(hh[0], int.from_bytes(hh[3:5], 'little')); sb = rom[ao + 6]
    o = fo(sb, int.from_bytes(rom[ao + 9:ao + 11], 'little')) + 2
    o += 1 + 5 * rom[o]; o += 1 + 8 * rom[o]; o += 1 + 5 * rom[o]
    cnt = rom[o]; o += 1
    objs = [o + 13 * i for i in range(cnt)]
    hit = [x for x in objs if rom[x] == 0x82]; assert len(hit) == 1, [rom[x] for x in objs]
    x = hit[0]
    rom[x] = NIDO_SPRITE
    rom[x + 3] = 0x06                                                   # SPRITEMOVEDATA_STANDING_DOWN
    assert rom[x + 7] == 0x90
    rom[x + 7] = NIDO_PAL << 4
    log.append('第126弾 6：ニビの ニドラン 人の絵 $%02X → 連れ歩きの 絵（%02X:%04X、$23:%04X）' % (NIDO_SPRITE, FB, ga, hook))


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    assert not any(rom[fo(FB, 0x4000):fo(FB, 0x8000)])
    f = Free(rom, FB, 0x4000)
    tackle(rom, log)
    gate(rom, log)
    route26(rom, log)
    follow(rom, log, f)
    bills_pc(rom, log, f)
    nidoran(rom, log, f)
    return rom
