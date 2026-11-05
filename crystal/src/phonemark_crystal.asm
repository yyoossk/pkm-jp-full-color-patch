; ポケギアの 電話帳で、再戦できる トレーナーに 印を つける … クリスタル（日本版）用
; 金銀の src/phonemark.asm と 同じ ことを する。クリスタルは
;   ・再戦が エンジンフラグ（ENGINE_○○_READY_FOR_REMATCH ＝ wDailyRematchFlags $dc12〜$dc14 の 24ビット。
;     EngineFlags $20:$4462 の $65〜$7c 番で 確かめた）。人も 金と ちがう（ビバリー・アーウィン・デリック・ケンジは 再戦 なし、
;     クリス の かわりに タリー、パーリーが いる）。
;   ・PokegearPhone_UpdateDisplayList の さいごの call は 電話の 回数（phonefreq_crystal.asm）が 使って いるので、
;     名前を かく「call $438e」（1行ずつ。b ＝ 人、de ＝ 名前の 場所）を 入口に して、その 行の x 18 に「！」を かく。
;   ・入口は バンク$24 の 使われていない EntireFlyMap の あき（$6460〜）、処理は バンク$76。
INCLUDE "src/charmap_jp.inc"

DEF PM_GEAR_BANK      EQU $24
DEF PM_HOOK           EQU $52b1     ; PokegearPhone_UpdateDisplayList の call $438e（名前と しょくぎょうを かく）
DEF PM_PrintName      EQU $438e
DEF PM_STUB           EQU $6460     ; 使われていない EntireFlyMap の あき（ぶんぷの 時間帯 $6439〜$645c の あと）
DEF PM_wRematchFlags  EQU $dc12     ; wDailyRematchFlags（3バイト）
DEF PM_BANK           EQU $76
DEF PM_ADDR           EQU $6600

SECTION "phonemark hook", ROMX[PM_HOOK], BANK[PM_GEAR_BANK]
	call PhoneMark_Stub

SECTION "phonemark stub", ROMX[PM_STUB], BANK[PM_GEAR_BANK]
PhoneMark_Stub:                       ; b ＝ 人、de ＝ 名前の 場所
	push bc
	push de
	call PM_PrintName
	pop de
	pop bc
	ld a, BANK(PhoneMark_Row)
	ld hl, PhoneMark_Row
	rst $08                           ; FarCall は bc・de を そのまま わたす
	ret

SECTION "phonemark", ROMX[PM_ADDR], BANK[PM_BANK]
PhoneMark_Row:
	ld a, b
	cp PhoneMark_BitsEnd - PhoneMark_Bits
	ret nc
	ld c, a
	ld b, 0
	ld hl, PhoneMark_Bits
	add hl, bc
	ld a, [hl]
	cp $ff
	ret z                             ; 再戦 なし
	ld c, a
	and 7
	ld b, a                           ; ビット
	ld a, c
	rrca
	rrca
	rrca
	and $1f
	ld c, a
	push bc
	ld b, 0
	ld hl, PM_wRematchFlags
	add hl, bc
	pop bc
	ld a, [hl]
	inc b
.bit
	rrca
	dec b
	jr nz, .bit
	ret nc
	ld hl, 16                         ; 名前（x 2）から x 18 へ
	add hl, de
	ld [hl], $e7                      ; ！
	ret

; 人の 番号（PHONE_○○）→ wDailyRematchFlags の ビット（$ff ＝ 再戦 なし）
PhoneMark_Bits:
	db $ff, $ff, $ff, $ff, $ff        ; 0 なし・ママ・オーキド・マサキ・ウツギ
	db 0, $ff, 1                      ; 5 ジャック・6 ビバリー・7 ヒュー
	db $ff, $ff, $ff
	db 2, 3, 4, 5, 6                  ; 11 ガビン・12 ベス・13 ホセ・14 レイナ・15 ジョーイ
	db 7, 8, 9, 10, 11                ; 16 ウェイド・17 ラルフ・18 リズ・19 アンソニー・20 トッド
	db 12, $ff, 13, 14                ; 21 ジーナ・22 アーウィン・23 アーニー・24 アラン
	db $ff
	db 15, 16, $ff, 17, 18            ; 26 ダナ・27 チャド・28 デリック・29 タリー・30 ブレント
	db 19, 20, 21, $ff, 22, 23        ; 31 ティファニー・32 バンス・33 ウィルトン・34 ケンジ・35 パーリー・36 エリン
PhoneMark_BitsEnd:
