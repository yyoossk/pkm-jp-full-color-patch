; ポケギアの 電話帳で、再戦できる トレーナーに 印を つける（金 日本版）
;
; ・電話で「また 戦おう」と いって きた トレーナー（EVENT_○○_READY_FOR_REMATCH が たって いる 人）の
;   行の 右はしに「！」を 出す（名前と しょくぎょうの あと。いちばん 長い しょくぎょうでも かさならない 所）。戦うと（イベントが 消えると）印も 消える。
;
; しくみ
;   ・PokegearPhone_UpdateDisplayList の さいごの「call PokegearPhone_UpdateCursor」を
;     バンク$24 の 空きの PhoneMark_Stub に（UpdateCursor の あと 新しい バンクの PhoneMark を farcall）。
;     UpdateDisplayList は 電話帳を かく とき・スクロール する とき に 呼ばれ、さいしょに 名前の 所を 空白で けすので、
;     印も そのたびに かきなおされる。
;   ・PhoneMark：見えて いる 4行（wPhoneList の wPokegearPhoneScrollPosition から）の 人の 番号を
;     PhoneMark_Events で イベントの 番号に して、たって いれば その 行の 右はし（x 18）に「！」。
;   ・イベントの 番号は 日本版 金の もの（英語版の 番号 ＋ 360）。PHONE_SCHOOLBOY_JACK（5）〜 PHONE_PICNICKER_ERIN（36）。
;
; 銀・クリスタルに 入れるとき：下の DEF と PhoneMark_Events を その ROM の 値に する
;   （銀の イベントの 番号は 金と 同じか、トレーナーの スクリプトの「checkevent ○○_READY_FOR_REMATCH」で 確かめる。
;     クリスタルは ENGINE_○○_READY_FOR_REMATCH（エンジンフラグ）なので 作りを かえる）

INCLUDE "src/charmap_jp.inc"

IF !DEF(PM_HOOK)
DEF PM_HOOK            EQU $5283      ; バンク$24 PokegearPhone_UpdateDisplayList の call PokegearPhone_UpdateCursor
DEF PM_HOOK_BANK       EQU $24
DEF PM_UpdateCursor    EQU $5220
DEF PM_STUB            EQU $7fe8      ; バンク$24 の 空き（10バイト）
DEF PM_PlaceString     EQU $0f46
DEF PM_wPhoneList      EQU $d98c
DEF PM_wScroll         EQU $c5d2      ; wPokegearPhoneScrollPosition
DEF PM_wEventFlags     EQU $d7aa
DEF PM_ROW0            EQU $c3a0 + 4 * 20 + 18   ; hlcoord 18, 4（1行め の 印）
DEF PM_ROWS            EQU 4
DEF PM_BANK            EQU $45
DEF PM_ADDR            EQU $6600
ENDC

SECTION "phonemark hook", ROMX[PM_HOOK], BANK[PM_HOOK_BANK]
	call PhoneMark_Stub
SECTION "phonemark stub", ROMX[PM_STUB], BANK[PM_HOOK_BANK]
PhoneMark_Stub:
	call PM_UpdateCursor
	ld a, BANK(PhoneMark)
	ld hl, PhoneMark
	rst $08
	ret

SECTION "phonemark", ROMX[PM_ADDR], BANK[PM_BANK]
PhoneMark:
	ld a, [PM_wScroll]
	ld e, a
	ld d, 0
	ld hl, PM_wPhoneList
	add hl, de
	ld c, 0                           ; 行
.loop
	ld a, [hli]
	push hl
	push bc
	call .IsReady
	jr nc, .next
	pop bc
	push bc
	ld hl, PM_ROW0
	ld de, 2 * 20
	ld a, c
	and a
	jr z, .place
.row
	add hl, de
	dec c
	jr nz, .row
.place
	ld de, .Mark
	call PM_PlaceString
.next
	pop bc
	pop hl
	inc c
	ld a, c
	cp PM_ROWS
	jr c, .loop
	ret

; a = 人の 番号 → キャリー：再戦できる
.IsReady
	cp PhoneMark_EventsEnd - PhoneMark_Events
	ret nc                            ; 表の 外（キャリーなし）
	ld e, a
	ld d, 0
	ld hl, PhoneMark_Events
	add hl, de
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	or h
	ret z                             ; 0 ＝ 再戦 なし
	ld a, l
	and 7
	ld b, a                           ; ビット
	srl h
	rr l
	srl h
	rr l
	srl h
	rr l
	ld de, PM_wEventFlags
	add hl, de
	ld a, [hl]
	inc b
.bit
	rrca
	dec b
	jr nz, .bit
	; いま キャリー ＝ その ビット
	ret

.Mark db "！@"

; 人の 番号（PHONE_○○）→ EVENT_○○_READY_FOR_REMATCH（日本版 金）
PhoneMark_Events:
	dw 0, 0, 0, 0, 0                                  ; 0 なし・ママ・オーキド・マサキ・ウツギ
	dw $0260, $0262, $0264                            ; 5 ジャック・6 ビバリー・7 ヒュー
	dw 0, 0, 0
	dw $026c, $026e, $0270, $0272, $0274              ; 11 ガビン・12 ベス・13 ホセ・14 レイナ・15 ジョーイ
	dw $0276, $0278, $027a, $027c, $027e              ; 16 ウェイド・17 ラルフ・18 リズ・19 アンソニー・20 トッド
	dw $0280, $0282, $0284, $0286                     ; 21 ジーナ・22 アーウィン・23 アーニー・24 アラン
	dw 0
	dw $028a, $028c, $028e, $0290, $0292              ; 26 ダナ・27 チャド・28 デリック・29 クリス・30 ブレント
	dw $0294, $0296, $0298, $029a, $029c, $029e       ; 31 ティファニー・32 バンス・33 ウィルトン・34 ケンジ・35 パーリー・36 エリン
PhoneMark_EventsEnd:
