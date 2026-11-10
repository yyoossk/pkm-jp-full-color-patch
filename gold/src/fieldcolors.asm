;フィールドの色を ピカチュウ版フルカラーパッチ に近づける（金 日本版）
;   1. フィールドに落ちている道具のボール：ピカチュウ版の道具のボールと同じ（上が赤・下が白。帯はない）
;   2. ウツギ研究所の机の上の ポケモンが入っているボール：上が赤・まん中に黒い帯とボタン・下が白 の モンスターボールの見た目
;      （ピカチュウ版も 研究所など ポケモンが入っているボールだけ この絵にしている。道具のボールとは 見た目が別）
;   3. ポケモンセンターで回復するときの 機械の上のボールを、赤と白（モンスターボールの色）にする
;   4. フィールドの人の 肌の色を 少し薄くして、肌色に見えるようにする
;
; ボールの色（1・2 共通）
;    ・元は 赤のパレット（肌色・赤・黒）だけで描いていて、下が肌色（オレンジっぽい）だった。
;      白・赤・黒 の3色を持つパレットはなく、OBJ のパレット8つは ぜんぶ使われているので、新しいパレットは作らない。
;    ・OBJ は 8×8 ごとに パレットを決められるので、上の2枚（タイル 0・1）は 今までどおり 赤のパレット（赤・黒。光る所は 肌色）、
;      下の2枚（タイル 2・3）は 白・灰・黒 のパレット（PAL_OW_EMOTE。！の吹き出し などのもの）にして、下を白にする。
;      そのため 赤と白の さかいめは 8ドットめ（ピカチュウ版の道具のボールは 赤が 1ドット下まである）。
;    ・InitSprite で そのものが ボール（SPRITE_POKE_BALL か 研究所のボール）なら hCurSpriteOAMFlags の bit0（元は使っていない）を立て、
;      OAM を書く所で bit0 が立っていて 下の2枚なら パレットを PAL_OW_EMOTE にする。
; 研究所のボール（2）
;    ・道具のボールと同じ SPRITE_POKE_BALL なので、使われていない SPRITE_UNUSED_GUY（$3f）の表を 研究所のボールの絵
;      （4枚・動かない・赤のパレット）にして、ウツギ研究所の 3つのボールの object_event の スプライトを $3f にする。
;    ・研究所の3つのほかに、ポケモンが入っているボールは 金銀クリスタルには ない（りゅうのあなのボールは りゅうのキバ＝道具）。
; 3. 回復の機械の色（HealMachineAnim の .palettes。白・肌色・赤・黒）の 肌色を 白にする（ボールの下が白になる）。
; 4. MapObjectPals（朝・昼・夜・暗い の 赤・青・緑・茶・ピンク）の 色1（肌色 31,19,10）を ピカチュウ版と同じ 31,24,17 にする。

;---------------------------------------------------------------------
; ROM ごとにちがう所（金 日本版）。tools/fieldcolors_find.py で調べられる
;---------------------------------------------------------------------
IF !DEF(FC_INIT_HOOK)
DEF FC_OBJ_BANK        EQU $01
DEF FC_INIT_HOOK       EQU $5996   ; InitSprite の xor a / bit IN_GRASS_F, e / jr z / or OAM_PRIO / ldh [hCurSpriteOAMFlags], a（9バイト）
DEF FC_ATTR_HOOK       EQU $5a14   ; .addsprite の and OAM_PAL1|XFLIP|YFLIP|PRIO / or d / ld [bc], a（4バイト。FC_END_HOOK が ある ときは 使わない）
DEF FC_END_HOOK        EQU $5a20   ; InitSprite の さいごの ld a, c / ldh [hUsedSpriteIndex], a（79 e0 bf）
DEF FC_hUsedSpriteIndex EQU $ffbf
DEF FC_wShadowOAM      EQU $c300
DEF FC_END_FREE        EQU $7b3f   ; FieldColors_End を 置く 所（使われて いない IsObjectFacingSomeoneElse。44バイト。$7fc8〜 に 入りきらない）
DEF FC_hCurSpriteOAMFlags EQU $ffc4
DEF FC_FREE            EQU $7fc8   ; 同じバンクの空き（50バイト）
DEF FC_BALLGFX_BANK    EQU $31     ; PokeBallSpriteGFX（道具のボールの絵）
DEF FC_BALLGFX         EQU $7380
DEF FC_SPRITES_BANK    EQU $05     ; OverworldSprites（6バイトずつ。SPRITE_CHRIS = 1 から）
DEF FC_SPRITES         EQU $47b0
DEF FC_LABOBJ_BANK     EQU $13     ; ElmsLab の object_event の CyndaquilPokeBallScript の所（13バイトずつ 3つ）
DEF FC_LABOBJ          EQU $74bc
DEF FC_LABGFX_BANK     EQU $3f     ; 研究所のボールの絵（64バイト）を置く空き
DEF FC_LABGFX          EQU $7f00
DEF FC_NPCPALS_BANK    EQU $02     ; MapObjectPals（npc_sprites.pal）
DEF FC_NPCPALS         EQU $7834
DEF FC_HEALPAL_BANK    EQU $04     ; HealMachineAnim の .palettes
DEF FC_HEALPAL         EQU $6698
ENDC
IF !DEF(SPRITE_POKE_BALL)
DEF SPRITE_POKE_BALL   EQU $54
ENDC
IF !DEF(FC_SPRITE_LAB_BALL)
DEF FC_SPRITE_LAB_BALL EQU $3f     ; SPRITE_UNUSED_GUY（金銀クリスタルで 使われていない）
ENDC
DEF FC_PAL_EMOTE       EQU 5       ; PAL_OW_EMOTE（白・白・灰・黒）

; 肌の色
MACRO fc_rgb
	dw (\1) | (\2) << 5 | (\3) << 10
ENDM
DEF FC_SKIN_R EQU 31
DEF FC_SKIN_G EQU 24
DEF FC_SKIN_B EQU 17

;---------------------------------------------------------------------
; 1. ボール
SECTION "fieldcolors init hook", ROMX[FC_INIT_HOOK], BANK[FC_OBJ_BANK]
	call FieldColors_InitFlags
	ds 6, 0                      ; のこり 6バイトは nop

IF DEF(FC_END_HOOK)
; ボールの 下の 2枚は、その 人の OAM を 書きおえた あと（InitSprite の さいごの ld a, c / ldh [hUsedSpriteIndex], a）で
; まとめて なおす（1枚 ごとに call して いると、人の 多い 所で 60fps版が 重く なった）
SECTION "fieldcolors end hook", ROMX[FC_END_HOOK], BANK[FC_OBJ_BANK]
	call FieldColors_End
ELSE
SECTION "fieldcolors attr hook", ROMX[FC_ATTR_HOOK], BANK[FC_OBJ_BANK]
	call FieldColors_Attr
	nop
ENDC

SECTION "fieldcolors body", ROMX[FC_FREE], BANK[FC_OBJ_BANK]
; bc = object_struct、e = OBJECT_FLAGS2（元の処理 ＋ ボールなら bit0）
FieldColors_InitFlags:
	xor a
	bit 3, e                     ; IN_GRASS_F
	jr z, .not_in_grass
	or $80                       ; OAM_PRIO
.not_in_grass
	ld h, a
	ld a, [bc]                   ; OBJECT_SPRITE
	cp SPRITE_POKE_BALL
	jr z, .ball
	cp FC_SPRITE_LAB_BALL
	ld a, h
	jr nz, .set
	db $fe                       ; cp n（つぎの ld a, h を 飛ばす）
.ball
	ld a, h
	or 1
.set
	ldh [FC_hCurSpriteOAMFlags], a
	ret

IF DEF(FC_END_HOOK)
IF DEF(FC_END_FREE)
SECTION "fieldcolors end", ROMX[FC_END_FREE], BANK[FC_OBJ_BANK]
ENDC
; c = この 人の OAM の おわり（元の ld a, c / ldh [hUsedSpriteIndex], a ＋ ボールなら 下の 2枚の パレット）
; 人の 絵の タイルの はじめは 4 の 倍数 なので、OAM の タイルの bit1 ＝ 下の 2枚
FieldColors_End:
	ldh a, [FC_hCurSpriteOAMFlags]
	rra
	jr nc, .set
	ldh a, [FC_hUsedSpriteIndex]      ; この 人の 最初の OAM
	ld l, a
	ld h, HIGH(FC_wShadowOAM)
.loop
	ld a, l
	cp c
	jr nc, .set
	inc l
	inc l
	ld a, [hli]                       ; タイル
	and 2
	jr z, .next
	ld a, [hl]
	and $f8
	or FC_PAL_EMOTE
	ld [hl], a
.next
	inc l
	jr .loop
.set
	ld a, c
	ldh [FC_hUsedSpriteIndex], a
	ret
ELSE
; a = facing の attr、d = パレット、[hl - 1] = facing のタイル番号（元の and / or d / ld [bc], a ＋ ボールの下の2枚）
FieldColors_Attr:
	and $f0                      ; OAM_PAL1 | OAM_XFLIP | OAM_YFLIP | OAM_PRIO
	or d
	ld e, a
	ldh a, [FC_hCurSpriteOAMFlags]
	rra
	jr nc, .done
	dec hl
	ld a, [hli]
	and 2                        ; タイル 2・3 = 下の2枚
	jr z, .done
	ld a, e
	and $f8
	or FC_PAL_EMOTE
	ld e, a
.done
	ld a, e
	ld [bc], a
	ret
ENDC

