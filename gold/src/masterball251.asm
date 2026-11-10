; 251ひき そろう版：コガネデパート 4F（ドーピングの 店）に ほのお・みず・かみなり・リーフ・つき・たいようの いし と
; おうじゃのしるし を 足す（ねだんは src/edition251_gold.asm）。
; バンク$05 に 空きが ないので、マスターボールの 店の しくみ（MasterBallMart。表の バンクを かえられる）に 足す。
; buildlist251 で src/masterball.asm の かわりに 組む（ふつうの 版の ROM は かわらない）
DEF MB_ED251 EQU 1
INCLUDE "src/masterball.asm"
