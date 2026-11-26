"""第128弾（報告の 直し）キットの 金版。
   setup(E)：マップを 移す 前（c2g.EXTRA_BGS）… 3 グレンジム（G26_061）の (17,13) に 像（上向きで 調べる）を 足す。
   apply(g, log, FB)：マップを 移した あと（FB ＝ この 弾の バンク）。
    1 おかあさんの 電話（36:58D1「もしもし… あら <PLAYER> ウツギはかせが よんでいたんじゃ なかったかしら？」：
      金で ウツギはかせから ポケモンを もらう 前の 文。カントーでは いつも これ）→「… げんき？ からだに きをつけて がんばってね！」。
    2 手持ちが いっぱいで 捕まえた ポケモン：マサキに 会う 前（イベント $835 が まだ）は「だれかの パソコンへ てんそうされた！」
      （03:6F2F の「ld hl, 03:718F / call PrintText」→ FB へ farcall、2つの 文の どちらかを 出す）。
    3 カントーの ジムの 像（ポート した 8つ、フラグ $22〜$29）：赤と 同じく バッジの 前は「<リーダー> にんてい トレーナー！ シゲル」、
      あとは「シゲル <PLAYER>」。像の スクリプトの はじめ 4バイトを FB への farsjump に。
    4 ニビ博物館1階（G26_079）の 化石：看板の callasm の 先の はじめに RefreshScreen（00:2E3C）。
    5 ニビの ニドラン（AE:408D の 人）：スクリプトの はじめに faceplayer。
    6・7 戦闘の 状態異常の 色（追加機能パッチ、バンク $49）：状態の 文字が HP 欄の どの マスに あっても 見つけて 色を つける。
      レベルアップの 能力値の 箱（0F:6EA0 / 0F:6EC3）の 前後で HP 欄の 行を ふつうの 色に／色を つけ直す（キットの p128_status）。
    9 GivePoke（03:6591）：SRAM を 開いて、ボックスへ 送る ポケモンの 持ち物を いつも 書く（0 ＝ なし）。
   10 自分の 部屋の ゲーム機：「ファミコンを してる！」→「ロクヨンを してる！」。
   8 おつきみ山：B2F の 隠し道具 2つは MOD 側（kj6/make_kj6.sh）、1F の ボール（みずでっぽう）は gold_tutor.py。
   11 たいあたり：金には 当てはまらない（金には 第126弾の たいあたりの 直しが ない。録画で 絵全体が 動く ことを 確かめた）。
"""
import os, re, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
import c2g, gold_tutor
RGBDS = os.environ.get('RGBDS', '/home/claude/rgbds-src')
def fo(b, a): return b * 0x4000 + a - 0x4000
def w16(v): return bytes([v & 0xFF, v >> 8])
def expect(g, o, h):
    b = bytes.fromhex(h.replace(' ', '')); assert bytes(g[o:o + len(b)]) == b, (hex(o), g[o:o + len(b)].hex(' '), h); return b
T, enc = gold_tutor.T, gold_tutor.enc

EVENT_MET_BILL = 0x0835
EFA, PRINT_TEXT, REFRESH_SCREEN = 0x2EEB, 0x0F30, 0x2E3C
GREEN = 0x39
BADGES = range(0x22, 0x2A)            # ENGINE_BOULDERBADGE〜ENGINE_EARTHBADGE（金）
CINNABAR = ('G26_061', (17, 13), 0x28, 0x2E)    # グレンジム、像、ENGINE_VOLCANOBADGE、BLAINE


def tail(g, b):
    B = g[b * 0x4000:(b + 1) * 0x4000]; e = len(B)
    while e and B[e - 1] == 0: e -= 1
    return 0x4000 + e + 2


class Free:
    def __init__(s, g, bank, start=None): s.g, s.bank, s.a = g, bank, start or tail(g, bank)
    def put(s, data):
        o = fo(s.bank, s.a); assert s.a + len(data) <= 0x8000 and not any(s.g[o:o + len(data)]), (hex(s.bank), hex(s.a))
        s.g[o:o + len(data)] = data; r = s.a; s.a += len(data); return r