SECTION "fieldcolors ball gfx", ROMX[FC_BALLGFX], BANK[FC_BALLGFX_BANK]
; 道具のボール（ピカチュウ版の道具のボールの絵。赤は 8ドットめまで）
; 上の2枚：1 = 光（肌色）、2 = 赤、3 = 黒。下の2枚：1 = 白、3 = 黒
	; タイル0（左上）
	db %00000000, %00000000   ; ........
	db %00000000, %00000000   ; ........
	db %00000011, %00000011   ; ......33
	db %00001100, %00001111   ; ....3322
	db %00010001, %00011110   ; ...32221
	db %00010001, %00011110   ; ...32221
	db %00100000, %00111111   ; ..322222
	db %00100000, %00111111   ; ..322222
	; タイル1（右上）
	db %00000000, %00000000   ; ........
	db %00000000, %00000000   ; ........
	db %11000000, %11000000   ; 33......
	db %00110000, %11110000   ; 2233....
	db %10001000, %01111000   ; 12223...
	db %10001000, %01111000   ; 12223...
	db %00000100, %11111100   ; 222223..
	db %00000100, %11111100   ; 222223..
	; タイル2（左下）
	db %00111111, %00100000   ; ..311111
	db %00111111, %00100000   ; ..311111
	db %00011111, %00010000   ; ...31111
	db %00011111, %00010000   ; ...31111
	db %00001111, %00001100   ; ....3311
	db %00000011, %00000011   ; ......33
	db %00000000, %00000000   ; ........
	db %00000000, %00000000   ; ........
	; タイル3（右下）
	db %11111100, %00000100   ; 111113..
	db %11111100, %00000100   ; 111113..
	db %11111000, %00001000   ; 11113...
	db %11111000, %00001000   ; 11113...
	db %11110000, %00110000   ; 1133....
	db %11000000, %11000000   ; 33......
	db %00000000, %00000000   ; ........
	db %00000000, %00000000   ; ........

SECTION "fieldcolors lab ball gfx", ROMX[FC_LABGFX], BANK[FC_LABGFX_BANK]
; 研究所のボール（ピカチュウ版の 研究所のボールの絵。黒い帯とボタン）
FieldColors_LabBallGFX:
	; タイル0（左上）
	db %00000000, %00000000   ; ........
	db %00000000, %00000000   ; ........
	db %00000011, %00000011   ; ......33
	db %00001100, %00001111   ; ....3322
	db %00011100, %00010011   ; ...31122
	db %00011000, %00010111   ; ...31222
	db %00100001, %00111111   ; ..322223
	db %00111111, %00111110   ; ..333331
	; タイル1（右上）
	db %00000000, %00000000   ; ........
	db %00000000, %00000000   ; ........
	db %11000000, %11000000   ; 33......
	db %00110000, %11110000   ; 2233....
	db %00001000, %11111000   ; 22223...
	db %00001000, %11111000   ; 22223...
	db %10000100, %11111100   ; 322223..
	db %11111100, %01111100   ; 133333..
	; タイル2（左下）
	db %00111111, %00111110   ; ..333331
	db %00111111, %00100001   ; ..311113
	db %00011111, %00010000   ; ...31111
	db %00011111, %00010000   ; ...31111
	db %00001111, %00001100   ; ....3311
	db %00000011, %00000011   ; ......33
	db %00000000, %00000000   ; ........
	db %00000000, %00000000   ; ........
	; タイル3（右下）
	db %11111100, %01111100   ; 133333..
	db %11111100, %10000100   ; 311113..
	db %11111000, %00001000   ; 11113...
	db %11111000, %00001000   ; 11113...
	db %11110000, %00110000   ; 1133....
	db %11000000, %11000000   ; 33......
	db %00000000, %00000000   ; ........
	db %00000000, %00000000   ; ........

; 使われていないスプライト（SPRITE_UNUSED_GUY）の表を 研究所のボールにする（overworld_sprite：dw 絵、db 長さ・バンク・形・パレット）
SECTION "fieldcolors lab ball sprite", ROMX[FC_SPRITES + (FC_SPRITE_LAB_BALL - 1) * 6], BANK[FC_SPRITES_BANK]
	dw FieldColors_LabBallGFX
	db 4 * 16, FC_LABGFX_BANK, 3, 0   ; 4枚、STILL_SPRITE、PAL_OW_RED

; ウツギ研究所の 3つのボール（object_event の はじめの 1バイト＝スプライト）
FOR FC_I, 3
SECTION "fieldcolors lab obj {d:FC_I}", ROMX[FC_LABOBJ + FC_I * 13], BANK[FC_LABOBJ_BANK]
	db FC_SPRITE_LAB_BALL
ENDR

;---------------------------------------------------------------------
; 2. 回復の機械（白・白・赤・黒）
SECTION "fieldcolors heal pal", ROMX[FC_HEALPAL + 2], BANK[FC_HEALPAL_BANK]
	fc_rgb 31, 31, 31

;---------------------------------------------------------------------
; 3. 肌の色（朝・昼・夜・暗い × 赤・青・緑・茶・ピンク の 色1）
FOR FC_T, 4
FOR FC_P, 5
SECTION "fieldcolors skin {d:FC_T} {d:FC_P}", ROMX[FC_NPCPALS + FC_T * 64 + FC_P * 8 + 2], BANK[FC_NPCPALS_BANK]
	fc_rgb FC_SKIN_R, FC_SKIN_G, FC_SKIN_B
ENDR
ENDR
