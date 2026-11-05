# ポケットモンスター青フルカラー 改良ソース

Ver.2.32 の12の版の ROM を土台にして、これからの直しや追加をここのソースに書き、
アセンブルして土台の ROM に当てる形で進める。

## 準備
1. RGBDS v0.9.2 を `tools/rgbds/` に置く（または PATH に入れる）
2. 元の「青」ROM（CRC32 E4468D14）から土台を作る
   `python3 build.py --makebase 元の青.gb`
   → `v232/` の ips から `base/<版>.gbc` が12個できる

## ビルド
`python3 build.py`（版を指定すればその版だけ）→ `out/<版>.gbc`
改良が何もないときは Ver.2.32 と同じ CRC になる。

## 版の名前
| 名前 | 版 |
|---|---|
| full_kin / full_kin_60 | 完全版 金銀グラフィック（通常／60fps） |
| full_sho / full_sho_60 | 完全版 初代グラフィック |
| color_kin / color_kin_60 | カラー化のみ 金銀グラフィック |
| color_sho / color_sho_60 | カラー化のみ 初代グラフィック |
| all151_kin / all151_kin_60 | 151匹そろう版 金銀グラフィック |
| all151_sho / all151_sho_60 | 151匹そろう版 初代グラフィック |

## 決まりごと
- 版ごとに違う場所（呼び出し口など）は `vars/<版>.inc` に書く
- 版を見分ける記号: `ED_FULL` `ED_COLOR` `ED_ALL151`, `GFX_KIN` `GFX_SHO`, `FPS60`
- 全版で空いているバンク: $24 $25 $35〜$3D（バンク0はほぼ空きがない）
