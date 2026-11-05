; Polished Crystal の 手持ちのポケモンの見た目（ミニアイコン）を移植（金銀版）
; （クリスタル追加機能キットの minis.asm から、日本版 銀（後期版）に合わせて作り直した）
;
; ・アイコンの絵：ポケモンごとの絵（Polished Crystal の gfx/minis、16×16 ×2コマ）
;   手持ち・名前入力・わざの画面・交換など、GetIconGFX でアイコンを読みこむ所はぜんぶこの絵になる。
; ・アイコンの色：手持ちの画面では、1匹ずつ専用の OBJ パレット（2〜7番）を使い、
;   そのポケモンの色（Polished Crystal のポケモンの色。色ちがいは色ちがいの色）にする。
;   どうぐ・メールを持っているときの印は 元のまま（パレット0）。
;
; クリスタルとちがう所
;   ・金銀は 1MB で空きのバンクがないので、ROM を 2MB にして バンク$40・$41 に絵、$42 に色と色の処理を置く
;     （build.py の rgbfix -p 0 で 2MB にのばし、ヘッダーの ROM の大きさも 2MB になる）。
;   ・金銀の色のデータ（wOBPals1・wOBPals2）は WRAM バンク0 にあるので、WRAM バンクは切りかえない。
;   ・種類番号は WRAM $de3c（ゲームデータの後ろの使われていない所。バグ修正が $de38〜$de3a、60fps が $de40〜）。
;   ・初代ゲームボーイ・スーパーゲームボーイ（hCGB = 0）では色を書かない（絵だけ変わる）。
;   ・金銀の VBlank は 色を送るフレームに 絵のコピーをしないので、hCGBPalUpdate は立てない
;     （手持ちの画面は アイコンのあとに SetDefaultBGPAndOBP で 色をまとめて送る）。
;
; データ（クリスタルのキットと同じもの。tools/mkminis.py で Polished Crystal から作れる）
;   gfxdata/minis.2bpp    … 0 = タマゴ、1〜251 = 図鑑番号順。1匹 8タイル（128バイト）
;   gfxdata/minipals.bin  … 0〜251、1匹 8バイト（ふつうの 明るい色・暗い色、色ちがいの 明るい色・暗い色）

INCLUDE "src/version.inc"

DEF hCGBPalUpdate      EQU $ffe7
DEF hCGB_GS            EQU $ffe8
DEF hObjectStructIndex EQU $ffb2
DEF wCurSpriteOAMFlags EQU $c5c0
DEF wPartySpecies      EQU $d9e9
DEF wPartyMon1DVs      EQU $d9f0 + 21
DEF wBGPals1           EQU $c200
DEF wBGPals2           EQU $c280
DEF wOBPals1           EQU $c240
DEF wOBPals2           EQU $c2c0
DEF wIconSpecies       EQU $de3c
DEF EGG                EQU $fd
DEF ICON_EGG           EQU $1c
DEF SPRITEANIMSTRUCT_VAR4 EQU $0f
DEF MINI_BANK          EQU $40       ; $40・$41（1バンクに128匹）
DEF MINIPAL_BANK       EQU $42
DEF ICONPAL_FIRST      EQU 2         ; 手持ちの1匹目 = OBJ パレット2
DEF Request2bpp        EQU $0de7

;---------------------------------------------------------------------
; バンク $23（アイコンの処理）
;---------------------------------------------------------------------
; ReadMonMenuIcon：種類番号を覚えておく（cp EGG / jr z, .egg）
SECTION "minis ReadMonMenuIcon", ROMX[$676f], BANK[$23]
	call Minis_SaveSpecies
	nop

; GetIconGFX：アイコンの絵の読みこみ先をポケモンごとの絵にする
;   ld a,[wCurIcon] … ld bc, BANK(Icons) << 8 | 8 / call Request2bpp（$66b9〜$66ce）
SECTION "minis GetIconGFX", ROMX[$66b9], BANK[$23]
	call Minis_GetIconSource       ; de = 絵、b = バンク、c = 8（hl はそのまま）
	call Request2bpp
	ds $66cf - @, 0
	ASSERT @ == $66cf

