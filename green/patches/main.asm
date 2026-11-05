; これからの 直しや 追加は ここに 書く（今は 空 ＝ Ver.1.8.0 と 同じ ROM）。
; ・SECTION で バンクと 番地を 決めて 書くと、その 所だけ 土台の ROM の 上に かさなる。
;     SECTION "あたらしい 処理", ROMX[$7158], BANK[$09]   ; 空きは ../空きバンク.txt
;     SECTION "呼ぶ 所", ROMX[$4d02], BANK[$09]            ; 元の 命令を かえる 所
; ・版ごとに 番地が ちがう ときは、INCLUDE EDITION_INC で patches/editions/<版>.inc の 名前を 使う。
;   版の 番号は ED_0〜ED_11（tools/build.py の EDITIONS の じゅん）で、IF DEF(ED_4) などで 分けられる。
; ・処理の 名前と 番地は ../disasm/ の 逆アセンブル（と ../disasm/include/home_names.inc）を 見る。
