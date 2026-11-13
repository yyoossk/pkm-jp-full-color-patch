# ポケットモンスター緑フルカラー ソース（Ver.1.8.0 から。今は Ver.1.12.0）

Ver.1.8.0 の ROM を 土台にして、これからの 直しや 追加を ソースで 書いて 当てる ための 一式です（金の 改良と 同じ やり方）。
元の ROM（緑 1.0・1.1）は 入って いません。

## 中身

| フォルダ・ファイル | 中身 |
|---|---|
| `base_ips/` | 土台：Ver.1.8.0 の パッチ 12種類（1.0・1.1 の どちらの 元の ROM に 当てても 同じ ROM） |
| `patches/main.asm` | **これからの 直しや 追加を 書く 所**（Ver.1.9.0・Ver.1.10.0・Ver.1.10.1・Ver.1.10.2・Ver.1.11.0・Ver.1.11.1・Ver.1.11.2・Ver.1.12.0 の 直し・追加が 入って いる） |
| `patches/dex_types.asm`・`patches/charmap.asm` | ずかんの キット（タイプ・進化・種族値）と、字の 番号 |
| `patches/tm_mart.asm` | 殿堂入りの あと、タマムシデパートの わざマシンの 店で 一回切りの わざマシンも 買える |
| `patches/changebox_fix.asm` | STARTボタンの「パソコン」で ボックスを かえた あと、話しかけると 止まるのを 直す |
| `patches/pc_item_swap.asm` | パソコンの どうぐの リストで、SELECT の 入れかえが できないのを 直す |
| `patches/pc_item_desc.asm` | パソコンの「どうぐを ひきだす」「どうぐを すてる」で、カーソルの 道具の 説明を 下の わくに 出す（ショップの 説明と 同じ。$D688 を 使う） |
| `patches/follow.asm`・`patches/follow/` | 連れ歩き（金銀グラフィックの 完全版・60fps版・151匹そろう版・151匹そろう版の60fps版だけ）。絵と 色は `tools/follow_gen.py` で 連れ歩きキットから 作る |
| `patches/editions/<版>.inc` | 版ごとに ちがう 番地を 書く 所（今は 空） |
| `tools/build.py` | 12種類の ROM を 組む（土台 ＋ patches）。CRC32 を 出す |
| `disasm/`（リポジトリには 入れない） | Ver.1.8.0 の 12種類 ぜんぶの 逆アセンブル（rgbds の 書き方）。処理の 場所を さがす ため。組み直すと 元と 1バイトも ちがわない。ROM の 中身が そのまま 入るので、下の 手順で 自分で 作る |
| `空きバンク.txt` | 版ごとの バンクの 空き（新しい 処理を おく 所） |
| `参考_キットのソース/` | Ver.1.8.0 で 足した 機能の うち、ソースが 残って いた もの（ボックスの数・コインとそだてや・わざマシンとサファリ・ずかんとわざの情報とショップ・PPの色）。今の ROM の 中身の 説明用（このままでは 組めません） |
| `tools/disasm.py`・`tools/asm.py`・`tools/sm83.py`・`tools/names.py` | 逆アセンブルを 作る 道具と、それを 組み直して 確かめる 小さい アセンブラ |

## 組み方

```
python3 tools/build.py 元の緑.gb
```

`out/` に 12種類の .gbc が できます。今の `patches/` で 組むと Ver.1.12.0 と 同じ CRC32 に なります
（8A34C561・E1B6143E・A43386BF・6DC756AD・F4C9FA71・AB1B65FF・C1B6A79E・29FC5B38・167984AA・18B25513・6CE035EF・C23F09F0）。

`patches/main.asm` が 空なら（土台だけ）Ver.1.8.0 と 同じ CRC32 に なります
（0EE87A90・7814120C・A43386BF・6DC756AD・9959DBBE・926B3C64・C1B6A79E・29FC5B38・8CC78F88・6319700C・2EB1FD3A・49C8A03C）。

`patches/main.asm` に 何か 書いた ときは rgbds（rgbasm・rgblink・rgbfix）が いります
（PATH に 通すか `tools/rgbds/` に おく。Windows の .exe も そのまま 使える）。`rgblink -O` で、書いた SECTION の 所だけ 土台の ROM の 上に かさねます。

## 逆アセンブルに ついて

作り方（`out/` に 12種類の ROM が ある ときに）：

```
python3 tools/build.py 元の緑.gb
python3 tools/disasm.py out disasm
```

- 元の ソースは なくなったので、Ver.1.8.0 の ROM から 作りました。処理の 名前や 説明は ほとんど なく、`B1c_6cfe` のような 番地の 名前です。
- 命令と 分かった 所は 命令、それ以外は `db`（データ、または 見つけられなかった 命令）です。
- 中身が 同じ バンクは 1つの ファイルに まとめて、`disasm/editions/<版>.asm` が その 版の バンクを ならべて います。
- 確かめ方：`python3 tools/asm.py disasm editions/<版>.asm 出力.gbc くらべるROM.gbc`（12種類とも「同じ」）。
  rgbds でも `cd disasm && rgbasm -o x.o editions/<版>.asm && rgblink -o x.gbc x.o` で 組めるように 書いて あります。