def setup(E):
    cname, (x, y), flag, cls = CINNABAR
    def f(E_, gb, alloc, grom):
        a = alloc(16, gb)
        sc = bytes([0x34, flag, 0x00, 0x09]) + w16(a + 9) + bytes([0x0C, 0x27, 0x00,      # checkflag / iftrue / jumpstd GymStatue1
                                                                   0x43, cls, 0x01, 0x01, 0x0C, 0x28, 0x00])  # gettrainername / GymStatue2
        grom[fo(gb, a):fo(gb, a) + 16] = sc
        return [bytes([y, x, 0x01]) + w16(a)]                                            # BGEVENT_UP
    c2g.EXTRA_BGS[cname] = f


def mom_call(g, log):
    # 電話の おかあさん（ウツギはかせから ポケモンを もらう 前）：「もしもし… あら <PLAYER> ウツギはかせが よんでいたんじゃ なかったかしら？」
    o = fo(0x36, 0x58D1); expect(g, o, '00 d3 bc d3 bc 75 51 b1 d7 7f 52 4f 82 91 06 ca b6 be 4a')
    old = bytes(g[o:g.index(0x57, o) + 1])
    new = old[:12] + enc('げんき？<PARA>からだに　きをつけて<LINE>がんばってね！<DONE>'); assert len(new) <= len(old)
    g[o:o + len(new)] = new
    log.append('第128弾 1 おかあさんの 電話：36:58D1')


def bill_transfer(g, log, f):
    at = 0x0C000 + 0x6F2F - 0x4000; expect(g, at, '21 8f 71 cd 30 0f')
    src = fo(3, 0x718F); e = g.index(0x58, src) + 1
    orig = bytes(g[src:e]); masaki = enc('は　マサキの　ところへ'); assert orig.count(masaki) == 1, orig.hex(' ')
    someone = orig.replace(masaki, enc('は　だれかの　パソコンへ'))
    tb = f.put(orig); ts = f.put(someone)
    code = bytes([0x11]) + w16(EVENT_MET_BILL) + bytes([0x06, 0x02, 0xCD]) + w16(EFA) + \
        bytes([0x79, 0xA7, 0x21]) + w16(tb) + bytes([0x20, 0x03, 0x21]) + w16(ts) + bytes([0xCD]) + w16(PRINT_TEXT) + bytes([0xC9])
    r = f.put(code)
    g[at:at + 6] = bytes([0x3E, f.bank, 0x21]) + w16(r) + bytes([0xCF])
    log.append('第128弾 2 ボックスへ 転送の 文：03:6F2F → %02X:%04X' % (f.bank, r))


def gym_statues(g, log, f):
    G_ = bytes(g); hits = []
    for m in re.finditer(rb'\x34(.)\x00\x09(..)\x0c\x27\x00\x43(..)\x01\x0c\x28\x00', G_, re.S):
        b = m.start() // 0x4000
        if b >= 0x80 and m.group(1)[0] in BADGES: hits.append(m.start())
    assert sorted(G_[h + 1] for h in hits) == list(BADGES), [hex(G_[h + 1]) for h in hits]
    head = bytes([0x01, 0xA8, 0xCF, 0x00, 0x7F]) + enc('にんてい　') + bytes([0x5D]) + enc('！<LINE>')   # <STRBUF4>　にんてい　{5D}！
    t1 = f.put(head + bytes([GREEN, 0x57])); t2 = f.put(head + bytes([GREEN, 0x7F, 0x52, 0x57]))
    k = {}
    for n, t in (('1', t1), ('2', t2)):
        k[n] = f.put(bytes([0x42, 0x00, 0x47, 0x4B, 0x36]) + w16(0x4B19) +                 # getcurlandmarkname / opentext / farwritetext CityGym
                     bytes([0x54, 0x4C]) + w16(t) + bytes([0x53, 0x49, 0x90]))
    for h in hits:
        flag = G_[h + 1]; cls = G_[h + 10:h + 12]
        s = f.put(bytes([0x43]) + cls + bytes([0x01, 0x34, flag, 0x00, 0x09]) + w16(k['2']) + bytes([0x03]) + w16(k['1']))
        g[h:h + 4] = bytes([0x04, f.bank]) + w16(s)
        log.append('第128弾 3 ジムの 像 %02X:%04X（バッジ %02X）→ %02X:%04X' % (h // 0x4000, 0x4000 + h % 0x4000, flag, f.bank, s))


def fossils(g, log):
    n = 0
    for a in (0x46D2, 0x46B1):
        o = fo(0x9D, a); assert g[o] == 0x0E
        cb, ca = g[o + 1], g[o + 2] | g[o + 3] << 8; r = fo(cb, ca)
        assert g[r] == 0x3E and g[r + 1] in (0x8D, 0x8E) and g[r + 2:r + 5] == b'\xea\xfe\xcf', g[r:r + 5].hex(' ')
        s = Free(g, cb).put(bytes([0xCD]) + w16(REFRESH_SCREEN) + bytes([0xC3]) + w16(ca))
        g[o + 2:o + 4] = w16(s); n += 1
        log.append('第128弾 4 化石の 看板 9D:%04X → %02X:%04X（RefreshScreen → %04X）' % (a, cb, s, ca))
    assert n == 2


def nidoran_face(g, log):
    o = fo(0xAE, 0x408D); expect(g, o, 'e3 09 08 06 00 ff ff 90 00 07 40')
    expect(g, fo(0xAE, 0x4007), '47 4c 11 40 83 20 00 53 49 90')
    s = Free(g, 0xAE).put(bytes([0x6A, 0x03]) + w16(0x4007))
    g[o + 9:o + 11] = w16(s)
    log.append('第128弾 5 ニドラン：faceplayer（AE:%04X）' % s)


def givepoke_box_item(g, log, f):
    # 金では .done（03:659D）に 手持ちの 道（03:6558・656A）からも 飛んで くるので、659D から あとは そのまま。
    # ボックスの 道の 12バイト（6591〜659C）を「farcall FB の ルーチン / jr 659D」に（バンク 3 には 空きが ない）
    o = fo(3, 0x6591); expect(g, o, 'fa fc cf a7 28 06 fa fc cf ea 31 ad fa fe cf ea 43 d1 ea df d0')
    sub = f.put(bytes.fromhex('3e01cd9d30' 'fafccfea31ad' 'c3ad30'))     # OpenSRAM 1 / 持ち物（0＝なし）/ CloseSRAM へ
    g[o:o + 12] = bytes([0x3E, f.bank, 0x21]) + w16(sub) + bytes([0xCF, 0x18, 0x04]) + bytes(4)
    assert o + 8 + 4 == fo(3, 0x659D)
    log.append('第128弾 9 GivePoke：ボックスの ポケモンの 持ち物（03:6591 → %02X:%04X）' % (f.bank, sub))


def console_text(g, log):
    o = fo(0x8A, 0x5374); expect(g, o, '00 52 ca 4f')
    e = g.index(0x57, o) + 1; body = bytes(g[o:e])
    fc = enc('ファミコン'); assert body.count(fc) == 1, body.hex(' ')
    new = body.replace(fc, enc('ロクヨン')); g[o:o + len(new)] = new
    log.append('第128弾 10 部屋の ゲーム機：ロクヨン（8A:5374）')


STATUS_ASM = r'''
DEF TM  EQU $c3a0
DEF AM  EQU $cccd
DEF SC_Kind       EQU $4000
DEF SC_SetColor3  EQU $401c
DEF SC_SetColor1  EQU $4041
DEF SC_WriteVRAM  EQU $40c7
DEF SC_String     EQU $4121
DEF SC_Strings    EQU $412f
DEF HUD_Update    EQU $41b6
DEF HUD_Party     EQU $41bb
DEF wBattleMonStatus   EQU $cb10
DEF wBattleMonNickname EQU $cafc
DEF E_ROW   EQU TM + 1 * 20
DEF P_ROW   EQU TM + 8 * 20
DEF E_VRAM  EQU $9800 + 1 * 32
DEF P_VRAM  EQU $9800 + 8 * 32

SECTION "p128", ROMX[CODE_ADDR], BANK[$49]

; HP box status (StatusColor_HUD, battle): bc = status cell, d = status
NewSide::
	ld a, b
	cp HIGH(P_ROW + 10)
	jr nz, .enemy
	ld a, c
	sub LOW(P_ROW + 10)
	cp 8
	jr nc, .enemy
	push bc
	ld a, d
	call SC_Kind
	push af
	ld de, $0106
	call SC_SetColor1
	pop af
	pop bc
	call PlayerAt
	jp HUD_Update
.enemy
	ld a, b
	cp HIGH(E_ROW + 2)
	jp nz, HUD_Party
	ld a, c
	sub LOW(E_ROW + 2)
	cp 8
	jp nc, HUD_Party
	push bc
	ld a, d
	call SC_Kind
	ld de, $0105
	call SC_SetColor3
	ld hl, AM + 1 * 20 + 2
	ld b, 9
	ld a, 2
	call Fill
	pop hl
	call EnemyCells
	jr CopyEnemy

; a = kind (0: none), bc = cell (row 8)
PlayerAt:
	push af
	call PlayerPlain
	pop af
	and a
	jr z, CopyPlayer
	push bc
	call SC_String
	ld hl, $9000 + $7c * 16
	call Glyphs
	pop hl
	ld a, $7c
	ld [hli], a
	inc a
	ld [hli], a
	inc a
	ld [hl], a
	dec hl
	dec hl
	call PlayerCells
CopyPlayer:
	ld hl, P_ROW + 10
	ld de, P_VRAM + 10
	ld b, 10
	jr CopyCells
CopyEnemy:
	ld hl, E_ROW
	ld de, E_VRAM
	ld b, 11
CopyCells:
.cell
	push bc
	push hl
	ld bc, AM - TM
	add hl, bc
	ld c, [hl]
	call ReadV1
	cp c
	jr z, .same
	pop hl
	push hl
	ld a, [hl]
	ld h, d
	ld l, e
	call SC_WriteVRAM
	dec hl
	ld a, c
	call WriteV1
.same
	pop hl
	pop bc
	inc hl
	inc de
	dec b
	jr nz, .cell
	ret

ReadV1:
	di
	ld a, 1
	ldh [$ff4f], a
.w
	ldh a, [$ff41]
	and %10
	jr nz, .w
	ld a, [de]
	push af
	xor a
	ldh [$ff4f], a
	pop af
	ei
	ret

WriteV1:
	push bc
	ld c, a
	di
	ld a, 1
	ldh [$ff4f], a
.w
	ldh a, [$ff41]
	and %10
	jr nz, .w
	ld [hl], c
	xor a
	ldh [$ff4f], a
	ei
	inc hl
	ld a, c
	pop bc
	ret

ReadV0:
	di
.w
	ldh a, [$ff41]
	and %10
	jr nz, .w
	ld a, [de]
	ei
	ret

Glyphs:
	ld b, 3
.char
	push bc
	ld a, [de]
	inc de
	push de
	push hl
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	bit 7, a
	ld de, $9000
	jr z, .low
	ld de, $8000
.low
	add hl, de
	ld d, h
	ld e, l
	pop hl
	ld b, 8
.row
	call ReadV0
	inc de
	inc de
	call WriteV1
	xor a
	call WriteV1
	dec b
	jr nz, .row
	pop de
	pop bc
	dec b
	jr nz, .char
	ret

Fill:
	push bc
.f
	ld [hli], a
	dec b
	jr nz, .f
	pop bc
	ret

PlayerPlain:
	push bc
	ld hl, AM + 8 * 20 + 10
	ld b, 10
	ld a, 3
	call Fill
	pop bc
	ret

PlayerCells:
	ld de, AM - TM
	add hl, de
	ld a, $0e
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ret

EnemyCells:
	ld de, AM - TM
	add hl, de
	ld a, l
	sub LOW(AM + 1 * 20)
	ld b, 11
	sub b
	cpl
	inc a
	cp 4
	jr c, .n
	ld a, 3
.n
	ld b, a
	ld a, 5
	jr Fill

LayoutEnemy::
	push bc
	push de
	ld hl, AM + 1 * 20 + 2
	ld b, 9
	ld a, 2
	call Fill
	ld hl, E_ROW + 8
	ld c, 7
.x
	push hl
	ld de, SC_Strings
	ld b, 5
.s
	ld a, [de]
	cp [hl]
	jr nz, .no
	inc hl
	inc de
	ld a, [de]
	dec de
	cp [hl]
	dec hl
	jr z, .found
.no
	inc de
	inc de
	inc de
	dec b
	jr nz, .s
	pop hl
	dec hl
	dec c
	jr nz, .x
	jr .done
.found
	pop hl
	call EnemyCells
.done
	pop de
	pop bc
	ret

; 金：HP 欄が 消えて いる（どうぐを 使った とき など、$7f）のに 状態異常 なら、名前の あとの ます（11 ＋ 名前の 長さ）を
;   色1 の 文字（バンク1・6本目）に（もとの gold_fixes.fix_statuscolor_item を 名前の 長さに 合わせた）
LayoutPlayer::
	push bc
	push de
	call PlayerPlain
	ld hl, P_ROW + 10
	ld b, 8
.x
	ld a, [hl]
	cp $7c
	jr z, .found
	inc hl
	dec b
	jr nz, .x
	ld a, [wBattleMonStatus]
	and a
	jr z, .done
	ld hl, wBattleMonNickname
	ld bc, P_ROW + 11
.len
	ld a, [hli]
	cp $50
	jr z, .got
	inc bc
	ld a, c
	cp LOW(P_ROW + 16)
	jr nz, .len
.got
	ld h, b
	ld l, c
	ld a, [hl]
	cp $7f
	jr nz, .done
.found
	call PlayerCells
.done
	pop de
	pop bc
	ret

BoxPre::
	xor a
	ld [$ce53], a
	ld a, $1f
	call $2e05
	ld hl, TM + 9
	ld b, 10
	ld c, 9
	call $0ec1
	ld hl, AM + 1 * 20 + 2
	ld b, 9
	ld a, 2
	call Fill
	call PlayerPlain
	call CopyEnemy
	jp CopyPlayer

; 金：箱の 下の タイルが VRAM に 移り きる 前に 状態の ますを 直に 書くと、残った 箱の 上に 色つきの 状態が 2コマ 出る。
;   状態の ます（$7C〜$7E）を いったん 空白に して WaitBGMap（00:33AE）で 移し 終えてから もどす
BoxPost::
	call $0a26
	call $3120
	ld hl, P_ROW + 10
	ld b, 8
.find
	ld a, [hl]
	cp $7c
	jr z, .hide
	inc hl
	dec b
	jr nz, .find
	call $33ae
	jr .shown
.hide
	push hl
	ld a, $7f
	ld [hli], a
	ld [hli], a
	ld [hl], a
	call $33ae
	pop hl
	ld a, $7c
	ld [hli], a
	inc a
	ld [hli], a
	inc a
	ld [hl], a
.shown
	call LayoutEnemy
	call LayoutPlayer
	call CopyEnemy
	jp CopyPlayer
'''
STATUS_ADDR = 0x5000


def status_colors(g, log):
    o = fo(0x49, STATUS_ADDR); assert not any(g[o:o + 0x400])
    expect(g, fo(0x49, 0x4000), '47 3e 01 cb 58 c0')
    expect(g, fo(0x49, 0x401C), 'd5 87'); expect(g, fo(0x49, 0x4041), 'd5 87')
    expect(g, fo(0x49, 0x40C7), 'c5 4f f3 f0 41 e6 02 20 fa 71 fb 23 79 c1 c9')
    expect(g, fo(0x49, 0x4121), '3d 5f 87 83 5f 16 00 21 2f 41')
    expect(g, fo(0x49, 0x412F), '70 b8 7f d4 b9 70 ba b5 d8 cf cb 7f c8 d1 d8')
    expect(g, fo(0x49, 0x413E), '21 e9 cc 3e 05 22 22 77')
    expect(g, fo(0x49, 0x4150), 'cd 00 7f 00 00 00 00 00 00 00 00 21 7d cd 22 22 77')
    expect(g, fo(0x49, 0x4185), 'fa 08 d1 a7 28 30 21 50 c4 cd f2 41 28 14 21 bc c3 cd f2 41 20 20')
    expect(g, fo(0x49, 0x41B6), '3e 01 e0 e7 c9 21 2d 09')
    expect(g, fo(0x0F, 0x6EA0), 'af ea 53 ce 3e 1f cd 05 2e 21 a9 c3 06 0a 0e 09 cd c1 0e 21 d3 c3')
    expect(g, fo(0x0F, 0x6EBE), '0e 1e cd 3c 03 cd 26 0a cd 20 31 af ea 53 ce')
    with tempfile.TemporaryDirectory() as d:
        open(d + '/a.asm', 'w').write(STATUS_ASM)
        open(d + '/in.gbc', 'wb').write(bytes(g))
        subprocess.run([RGBDS + '/rgbasm', '-D', 'CODE_ADDR=$%X' % STATUS_ADDR, '-o', d + '/a.o', d + '/a.asm'], check=True)
        subprocess.run([RGBDS + '/rgblink', '-O', d + '/in.gbc', '-o', d + '/out.gbc', '-n', d + '/out.sym', d + '/a.o'], check=True)
        new = open(d + '/out.gbc', 'rb').read()
        sym = {l.split()[1]: int(l.split()[0].split(':')[1], 16) for l in open(d + '/out.sym') if re.match(r'[0-9a-f]+:[0-9a-f]+ ', l)}
    diff = [i for i in range(len(g)) if g[i] != new[i]]
    assert diff and min(diff) >= o and max(diff) < fo(0x49, 0x5400), (hex(min(diff)), hex(max(diff)))
    g[min(diff):max(diff) + 1] = new[min(diff):max(diff) + 1]
    def W(b, a, data): g[fo(b, a):fo(b, a) + len(data)] = bytes(data)
    W(0x49, 0x413E, bytes([0xCD]) + w16(sym['LayoutEnemy']) + bytes(5))
    W(0x49, 0x4150, bytes([0xCD]) + w16(sym['LayoutPlayer']) + bytes([0x18, 0x0C]) + bytes(12))
    W(0x49, 0x418B, bytes([0xC3]) + w16(sym['NewSide']))
    W(0x0F, 0x6EA0, bytes([0x3E, 0x49, 0x21]) + w16(sym['BoxPre']) + bytes([0xCF, 0x18, 0x0B]) + bytes(11))
    W(0x0F, 0x6EC3, bytes([0x3E, 0x49, 0x21]) + w16(sym['BoxPost']) + bytes([0xCF]))
    log.append('第128弾 6・7 状態異常の 色（HP 欄の どの ますでも）・レベルアップの 箱：49:%04X（%d バイト）' % (STATUS_ADDR, max(diff) + 1 - o))


def apply(g, log, FB):
    f = Free(g, FB, 0x4000)
    mom_call(g, log)
    bill_transfer(g, log, f)
    gym_statues(g, log, f)
    fossils(g, log)
    nidoran_face(g, log)
    status_colors(g, log)
    givepoke_box_item(g, log, f)
    console_text(g, log)