; LoadMenuMonIcon の表の MONICON_PARTYMENU：手持ちの画面のアイコンに色をつける
SECTION "minis party icon", ROMX[$65bf], BANK[$23]
	dw Minis_PartyMenuIcon

; アニメの1コマを作るとき（UpdateAnimFrame の call GetSpriteAnimFrame）：
;   色の番号を wCurSpriteOAMFlags の下の3ビットに入れる
SECTION "minis frame", ROMX[$5086], BANK[$23]
	call Minis_GetSpriteAnimFrame

; OAM の属性（GetSpriteOAMAttr）：色の番号があれば使う
SECTION "minis oam attr", ROMX[$5115], BANK[$23]
	jp Minis_GetSpriteOAMAttr

SECTION "minis bank 23", ROMX[$7e00], BANK[$23]
Minis_SaveSpecies:
	ld [wIconSpecies], a
	cp EGG
	ret nz
	pop hl                       ; ReadMonMenuIcon からぬける
	ld a, ICON_EGG
	ret

Minis_GetIconSource:
	ld a, [wIconSpecies]
	cp EGG
	jr nz, .species
	xor a                        ; タマゴ = 0番
.species
	ld b, MINI_BANK
	bit 7, a
	jr z, .low
	inc b
.low
	and $7f
	push hl
	ld l, a
	ld h, 0
REPT 7
	add hl, hl                   ; × 128
ENDR
	ld de, $4000
	add hl, de
	ld d, h
	ld e, l
	pop hl
	ld c, 8
	ret

Minis_PartyMenuIcon:
	call $65c7                   ; PartyMenu_InitAnimatedMonIcon（bc = アニメの構造体）
	ldh a, [hObjectStructIndex]
	add ICONPAL_FIRST
	or $80
	ld hl, SPRITEANIMSTRUCT_VAR4
	add hl, bc
	ld [hl], a                   ; 印：$80 | パレット番号
	ldh a, [hCGB_GS]
	and a
	ret z                        ; ゲームボーイカラーでないときは 色を書かない
	push bc
	ld a, BANK(Minis_LoadPartyIconPal)
	ld hl, Minis_LoadPartyIconPal
	rst $08
	pop bc
	ret

Minis_GetSpriteAnimFrame:
	call $5169                   ; GetSpriteAnimFrame
	push af
	push hl
	ld hl, SPRITEANIMSTRUCT_VAR4
	add hl, bc
	ld a, [hl]
	bit 7, a
	jr z, .done
	and %111
	ld l, a
	ld a, [wCurSpriteOAMFlags]
	and ~%111
	or l
	ld [wCurSpriteOAMFlags], a
.done
	pop hl
	pop af
	ret

; hl = OAM データの属性の所（その1つ前がタイルの番号）
Minis_GetSpriteOAMAttr:
	ld a, [wCurSpriteOAMFlags]
	ld b, a
	ld a, [hl]
	xor b
	and $e0
	ld b, a
	ld a, [hl]
	and $1f
	or b
	ld b, a
	ld a, [wCurSpriteOAMFlags]
	and %111
	jr z, .keep
	dec hl
	ld a, [hl]
	inc hl
	cp 8
	jr nc, .keep                 ; どうぐ・メールの印は元の色
	ld a, b
	and ~%111
	ld b, a
	ld a, [wCurSpriteOAMFlags]
	and %111
	or b
	ret
.keep
	ld a, b
	ret

;---------------------------------------------------------------------
; 絵（バンク $40・$41）
;---------------------------------------------------------------------
SECTION "minis gfx 1", ROMX[$4000], BANK[MINI_BANK]
	INCBIN "gfxdata/minis.2bpp", 0, 128 * 128
