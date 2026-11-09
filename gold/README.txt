ポケットモンスター金 追加機能パッチ　ソース（Ver.1.2.1 のあと）
==================================================

このフォルダで python3 build.py を 実行すると、今の ROM が できます。
  ・kin.gbc（通常版）　CRC32 B87442D9
  ・kin60.gbc（60fps版）CRC32 7C3EB7B8
  （Ver.1.2.1 の あと、場所の名前の札を クリスタルと 同じに した。まだ リリースして いない。
    Ver.1.2.1 の リリースは 通常版 282A970B・60fps版 25F5129D）

用意するもの
  ・元の ROM：ポケットモンスター金 後期版（CRC32 4EF7F2A5）を base.gbc の 名前で このフォルダに おく
    （ROM は 入って いません）
  ・RGBDS 1.0.4（rgbasm・rgblink・rgbfix）。PATH に 入れるか、環境変数 RGBDS に その フォルダを 書く
  ・Python 3

フォルダ
  src/       追加機能・バグ修正の ソース（ファイルの 先頭に しくみの 説明）
  src/safari サファリゾーン（safari_gen.asm は ピカチュウの データから 作った もの）
  bf/        バグ修正で 使う データ
  gfxdata/   アイコン・ボールの 絵と 色
  data/      野生の ポケモンの 表
  tools/     アドレスを さがした ときの スクリプトなど（組み立てには 使わない）
  pokegold/  pret/pokegold の 定数・マクロ（includes.asm・constants・macros）
  build.py   組み立て
