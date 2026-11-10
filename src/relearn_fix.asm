; わざを思い出させてくれる人（クチバシティのポケモンだいすきクラブ）で、わざをえらぶと
; 暴走することがある（カブトプスの「きりさく」など）のを直す
;
; 原因：わざの一覧はリストメニュー（わざのリスト：wListMenuID = 1）で出している。リストメニューで A を
;   押すと、えらんだものの名前を GetName で読むが、名前の表のバンク（$D094）をいつも 1（道具の名前の
;   バンク）にしている（元のゲームのまま。元のゲームはわざのリストで A を押す所がない）。
;   わざの名前の表はバンク 4 なので、バンク 1 の同じ番地から「$50 を わざの番号ぶん」数えた所を
;   名前として 20 バイト写してしまう。その中に $50 がないと、名前を写す処理（$37CC）が止まらず、
;   メモリを全部上がきして暴走する（わざの番号によって、たまたま $50 があると止まる）。
; 直し方：名前の種類（$D093）が「わざ」（2）なら、バンクを 4 にしてから GetName を呼ぶ。

IF HAS_MOVE_RELEARN

DEF wNameListType EQU $D093
DEF wNameListBank EQU $D094
DEF MOVE_NAME EQU 2
DEF MOVE_NAMES_BANK EQU $04  ; GetMoveName（$3015）と同じ
DEF ITEM_NAMES_BANK EQU $01

; ld a, 1 / ld [$D094], a / call GetName（8 バイト）を、バンクを切りかえて呼ぶ形にする
SECTION "リストメニュー 名前のバンク", ROM0[ListMenuGetNameAddr]
	ld b, BANK(ListMenuGetName)
	ld hl, ListMenuGetName
	call Bankswitch

FreeBankA
ListMenuGetName:
	ld a, [wNameListType]
	cp MOVE_NAME
	ld a, ITEM_NAMES_BANK
	jr nz, .set
	ld a, MOVE_NAMES_BANK
.set
	ld [wNameListBank], a
	jp GetName

ENDC
