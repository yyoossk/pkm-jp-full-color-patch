ポケットモンスター金 追加機能パッチ　ソース（Ver.1.4.0）
==============================================

このフォルダで python3 build.py を 実行すると、Ver.1.4.0 の ROM が できます。
  ・kin.gbc（通常版）　CRC32 5DB51AED
  ・kin60.gbc（60fps版）CRC32 26DD595B
  ・kin251.gbc（251ひき そろう版の 通常版）　CRC32 4D0166B5
  ・kin251_60.gbc（251ひき そろう版の 60fps版）CRC32 FE6A42BC
    251ひき そろう版：野生（src/wild251_gold.asm）・ショップ（src/masterball251.asm）・ずかんの 文字（src/dexinfo251_gold.asm）を
    かえて、src/edition251_gold.asm を 足す（build.py の FILES251）。ふつうの 版の ROM は かわらない。
    ・野生：その 版で 出ない ポケモンを、ほかの 2つの 版と 同じ マップ・枠・レベルに（朝・昼に 足して 夜は 元の まま など）。
      tools/wild251_jp.py で、data/251/かえる枠_金.txt を src/wild_gold.asm（殿堂入りの 前の 書きかえ）と 日本版の 表に あてて 作る
      （日本版の 金は ヒメグマ・リングマ と ゴマゾウ・ドンファン が 英語版と 逆 なので 入れかえて 読む）。
    ・つうしん しんかの 10ぴきは Lv37 で しんか（ヤドンは おうじゃのしるし を もたせて Lv37 で ヤドキング、なしなら ヤドラン）。
    ・ウツギ はかせの けんきゅうじょで 3びき とも もらえる（えらんだ 1ぴき だけ きのみ）。
    ・まえの 版の セーブデータ（1ぴき もらった あと）でも、ウツギ はかせに はなしかけると のこりの 2ひきを くれる。
    ・殿堂入りの あと：アルフの いせきの けんきゅうじょで オムナイト・カブト（Lv30）、シロガネやまの おくに ミュウツー（Lv70）、
      グレンじまに ミュウ（Lv50）。しるしは wEdFlags（$d7a3）。
    ・コガネデパート 4F で しんかの いし 6つ・おうじゃのしるし を 2100円で 売る。
  （Ver.1.4.0 の あと（まだ リリースして いない）：
    ・src/tmshop.asm：1回しか もらえない わざマシン 32こを タマムシデパート 3F で 買える（メニューで 3つの 店に わける。
      表は src/masterball.asm の GetMart の フックから TmShopMart）。
    ・src/daycareout.asm：タマゴが みつかった ときの そだてやの おじいさんを 外の 道（10, 15）に 立たせる。
    ・src/eggfast.asm：タマゴが うまれるまでの 歩数を 半分（128歩 ごとに へる）。src/eggsteps.asm の 計算も 128歩 ごとに。
    ・連れ歩きの 後ろ・横の 色：スイクン・ポッポ の 色の あて方を 手で きめた（tools/follow_gen.py の WALK_SWAP_FIX）。
    CRC32：通常版 9E772173・60fps版 C04909A5・251ひき 1B1835A6・251ひき 60fps D4E14548）
  （Ver.1.4.0 で 足した・直した もの：
    ・251ひき そろう版（上）を 足した。
    ・場所の 名前の 札が 出て いる 間に となりの マップへ 歩いて 入ると、札が しばらく 白く なった。
      wMSState の ビット6 を「wBGPals2 の パレット7 も 札の 色に した」しるし に して、札を 出す とき・MapSign_Init・
      ApplyMapPalettes の 行（割りこみを 止めて 呼ぶ）で wBGPals2 の パレット7 を 札の 色に、Hide で wBGPals1 から もどす。
      札の 絵は $45:$6f00 に うつした（src/mapsign.asm）
    Ver.1.3.3 の リリースは 通常版 D4AF6B5B・60fps版 F22C69C6）
  （Ver.1.3.3 で 直した もの：
    ・場所の 名前の 札が 消える とき、1フレーム だけ 白く 出る ことが あった（パレット7 を 先に もどして いた）。
      札（ウィンドウ）を 先に 消して、札の 行（LY 112〜143）を かいて いない ときに もどす（src/mapsign.asm の MapSign_Hide）
    Ver.1.3.2 の リリースは 通常版 ED41E1F6・60fps版 D2516C02）
  （Ver.1.3.2 で 直した もの：
    ・殿堂入りの あとの フリーザー・サンダー・ファイヤーが 出なかった（連れ歩きの マップオブジェクト〔人の 数＋2 の 番号〕と
      同じ 番号に 書いて いて、連れ歩きに 上書き されて いた）。鳥の 番号を その つぎに した（src/legends.asm）
    Ver.1.3.1 の リリースは 通常版 EDF43780・60fps版 B0041D37）
  （Ver.1.3.1 で 直した もの：
    ・手持ちの 画面の ★の 場所を かえた。状態異常の 文字と かさなって「ねむり」が こわれて いた。
      色ちがいの ★は「ＨＰ：」の 上（src/partyshiny.asm）、連れ歩きの 赤い ★は HP の 数字の 右（src/follow_gold_update.inc）、
      その ますの 色は src/statuscolor_gold.asm の .marks
    Ver.1.3.0 の リリースは 通常版 7A2908AB・60fps版 867FDB62）
  （Ver.1.3.0 で 足した もの：
    ・場所の名前の札を クリスタルと 同じに した
    ・全ポケモンの 連れ歩き（src/follow_gold.asm。金銀連れ歩きキットから。話しかけると 会話・ピカチュウは 表情の 絵、
      手持ちの 画面の SELECT で 連れ歩く ポケモンを えらぶ、ボールの 出入り、Bダッシュ）
    ・相手の HP の わくの 線を 数字の 下に（src/enemyhp_gold.asm）
    ・クリスタル追加機能キットの 51〜57：16この バッジの あとの 四天王・ワタル・ライバル（src/league.asm）、
      景品の わざマシンの わざの 名前（src/prizetm_gold.asm）、サファリの 歩数・ボールの 表示（src/safari/safari.asm）、
      そだてやで 今の レベル（src/daycarehint.asm）、状態異常・PP の 色（src/statuscolor_gold.asm）、
      ずかんの タイプ・種族値・進化の ページ（src/dexinfo_gold.asm）
    ・スタートメニューの ならび：ずかん・ポケモン・リュック・ポケギア・パソコン・主人公・レポート・せってい
    ・むしとり大会で パソコンへ おくる とき、いまの ボックスが いっぱい なら 次の あいて いる ボックスへ おくる
      （「○○を ボックス２に おくりました！」。src/contestpc.asm。戦いの 中なので SRAM から SRAM へ 1バイトずつ 写す）
    ・人が 多い 所で 重いのを 直した：フィールドの ボールの 色は その人の OAM を 書きおえた あとで まとめて なおす
      （src/fieldcolors.asm の FC_END_HOOK）、60fps の まん中の 位置の 計算と もどす 所を call なしで（src/fps60.asm）、
      連れ歩きの 白い 下じきは OAM が いっぱい なら さがさない（src/follow_gold_vram.inc）
    前の Ver.1.2.1 は 通常版 282A970B・60fps版 25F5129D）

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