SECTION "minis gfx 2", ROMX[$4000], BANK[MINI_BANK + 1]
	INCBIN "gfxdata/minis.2bpp", 128 * 128

;---------------------------------------------------------------------
; 色（バンク $42）
;---------------------------------------------------------------------
SECTION "minis pals", ROMX[$4000], BANK[MINIPAL_BANK]
MiniIconPals:
	INCBIN "gfxdata/minipals.bin"

; [hObjectStructIndex] 番目の手持ちの色を OBJ パレット（2〜7）に入れる
Minis_LoadPartyIconPal:
	ldh a, [hObjectStructIndex]
	ld e, a
	ld d, 0
	ld hl, wPartySpecies
	add hl, de
	ld a, [hl]
	cp EGG
	jr nz, .got
	xor a
.got
	ld l, a
	ld h, 0
REPT 3
	add hl, hl                   ; × 8
ENDR
	ld bc, MiniIconPals
	add hl, bc
	push hl
; 色ちがい？（ぼうぎょ・すばやさ・とくしゅ が 10、こうげきが 2,3,6,7,10,11,14,15）
	ldh a, [hObjectStructIndex]
	ld hl, wPartyMon1DVs
	ld bc, PARTYMON_STRUCT_LENGTH
	call AddNTimes
	ld a, [hli]
	ld b, a
	ld a, [hl]
	pop hl
	cp $aa
	jr nz, .normal
	ld a, b
	and $0f
	cp $0a
	jr nz, .normal
	bit 5, b
	jr z, .normal
	inc hl
	inc hl
	inc hl
	inc hl
.normal
	ld a, [hli]
	ld c, a
	ld a, [hli]
	ld b, a
	ld a, [hli]
	ld e, a
	ld d, [hl]                   ; bc = 明るい色、de = 暗い色
	ldh a, [hObjectStructIndex]
	add ICONPAL_FIRST
	add a
	add a
	add a                        ; × 8（1パレット）
	ld l, a
	ld h, 0
	push hl
	push de
	ld de, wOBPals1
	add hl, de
	pop de
	call .write
	pop hl
	; 画面に出ている色（wOBPals2）にも書くのは、画面が できあがって いる ときだけ。
	; 開く とちゅう（白い 画面）に 書くと、アイコン だけ 先に 色が ついて 見える ことが ある。
	; できあがって いるか どうかは BG パレット0 が wBGPals1 と wBGPals2 で 同じか で 見る
	; （ちがう ときは、このあとの SetDefaultBGPAndOBP が wOBPals1 から うつす）
	push hl
	push de
	ld hl, wBGPals1
	ld de, wBGPals2
	ld a, 8
.cmp
	push af
	ld a, [de]
	cp [hl]
	jr nz, .notshown
	pop af
	inc hl
	inc de
	dec a
	jr nz, .cmp
	pop de
	pop hl
	push de
	ld de, wOBPals2
	add hl, de
	pop de
	jp .write
.notshown
	pop af
	pop de
	pop hl
	ret
; hCGBPalUpdate は立てない。金銀の VBlank は 色を送るフレームには 絵のコピー（Request2bpp）をしないので、
; ここで立てると 次のポケモンの絵のコピーが捨てられる。手持ちの画面は アイコンを読んだあとに
; SetDefaultBGPAndOBP（wOBPals1 → wOBPals2 → 送る）を通るので、色はそこでまとめて送られる。
; （前は 1フレーム待っていたが、画面ができる前に 白い画面にアイコンだけが出てしまった）

.write
	ld a, $ff                    ; 0：白（透明）
	ld [hli], a
	ld a, $7f
	ld [hli], a
	ld a, c                      ; 1：明るい色
	ld [hli], a
	ld a, b
	ld [hli], a
	ld a, e                      ; 2：暗い色
	ld [hli], a
	ld a, d
	ld [hli], a
	xor a                        ; 3：黒
	ld [hli], a
	ld [hl], a
	ret
