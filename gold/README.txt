ポケットモンスター金 追加機能パッチ　ソース（Ver.1.2.1 のあと）
==================================================

このフォルダで python3 build.py を 実行すると、今の ROM が できます。
  ・kin.gbc（通常版）　CRC32 6756A590
  ・kin60.gbc（60fps版）CRC32 2BB1A520
  （Ver.1.2.1 の あと、まだ リリースして いない もの：
    ・場所の名前の札を クリスタルと 同じに した
    ・全ポケモンの 連れ歩き（src/follow_gold.asm。金銀連れ歩きキットから。話しかけると 会話・ピカチュウは 表情の 絵、
      手持ちの 画面の SELECT で 連れ歩く ポケモンを えらぶ、ボールの 出入り、Bダッシュ）
    ・相手の HP の わくの 線を 数字の 下に（src/enemyhp_gold.asm）
    ・クリスタル追加機能キットの 51〜57：16この バッジの あとの 四天王・ワタル・ライバル（src/league.asm）、
      景品の わざマシンの わざの 名前（src/prizetm_gold.asm）、サファリの 歩数・ボールの 表示（src/safari/safari.asm）、
      そだてやで 今の レベル（src/daycarehint.asm）、状態異常・PP の 色（src/statuscolor_gold.asm）、
      ずかんの タイプ・種族値・進化の ページ（src/dexinfo_gold.asm）
    ・スタートメニューの ならび：ずかん・ポケモン・リュック・ポケギア・パソコン・主人公・レポート・せってい
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
  gfxdata/   アイコン・ボールの 絵と 色、連れ歩きの 絵（follow・follow_cc・follow_icon）、ピカチュウの 表情の 絵（pikapic）
  data/      野生の ポケモンの 表
  tools/     アドレスを さがした ときの スクリプトなど（組み立てには 使わない）
  pokegold/  pret/pokegold の 定数・マクロ（includes.asm・constants・macros）
  build.py   組み立て

クレジット（連れ歩き。公開する ときは ブログ用 HTML の クレジットの 節にも 書く）
  ・連れ歩きのしくみ：Vulcandth さん、AtmaBuster さん
    （fellowship-of-the-roms/pokecrystal 「follow-mons」）
    https://github.com/fellowship-of-the-roms/pokecrystal/tree/follow-mons
  ・連れ歩きの見た目と動き（アイコンで歩く絵・色・2コマの歩き・SELECT で選ぶ・ボールのアニメ）：Pokémon Crystal Crunch（gomojoeb さん）
    https://github.com/joseph-bayer/crystal-for-friends
  ・連れ歩きのアイコンの絵とポケモンの色：Sour Crystal（SoupPotato さん）
    https://github.com/SoupPotato/sourcrystal
  ・アンノーンのアイコン：Polished Crystal（Rangi42 さん）
    https://github.com/Rangi42/polishedcrystal
  ・土台：pret/pokecrystal
    https://github.com/pret/pokecrystal
