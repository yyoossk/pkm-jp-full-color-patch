ポケットモンスター クリスタル（日本版）追加機能キット
====================================================

元にしたROM：Pocket Monsters - Crystal Version (Japan)  CRC32 270C4ECC
組み立てかた（rgbds 1.0.4。pokecrystal/ は pret/pokecrystal の 定数・マクロだけを 入れた もの）：
  元の ROM を base.gbc として このフォルダに 置いて
    python3 build.py feat.gbc $(cat buildlist.txt)
    python3 build.py feat60.gbc $(cat buildlist.txt) src/fps60.asm
  （buildlist.txt の 先頭が src/features.asm。60fps 版は 最後に src/fps60.asm を 足す）
パッチの版：Ver.1.1

■ 入っている機能
  1. Bボタンダッシュ（ランニングシューズ）
       B を押しながら歩くと自転車と同じ速さ。なみのり中も速くなる。
  2. メニューに「パソコン」
       スタートメニューの ならびを ずかん・ポケモン・リュック・ポケギア・パソコン・主人公の名前・レポート・せってい に する
       （「とじる」は 出さない。B／START で閉じられる）。
       ポケモンセンターのパソコンと同じメニュー（マサキ／じぶん／オーキド…）がどこでも使える。
       むしとり大会中は パソコンを 出さず、さいごに「とじる」（大会中にパソコンを使わせないため）。
       ・ポケギアの あとの「ld a, STARTMENUITEM_STATUS / call .AppendMenuList」（$04:$6740。StartMenu_StatusAppend）を
         call StartMenu_PCAndStatus に、さいごの とじる（$04:$675e。StartMenu_ExitAppend）を call StartMenu_ExitInContest に する。
         金銀に 入れる ときは この 2か所（3e 03 cd ?? ?? ／ 3e 06 cd ?? ??）を その ROM で 探す。
  3. 手持ちのポケモンを選ぶと「なまえ」
       ニックネームを変えられる（人からもらったポケモンも）。何も入れなかったら今の名前のまま。
  4. 手持ちのポケモンを選ぶと「わすれる」
       わざを選んで忘れさせる。ひでんわざも忘れられる。わざが1つしかないときは忘れられない。
  5. ひでんマシンを全ポケモンに
       ひでんマシン01〜07を全ポケモン（251匹）が覚えられる。
  6. 60fps（別の版）
       フィールドの移動を1ドットずつ（60fps）にする。ゲームの速さ・タイミングは元のまま。
  8. 手持ちのポケモンの見た目（Polished Crystal から移植。src/minis.asm）
       ・アイコンを、約40種類の使い回しではなく ポケモンごとの絵（Polished Crystal のミニアイコン）にする。
         手持ち・名前入力・わざの画面・交換など、アイコンを読みこむ所はぜんぶこの絵になる。
       ・手持ちの画面では、1匹ずつ専用の色（OBJ パレット2〜7）。名前入力・わざの画面のアイコンも その色（OBJ パレット7）。
         色をつけるのは 手持ちのアイコンのアニメ（フレームセット1〜6）だけ（セレビィ・そらをとぶ のアニメも VAR4 を使うため）。
       ・色は Polished Crystal のポケモンの色、
         色ちがいは色ちがいの色。どうぐ・メールの印は元の色のまま。タマゴも Polished Crystal の絵。
         色ちがいの色は クリスタルの 色ちがいの 色（pret/pokecrystal の shiny.pal）に そろえた（Polished Crystal の 色の ままだと
         ピカチュウが 青 など、つよさの 画面・戦闘の 色と ちがう ポケモンが 56 ひき いた。tools/minipals_shiny.py）。
       ・絵と色のデータは gfxdata/（tools/mkminis.py で Polished Crystal のフォルダから作り直せる）。
       ・アイコンの 色を 画面の 色（wOBPals2）にも 書くのは、画面が できあがって いる とき（BG パレット0 が wBGPals1 と wBGPals2 で 同じ）だけ。
         手持ちの 画面を ひらく ときは ClearBGPalettes で 白く した あとに アイコンを 作るので、wOBPals2 にも 書くと
         白い 画面の なかで アイコン だけ 先に 見えて いた（このあとの SetDefaultBGPAndOBP が wOBPals1 から うつすので、
         画面と いっしょに 出る）。ならびかえ の あと など、画面が 出て いる ときは 今までどおり すぐ 色が かわる。
         金銀に 入れる ときは wBGPals1・wBGPals2 を その ROM の 値に する。
  9. ひでんわざ（いあいぎり・なみのり・かいりき・うずしお・たきのぼり）を、ポケモンが覚えていなくても
     フィールドで使える（バッジがないと使えないのは今までどおり。src/hmfield.asm）
       ・覚えているポケモンがいれば そのポケモン、いなければ手持ちのいちばん前（タマゴはとばす）が使う。
       ・ずつき（木）・いわくだき（岩）も、そのわざマシンを もらったあとなら 覚えていなくても使える（いちばん前のポケモンが使う）。
         もらう前は今までどおり。わざマシンは使うとなくなるので、「もらった」イベントフラグで決める
         （EVENT_GOT_TM02_HEADBUTT = $5f：ウバメのもり、EVENT_GOT_TM08_ROCK_SMASH = $4b：36ばんどうろ。wEventFlags = $da65）。
       ・そらをとぶ・フラッシュ（手持ちのメニューから使う）は変わらない。
       ・クリスタル用の値は src/hmfield_crystal.asm（tools/hmfield_find.py で調べた値）。
  10. ずかんの「ぶんぷをみる」に、つりざおで釣れる場所も出す（釣りの場所は青いマーク。src/fishnest.asm）
       ・草むら・水の上で出る場所と同じ所は 今までのマーク。ゲームのデータどおり、実際に釣れる所だけに出る。
       ・クリスタル用の値は src/fishnest_crystal.asm（tools/fishnest_find.py で調べた値）。
         釣りの場所の表 src/fishnest_maps_crystal.inc は、日本版クリスタルの ROM から作り直しても同じになることを確かめた。
  11. カントーのジムリーダーと再戦（src/rematch.asm。金・銀・クリスタル共通）
       ・カントーのバッジを8つ ぜんぶ持っているとき、ジムリーダー（タケシ・カスミ・マチス・エリカ・アンズ・ナツメ・カツラ・グリーン）に
         話しかけると「もういちど しょうぶ するか？」と聞かれ、「はい」なら 強い手持ち（6匹・Lv66〜74・わざと持ち物つき）で戦える。何度でも戦える。
       ・「いいえ」のときや バッジがそろっていないときは 元のゲームと同じ（勝ったあとのセリフ・わざマシンなど）。初めて戦うときも元のまま。
       ・しくみ：
           1) 話しかけのスクリプトの「checkflag バッジ / iftrue .FightDone」（6バイト）を「farsjump 新しいスクリプト」に書きかえる。
           2) 8人のトレーナーのデータ（グループ）を トレーナーのバンクの空き場所に移し、1回目（元のデータそのまま）のあとに
              2回目（再戦用。src/rematch_parties.inc）を足して、TrainerGroups の指す先を変える → loadtrainer 人, 2 で戦える。
              名前・お金・AI・音楽などは 1回目と同じ。
           3) 負けたときのセリフ（winlosstext）は ふつうは マップのスクリプトのバンクから読むので（PrintWinLossText の call GetMapScriptsBank）、
              スクリプトが新しいバンクで動いているとき（wScriptBank = 新しいバンク）だけ そのバンクから読むようにする。
       ・アドレスは tools/rematch_find.py で ROM から探す（金・銀・クリスタルで同じ探し方。バッジのフラグ番号も探す）。
         クリスタル用は src/rematch_crystal.inc（これを作った結果）と src/rematch_crystal.asm（組み立てるファイル）。
  12. 殿堂入りの前に、殿堂入りのあと（カントー・シロガネやま）にしか出ないポケモンを出す
       ・ジョウトの草むら・洞くつの出現表で、同じ時間帯に2回以上出てくるポケモンの枠（おもに4%の枠）を書きかえる。
         もとから出るポケモンは 1匹も消えない（時間帯ごとに確かめてある）。ずかんの「ぶんぷ」にも出る。
       ・出現表は「元の表（47バイト）→ 新しい表」のルール（data/wild_crystal.txt・wild_gold.txt・wild_silver.txt）にしてあり、
         tools/wild_find.py が ROM の中で元の表を探して、書きかえる asm を作る（見つからない・2か所あるときは止まる）。
       ・クリスタル（〔〕は時間）：
           デルビル 37ばんどうろ〔夜〕 / ヤミカラス 37ばんどうろ〔夜〕 / ムウマ やけたとう1F〔夜〕・スズのとう2F〔夜〕
           マグマッグ やけたとうB1F / ブーバー やけたとうB1F / ピカチュウ 34ばんどうろ〔朝昼〕 / ポリゴン 34ばんどうろ〔夜〕
           ピッピ もうじゃやま1F〔夜〕 / ディグダ くらやみのほらあな（キキョウ側） / ダグトリオ くらやみのほらあな（フスベ側）
           ベトベター ヤドンのいど B1F / ベトベトン ヤドンのいど B2F / ガルーラ 44ばんどうろ〔朝昼〕 / ラッキー 42ばんどうろ〔朝昼〕
           ヨーギラス もうじゃやま B1F / エレブー 43ばんどうろ〔朝昼〕 / バリヤード 36ばんどうろ〔朝昼〕
           プテラ アルフのいせき（外） / カビゴン 45ばんどうろ〔夜〕
       ・金・銀：上と同じ場所に、金銀で殿堂入りのあとにしか出ないもの（カラカラ ＝ つながりのどうくつB1F、
         ニューラ ＝ こおりのぬけみちB1F〔夜〕も足す。ブーバーは金銀では もとから出るので足さない）。
  13. せっていに「とけい」（src/clockopt.asm）
       ・「おわり」は なくす（せっていは B・START で とじる）。今までの項目を 1行ずつ上げ（1行目の「はなしの はやさ」は濁点がない）、
         15行目に「とけい　▶ひる　 せってい」を出す（とけい 1列目、あさ・ひる・よる 6列目、せってい 11列目）。
       ・とけいの行では 左右で「ひる」か「せってい」を選ぶ（ひらいたときは「ひる」の側）。
         「ひる」で A … ▷ になり、左右で あさ（4:00）・ひる（10:00）・よる（18:00）に 時計を合わせる（曜日はそのまま。分・秒は 0）。
           A・B で ▶ にもどる（この B では とじない）。せっていを閉じると フィールドの色も その時間になる。
         「せってい」で A … 曜日・時・分を合わせる画面（元の RestartClock の「ld hl, wOptions」の所 $08:$4027 から。
           「とけいが くるっている かも」の文は出さない）。おわったら WaitBGMap して、ボタンを はなすまで待つ。
       ・時計の合わせ方は RestartClock と同じ：UpdateTime → GetWeekday → wStringBuffer2 に 曜日・時・分・秒を入れて InitTime。
       ・いちばん下の項目は とけい（7）：項目の表（GetOptionPointer の .Pointers）を 8つ（7 = とけい）にして、
         OptionsControl の いちばん下を 7、上から回りこむ値を 8 に。カーソルの場所の計算を置きかえる。
       ・タイトルの「せっていを かえる」（ゲームを始める前。wMapGroup = 0）では「とけい　▶ーー」だけで、左右・A は効かない。
       ・とけいの行で選んでいる所（wClockSub）は、WRAM バンク1 に 使われていない所がないので WRAM バンク2 の $dfc2 に置く
         （読み書きのときに バンクを切りかえる）。
       ・JoyTextDelay・GetJoypad・DelayFrame・WaitBGMap・hJoyDown・RestartClock の途中は tools/clockopt_find.py で調べた
         （WaitBGMap は 3か所の候補のうち 呼ばれている $31c2、DelayFrame は DelayFrames から呼ばれている $045a）。
  14. わざを覚えるとき A ボタンの連打で わざを上書きしない（src/learnno.asm）
       ・レベルアップ・わざマシンで 4つ覚えているときの「ほかの わざを わすれさせますか？」と
         「○○を おぼえるのを あきらめますか？」の「はい／いいえ」を、はじめから「いいえ」にする。
       ・A を連打すると 2つの質問を くり返す（ループ）だけで、わざを忘れたり あきらめたりしない。
         覚えさせる・あきらめるときは「はい」に合わせて A。
       ・YesNoBox と同じことをして、メニューの見出しを写したあと はじめのカーソル（wMenuCursorPosition）を 2 にする
         YesNoBox_DefaultNo を作り、ForgetMove と LearnMove.cancel の call YesNoBox を それに置きかえる。
  15. 戦闘で投げる モンスターボール・スーパーボール・ハイパーボール・マスターボール を それぞれの絵にする（src/ballgfx.asm）
       ・絵と色は ピカチュウ版フルカラー（ポケットモンスターピカチュウフルカラー）の 投げるボールから作った。
         マスター＝むらさきに M、ハイパー＝黒に 黄色の H、スーパー＝青に 赤い もよう、モンスター＝赤。
         投げる・あたって開く・ゆれる・つかまえたあと残るボール・トレーナーにはじかれる の全部で その絵になる。
         ほかのボール（レベルボール など）は元のまま。
       ・1つのボールで色を2つ使う（上半分・下半分）。OBJ パレット5（みどり）・6（あお）に入れる。
         ボールを投げるアニメでは みどり・あお のほかの物は出てこない（けむり＝グレー、マスターボールのキラキラ＝ちゃいろ）。
         どの技のアニメも はじめに パレット5・6 を 元の色に もどす。
       ・しくみ（バンク$33）：
           LoadBattleAnimGFX … ボールの絵（$0b）を読むとき、wCurItem のボールの絵（バンク$70:$5800、10タイル）を読む。
             元の絵の 9・10番目のタイルは使っていないので、閉じたボールの右半分を入れる。
           GetBallAnimPal … 色を wOBPals1・wOBPals2 の パレット5・6 に入れ、ボールのパレットを 5 | $80（$80 = 印）にする。
           BattleAnimOAMUpdate の属性を作る所 … 印があれば 上の段 = 5、下の段・開いたボール = 6。
             閉じたボールの右半分（データでは左を反転）は 反転しないで +8 のタイルにする（左右ちがう絵にできる）。
           _PlayBattleAnim の BattleAnimAssignPals の前 … パレット5・6 を BattleObjectPals の元の色にもどす。
         色のデータは ROM0 の $0070〜（バンク$33 の空きが足りないため）。
       ・絵：gfxdata/balls_crystal.2bpp（マスター・ハイパー・スーパー・モンスター の順に 10タイルずつ）、
         asm 用は src/ballgfx_gfx.inc（そのまま読める LZ 形式）・src/ballgfx_pals.inc。
  16. 「つよさをみる」の わざのページ（2ページ目・緑）で わざを並べかえる（src/statsmove.asm。金のキットの 17 をクリスタルに合わせた）
       ・SELECT で始める → 上下で ▶ を動かし、A で選ぶ（▷ が残る）→ もういちど A で入れかえ（わざと PP がいっしょに動く）。
         同じわざで A、または B・SELECT で 選ぶのをやめる。選んでいないときの B・SELECT で おわり。
       ・手持ちのポケモンだけ（ボックス・相手・タマゴは できない）。わざが1つのときと、戦闘中は できない。
       ・カーソルは 枠の線（8列目、6・9・12・15行目）の上に出す。
       ・しくみ：MonStatsJoypad.next（$13:$5c81）の and $f3 / jp StatsScreen_JoypadAction を バンク$13 の空き（$7760）の入口へ。
         SELECT で 緑のページなら $70:$5c00 を farcall。入れかえたら 手持ちのデータ（わざ・PP）と wTempMon を入れかえ、
         LoadGreenPage（$13:$5fcc）で書き直す。作業用の値は レジスタとスタックに置く（WRAM は使わない）。
  17. 戦闘と ずかんの「ボールの印」を モンスターボールの赤と白に（src/redballs.asm。金銀クリスタル共通）
       ・トレーナー戦の始まりや 相手の入れかえで並ぶ 手持ちの数のボール：元気なポケモンのボールが赤白（状態異常・ひんし・空きは今までどおり）。
       ・野生の戦闘で つかまえたことのあるポケモンの名前の左の印、ずかんの一覧の つかまえた印：上が赤・下が白で まん中に黒い帯。
       ・クリスタルの値は src/redballs_crystal.inc（tools/redballs_find.py で出した値 ＋ 空きの場所 ＋ ホームの処理）。
         src/redballs_crystal.asm で .inc を先に読んでから redballs.asm を読む。
       ・戦闘画面の 背景のパレット5 を使う。クリスタルの戦闘では 印の場所（1, 1）のほかに パレット5 を使っている所がないことを確かめた。
  18. ずかんの一覧と パソコンの ポケモンの絵を、白い背景に そのポケモンの色で出す（src/picpal.asm。金銀クリスタル共通）
       ・ずかん：カーソルを動かすと そのポケモンの色になる。見たことがないポケモン（？の絵）は 今までどおり 緑。
       ・パソコン（あずける・つれていく）：選んでいるポケモンの色（色ちがいは色ちがいの色）。「やめる」では 絵が消える。
       ・ずかん・パソコンで 絵の 色を 画面の 色（wBGPals2）にも うつすのは、画面が できあがって いる とき だけ
         （パレット0 が wBGPals1 と wBGPals2 で 同じ で、まっくらでない とき。PicPal_PushIfShown）。
         ずかんを ひらく とき（ClearBGPalettes で 白い 画面）に うつすと、白い 画面の なかで 絵の ところ だけ 緑の 四角が 一瞬 見えた。
         ぶんぷから もどる とき（Pokedex_BlackOutBG は wBGPals1 も 0 に する）に うつすと、前の 画面が のこった まま パレット1 だけ
         色が ついて へんな 画面が 見えた。どちらも このあと GetSGBLayout が 色を ぜんぶ 作りなおす。
       ・クリスタルの値は src/picpal_crystal.inc（tools/picpal_find.py で出した値 ＋ 空きの場所）。src/picpal_crystal.asm で組み立てる。
         PP_hCGBPalUpdate は $ffe5。色を作る処理は バンク$02:$7800、ホームの入口は $00c0（ずかん）・$00f0（パソコン）。
       ・しまっておく種類（wDexPicSpecies・wPCPicSpecies）は、WRAM バンク1 に 使われていない所が見つからないので、
         60fps・手持ちの見た目と同じ WRAM バンク2 の $dfc0・$dfc1 に置いた。そのために picpal.asm に
         PP_VARS_WRAMBANK（0 なら今までどおり。金銀は 0 のままでよい）を足し、読み書きのときに バンクを切りかえる。
  19. フィールドのボール・回復の機械・人の肌の色を ピカチュウ版フルカラーに近づける（src/fieldcolors.asm。金銀クリスタル共通）
       ・フィールドに落ちている道具のボール：ピカチュウ版の道具のボールと同じ（上が赤・下が白。黒い帯はない）。
       ・ウツギ研究所の机の上の ポケモンが入っている3つのボールだけ：上が赤・黒い帯とボタン・下が白。
         使われていない SPRITE_UNUSED_GUY（$3f）の表を 研究所のボールの絵（4枚・STILL_SPRITE・PAL_OW_RED）にして、
         研究所の3つの object_event の スプライトを $3f にする。
       ・どちらも 上の2枚は 赤のパレットのまま、下の2枚だけ PAL_OW_EMOTE（白・白・灰・黒）にする（SPRITE_POKE_BALL と $3f）。
       ・ポケモンセンターの回復の機械：上のボールが 赤と白（機械のパレットの肌色を白に。画面の光る線も白になる）。
       ・フィールドの人の肌の色を 31,19,10 → 31,24,17（朝・昼・夜・暗い × 赤・青・緑・茶・ピンク）。
       ・クリスタルの値は src/fieldcolors_crystal.inc（tools/fieldcolors_find.py で出した値 ＋ 空き）。src/fieldcolors_crystal.asm で組み立てる。
         値は パッチを入れる前の ROM で調べる（道具のボールの絵を 元の絵で さがすため）。
         処理（50バイト）は バンク$01:$7f00（$7ea0〜$7eb2 は わざの上書き防止なので そのあと）、研究所のボールの絵は $70:$6000。
  20. ルギア・ホウオウが 専用わざ（エアロブラスト・せいなるほのお）を 覚えられる（src/sigmove.asm。金銀クリスタル共通）
       ・元は 専用わざを レベル1 でしか覚えず、レベル60 で出てくる クリスタルの ルギア・ホウオウは 覚えていなかった
         （野生のポケモンは そのレベルまでに覚える わざの 最後の4つを持つため。わざを思い出させる人もいない）。
       ・レベルアップで覚える わざの表に「レベル60 で 専用わざ」を足す（レベル1 は そのまま）。
         レベル60 で出てくる ルギア・ホウオウは 専用わざを 覚えている。すでに つかまえていても、レベル60 に上がるときに 覚えられる。
       ・うずまきじまの ルギア・スズのとうの ホウオウを 両方 レベル40 にする（元は 60。loadwildmon の レベルの所 $1c:$4ad4・$1a:$5f62）。
         レベル40 なら 専用わざ（レベル1）を 覚えて出てくる（金銀の 元の 低いほうと 同じ レベル）。
       ・表が 2バイト ふえるので、ルギア・ホウオウの表を 同じバンク（$10）の空き $7e40 に置きなおし、
         EvosAttacksPointers の 2つ（$10:$6943・$6945）を 書きかえる。値は src/sigmove_crystal.inc（tools/sigmove_find.py で調べた）。
  21. サファリゾーン（ピカチュウ版フルカラーパッチと同じ。src/safari/。金の キットの サファリゾーンを クリスタルに合わせた）
       ・セキチクシティの 北の とじていた入口から 入れる。入口・ちゅうおう・ひがし・きた・にし・きゅうけいハウス 4つ・ひみつの家 の 10マップ。
         マップの形・絵・色・看板・人・落ちている道具・出るポケモン・つり・段差は ピカチュウ版と同じ。
       ・500円で サファリボール 30こ・502歩。戦いは ボール・エサ・いし・にげる（手もちの ポケモンは 出さない・ボールの 表示も 出さない）。
         投げる ボールは サファリボールの 絵と色（投げるボールの絵 15 の 5つめ。wCurItem = $b3 を 印にする）。
       ・ピカチュウ版と 同じに した所：
           曲：サファリゾーンの中は ピカチュウ版の サファリの曲（バンク$75 に 曲を足し、PlayMusic のフック $3a:$4b39 で 曲の表を広げる）。
           アナウンスの音：時間・ボールが なくなったとき 曲を とめて「ピンポーン」の 効果音（PlaySFX のフック $3a:$4c78）。
           戦いの始まり：手もちの ボールの 表示を 出さない（BattleStart_TrainerHuds のフック。$0b:$7e60）。
           にげだした ポケモン：右へ すべって 消える（SlideBattlePicOut を使う。$0f:$7fe0）。
           あなぬけのヒモ・あなをほる：サファリの中では 入口ではなく さいごに 立ちよった ポケモンセンターへ
             （DigFunction の farscall Script_AbortBugContest $03:$4d02 を かえる。サファリの外は 元のまま）。
           ずかんの「ぶんぷ」：カントーの 地図で サファリに 出る ポケモンは セキチクシティに 印（草むら＝ふつうの印、つり＝釣りの印。
             src/fishnest.asm の FishNest_Extra。表は src/safari/safari_nest.inc）。
           ポケギアの 地図：サファリの中では 地名を「サファリゾーン」に（GetLandmarkName のフック $24:$505a）。
           地名の 看板：サファリの中では「サファリゾーン」（サファリの マップの 地名は セキチクシティ なので。
             PlaceMapNameCenterAlign の farcall GetLandmarkName $2e:$40e5 を ポケギアと 同じ 処理に かえる）。
           つりの 文：サファリの中は ピカチュウ版の「つれないなー……」「おっ！ ひいてる ひいてる！」（外は 元の 文）。
             Script_NotEvenANibble の writetext / sjump（$03:$523f）を farsjump SafariFishNibbleScript に、Script_NotEvenANibble2 の
             writetext（$03:$5248）を そこへの sjump に、Script_GotABite の writetext RodBiteText（$03:$526c）から あとを farsjump SafariFishBiteScript に。
           ボックスが いっぱい（手もち 6匹・ボックス 30匹）で ボールを 投げようと したときは ピカチュウ版の
             「ボックスに あずけている ポケモンが いっぱいなので つかえません！」（ボールは へらない）。
       ・セキチクの「サファリゾーンが しまっている」話を ピカチュウ版の 話に：日本版 クリスタルにも 文の 命令 text_far（$16）は ない
         （TextCommands ROM0 $1431 は $00〜$15）ので、元より 短い 文は 元の 場所に 書く（safari_gen.py の INPLACE）：
         女の人 $28:$616d ← ピカチュウ版 0x1a8ba、事務所の 看板 $28:$61e1 ← 0x1a9d8、フレンドリィショップの つりびと $1e:$581b ← 0x1e869。
         えんちょうの まごは スクリプトの 頭（$1e:$5e86）を farsjump SafariGranddaughterScript に して バンク$74 で 同じ 流れ
         （1回め：金の 文の さいごの 段だけ「サファリゾーンは かかりの ひとたちが ちゃんと あけて くれてるわ！」、2回め：ピカチュウ版 0x74fa3）。
       ・ポケギアの 地図・ずかんの ぶんぷ：サファリゾーンを セキチクの 北の 別の 点（地名 $60。x 100, y 120。セキチクは x 100, y 132）に。
         クリスタルの 地名は $00〜$5f（$5f は LANDMARK_FAST_SHIP）なので、金の $5f ではなく 使われていない $60 に した。
         GetLandmarkCoords（$24:$652a）：$60 なら その点（バンク$24 の さいごの 空き $7feb）。地名：$60 なら「サファリゾーン」。
         ポケギアを ひらいた とき（.LoadLandmark $24:$4d07）：サファリの中で セキチクなら 自分の 場所・カーソルを $60 に。
         カーソルの 上下（.up $24:$4fc3・.down $24:$4fd0）：セキチク（$51）と 19ばんすいどう（$52）の あいだに $60 を はさむ。
         バンク$24 は 空きが 少ないので、使われていない DebugPrintSlotBias・AnimateSlotReelIcons（$24:$6d84〜）に 入口を 置き、判定は バンク$74。
         ずかんの サファリの マークは FISHNEST_EXTRA_LANDMARK $60。マップの 見出しの 地名は セキチクの まま。
         地名の 看板は 別の 処理（SafariSignName：サファリの中の セキチクを「サファリゾーン」）。
       ・セキチクの サファリゾーン じむきょく（中に だれも いない）に 案内の 人：SafariZoneMainOffice_MapAttributes（$25:$6200）の
         +6〜+10 を バンク$74 の SafariOffice_MapScripts・_MapEvents に（ワープは 元と 同じ、SPRITE_GRAMPS（5, 3）が
         ピカチュウ版 0x1a8e6「サファリ ゾーンは いりぐち ふきんは どうぶつえんで…」を 話す）。
       ・時間で 色を かえる（外の 4つ だけ）：safari_header に 色の 引数を 足し、ちゅうおう・ひがし・きた・にしは PALETTE_AUTO、
         ほかは PALETTE_DAY。SafariMapPals（LoadMapPals の フック $02:$7206）で 外の タイルセットなら wTimeOfDayPal（$d834）& 3 が
         0 → 朝の 表、1 → 昼（ピカチュウ版の 色）、2・3 → 夜の 表を 写す（朝・夜の 表は 金と 同じ）。家の中は 時間で かわらない。
       ・入口の マップ見出しの 環境を GATE → INDOOR に（ピカチュウ版と 同じく じてんしゃは 入ると おり、使うと「オーキドの ことば…」）。
       ・LoadMetatiles の ブロック 128こ より あとが 0〜 に もどる クリスタルの 元からの バグを 直した（ROM0 $2177。pokecrystal の
         bugs_and_glitches.md と 同じ 直し方）。サファリの 外の タイルセットは ワープの ブロックを 足して 128こ より 多く、
         エリアの さかいめ（ワープの 矢印）が 黒い ブロックに、セキチクの 入口の ドア（ブロック $80）が べつの 絵に なっていた。
         128こ より 少ない ほかの タイルセットは 同じ 絵の まま。
       ・データは tools/safari_gen.py で ピカチュウ版フルカラーの ROM から 作る（src/safari/safari_gen.asm）：
           python3 tools/safari_gen.py ピカチュウ版.gbc base.gbc src/safari/safari_nest.inc > src/safari/safari_gen.asm
         （3つめの ファイルは ずかんの「ぶんぷ」で使う サファリの ポケモンの 表）
       ・組み立てには pret/pokecrystal の 定数・マクロを使う（スクリプトの命令だけ pret/pokegold のもの＝src/safari/pokegold_events.asm。
         日本版クリスタルの 命令の番号は 英語版 金銀と同じ）。POKECRYSTAL=pokecrystal のフォルダ で build.py を動かす。
       ・日本版クリスタルの アドレスは src/safari/jp_crystal.inc（英語版の ラベルの名前 → 日本版の アドレス・RAM）と
         src/safari/safari_crystal.inc（フックの場所・空き）。
       ・金と ちがう所：使う バンクは $74（マップ・スクリプト・文章）・$75（タイルセット）、新しい タイルセットは $21〜$23、
         タイルの色の表は バンク$13、戦いの種類は SUICUNE の つぎ（$0d）、ボックスは 30匹、背景の色は FarCopyWRAM（WRAM バンク5）、
         GetPokeBallWobble の フックは jr nz, .done の形、セキチクの 北の ブロック（9, 1）を ドアのある $80 に。
  22. ボックスが いっぱいに なったら 自動で 次の ボックスに 切りかえる（ピカチュウ版フルカラーと 同じ。src/autobox.asm。金銀クリスタル共通）
       ・フィールドで いまの ボックスが いっぱい（30匹）なら、次の あいている ボックスに 切りかえて レポートを 書く
         （次の ボックスは いまの 次から じゅんに さがす。9 の 次は 1）。
         「ポケモン ボックス１が いっぱいに なりました！／ポケモン ボックス２に じどうで きりかえました！／
           ボックスを きりかえたので レポートを かきました！」（ピカチュウ版の 文）
       ・ぜんぶ いっぱいなら「ポケモン ボックスが ぜんぶ いっぱいです！ パソコンで ボックスを せいり してください」（1回だけ）。
       ・まだ 1回も レポートを 書いていないとき・ちがう 人の レポートが あるときは しない。
       ・しくみ：CheckTimeEvents（$25:$693a）.do_daily の さいごの farcall CheckPhoneCall（$25:$695d）を AutoBox_Check に かえる
         （電話が かからなければ ボックスを 調べて CallScript）。切りかえは パソコンの「ボックスを かえる」と 同じ
         （PauseGameLogic → SaveBox → wCurBox → LoadBox → _SaveGameData → ResumeGameLogic。たずねない）。
         ほかの ボックスの 数は GetBoxCount.BoxBankAddresses（$38:$7de0。金と 同じ 表）で SRAM から 読む。
       ・クリスタルの 値は src/autobox_crystal.asm（英語版 pokecrystal と 命令の 並びで 照らし合わせた）。処理は バンク$76:$4000。
         wAutoBoxDone・wAutoBoxNew は WRAM バンク1 に 空きが ないので WRAM バンク2 の $dfc3・$dfc4 に 置く
         （そのために autobox.asm に AUTOBOX_VARS_WRAMBANK を 足した。0 なら 金と 同じ 命令）。
  23. ウツギ博士から マスターボールを もらった あと、セキエイこうげんの ショップで マスターボールを 売る（10000円。src/masterball.asm。金銀クリスタル共通）
       ・EVENT_GOT_MASTER_BALL_FROM_ELM（日本版 クリスタルは イベント $007c → wEventFlags $da65 ＋ 15 の ビット 4）が たって いれば、
         セキエイの 店（MartIndigoPlateau $05:$661f）の 一番 上に マスターボール。もらう 前は 元の 品ぞろえ。
       ・ItemAttributes（$01:$69fa）の MASTER_BALL の 値段を 10000円に。GetMart（$05:$5ce1。金と 同じ 22バイト）を 書きなおし、
         店の 場所を 読んだ あと バンク$76:$4200 の MasterBallMart を farcall（b = 品ぞろえの バンク）。
         元の「店の 番号が NUM_MARTS 以上なら DefaultMart」は 使われていないので 0 番の 店に した。
       ・クリスタルの 値は src/masterball_crystal.asm（セキエイの 品ぞろえは 金と 同じ 7こ）。
  24. むしよけの ききめが きれたとき、リュックに のこりが あれば「○○を つかいますか？」と きく（src/repelask.asm。金銀クリスタル共通）
       ・きく ものは さいごに つかった むしよけ（なければ むしよけスプレー → シルバー → ゴールド の じゅん）。はい で その場で つかう。
       ・DoRepelStep（$25:$6bd7）の RepelWoreOffScript の 行き先（$25:$6be1）を かえ、UseRepel（$03:$77c4。金と 同じ 17バイト）を 書きなおす。
       ・さいごに つかった・きいている むしよけは WRAM バンク2 の $dfc5・$dfc6（repelask.asm に RA_VARS_WRAMBANK を 足した）。処理は $76:$4300。
  25. せっていの「はなしの はやさ」に「さいこう」（文字が 一度に 出る）を 足す（src/textspeed.asm。金銀クリスタル共通）
       ・さいこう・はやい・ふつう・おそい を 左右で。さいこう は wOptions の 文字の 待ちを 0 に（PrintLetterDelay は 待たない）。
       ・Options_TextSpeed（$39:$42a9）の 頭を $76:$4400 への farcall に。文字の 場所は せっていの とけい（2）で 1行 上げた $c4bf。
  26. ポケギアの 電話の 画面で、かかってくる 電話の 回数を えらべる（ふつう／すくない／なし。src/phonefreq_crystal.asm）
       ・電話の 一覧の 下（11行目）に「でんわ・ふつう　セレクトで　かえる」。SELECT で ふつう → すくない（4分の1）→ なし。
       ・とまるのは ふつうの 電話（CheckPhoneCall）だけ。話の 中で かかってくる 電話（CheckSpecialPhoneCall）は とまらない。
       ・せっていは wOptions2（$cfc5）の ビット 1・2（レポートに 書かれる）。
       ・クリスタルは バンク$24 に 空きが ほとんど ないので、金銀の phonefreq.asm とは 別の ファイルに した：
         使われていない LoadPokegearRadioChannelPointer（$24:$5806）と $24:$6da7 に 小さな 入口だけ 置き、処理は $76:$4500。
         フックは CheckPhoneCall の call CheckStandingOnEntrance（$24:$4074）・PokegearPhone_Joypad の ld hl, hJoyPressed（$24:$510c）・
         PokegearPhone_UpdateDisplayList の さいごの call PokegearPhone_UpdateCursor（$24:$52c0。一覧を かきなおす たびに 文字も かく）。
  27. フスベシティの わざわすれの 家に、わざを おもいださせて くれる おばあさん（src/moverelearn.asm。金銀クリスタル共通）
       ・いまの レベルまでに レベルで おぼえる わざの うち、おぼえて いない わざを 一覧で えらんで おぼえなおす。お金は いらない。
       ・MoveDeletersHouse_MapAttributes（$25:$5d5c）の スクリプト・イベントを $76:$5000 の 新しい 表に（わざわすれの 人 special $21・
         本だな jumpstd $0001 は 元の バイトで 確かめて 同じ。人は 2人）。おばあさんは（5, 4）。
       ・LearnMove（$01:$6650）は メニューの 画面（FadeToMenu → SCGB_MOVE_LIST → LearnMove → CloseSubmenu）で 呼ぶ。
         わざの 表は EvosAttacksPointers（$10:$6753）、一覧の 作業用は wBufferMon（$d00e）。
  28. ずかんの「ぶんぷ」で START を おすと あさ・ひる・よる に 出る 場所を 切りかえて 見られる（src/nesttime_crystal.asm）
       ・ぜんぶ → あさ → ひる → よる。その 時間に 草むら・どうくつで 出る 場所だけ マーク。わくの 右に「あさ」「ひる」「よる」。
         カントーを 見て いた ときは カントーの まま。
       ・クリスタルの すみかの 画面・FindNest は 金と 同じ 形。FindNest .FindGrass（$0a:$604b）・すみかの 画面の くりかえし（$24:$5e88）・
         わくを かく 所（$24:$5f3c）を かえる。バンク$24 の 入口は 使われていない EntireFlyMap（$24:$6439〜）の 場所、
         時間帯は WRAM バンク2 の $dfc7・$dfc8 なので 金銀の nesttime.asm とは 別の ファイルに した。
  29. そだてやの 中の おじいさんが、２ひきの なかの よさと タマゴの ようすを おしえる（src/daycarehint.asm。金銀クリスタル共通）
       ・おばあさんにも あずけて いて（２ひき）タマゴが まだ ない とき、ひきとるか きく 前に「２ひきは とっても なかが いい ようじゃ」
         「なかが いい」「まあまあ なかが いい」「あまり なかが よくない」（タマゴが できる みこみの ４だんかい）と、
         「タマゴが そろそろ みつかるかも しれんぞ」（つぎに しらべる まで 40ぽ いない）／「タマゴは まだまだ じゃな」。
         いっしょに あそばない ２ひきなら「タマゴは できそうに ないわい」。
       ・クリスタルの DayCareMan（$05:$6bb7）は 金と 同じ 形。.AskWithdrawMon（$05:$6bdf）の farcall GetBreedMon1LevelGrowth を かえる。
         wDayCareMan $de89・wDayCareLady $deb6・wStepsToEgg $deb7・wBreedingCompatibility $d296（2ひきめは $dec5〜）。
  30. 殿堂入りの あと、ウバメのもりの ほこらで セレビィ（Lv30）、うずまきじま 地下2階・イワヤマトンネル 地下1階・シロガネやまの 中で
      フリーザー・サンダー・ファイヤー（Lv50）に 会える（src/legends.asm。金銀クリスタル共通）
       ・どれも 1回だけ（つかまえても たおしても にげても いなくなる）。まけた ときは また 会える。
       ・ほこら：bg_event の スクリプト（$19:$64ce）を バンク$19 の 空き（$7ff8）の「farsjump」に。殿堂入り前・会った あと・
         森が さわがしい（GSボールの イベント。EVENT_FOREST_IS_RESTLESS $00c0）ときは 元の スクリプト（$19:$6022）に もどる。
       ・鳥：3つの マップの MapScripts〜イベントの 表を バンク$77 の 同じ 場所に 写し（$1c:$4a5f〜・$1f:$6e75〜・$1c:$4b5a〜。
         ほかの パッチは 入っていない）、callback（MAPCALLBACK_OBJECTS）で wMapObjects（$d711。1人めが 1番）の 4番に 鳥を 書き、
         RefreshSprites（$05:$4159）で 絵を 読みこむ（クリスタルの AddSpriteGFX は 作りが ちがう）。
       ・日本版の disappear は 番号 − 1 の 人（GetScriptObject $25:$71e1）なので 4番の 鳥は disappear 5。
         鳥には イベントの フラグが ない ので wObjectMasks（$d811）にも かくす しるしを たてる。
       ・会ったか どうかは $d836（wTimeOfDayPal の あとの 使われていない 4バイト。レポートに 書かれる）の ビット 0〜3。
  31. フシギダネ・ヒトカゲ・ゼニガメ（Lv10）を ピカチュウ版と 同じ 人・同じ 文・同じ 色（青）で もらえる（src/starters.asm。金銀クリスタル共通）
       ・フシギダネ：ハナダシティの こうかんの 話の 家の 女の人（いつでも）。ヒトカゲ：24ばんどうろ（ゴールデンボールブリッジの 北の はし）の 男の人。
         ゼニガメ：クチバシティの ジュンサー（オレンジバッジが いる）。もらう と「○○は フシギダネを てにいれた！」→ ニックネーム。
         手もちが いっぱいなら ボックスへ。もらった あとは「フシギダネ がんばってます？」など。
       ・3つの マップの スクリプト〜イベントの かたまりを 写し、人を 1人 足した イベントの 表を 作る：
         ハナダの 家（7-3）$1c:$5bf6〜$5cac・24ばんどうろ（7-15）$28:$6bab〜$6e07 → バンク$77、クチバシティ（12-3）$27:$6e7f〜$7240 → バンク$78
         （$77 の イワヤマトンネルの 写しと 場所が かさなるため）。足した 人の 場所は 金と 同じ（6,3）・（9,1）・（19,15）。
       ・ジュンサーの 絵：使われていない SPRITE_OLD_LINK_RECEPTIONIST（$58）の OverworldSprites（$05:$4727 ＋ 6 ×（$58 − 1））を
         ピカチュウフルカラーの 絵に（tools/starters_gen.py で 取り出す）。クリスタルは クチバの 外の 絵の 表（$05:$457e）に もとから $58 が あるので 表は かえない。
       ・もらった しるしは $d836（セレビィと 伝説の 鳥と 同じ バイト）の ビット 4〜6。オレンジバッジは wKantoBadges（$d84b）の ビット 2。
       ・ジュンサーの 絵（$58）の 種類は STANDING_SPRITE（2。元の $58 と 同じ）に する（ST_JENNY_SPRITETYPE。金銀は WALKING_SPRITE の まま）。
         クリスタルは $58 が どの 町・道路の 外の 絵の 表（OutdoorSprites $05:$489b〜 の 各グループ）にも 入って いて、WALKING_SPRITE に すると
         VRAM の わりあてが ずれ、町で 歩く 人（ヒワダの おじいさん など）の 歩く 絵が VRAM バンク0 の 字の 所を 指して こわれて いた。
         ジュンサーは 歩かないので 向きの 絵（12タイル）だけで よい。金銀は 外の 絵の 表に $58 が ないので おきない。
  32. 戦闘で わざを えらぶ とき、右下の わくに 威力と 命中（％）と 相手への 効き目も 出す（src/movepower.asm。金銀クリスタル共通）
       ・わくの 中は 上から「PP／タイプ　×2／いりょく／めいちゅう」。威力 0・1 は「ー」で 効き目は 出さない。命中は ×100÷255 を 四捨五入。
         （タイプを いちばん 下の 行に かくと、上の 行の 命中の 数と 濁点が かさなって「ドラゴン」→「トラコン」「エスパー」→「エスハー」に
         なって いたので、タイプを 14行め（hlcoord 10, 14）に した。濁点は 13行めの PP の 左の 空いた 所に 出る）
       ・効き目は 相手の タイプ（2つ）への ばいりつ（×4・×2・×1・×1／2・×1／4・×0）。タイプの 右（hlcoord 15, 14）。
         TypeMatchups $0d:$4bb1（英語版と 同じ）、wEnemyMonType1・2 $d255・$d256、GetFarByte $3019。「タイプ／」の 文字は やめた。
       ・クリスタルの MoveInfoBox（$0f:$66d7）は 金と 同じ わく・同じ 文字の 場所。さいごの「ld hl, $c5ef / predef PrintMoveType / ret」（$0f:$6755）を かえる。
         wPlayerMoveStruct $c60f（+2 威力・+4 命中）。処理は $76:$6200。
  33. ダウジングマシンが はんのう した とき、元の 文の あと「どうぐは　ひだりの　ほうに／あるみたいだ！」のように 方向を 出す
      （src/itemfinder.asm。金銀クリスタル共通）
       ・うえ・した・ひだり・みぎ・ななめ（ひだりうえ など）・あしもと。いくつか ある ときは いちばん 近い もの（たて＋よこ の 歩数）。
       ・クリスタルの ItemFinder（$04:$6433）・CheckForHiddenItems（$2e:$4152）は 金と 同じ 作り。farcall CheckForHiddenItems（$04:$6433）を
         ItemFinder_Check に、.Script_FoundSomething（$04:$6460）の writetext（$04:$6468）を farsjump に。元の 文 $04:$6476（38バイト）を 写す。
         ずれは 使われていない $d838・$d83c、しらべる あいだの 歩数・数は wStringBuffer2（$d066・$d067）。処理は $76:$6400。
  34. ポケギアの 電話帳で、再戦できる トレーナーの 行の 右はし（x 18）に「！」（src/phonemark_crystal.asm。金銀は src/phonemark.asm）
       ・クリスタルは 再戦が エンジンフラグ（wDailyRematchFlags $dc12〜$dc14。EngineFlags の $65〜$7c 番）。人も 金と ちがう
         （ビバリー・アーウィン・デリック・ケンジは 再戦 なし、クリスの かわりに タリー、パーリー）ので クリスタル用の ファイルに した。
       ・PokegearPhone_UpdateDisplayList の さいごの call は 電話の 回数が 使って いるので、名前を かく「call $438e」（$24:$52b1）を
         入口（$24:$6460。使われていない EntireFlyMap の あき）に して、その 行に 印を かく。処理は $76:$6600。
  35. ポケギアの 文字の 後ろ（うすい 黄緑）を 白に（src/pokegearwhite.asm。金銀クリスタル共通）
       ・時計・電話帳・ラジオ・下の 文の わく・地図の 地名の わく。地図の 道も 同じ 色なので 白に なる。
       ・クリスタルは 男の子（PokegearPals $02:$76e6）と 女の子（PokegearFPals $02:$7716）の 2つ。どちらも 6組の 色0 を 白（$7fff）に。
  36. 野生の 戦闘の メニューで SELECT を おすと、前に 使った ボールを リュックを ひらかずに 投げる（src/quickball_crystal.asm。金銀は src/quickball.asm）
       ・まだ 使って いない・もう ない ときは リュックが ひらく。トレーナー戦では なにも しない。おぼえた ボールは 電源を 切ると わすれる。
       ・SELECT で 投げる ときは、PokeBallEffect の はじめの _ReturnToBattle_UseBall（$09:$74b5。リュックの 画面から 戦闘の 画面を
         作りなおす。画面を 白くして 絵・文字・色を 読みなおす）を とばす（頭の call ClearBGPalettes → $09:$7f70。投げて いる あいだ
         wQuickBall ＝ $80）。とばさないと 画面ぜんたいが 一瞬 白く なって いた。
       ・MenuData（$09:$4f44）に STATICMENU_ENABLE_SELECT、CommonBattleMenu の call $1ffc（$09:$4f0e）→ $09:$7f50、
         BattleMenu .next（$0f:$6179）→ $0f:$7fe8、.got_item の call .UseItem（$0f:$620d）→ $0f:$7fd7。きめる・投げる 所は $76:$6900。
         バンク$0f の 空きが すくない ので 金と 作りを かえた。wLastBall・wQuickBall は WRAM バンク2 $dfc9・$dfca。
  37. つよさの 画面の 1ページめに「なつきど ♥♥♡♡♡」（src/hearts_crystal.asm。金銀は src/hearts.asm）
       ・ハートの 数 ＝（なつき度 ＋ 50）÷ 51。クリスタルは 絵と うごきが VRAM バンク1 なので、ハートは バンク0 の タイル $5e・$5f
         （町の 絵の のこり。どの ページでも 使って いない）に 書き、hlcoord 9, 8 に。LoadPinkPage の さいごの 10バイト（$13:$5f59）を farcall に。処理は $76:$6a00。
  38. ポケギアの 時計の 画面の 下の 文を、今日 曜日きょうだいの いる 場所と むしとりたいかい（火・木・土）・ラプラス（金）に（src/gearday.asm。金銀クリスタル共通）
       ・PokegearClock_Init（$24:$4e8f）の ld hl, PokegearPressButtonText / call PrintText（$24:$4e92）を farcall に。GetWeekday $3342。処理は $76:$6800。
  39. タマゴの つよさの 画面に「あと ○○ほ」（src/eggsteps.asm。金銀クリスタル共通）
       ・歩数 ＝ $80 − wStepCount（0 なら 256）＋（のこりの 回数 − 1）× 256。hlcoord 9, 15。
       ・クリスタルの EggStatsScreen（$13:$61bf）は WaitBGMap を 呼ばない ので、タマゴの 文の あとの「ld hl, $cf58 / set 5, [hl] / call $32c5」
         （$13:$6215）を farcall に した（ES_AFTER_NOPS）。wStepCount $dc39。処理は $76:$6b00。
  40. 手持ちの 画面で 色ちがいの ポケモンの 名前の 右上（「：Ｌ」の 上）に ★（src/partyshiny.asm。金銀クリスタル共通）
       ・タマゴは なし。★の 絵は 背景の タイル $5e（戦闘では けいけんちの バー $55〜$5d の つぎで 使われて いない。
         町は 手持ちを とじる とき 読みなおされる）。PlacePartyNicknames の さいご（$14:$40c1）を farcall に。処理は $76:$6c00。
  41. つよさの 画面の わざの ページで、めざめるパワーの 名前の 所に「めざパ　こおり57」（タイプ・威力）（src/hpower.asm。金銀クリスタル共通）
       ・クリスタルの LoadGreenPage（$13:$5fcc）は わざの 名前が 金と 同じ hlcoord 9, 6 から 3行ずつ。LoadStatsScreenPals を 呼ばない ので
         さいごの「hlcoord 11, 7 / predef ListMovePP」の 13バイト（$13:$600a）を farcall に（HP_HOOK_NOPS・HP_PP_PREDEF）。処理は $76:$6d00。
  42. つよさの 画面の 3ページめで SELECT を おす たびに のうりょく → 個体値 → きそポイント（努力値。0〜65535）→ のうりょく
      （src/dvview_crystal.asm。金銀は src/dvview.asm）
       ・きそポイントの ときは わくの 上の 線に「きそポイント」、4行めに「たいりょく」。数は 5けたで x 14〜18（たいりょく だけ 1つ 右の x 15〜19。5けたでも 字と くっつかない）。
         wTempMon の きそポイントは $d0d9 から（大きい ほうが 先）。足した 処理は $76:$7100。
       ・StatsScreen_GetJoypad の call GetJoypad（$13:$5ccc）→ $13:$7780 → $76:$6e00。青の ページで SELECT なら きりかえて
         ページを 読みなおす（wJumptableIndex を LoadPage）。LoadBluePage の さいご（$13:$604d）を farcall に。数は x 15〜17（金は 16〜18）。
         きりかえの 印は WRAM バンク2 $dfcb。2ページめの SELECT（わざの ならびかえ）は 元のまま。
  43. 戦闘で 相手の HP バーの 下に「 58／ 65」。HP が へる とき 数字も うごく（src/enemyhp.asm。金銀クリスタル共通）
       ・わくの 下の 線は 数字の 下（4行め）に うつす（数字に 線が かさなって とぎれて いた。EH_LINE_BELOW）。相手の HUD を けす
         所（hlcoord 1, 0 / lb bc, 4, 10・4, 11 / call ClearBox、クリスタルは 8か所）を 5行に（enemyhp_crystal.asm の EH_CLEAR5）。
       ・DrawEnemyHUD の farcall DrawEnemyHUDBorder（$0f:$6044）、HPBarAnim_UpdateHPRemaining（$03:$5a04。金と 同じ 形）。
         wEnemyMonHP $d247・MaxHP $d249。処理は $76:$6f00。
  44. 手持ちの 画面で カーソルの ポケモンの 道具を「もちもの／○○」（src/partyitem.asm。金銀クリスタル共通）
       ・SpriteAnimFunc_PartyMon の ld a, [wMenuCursorY]（$23:$52a2）→ $23:$7fe0。hlcoord 6, 13。前の カーソルは $d832。処理は $76:$7400。
       ・右に 出る メニュー（わざ・つよさをみる・いれかえる など）を ひらく 前に 道具の 名前を けす（けさないと「もちもの／な」が
         わくの 左に はみ出して いた）。金は LoadMenuHeader の call CopyMenuHeader を つなぐが、クリスタルの 戦闘の 手持ちの メニューは
         CopyMenuHeader を じかに 呼ぶので、CopyMenuHeader（$1d07）の 頭の「ld de, wMenuHeader（$cf75）」を つなぐ（PI_wMenuHeader を 決める）。
         入口は ROM0 の 空き $2d15（DummyEndPredef の nop 16こ。どこからも 呼ばれない）。
       ・手持ちの 画面を ひらく とき、PlacePartyMenuText（下の 文の わく）の おわりでも 道具の 名前を かく（PI_TEXT_HOOK を 決めた とき）。
         アイコンの うごきの 所 だけ だと、画面が 出て から 4フレーム ほど おくれて「もちもの／…」が 出て いた。
         クリスタルは PlacePartyMenuText の おわりの「pop af / ld [wOptions], a / ret」（$14:$44c1、f1 ea c0 cf c9）を
         $14:$7a00 に つなぐ（PI_TEXT_HOOK・PI_TEXT_BANK・PI_TEXT_STUB・PI_wOptions）。金銀は その ROM の 値を さがして 決める（決めなければ 今までどおり）。
       ・2列の メニューの 修正（金銀の monmenu_fix.asm）は クリスタルには いらない（9つ以上で 奇数に なる ときは「もどる」を 入れないので 空いた 所が ない）。
  45. つりざおで かならず かかる（src/fishbite.asm。金銀クリスタル共通）
       ・Fish.Fish（$24:$698d）の jr nc, .no_bite（$24:$6991）を nop 2つに。サファリゾーンの 中の つりは 21 の 別の しくみ（ピカチュウ版と 同じ）なので かわらない。
  46. 手持ちの「つかえるわざ」で、「いりょく／ ○○」の 上の 行に「めいちゅう／ 95」（src/moveacc.asm。金銀クリスタル共通）
       ・命中は ×100÷255 を 四捨五入。PlaceMoveData の「hlcoord 1, 14 / predef PrintMoveDescription」（$04:$7301）を farcall に。
         Moves $10:$5c69、wCurSpecies $cf54。hlcoord 9, 11（数は x 15〜17。いりょく と そろう）。処理は $76:$7200。
  47. 倒して しまった 伝説の ポケモン（ホウオウ・ルギア・スイクン・ライコウ・エンテイ）に、殿堂入り するたびに もう いちど 会える
      （つかまえた ポケモンは もどさない。src/legendrevive.asm。金銀クリスタル共通）
       ・HallOfFame の farcall SaveGameData（$21:$6608）を farcall に して、もどして から レポート。
       ・ホウオウ・ルギア：EVENT_FOUGHT_HO_OH（$317）・LUGIA（$318）を けす。
       ・クリスタルは スイクンが あるきまわらない：EVENT_FOUGHT_SUICUNE（$335）を けし、スズのとう 1かいの scene（$d999）を 0 に もどす。
         ライコウ・エンテイ は EVENT_RELEASED_THE_BEASTS（$7b）の あと wRoamMon（$df45）が 0 なら InitRoamMons と 同じ 値（42・37ばんどうろ、Lv40）。
         処理は $76:$7300。
  48. ジョウトの ジムリーダー 8人とも、殿堂入りの あと 再戦できる（src/rematch.asm の いちばん 下。金銀クリスタル共通）
       ・殿堂入りの あと（EVENT_BEAT_ELITE_FOUR $44）、ジムリーダーに 話しかけると「もう いちど しょうぶ する？」→「はい」で
         強い 手持ち（Lv52〜58・わざと 持ち物つき。src/rematch_johto_parties.inc）で 戦える。何度でも 戦える。
       ・「いいえ」・殿堂入り まえ・初めて 戦う ときは 元の ゲームと 同じ。
       ・話しかけの「checkevent EVENT_BEAT_○○ / iftrue .FightDone」（6バイト）を farsjump に かえる。
         アカネは faceplayer の あと opentext の 前（RMJ_WHITNEY_OPEN 0）、イブキは「checkflag ライジングバッジ（$22）/ iftrue .AlreadyGotBadge」。
       ・クリスタルの 値は src/rematch_johto_crystal.inc（マップの スクリプトを ROM から 探して 決めた）。
       ・手持ちは RM_PARTY_FAR（11 の 再戦も いっしょに 新しい バンク $70 から 読む。ReadTrainerParty の
         ld a, [wOtherTrainerClass]（$0e:$57ab）を call に して、wScriptBank が $70 の ジムリーダー なら 元の TrainerType4 を 写した 処理で 読む）。
         クリスタルは トレーナーの バンクに 空きは あるが、ジョウトの グループを 足す 作りが まだ ないので こちらに した。
         loadtrainer は 人, 1（名前・お金・個体値は 1回目と 同じ）。tools/rematch_find.py で RM_PARTY_FAR 用の アドレスも 探す。
       ・置き場所：$70:$6100 手持ちを 読む 処理と カントーの 手持ち ／ $6800 ジョウトの 手持ち ／ $7400 ジョウトの スクリプトと セリフ ／ $0e:$7710 入口（23バイト）
  49. むしとり大会で つかまえた ポケモンを、にがす かわりに パソコンへ おくれる（src/contestpc_crystal.asm。クリスタル用）
       ・2匹めを つかまえて「ポケモンを いれかえる？」→ はい なら 前の ポケモン、いいえ なら つかまえた ポケモンを
         「○○を パソコンに おくりますか？」→ はい で ボックスへ（つかまえた 場所は しぜんこうえん）、いいえ なら 元の ゲームと 同じ（にがす）。
       ・ボックスが いっぱい（30匹）なら「ボックスが いっぱいなので パソコンに おくれません！」で 元の まま。
       ・ニックネームは きかない（戦いの 中で 名前の 画面を ひらくと、もどった あと フィールドの 画面に なるため）。
       ・BugContest_SetCaughtContestMon（$03:$697c）の「lb bc, 14, 12 / call PlaceYesNoBox / ret c」（$03:$6991。7バイト）を
         farcall ContestPC_YesNo / ret c に。ボックスへは CheckPartyFullAfterContest.TryAddToBox（$13:$592c）を まねて 入れる
         （wContestMon $df12 → wBufferMon → InsertPokemonIntoBox $14:$53b8、SetBoxMonCaughtData $13:$5a23）。
         入れかえない ときは 前の ポケモンを WRAM バンク2 の $dfd0〜$dfff に よけ、.generatestats（$03:$69ab）で
         つかまえた ポケモンを wContestMon に 作って おくり、前の ポケモンを もどす。処理は $76:$7600。
  50. 連れ歩き：手持ちの 先頭の ポケモンが 主人公の 後ろを ついて 歩き、話しかけると 鳴いて アイコンを 出して しゃべる
      （src/follow_crystal.asm・follow_talk.inc・follow_talk_data.inc・follow_data.inc。クリスタル用。連れ歩きキットから）
       ・連れ歩くのは 先頭の ポケモン（ひんしの ときは かくれる。タマゴも 歩く）。じてんしゃ・なみのり などの ときは かくれ、
         おりると 主人公の 場所から また ついて くる。ドア・そらをとぶ などで 来た ときは 主人公と かさなって 見えず、1歩 目から 出る。
         マップの つながりでは 主人公の 後ろに いる まま。段差も いっしょに とぶ。主人公は 連れ歩きに ぶつからない（ふりかえると 入れかわる）。
       ・Crystal Crunch（joseph-bayer/crystal-for-friends）の 連れ歩きと 同じ 見た目・動き（ユーザーの 希望）。データは
         tools/follow_cc_extract.py で Crystal Crunch の リポジトリから gfxdata/follow_cc/ に 取り出した もの。
       ・絵：Crystal Crunch の 手持ちの アイコン（gfxdata/follow_cc/icons/*.png。16×32 ＝ 2コマ）から GetFollowerIconSprite と 同じに
         作る：下向き（正面）は 手持ちと まったく 同じ 絵（gfxdata/minis.2bpp の Polished Crystal の ミニアイコン。止まり ＝ 1コマ目、
         歩き ＝ 2コマ目、左右反転 しない。ユーザーの 希望）。手持ちの アイコンは 目・顔の 白を 透明で かいて いて フィールドでは
         すけるので、あな（外と つながって いない 透明）だけの「白い したじき」（gfxdata/follow_icon/mask.bin、バンク $67〜$6d、
         1匹 24タイル。正面・後ろ・横 とも。後ろ・横の 歩行グラフィックの すける 所も 白）を VRAM バンク0 タイル $64〜$7b に 読み、スプライトを 並べた あと（_UpdateSprites の call InitSprites $01:$5930 → F1_InitSprites
         $01:$7fe8 → Fw_Underlay）連れ歩きの 4枚の 後ろに パレット5（銀。色1 ＝ 白、朝・昼・夜・暗い 所 とも 白）で 足す。
         VRAM は 人の 絵の 2つめの 表の $e4〜$fb を Fw_FixOverflow で あけて おく（$7c〜 は ポケモンセンターの 回復の 絵）（使わない 組を けす。あけられない マップでは
         wFwMaskOK $dfbf = 0 で したじきなし。テスト用 ROM で 全 388 マップに 移動して 調べ〔382 マップは 着いて すぐ、6 マップは 着いた とき イベント中〕、あけられない マップは なかった）。人の 絵を 読みこんだ あと（LoadUsedSpritesGFX の さいご $05:$4202 → F5_Misc）にも
         読みなおす（メニューから もどった とき）。アイコンには 後ろ・横の 絵が ないので、
         後ろ・横は 向きの ある 歩行グラフィック（gfxdata/follow/*.2bpp の 止まり・歩きの 上・横）を 使う（ユーザーの 希望）。
         アンノーンは 文字ごと、タマゴは タマゴ。
         tools/follow_gen.py → gfxdata/follow_icon/*.2bpp、バンク$60〜$66（278 ＝ ボールの 絵）。
       ・色：正面は 手持ちと 同じ（FollowerOwnPals $7b:$6000）。後ろ・横も その ポケモンの 同じ 2色（FollowerWalkPals $7b:$67e0）で、
         歩行グラフィックの 明るい 所・暗い 所に どちらを あてるかを ポケモンごとに 自動で 決める（tools/follow_gen.py の walk_swap：
         正面と 後ろ・横で 2色の しめる 広さが 同じに なる 方。差が 小さければ、絵が かかれた 元の 色〔はだ (31,19,10)＋フィールド色〕に
         近い 方）。元の 色の まま だと、ピカチュウの 横が はだ色、アリゲイツの 横が 赤 など、正面と ちがって 見えた。連れ歩きの 向き（OBJECT_DIRECTION）が
         正面 ⇔ 後ろ・横 で かわったら Fw_FaceCheck が 7本目の 色を 書きなおす（WRAM バンク2 $dfbe wFwLoadedFace）。
         Fw_FaceCheck は Fw_Update と Fw_Underlay（スプライトを 並べる たび）の 両方で 呼ぶ（話しかけた とき など スクリプトの 間は
         Fw_Update が まわらず、向きが かわっても 色が 1秒ほど 前の まま で 一瞬 色が かわって 見えた）。
       ・色：手持ちと 同じ（gfxdata/minipals.bin。以前は Crystal Crunch の 色 gfxdata/follow_cc/pals.bin）。もとの 説明：Crystal Crunch と 同じ（戦闘の 絵の 2色を icon_palette_order の あて方（入れかえ・明るい 方を 白）で ならべた もの。
         gfxdata/follow_cc/pals.bin → FollowerOwnPals $7b:$6000）。Crystal Crunch は 夜・暗い 所で 暗く するが、ユーザーの 希望で しない。
         OBJ パレットの 7本目（PAL_OW_ROCK）を 連れ歩き 専用に（岩・かいりきの 岩の スプライトは パレット 3 に）。LoadMapPals が OBJ の
         色を 写す call FarCopyWRAM（$02:$7203 → $02:$7f80）の あとで 7本目を 書く。読みなおす とき（Fw_CheckReload）は
         INVISIBLE ＋ UpdateSprites で いったん けしてから 絵を 読み、色を wOBPals1・2 と OCPD（VBlank を まって じかに）に 書いて もどす
         （絵の 読みこみに 何フレームか かかり、前の 色の 新しい 絵が 見えた）。
       ・動き（SetFacingFollowerStep・Run・Idle）：ObjectActionPairPointers（$01:$445f）の STAND・STEP を $01:$7f40 の F1_ に。
         連れ歩き（スプライト $e2）だけ、歩く ときは 2コマ（8フレームごと、Bダッシュ中は 4フレームごと）だけ かえて、止まりの コマで
         1ドット 上げて はねる。止まって いる ときは 16フレームごとに 2コマを かえる（スクリプト中は 止まり）。
       ・えらぶ（Crystal Crunch と 同じ）：手持ちの 画面で SELECT を おした ポケモンが 連れ歩く。えらんで いる ポケモンで SELECT なら
         だれも 連れ歩かない。wFwSlot（$d833。レポートに 書かれる。0 ＝ 1匹目（はじめ・前の レポート）、1〜6、$ff ＝ だれも）。
         InitPartyMenuWithCancel（$14:$441b）の wMenuJoypadFilter を A・B・SELECT に、PartyMenuSelect（$14:$444b）の
         call StaticMenuJoypad を F14_MenuJoypad（$14:$7b00。SELECT なら Fw_PartySelect して もう一度 まつ）に。
         赤い ★：PartyShiny（色ちがいの ★）の あとで Fw_PartyMark が「：Ｌ」の 右上（hlcoord 9, 0 ＋ 2行ごと）に タイル $5f
         （色2 の ★）を かき、色の 番号を 3（HP の 赤）に。SELECT の あとは WaitBGMap2（$31cc。色の 番号も 送る）。
         番号を 追う：_SwitchPartyMons の call .SwapMonAndMail（$14:$4fba）→ Fw_SwapSlots、RemoveMonFromPartyOrBox の 頭（$03:$628f）→
         Fw_RemoveSlot（その ポケモン なら 1匹目、後ろ なら 1つ 前。あずける・にがす・そだてや など ぜんぶ）。
         連れ歩く ポケモンの 種類・個体値・HP・状態・なつき度・なまえ は ぜんぶ wFwSlot から（会話の 〈なまえ〉は wStringBuffer1 に 写す）。
       ・ボール（Crystal Crunch の StepFunction_PokeballClosing・Opening）：連れ歩かなく なる とき（じてんしゃ・なみのり・ひんし・
         だれも えらんで いない）は ボールに もどる（開いた → 半分 → とじた、4フレームずつ）。もどって いた あと 出る ときは、主人公と
         かさならなく なった ところで ボールから 出る。絵は Crystal Crunch の anim_pokeball.png（番号 278）、色は PAL_OW_RED の 2色。
         コマは オブジェクトの OBJECT_RANGE（$20）に 入れて F1_ の 動きが 向きに する（1 とじた ＝ 横、2 半分 ＝ 上、3 開いた ＝ 下）。
         WRAM バンク2 $dfbb〜$dfbd（wFwBall・wFwBallT・wFwHidden）。
       ・Bダッシュ：主人公と はなれず いっしょに 走る。Bダッシュ中（B と 十字キー）は まいフレーム、連れ歩きの 歩く 予定
         （wFollowMovementQueue $d4c4〜、5バイト）の ふつうの 歩き（$0c〜$0f）を はやい 歩き（$10〜$13）に かえる（ふりかえって
         主人公と 入れかわった あとや follow を しなおした あとの 1歩目が ふつうの 速さで、1マス おくれた まま 走って いた）。
         さらに MovementFunction_Follow（$01:$48a0 の ld hl, GetFollowerNextMovementIndex）を F1_NextMove（$01:$7f40）に かえ、
         連れ歩きが 次の 1歩を 出す ときに ふつう・はやいを いまの 主人公の 速さに あわせる（1歩 おくれで たどるので、ダッシュの はじめは
         1マス おくれて はなれ、ダッシュを やめた あとは 追いついて 主人公に かさなって いた）。
       ・おきなおし（follow の しなおし・主人公の 後ろに おく）は 主人公が 歩いて いる 途中は しない（途中で おくと 絵の 場所が
         4ドット ずれた まま に なった。つながりを Bダッシュで こえた 直後 など）。
       ・つながりで となりの マップに 入った とき、マップの 人の 絵が wUsedSprites に なければ スプライトを ぜんぶ 読みなおす
         （Fw_MapSpritesOK。使わない 組を けして いる ため、人が 主人公の 絵で 出て いた）。
       ・ふりかえり：主人公と 入れかわる ときも 見えた まま。主人公が 手前に かかれ、連れ歩きは 主人公の 奥を とおる（ユーザーの 希望。
         入れかわる 間 かくす やり方は「消える」ので やめた）。
         （Fw_Update の かさなりの チェックで、Fw_DesiredNow の あとの bc（マップの 人）が こわれて いたのも 直した）
         follow 中に 止まって いて 2マス 以上 はなれて いれば、主人公の 後ろ（歩いた 向きの 反対）に おきなおす（つながりを 走って こえた あと など）。
       ・しくみ（元の ゲームの follow を 使う）：
         LoadMapObjects（$05:$5573）の OBJECTS の コールバックの あと → マップの 人の 数＋1 の マップオブジェクトを 連れ歩き用に 書く（スプライト $e2・
           OBJECTTYPE_3・STANDING_DOWN。ドアなどは 主人公の 場所、つながり（hMapEntryMethod = $f7）は wPlayerStepDirection の 反対）。
           15人 いる マップ（コガネシティ）では、いま かくれて いる 人（イベントフラグが 立って いる。後ろから さがす）の 番号を 借りる
           （コールバックで 人を 出す・けす（コガネの おしえオヤジ）の あとで えらぶ ため、コールバックを 先に した）。
           follow の 変数（$d4c0・$d4c1）も ここで けす。
         HandleMap の call HandleMapObjects（$25:$6788）→ $25:$7fe0 → Fw_Update（まいフレーム）：
           連れ歩かない とき（手持ち なし・先頭が ひんし・wPlayerState が 0 で ない）は DeleteObjectStruct。
           主人公と 同じ 場所の 間は INVISIBLE。スクリプト中（wScriptMode $d428 ≠ 0）は ここで おわり。
           先頭が かわって いれば 絵（GetUsedSprite $05:$43b9）と 色を 読みなおす。
           出て いなければ 主人公の 場所に おいて UnmaskCopyMapObjectStruct、follow が 主人公 → 連れ歩き で なければ
           となり なら StartFollow（$01:$5803）、はなれて いれば おきなおして StartFollow（イベントの follow の あとも もどる）。
           マップに 連れ歩きが いない（はじめての ポケモンを もらった とき）は 空いた 番号に 作る（スプライトを ぜんぶ 読みなおし、
           出て いる 人の OBJECT_SPRITE_TILE を GetSpriteVTile で なおす）。
         GetMonSprite（$05:$424a）の cp $e0 → $05:$7e00：$e2 なら 先頭の 絵（de・b = バンク、c = 12、l = WALKING_SPRITE、carry）。
         LoadAndSortSprites の call ArrangeUsedSprites（$05:$42d2）の 前で wUsedSprites を 並べかえ：$e2 を 1番め（タイル $0c〜$17・
           歩きは $8c〜$97）に、その あと この マップの 人が 使う 歩く・立つ スプライトを 前に よせる。足した ぶん のらなく なる ときは
           この マップで 使わない 組を けす（元の ArrangeUsedSprites は のらない 組の タイルを 決めず、GetUsedSprites が 種類の 数を
           タイルと して 読み、主人公の 絵を こわして いた）。
         主人公の ぶつかり：DoPlayerMovement .CheckNPC の farcall IsNPCAtCoord（$20:$435a）→ Fw_IsNPCAtCoord（連れ歩きなら なし に する）。
         話しかけ：TryObjectEvent の 種類の 表（$25:$69ee）の OBJECTTYPE_3（$25:$6a30。元は xor a / ret が 4つ）を
           ld a, $79 / ld hl, FollowerTalkScript / jp CallScript に。4〜6 は $25:$69ec（xor a / ret）に。
       ・会話：faceplayer → 鳴き声 → 表（会話文案.md の 順。状態異常 → 場所・タイプ → ふつう）の さいしょに 合った 行の アイコン・文
         （2つ 以上 あれば ランダム）。「ふつう」では 1/32 で きんのたま を 見つける（ひろいますか？）。タマゴは「ときどき うごいている……」
         （キットに ないので 足した）。ランドマークは GetWorldMapLocation、タイプは 基本データ（$14:$54ba）、状態は 先頭の 状態、
         ヤドンのいどは EVENT_CLEARED_SLOWPOKE_WELL（$2b。日本版の スクリプトで 同じ 番号を 確かめた）。
         スクリプトの 命令の 番号は 日本版の 表（$25:$6cb1）で 調べた（英語版と ちがう：waitbutton $53・faceplayer $6a・showemote $74・
         end $90・verbosegiveitem $9d など）。tools/follow_talk_gen.py で 表と 文を 作る。
       ・ピカチュウ（先頭が ピカチュウの とき）だけは ピカチュウフルカラーと 同じに、話しかけると 表情の 絵（src/follow_pika.inc）：
         ねむり → ねむる、ほかの 状態異常 → なく、それ以外は なつき度（ピカチュウ版の 表の 行）と 気分（クリスタルには ないので 列3・列4 を ランダム）で
         表情を えらぶ。ピカチュウの 上に アイコン（ピカチュウ版の 吹き出し → ハート・にこにこ・ねむり・いなずま・つり・！。どくろは かなしい）→
         わく（6, 5 から 7×7。ピカチュウ版と 同じ 場所）に 表情の 絵を コマ送りで 出し、鳴き声（クリスタルの ピカチュウの 声）→ 自動で とじる。文章は 出ない。
         絵は ピカチュウフルカラーの ROM で 29 の 表情を うごかして 1フレームずつ とり（tools/follow_pika_capture.py。DisplayStartMenu を
         RunPikapic を 呼ぶ ように かえた ROM で START を おす）、わくの 中 5×5 の コマと 長さに した もの（gfxdata/pikapic/ypikadata.pkl →
         tools/follow_pika_gen.py → src/follow_pika_data.inc、バンク$7a・$7b、表は $79:$7d00）。いなずまの 画面 ぜんたいの 光りは 入れて いない。
         出し方：opentext から 文の わくを ぬいた もの（ClearWindowData・ReanchorBGMap_NoOAMUpdate $01:$659c・HDMATransferTilemapAndAttrmap_Menu・
         LoadFonts_NoOAMUpdate $01:$6607。しないと wTilemap と 画面が 2 マス ずれ、歩いて くる 前の 行が 出た）→ MenuBox → 画面（wAttrmap $cdcd）で
         使って いない パレットを さがして わくの 中の 色に し、しろ・オレンジ・ちゃいろ・くろ に する（文の 色 7 だと 7 を 使う 木や 段差が
         オレンジに なった）→ タイルを 字の 所（$8800〜）に → コマを wTilemap に 書いて WaitBGMap → おわりは closetext。
         色は wBGPals2 だけ 書きかえ、ApplyTilemap の あと（＋1フレーム まつ）に 書く（前に 書くと、コガネで VBlank の 色の 書きこみが
         おくれて 画面に 入らず、絵が みどりの まま だった）。とじる ときは ClosePokepic と 同じ 手順だが GetMemSGBLayout（マップの 色の
         読みなおし）は せず、かりた パレット 1つだけ wBGPals1 から もどす（ClosePokepic では かりた 色が 画面に のこり、マップの 色も
         読みなおして いた。ほかの 色・連れ歩きや 人の 色と きょうごう しない ように した）。
       ・WRAM：バンク2 の $dfb8〜$dfba（読みこんで いる 絵の 番号・色）。調べる 間の 一時は wStringBuffer2（$d066〜）。
       ・コードは バンク$79、色の 表は $79:$7c00。
       ・WRAM：バンク2 の $dfbb〜$dfbd（ボール）、$d833（えらんだ 番号。レポートに 書かれる）。
       ・クレジット：連れ歩きの コード Vulcandth・AtmaBuster（fellowship-of-the-roms/pokecrystal の follow-mons ブランチ）、
         Crystal Crunch（joseph-bayer / gomojoeb。アイコンで 歩く 絵・色の あて方・動き・SELECT で えらぶ・ボールの アニメ）、
         手持ちの アイコンの 絵と ポケモンの 色 Sour Crystal（SoupPotato）、アンノーンの アイコン Polished Crystal（Rangi42）。
         公開する ときは ブログ用 HTML の クレジットに 書く（連れ歩きキットの クレジット.txt）。
  51. バッジを 16こ ぜんぶ あつめた あとは、四天王・ワタル・ライバルが 強くなる（src/league.asm。金銀クリスタル共通）
       ・ジョウトと カントーの バッジが 16こ そろって いると、イツキ・キョウ・シバ・カリン・ワタル と
         ライバル（オツキミやま・セキエイこうげん）の 手持ちが 6ぴき・Lv67〜76・強い わざ・持ち物 つきに なる
         （HGSS の 再戦 くらい。src/league_parties.inc。tools/league_gen.py で 名前から 作る）。
         ライバルの 最後の 1ぴきは 元と 同じ（メガニウム・バクフーン・オーダイル）。オツキミやまは セキエイより 3 レベル 下。
       ・16こ そろう 前は 元の まま。名前・お金・AI は 元の まま（お金は 最後の ポケモンの レベルで ふえる）。
       ・しくみ：48 の 再戦と 同じ 入口（ReadTrainerParty の ld a, [wOtherTrainerClass] → $0e:$7710）を つかう。
         RM_LEAGUE を DEF すると、入口は いつも Rematch_ReadParty を 呼び、その 頭で League_ReadParty が
         wJohtoBadges（$d84a）と wKantoBadges（$d84b）が どちらも $ff か 見て、表（クラス・番号）に あれば
         元の TrainerType4 の 写しで 読む。ライバル（RIVAL2 $2a）は wOtherTrainerID（$d262）の 1〜3・4〜6 で 分ける。
       ・置き場所：$70:$6a00（約 570 バイト）。値は src/rematch_crystal.asm の LG_～。
       ・金銀に 入れる とき：LG_wJohtoBadges・LG_wKantoBadges・LG_wOtherTrainerID（wOtherTrainerClass ＋ 2）を その ROM の 値に して、
         RM_LEAGUE と いっしょに rematch.asm の あとに league.asm を INCLUDE する。金銀も ライバルの 番号
         （オツキミやま 1〜3・セキエイこうげん 4〜6、メガニウム・バクフーン・オーダイルの 順）と クラスの 番号は 同じ。
  52. ゲームコーナーの 景品の わざマシンに わざの 名前を 出す（src/prizetm_crystal.asm）
       ・「わざマシン25　5500」→「25　かみなり　　　5500」（コガネ・タマムシの 景品交換所）。
       ・メニューの 見出し（コガネ $15:$625c・タマムシ $1a:$7491）の 右はしを 15 → 17 に 広げ、
         中身を 同じ バンクの 空き（$15:$7f00・$1a:$7f80）に 新しく 置く。値段・えらんだ あとの スクリプトは 元の まま。
  53. サファリゾーンで 歩いて いる あいだも 画面の 下に のこりの 歩数と ボールを 出す（src/safari/safari.asm の SafariHUD）
       ・「あと 498ほ　ボール 30こ」（ボ の ゛ は 上の 行）。サファリゲーム中で サファリの 中 だけ。
       ・PlaceMapNameSign の .disappear（$2e:$40be。フィールドで 毎フレーム）を SafariHUD への farcall に して、
         ウィンドウを 128（下の 2行）に 出し、ウィンドウの 1・2行め（$9c00・$9c20）に STAT を 見て 1バイトずつ かく。
         hWY が 128 で ない とき（地名の 看板・メニューの あと）は 2行 ぜんぶ、数字は 毎フレーム かく。
       ・色は BG の 8本目を 白・黒に（wBGPals1・2 の 8本目が ちがえば 書いて hCGBPalUpdate）。
  54. そだてやで あずけた ポケモンの 今の レベルも おしえる（src/daycarehint.asm の DH_LEVEL。金銀クリスタル共通）
       ・おじいさん「○○は いま レベル50 じゃ」・おばあさん「…よ」。そのあと 今までの 話（相性・タマゴ・ひきとる か）。
       ・おじいさんは 41 の 入口（GetBreedMon1LevelGrowth の farcall）で、おばあさんは DayCareLady の
         farcall GetBreedMon2LevelGrowth（$05:$6c33）を DayCareLevel_Lady に。レベルは e（今の レベル）を
         wStringBuffer2＋7 に おいて text_decimal で 出す。
       ・金銀に 入れる とき：DH_LEVEL を DEF して DH_LADY_HOOK・DH_GetBreedMon2LevelGrowth・
         DH_wBreedMon1Nickname・DH_wBreedMon2Nickname・DH_wLevelTemp・DH_LEVEL_ADDR を その ROM の 値に。
  55. 状態異常の 文字に 色（src/statuscolor_crystal.asm）
       ・どく むらさき・やけど 赤・こおり 水色・まひ 黄色・ねむり 灰色。戦闘の 自分と 相手の HP の わく、手持ちの 画面（5種類 ぜんぶ）。
       ・戦闘：相手は 5本目（つかまえた 印と いっしょ。印の 黒を 色1 に うつし、色3 を 状態異常の 色に。
         src/redballs.asm の RB_STATUSCOLOR）。自分は 6本目の 色1：文字の 絵を「色1 で かいた もの」に して
         VRAM の バンク1 $7c〜$7e に 作り、ます（16〜18, 8）を その タイル・6本目＋バンク1 に（6本目の 色3 は PP 用）。
         4本目（けいけんちの バー）は バーの 下の 線が 色3 を つかうので つかわない。
       ・手持ちの 画面（_CGB_PartyMenu の おわり $02:$519d）：どく 4本目・やけど 5本目・こおり 6本目 の 色3、
         まひ 4本目・ねむり 5本目 の 色1（色1 の 文字を バンク1 $72〜$74・$75〜$77 に 作る）。
       ・色1 の 文字は PlaceNonFaintStatus（$14:$4dca）の あと（$14:$7c00 の 入口から バンク$76）と 画面の 色を きめる 所の
         両方で 作る（手持ちの 画面は HP の バーを かく 所で 色を きめ、状態は その あとに かかれる）。
       ・VRAM の バンク1 の タイル $60〜$7f は 町の タイル（$00〜$5f）にも 戦闘の 相手の 絵の うごき（多くて $61 まで）にも
         つかわれない（つよさを みる 画面が $7f を つかう だけ）。
  56. わざを えらぶ とき、PP の のこりが 4分の1 いか なら 黄色、0 なら 赤（src/statuscolor_crystal.asm）
       ・MovePower_Draw の はじめ（movepower.asm の MP_PPCOLOR）で 右下の わくの「cc／mm」（14〜18, 13）を 読んで 6本目の 色3 を かえる。
       ・わざを えらび おわったら 黒に もどす（BattleMenu_Fight の call MoveSelectionScreen（$0f:$4461）→
         ROM0 $3ff6・$00e6 の 入口 → StatusColor_PPReset。下の テキストの 濁点が 色つきに ならない ように）。
  57. ずかんの 説明の ページで SELECT を おすと、タイプ・種族値・進化の しかたの ページに（src/dexinfo_crystal.asm）
       ・つかまえた ポケモン だけ。説明の 右下に ▼。SELECT で つぎの ページ、さいごの つぎは 説明に もどる。
         2ページめ：タイプ・たいりょく・こうげき・ぼうぎょ・すばやさ／3ページめ：とくこう・とくぼう・進化 2行／
         4ページめ から：進化の のこり（3行ずつ。イーブイ など）。文字は 説明の わく（3行）の 中 だけに かく（見きれない）。
       ・進化の 行：「なまえ　じょうけん」（レべル nn・どうぐ・つうしん・なつく ひる／よる）。もたせて つうしん・
         カポエラー など は 2行めに「もたせる　どうぐ」・「こうげきが　たかい」など。
       ・つかまえたか は wPokedexCaught（$de2d）。ページは WRAM バンク2 の $dfc0・$dfc1。
  ※ ピカチュウ版の「コインを 買える」（コガネ・タマムシで 50まい 1000円・500まい 10000円）と
    「自分の パソコンの 道具の 説明（ひきだす・すてる）」は もとの クリスタルに あるので 足して いない。
  ※ 場所の名前の札（金に 足した もの。src/mapsign.asm）は、クリスタルには もとから あるので 入れていない。
  ※ ガンテツの ボールを まとめて 作る（金に 足した もの）は、クリスタルでは もとから 数を えらんで わたせる
     （Kurt_SelectQuantity $22:$40d7・verbosegiveitemvar）ので 入れていない。
  7. オリジナルからあるバグの修正（src/bugfix.asm、通常版・60fps版の両方に入れる）
       pret/pokecrystal の docs/bugs_and_glitches.md の直し方に合わせた。29か所：
        バトル  ・ほろびのうた／まきびし で HP 0 なのに ひんしにならない
                ・ふといホネ／でんきだま で こうげき（とくこう）が 1024 を超えると小さくなる
                ・追加効果100%のわざが 1/256 で効果なし（通信対戦は元のまま）
                ・はらだいこ：HP が半分なくても こうげきが上がる
                ・はかいのいでんし の こんらんが 256ターン続く
                ・カウンター／ミラーコート：相手が道具を使ったターンでも成功
                ・かなしばり＋ポイントアップのわざで わるあがきにならない
                  （$0f:$67c1 を jp に した ため、PP が ぜんぶ 0 の ときの jr .force_struggle（$67ac → $67c3）が jp の まん中に
                   とんで「だすことの できる わざが ない」の 文が こわれて いた。その jr を $67c1 に むけて 直した。
                   PP 0 → 「イは だすことの できる わざが ない！」→「わるあがきを した！」を 通常版・60fps版で 確かめた）
                ・ロックオン／こころのめ のあと、そらをとぶ・あなをほる中の相手に効かないわざがある
                ・おんがえし／やつあたり の ダメージが 0 になる
                ・最大HP 3以下のポケモンとの入れかえで止まる
                ・ぼうぎょを下げるわざが みがわりを壊した後でも下げる
                ・攻撃して能力を上げるわざが 相手をたおすと上がらない
                ・へんしん中に スケッチで 覚えられないわざを覚える
                ・入れかえで出てきた相手に まひ／やけど の能力ダウンがかからない
                ・グレイシャバッジで とくぼうが上がらないことがある
                ・野生のポケモンの テレポートが 必ず成功する
                ・かしこいAI：自分がもうどくなのに くろいまなざしを使いたがる
                ・りゅうのキバではなく ドラゴンのウロコで ドラゴンわざが強くなる
        捕獲    ・へんしん中のポケモンを捕まえると メタモンになる
                ・どく／まひ／やけど で 捕まえやすくならない
                ・最大HP 342以上の 捕まえやすさの計算
                ・ムーンボールが効かない／ラブラブボールが同じ性別に効く／スピードボールが3匹にしか効かない
                ・捕まえ方を見せる人：手持ちとボックスがいっぱいだと止まる
        その他  ・レベル1 の「やや遅い」成長の けいけんちがおかしくなる
                ・育て屋から引き取ると けいけんちが減ることがある
                ・ポケモン（人）の上で つりができる
                ・もらったけいけんちが 5けただと 正しく出ない
       ※ ヘビーボールの重さのまちがいは、日本版は作りがちがっていて起きないので直していない。
       ※ バトルの直しが入るので、元のゲームとの通信対戦は ずれることがある。

  ※ 手持ちのメニューの項目が9つ以上になったとき（ひでんわざを3つ以上覚えているときなど）は
     横2列に並べる。日本版は濁点・半濁点が上の行に出るので、1行ずつに詰められないため。
     「もどる」を入れると9つ以上の奇数になるときは「もどる」を入れない（B でもどれる）。
     横2列で空いた所にカーソルが入らないようにするため（元のゲームも項目がいっぱいのときは「もどる」を入れない）。

■ ファイル
  src/features.asm   1〜4（5 は build.py で基本データの TM/HM ビットを書きかえる）
  src/fps60.asm      6（60fps）
  src/bugfix.asm     7（バグ修正。直した場所ごとに 日本版クリスタルのアドレスつき）
  src/minis.asm      8（手持ちのポケモンの見た目）
  src/hmfield.asm    9（ひでんわざ。金・銀・クリスタル共通）
  src/hmfield_crystal.asm  9 のクリスタル用の値（これを組み立てる）
  tools/hmfield_find.py    9 のアドレスを ROM から調べる
  src/fishnest.asm         10（ぶんぷの釣り。金・銀・クリスタル共通）
  src/fishnest_maps.inc / fishnest_maps_crystal.inc  10 の釣りの場所の表（金銀／クリスタル）
  src/fishnest_crystal.asm 10 のクリスタル用の値（これを組み立てる）
  tools/fishnest_find.py・fishnest_maps.py  10 のアドレスを調べる／表を作る
  src/rematch.asm          11（ジムリーダー再戦の本体とセリフ。金・銀・クリスタル共通）
  src/rematch_parties.inc  11 の再戦用の手持ち（金・銀・クリスタル共通。種類・わざ・どうぐの番号は同じ）
  src/rematch_crystal.inc / rematch_crystal.asm  11 のクリスタル用の値／組み立てるファイル
  tools/rematch_find.py    11 のアドレスを ROM から調べて rematch_<版>.inc を作る
  src/league.asm           51（16この バッジの あとの 四天王・ワタル・ライバル。金・銀・クリスタル共通）
  src/league_parties.inc   51 の 手持ち（tools/league_gen.py で 作る。金・銀・クリスタル共通の 番号）
  src/prizetm_crystal.asm  52（景品の わざマシンの 名前）
  src/statuscolor_crystal.asm 55・56（状態異常・PP の 色）
  src/dexinfo_crystal.asm  57（ずかんの タイプ・種族値・進化）
  data/wild_crystal.txt・wild_gold.txt・wild_silver.txt  12 の出現表のルール（版ごと）
  tools/wild_find.py       12 のルールから 書きかえる asm を作る（クリスタルは src/wild_crystal.asm）
  src/redballs.asm         17（ボールの印を赤白に。金銀クリスタル共通）
  src/redballs_crystal.inc / redballs_crystal.asm  17 のクリスタル用の値／組み立てるファイル
  tools/redballs_find.py   17 のアドレスを ROM から調べる
  src/picpal.asm           18（ずかん・パソコンの絵をカラフルに。金銀クリスタル共通）
  src/picpal_crystal.inc / picpal_crystal.asm  18 のクリスタル用の値／組み立てるファイル
  tools/picpal_find.py     18 のアドレスを ROM から調べる
  src/fieldcolors.asm      19（フィールドのボール・回復の機械・肌の色。金銀クリスタル共通）
  src/fieldcolors_crystal.inc / fieldcolors_crystal.asm  19 のクリスタル用の値／組み立てるファイル
  tools/fieldcolors_find.py 19 のアドレスを ROM から調べる
  src/sigmove.asm          20（ルギア・ホウオウの 専用わざ。金銀クリスタル共通）
  src/sigmove_crystal.inc / sigmove_crystal.asm  20 のクリスタル用の値／組み立てるファイル
  tools/sigmove_find.py    20 のアドレスを ROM から調べる
  src/safari/              21（サファリゾーン。safari.asm 本体・safari_gen.asm データ・jp_crystal.inc・safari_crystal.inc・crystal_includes.asm・pokegold_events.asm・safari_nest.inc ぶんぷの表）
  tools/safari_gen.py      21 の データを ピカチュウ版フルカラーの ROM から作る
  src/autobox.asm          22（ボックスの 自動切りかえ。金銀クリスタル共通）
  src/autobox_crystal.asm  22 の クリスタル用の 値／組み立てる ファイル
  src/masterball.asm       23（マスターボールを 売る。金銀クリスタル共通）
  src/masterball_crystal.asm  23 の クリスタル用の 値／組み立てる ファイル
  src/repelask.asm / repelask_crystal.asm      24（むしよけ。共通／クリスタルの 値）
  src/textspeed.asm / textspeed_crystal.asm    25（文字の 速さ。共通／クリスタルの 値）
  src/phonefreq.asm / phonefreq_crystal.asm    26（電話の 回数。金銀用／クリスタル用）
  src/moverelearn.asm / moverelearn_crystal.asm  27（技を 思い出させる 人。共通／クリスタルの 値）
  src/nesttime.asm / nesttime_crystal.asm      28（ぶんぷの 時間帯。金銀用／クリスタル用）
  src/daycarehint.asm / daycarehint_crystal.asm  29（育て屋の 話。共通／クリスタルの 値）
  src/legends.asm / legends_crystal.asm        30（セレビィと 伝説の 鳥。共通／クリスタルの 値。base.gbc を INCBIN で 読む）
  src/starters.asm / starters_crystal.asm      31（カントー御三家。共通／クリスタルの 値。base.gbc を INCBIN で 読む）＋ starters_texts.inc（文）・starters_jenny.inc（ジュンサーの 絵）
  tools/starters_gen.py    31 の 文と 絵を ピカチュウフルカラーの ROM から 作る
  src/movepower.asm / movepower_crystal.asm    32（わざの 威力と 命中。共通／クリスタルの 値）
  src/itemfinder.asm / itemfinder_crystal.asm  33（ダウジングマシンの 方向。共通／クリスタルの 値。base.gbc を INCBIN で 読む）
  src/phonemark.asm / phonemark_crystal.asm    34（電話帳の 再戦の 印。金銀用／クリスタル用）
  src/pokegearwhite.asm / pokegearwhite_crystal.asm  35（ポケギアの 文字の 後ろを 白に。共通／クリスタルの 値）
  src/quickball.asm / quickball_crystal.asm    36（前の ボールを すぐ 投げる。金銀用／クリスタル用）
  src/hearts.asm / hearts_crystal.asm          37（なつき度の ハート。金銀用／クリスタル用）
  src/gearday.asm / gearday_crystal.asm        38（ポケギアの 今日の できごと。共通／クリスタルの 値）
  src/eggsteps.asm / eggsteps_crystal.asm      39（タマゴの 歩数。共通／クリスタルの 値）
  src/partyshiny.asm / partyshiny_crystal.asm  40（手持ちの 色ちがいの 星。共通／クリスタルの 値）
  src/hpower.asm / hpower_crystal.asm          41（めざめるパワー。共通／クリスタルの 値）
  src/dvview.asm / dvview_crystal.asm          42（個体値。金銀用／クリスタル用）
  src/enemyhp.asm / enemyhp_crystal.asm        43（相手の HP の 数字。共通／クリスタルの 値）
  src/partyitem.asm / partyitem_crystal.asm    44（手持ちの 道具の 名前。共通／クリスタルの 値）
  src/fishbite.asm / fishbite_crystal.asm      45（つりで かならず かかる。共通／クリスタルの 値）
  src/moveacc.asm / moveacc_crystal.asm        46（つかえるわざの 命中。共通／クリスタルの 値）
  src/legendrevive.asm / legendrevive_crystal.asm  47（倒した 伝説が もどる。共通／クリスタルの 値）
  src/contestpc_crystal.asm  49（むしとり大会の ポケモンを パソコンへ。クリスタル用）
  src/follow_crystal.asm   50（連れ歩き。本体）／ src/follow_talk.inc（話しかけた とき）／ src/follow_talk_data.inc（会話の 表と 文。作った もの）
  src/follow_data.inc      50 の 絵と 色の 表（作った もの）／ gfxdata/follow/（絵 278 と 一覧.csv）
  tools/follow_png2bpp.py  50 の 歩行グラフィック（png）を 2bpp に する ／ tools/follow_gen.py → src/follow_data.inc
  tools/follow_talk_gen.py 50 の 会話の 表と 文 → src/follow_talk_data.inc
  src/follow_pika.inc      50 の ピカチュウの 表情の 絵 ／ src/follow_pika_data.inc（絵の データ。作った もの）
  tools/follow_pika_capture.py・follow_pika_gen.py  50 の 表情を ピカチュウフルカラーの ROM から とる ／ データに する（gfxdata/pikapic/）
  src/rematch_johto_crystal.inc・rematch_johto_parties.inc  48（ジョウトの ジムリーダー 再戦）の クリスタルの 値・再戦用の 手持ち
  src/statsmove.asm        16（つよさをみるで わざを並べかえ。日本版クリスタルのアドレスつき）
  src/ballgfx.asm          15（投げるボールの絵。日本版クリスタルのアドレスつき）＋ ballgfx_gfx.inc・ballgfx_pals.inc
  src/learnno.asm          14（わざの上書き防止。日本版クリスタルのアドレスつき）
  src/clockopt.asm         13（せっていの とけい。日本版クリスタルのアドレスつき）
  tools/clockopt_find.py   13 で使う RestartClock の途中・ホームの処理を ROM から調べる
  gfxdata/           8 の絵と色のデータ
  tools/mkminis.py   8 のデータを Polished Crystal から作る
  tools/minipals_shiny.py  8 の minipals.bin の 色ちがいの 色を pokecrystal の shiny.pal に そろえる
                     （python3 tools/minipals_shiny.py <pokecrystal> gfxdata/minipals.bin。mkminis.py の あとに 1回）
  src/crystal_jp.inc 日本版クリスタルのアドレス一覧（英語版の逆アセンブル pret/pokecrystal と照らし合わせて調べた）
  src/charmap_jp.inc 日本版 金銀クリスタルの文字コード
  build.py           組み立て（rgbds 1.0.4 の rgbasm / rgblink -O / rgbfix）
  mkips.py           IPS パッチを作る

  組み立てかた：
    元のROMを base.gbc という名前で置き、pret/pokecrystal を pokecrystal というフォルダに置いて（または POKECRYSTAL= そのフォルダ）
      python3 tools/rematch_find.py base.gbc src/rematch_crystal.inc       … 11 のアドレス（入っているものと同じになる）
      python3 tools/wild_find.py base.gbc data/wild_crystal.txt src/wild_crystal.asm   … 12
      python3 build.py feat.gbc src/features.asm src/bugfix.asm src/minis.asm src/hmfield_crystal.asm src/fishnest_crystal.asm src/rematch_crystal.asm src/wild_crystal.asm src/clockopt.asm src/learnno.asm src/ballgfx.asm src/statsmove.asm src/redballs_crystal.asm src/picpal_crystal.asm src/fieldcolors_crystal.asm src/sigmove_crystal.asm src/safari/safari.asm src/autobox_crystal.asm src/masterball_crystal.asm src/repelask_crystal.asm src/textspeed_crystal.asm src/phonefreq_crystal.asm src/moverelearn_crystal.asm src/nesttime_crystal.asm src/daycarehint_crystal.asm src/legends_crystal.asm src/movepower_crystal.asm src/starters_crystal.asm src/itemfinder_crystal.asm src/phonemark_crystal.asm src/pokegearwhite_crystal.asm src/gearday_crystal.asm src/quickball_crystal.asm src/hearts_crystal.asm src/eggsteps_crystal.asm src/partyshiny_crystal.asm src/fishbite_crystal.asm src/hpower_crystal.asm src/dvview_crystal.asm src/enemyhp_crystal.asm src/partyitem_crystal.asm src/moveacc_crystal.asm src/legendrevive_crystal.asm src/contestpc_crystal.asm src/follow_crystal.asm                    … 通常版
      python3 build.py feat60.gbc src/features.asm src/fps60.asm src/bugfix.asm src/minis.asm src/hmfield_crystal.asm src/fishnest_crystal.asm src/rematch_crystal.asm src/wild_crystal.asm src/clockopt.asm src/learnno.asm src/ballgfx.asm src/statsmove.asm src/redballs_crystal.asm src/picpal_crystal.asm src/fieldcolors_crystal.asm src/sigmove_crystal.asm src/safari/safari.asm src/autobox_crystal.asm src/masterball_crystal.asm src/repelask_crystal.asm src/textspeed_crystal.asm src/phonefreq_crystal.asm src/moverelearn_crystal.asm src/nesttime_crystal.asm src/daycarehint_crystal.asm src/legends_crystal.asm src/movepower_crystal.asm src/starters_crystal.asm src/itemfinder_crystal.asm src/phonemark_crystal.asm src/pokegearwhite_crystal.asm src/gearday_crystal.asm src/quickball_crystal.asm src/hearts_crystal.asm src/eggsteps_crystal.asm src/partyshiny_crystal.asm src/fishbite_crystal.asm src/hpower_crystal.asm src/dvview_crystal.asm src/enemyhp_crystal.asm src/partyitem_crystal.asm src/moveacc_crystal.asm src/legendrevive_crystal.asm src/contestpc_crystal.asm src/follow_crystal.asm    … 60fps版
      python3 mkips.py base.gbc feat.gbc feat.ips

■ 追加したコード・データを置いた場所（日本版クリスタル）
  バンク$20:$5f40  Bダッシュ
  バンク$04:$7f10  スタートメニューの新しい表・パソコン、手持ちメニューの動きの表
  バンク$09:$7de0  手持ちメニューの項目の表・2列表示
  バンク$70:$4000  なまえ・わすれる の本体／ $70:$4400 ひでんわざ ／ $70:$4480 ぶんぷの釣り ／ $70:$4800 60fps
  バンク$25:$7fa0  60fps（フィールドの処理から呼ぶ所）
  バンク$00:$3f90  60fps（VBlank でもとにもどす所）
  WRAM バンク2 $df00〜  60fps の作業用、$dfb0 アイコンの種類番号
  バンク$70:$5000  ジムリーダー再戦のスクリプトとセリフ ／ $70:$6100・$6800・$7400 再戦用の手持ち・ジョウトの再戦 ／ $70:$6a00 16この バッジの あとの 四天王などの 手持ち ／ バンク$0e:$7710 再戦用の手持ちを読む入口 ／ バンク$00:$3fe0 負けたときのセリフのバンク
  バンク$39:$7e40  せっていの とけい ／ バンク$01:$7ea0 わざの上書き防止
  バンク$33:$7ee0  投げるボールの絵の処理 ／ バンク$70:$5800 ボールの絵 ／ ROM0 $0070 ボールの色
  バンク$70:$5c00  つよさをみるの並べかえ（入口は バンク$13:$7760）
  バンク$70:$5e00  ボールの印の処理 ／ バンク$0b:$7f00 手持ちの数のボールの色
  バンク$02:$7800  ずかん・パソコンの絵の色 ／ ホーム $00c0・$00f0 その入口 ／ WRAM バンク2 $dfc0・$dfc1 しまっておく種類
  バンク$01:$7f00  フィールドのボールのパレット ／ バンク$31:$7380 道具のボールの絵 ／ バンク$70:$6000 研究所のボールの絵 ／ バンク$05:$4727+ $3f の表 ／ バンク$1b:$7313 研究所の3つのボール ／ バンク$02:$7426 人の肌の色 ／ バンク$04:$62db 回復の機械の色
  バンク$10:$7e40  ルギア・ホウオウの わざの表
  バンク$74・$75   サファリゾーン（ほかに $02:$7900・$03:$7fa0・$09:$7f30・$0f:$7fb0・$13:$7800・$20:$5f60・$25:$7fb0・$28:$72e0・$32:$7dc1・$33:$7ff0・$3f:$7600・ROM0 $3fea、改良で $0b:$7e60・$0f:$7fe0・$3a:$7fc2 の空き）
  ROM0 $3f7f       サファリボールの色
  バンク$76:$4000  ボックスの 自動切りかえ（WRAM バンク2 $dfc3・$dfc4）
  バンク$76:$4200  マスターボールを 売る（ほかに $05:$5ce1 GetMart を 書きなおし）
  バンク$76:$4300  むしよけ（WRAM バンク2 $dfc5・$dfc6）／$4400 文字の 速さ／$4500 電話の 回数／$5000 技を 思い出させる 人／$5800 ぶんぷの 時間帯（WRAM バンク2 $dfc7・$dfc8）
  バンク$24        使われていない 所を 入口に：$5806（LoadPokegearRadioChannelPointer）、$6439〜（EntireFlyMap）、$6d84〜（DebugPrintSlotBias ほか）
  バンク$0a:$7e00  ぶんぷの 時間帯（草むらの 表）
  バンク$76:$6000  育て屋の 話
  バンク$77        セレビィと 伝説の 鳥（$6000 本体、$4a5f・$4b5a・$6e75 写した マップの スクリプトと イベント）／ バンク$19:$7ff8 ほこらの 入口 ／ $d836 会った しるし
  バンク$77        カントー御三家（$6200 本体、$6800 ジュンサーの 絵、$5bf6・$6bab 写した マップ、$7400・$7500 イベントの 表）／ バンク$78 クチバシティの 写し（$6e7f〜）と イベントの 表（$7400）／ $05:$4931 SPRITE $58 の 表
  バンク$02:$76e6・$7716  ポケギアの 色（色0 を 白に）
  バンク$76:$6b00  タマゴの 歩数 ／ $6c00 手持ちの 色ちがいの 星
  バンク$76:$6d00  めざめるパワー ／ $6e00・$7100 個体値・きそポイント（$13:$7780、WRAM バンク2 $dfcb）／ $6f00 相手の HP ／ $7400 手持ちの 道具（$23:$7fe0、$d832、ROM0 $1d07・$2d15）／ $7200 つかえるわざの 命中 ／ $7300 倒した 伝説が もどる ／ $7600 むしとり大会の パソコン（WRAM バンク2 $dfd0〜$dfff）
  バンク$76:$6800  ポケギアの 今日の できごと ／ $6900 前の ボール（$09:$7f50・$0f:$7fd7・$0f:$7fe8、WRAM バンク2 $dfc9・$dfca）／ $6a00 なつき度の ハート
  バンク$76:$6200  わざの 威力と 命中 ／ $6400 ダウジングマシンの 方向（$d838・$d83c）／ $6600 電話帳の 再戦の 印（入口 $24:$6460）
  バンク$0a        出現表（元の表の場所を そのまま書きかえ）
  バンク$23:$7f10  手持ちの見た目（アイコンの処理）／ バンク$71・$72 ミニアイコンの絵 ／ バンク$73 色と色の処理

■ 金銀（日本版）に移植するときのポイント
  ・処理の作りはクリスタルとほぼ同じ。英語版 金銀の逆アセンブル pret/pokegold を組み立てて、
    ラベル名 → 日本版 金銀のアドレス を探す（命令の並びで検索し、16ビットのアドレス部分は無視して照合）。
    crystal_jp.inc の各アドレスを、日本版 金銀のものに置きかえれば、asm はほぼそのまま使える。
  ・WRAM の位置は英語版と日本版でずれる（名前の長さがちがうため）。必ず日本版のコードから読み取る。
      例：wPartyMonNicknames、wStringBuffer1/2、wMonSubmenuCount など
  ・名前の長さ：日本版は ポケモン名・プレイヤー名とも 5文字＋終わり記号で 6バイト。
  ・クリスタルにある「つかえるわざ」（わざの並べかえ）は金銀の手持ちメニューにもある。
    項目の数の上限（8）を超えたら横2列にする仕組みはそのまま使える。
  ・「わすれる」の画面は ChooseMoveToDelete（わざ忘れおやじの画面）を使っている。金銀にもある。
  ・パソコンは、ポケモンセンターのパソコンのスクリプト（opentext / special PokemonCenterPC / closetext / end）を
    スタートメニューから FarQueueScript で動かしている。金銀でも同じスクリプトを探して使う。
    スクリプトの end などの命令の番号は日本版と英語版でずれていることがある（クリスタル日本版は end = $90）。
  ・スタートメニューは画面の高さで8項目まで。金銀は ポケギア・ずかん・ポケモン・リュック・主人公・レポート・せってい・とじる
    の8つなので、クリスタルと同じく「とじる」を「パソコン」に替える。
  ・ひでんマシン：基本データ（1匹32バイト）の 24〜31 バイト目が TM/HM のビット。
    HM01〜06 = 30バイト目のビット2〜7、HM07 = 31バイト目のビット0（クリスタルの31バイト目ビット1〜3は教え技）。
    金銀には教え技がないので、31バイト目のビット0だけ立てればよい。
  ・60fps：
      HandleMap の最後（NextOverworldFrame → HandleMapBackground）の HandleMapBackground を置きかえ、
      _UpdateSprites / ScrollScreen / PlaceMapNameSign のあとで、前の位置とのまん中を hSCX・hSCY・wShadowOAM に書く。
      VBlank_Normal の「wVBlankOccurred を 0 にする所」から呼ぶ処理で、まん中のままの所だけを今の値にもどす。
      ScrollScreen の直前の hVBlankCounter を覚えておき、まん中を書くまでに VBlank があったらその回は補間しない。
      WRAM バンク2 の空き（$df00〜$dfa7）を使う。金銀でも空いているか確かめること。

  ・バグ修正（bugfix.asm）：
      直し方は英語版の docs/bugs_and_glitches.md（pret/pokecrystal）と同じ。金銀は pret/pokegold の同じ名前の文書を見る。
      金銀にはクリスタルにないバグ（リフレクター・プレゼントのバグがふだんの対戦でも起きる など）や、
      クリスタルで直されているバグがあるので、金銀の文書の一覧で選び直す。
      わざの効果の並び（effectchance など）、道具のデータ（1つ7バイト）は 日本版 金銀の中で同じ並びを探して書きかえる。
      日本版はヘビーボールの作りがちがうので、金銀でも日本版のコードを見てから直すかどうか決める。

  ・手持ちの見た目（minis.asm）：
      金銀もアイコンの処理（ReadMonMenuIcon・GetIcon・InitPartyMenuIcon、スプライトアニメの UpdateAnimFrame・GetSpriteOAMAttr）は
      クリスタルとほぼ同じ。日本版 金銀でそれぞれの場所を探して置きかえる。
      アニメの構造体の VAR4 に「$80 | パレット番号」の印をつけ、1コマ作るときに wCurSpriteOAMFlags の下3ビットへ入れ、
      OAM の属性を作るときにその番号を使う（タイルの番号が 8 以上＝どうぐ・メールの印は元の色）。
      絵（gfxdata/minis.2bpp）と色（gfxdata/minipals.bin）はそのまま使える。

  ・ジムリーダー再戦（rematch.asm）：（48 から クリスタルも RM_PARTY_FAR。下の 2) の グループを 移す 作りは 使っていない）
      日本版 金銀でも tools/rematch_find.py をそのまま使う（英語版 金銀を組み立てた ROM で、8人・トレーナーの表・PrintWinLossText・
      wScriptBank が見つかり、組み立てまで通ることを確かめた）。rematch_gold.inc／rematch_silver.inc を作り、
      rematch_crystal.asm をまねて RM_SCRIPT_BANK・RM_SCRIPT_ADDR（新しいスクリプトの空き）と RM_BANK0_FREE（ROM0 の空き 9バイト）を決める。
      スクリプトの命令の番号は 英語版 金銀 ＝ 日本版クリスタル（farjumptext がない）なので、日本版 金銀も同じはず。
      ちがっていたら rematch.asm の SC_～ を 日本版 金銀の ScriptCommandTable で確かめて直す（IF !DEF で上書きできる）。
      アンズだけは 話しかけの頭が checkflag なので（applymovement のため）、新しいスクリプトの中で faceplayer・opentext をする（RM_JANINE_OPEN = 0）。
  ・殿堂入り前のポケモン（wild_find.py）：
      data/wild_gold.txt・wild_silver.txt は 英語版 金銀（pret/pokegold）の表から作った。日本版も同じ表なら そのまま使える
      （クリスタルは 英語版と日本版で 表が同じだった）。見つからないと止まるので、そのときは その表を日本版の ROM で確かめる。

  ・せっていの とけい（clockopt.asm）：
      金銀にも 時計を合わせなおす処理（UpdateTime・GetWeekday・InitTime）と 同じ作りの せってい画面がある。
      日本版 金銀の せってい画面（_Option）を見て、項目の名前・値を置く「ld hl, 画面の場所」を同じように 1行上げ、
      .Pointers の表・上下の移動・カーソルの場所を clockopt.asm と同じように置きかえる（金は clockopt_gold.asm）。

  ・わざの上書き防止（learnno.asm）：
      金銀も LearnMove・ForgetMove・YesNoBox は同じ作り。日本版 金銀で 2つの call YesNoBox と、
      YesNoBox の中の「CopyMenuHeader のあと」・YesNoMenuHeader・wMenuCursorPosition を探して置きかえる。

  ・投げるボールの絵（ballgfx.asm）：
      金銀の戦闘のアニメ（LoadBattleAnimGFX・GetBallAnimPal・BattleAnimOAMUpdate・_PlayBattleAnim）は クリスタルと同じ作り。
      日本版 金銀で それぞれの場所と、wCurItem・wBattleAnimTempPalette・BattleObjectPals を探して置きかえる。
      ボールの絵・色のデータは そのまま使える。

■ 確かめたこと（SameBoy で）
  ・Bダッシュ：歩き 1マス16フレーム → B 押しで8フレーム（自転車と同じ）
  ・パソコン：メニューから マサキのパソコン → ポケモンをつれていく などが開く
  ・なまえ：名前入力画面が出て、変えた名前が手持ちに出る
  ・わすれる：ひでんわざ（なみのり）を選んで「はい」→ 忘れた。わざが詰まり、PPも一緒に詰まる
  ・手持ちメニュー 11項目（ひでんわざ4つ）で横2列に並び、選んだ項目が正しく動く
  ・60fps：1マスの間 1ドットずつ動く。メニューを開いても画面がずれない。外・家の中・自転車の速さで確認
  ・ひでんわざ：なみのりを覚えていない手持ち（先頭はタマゴ）で水に話しかける →「なみのりを つかいますか？」→ 2匹目で なみのりできる。
    バッジがないときは今までどおり使えない
  ・ぶんぷの釣り：コイキングの「ぶんぷをみる」で、釣りの場所に青いマーク、いかりのみずうみ などは今までのマーク。点めつもする
  ・手持ちの見た目：6匹（どうぐ持ち・色ちがい・タマゴを含む）でそれぞれの絵と色が出る。入れかえ・名前入力・フィールドに戻っても色がくずれない
  ・全251匹＋タマゴのアイコンと色を 手持ちの画面で1匹ずつ表示して確かめた
  ・バトル中の手持ち・入れかえ・どうぐを使う・パソコン・ならびかえ・わざの画面・名前入力・つり・なみのり・ドアの出入りで、
    画面のくずれ・文字化け・色のくずれがないこと（WRAM バンク2 の作業用の所に ほかの処理が書いていないこと）を確かめた
  ・バグ修正版：野生のポケモンと戦って たおす・けいけんち・レベルアップ・わざを覚える・ボールを投げる まで動く
  ・ジムリーダー再戦：8人とも（カスミ・グリーンは いる状態にして）話しかけ →「はい」→ 再戦用の手持ちで戦いが始まる。
    タケシは最後まで戦って、6匹たおす → 負けたときのセリフ（新しいバンクの文）→ 賞金 → 戦いのあとのセリフ まで確かめた。
    「いいえ」→ 元の勝ったあとのセリフ。バッジがそろっていない → 元のセリフ。グレーバッジがない → 元の初めての戦い。
    アンズ（話しかけの作りがちがう）も「はい」「いいえ」の両方を確かめた
  ・殿堂入り前のポケモン：デルビル・ムウマ・ヨーギラスの「ぶんぷをみる」で ジョウトの足した場所にマークが出る
    （元のゲームでは出ない）。変えたのは 出現表の 書きかえた所だけ（ROM をくらべて確かめた）
  ・せっていの とけい：とけいの行で 左右 → ▶ が「ひる」と「せってい」を いったりきたり。
    「ひる」で A → ▷、右 → よる、右 → あさ、B → ▶ にもどる（せっていは とじない）。閉じるとフィールドの色が その時間になる。
    「せってい」で A → 曜日・時・分の画面。B で とりけし → せっていに もどる。曜日を変えて A → 「これで いいですか？」→ はい →
    「じかんを さいせってい しました！」→ せっていに もどる（とじた A で もういちど 入らない）。
    とけいで 下 → いちばん上、上 → とけい。ウインドウで B → とじる。
    タイトルの「せっていを かえる」：「とけい　▶ーー」、右・A で 何も起きない。60fps版でも同じ
  ・わざの上書き防止：レベルアップで 10まんボルトを覚えるとき A を90回連打しても わざは変わらず、2つの質問をくり返す。
    「はい」に合わせると わざを選んで覚えられる。「あきらめますか？」で「はい」だと 覚えずに終わる
  ・投げるボールの絵：野生のキャタピーに 4種類を投げて、投げる・開く・ゆれる・つかまえたあと（マスターボール）が それぞれの絵と色になる。
    レベルボールは 元のゲームと同じ画面
  ・ずつき・いわくだき：わざを覚えていない手持ちで、わざマシンを もらったフラグがあれば 使える（いちばん前のポケモン）。フラグがなければ 今までどおり使えない
  ・つよさをみるの並べかえ：でんきショック・なきごえ・10まんボルト・でんこうせっか で SELECT → A → 下下 → A →
    1つ目と3つ目が入れかわる（手持ちのデータの わざ と PP も）。B でカーソルが消えて 枠の線がもどる。
    戦闘中の つよさをみる では SELECT を押しても何も起きない（わざも変わらない）
  ・ボールの印：タケシの再戦の始まりで 相手6つ・自分の元気な2つが赤白、空きの4つは 黄色のまま（60fps版でも同じ）。
    野生のキャタピー（つかまえたことがある）で 名前の左の印が赤白。かみなり（画面が光るわざ）のあとも 色がもどる。
    ずかんの一覧の印が赤白。わざの説明・オプション・けんさく から もどっても赤白のまま。HP の枠・経験値のバーも くずれない
  ・ずかん・パソコンの絵の色：ずかんの一覧で カーソルを動かすと チコリータ・ベイリーフ・メガニウム・ヒノアラシ…が それぞれの色、
    見たことがない所は 緑の ？。説明のページ・オプション・けんさく から もどっても 同じ色。
    パソコンの あずける・つれていく で それぞれの色（色ちがいのギャラドスは赤）、タマゴは タマゴの色、やめる で 絵が消える。
    ようすを みる から もどっても 同じ色。60fps版でも同じ。
    手持ち・つよさをみる・戦闘の画面は 前の版と 同じ画面（画面写真をくらべた）
  ・フィールドの色：ウツギ研究所の机の上の3つのボールが 上が赤・下が白・黒い帯とボタン（元は オレンジ1色）。
    29ばんどうろの 道具のボール（マップに入り直して）が 上が赤・下が白で 帯なし。
    ポケモンセンターで回復：機械の上のボールが 赤と白（元は 赤とオレンジ）。
    人の肌の色（OBJ のパレットの色1）が 31,24,17。ほかの人・物の色は そのまま。60fps版でも同じ
  ・ルギア・ホウオウの 専用わざ：うずまきじまの ルギア・スズのとうの ホウオウの スクリプトを そのまま動かして、
    両方 レベル40 で出て、ルギアは エアロブラスト・しんぴのまもり・かぜおこし・じこさいせい、
    ホウオウは せいなるほのお・しんぴのまもり・かぜおこし・じこさいせい を 覚えていた。
    （レベル60 で出したときの 確かめ）レベル60 の 野生の ルギアが じこさいせい・ハイドロポンプ・あまごい・エアロブラスト、
    ホウオウが じこさいせい・だいもんじ・にほんばれ・せいなるほのお（元は かぜおこし・じこさいせい・ハイドロポンプ・あまごい）。
    レベル70 の ルギアは ハイドロポンプ・あまごい・エアロブラスト・スピードスター、レベル40 の ホウオウは せいなるほのお など 元と同じ。
    マスターボールで つかまえて「ようすを みる」で エアロブラストを 確かめた。
    エアロブラストを 覚えていない レベル59 の ルギアに ふしぎなアメ → レベル60 で「エアロブラストを おぼえたい……！」
  ・サファリゾーン：セキチクの 北の 入口 → 500円で 30こ・502歩 → ちゅうおう。スタートメニューに「502/500」「ボール 30こ」。
    草むらで サイホーン：メニュー「サファリボール×30 エサをなげる／いしをなげる にげる」。ボールは サファリボールの 絵と色で、
    「ざんねん！ ポケモンが ボールから でてしまった！」、つかまえる → 図鑑 → ニックネーム。エサ（たべてる）・いし（おこってる → にげだした）・にげる。
    歩数 0 → アナウンス → 入口「ごくろうさま」。入口に もどる →「もう おわりに する？」。
    つり：ボロ＝コイキング5（「つりあげた コイキングが とびかかってきた！」のあと サファリの 戦い）、すごい＝ミニリュウ・コイキング・つれない。
    ひがしの 段差：草むらから 上に 行けない（判定を はずした ROM では 行ける）。きゅうけいハウス 4つ・ひみつの家（棚の前は 黒くならない）。
    セキチクの 看板「めいぶつ！ サファリ ゲーム！」。ほかの 場所の ふつうの 戦いは 元のまま。60fps版でも 入口・草むら・ボールを 確かめた
    曲：サファリの中で 曲の番号 $67（バンク$75）が 鳴る。アナウンス：曲が とまり 効果音 $cf（バンク$75）が 鳴ってから「アナウンス『ピンポーン！』」。
    戦いの始まりに 手もちの ボールの 表示が 出ない（ふつうの 戦いでは 出る）。「にげだした！」の あと 相手が 右へ すべって 消える。
    あなぬけのヒモ：サファリの中 → セキチクの ポケモンセンターの前（サファリの 外の どうくつでは 元のとおり 入ってきた 入口へ）。
    ずかんの ぶんぷ（カントー）：ラッキーは セキチクシティに 印（13〜15ばんどうろ の 印は 元のまま）、ミニリュウは セキチクに 釣りの印。
    通し：入口 500円（3000円 → 2500円）・ボール 30こ・502歩 → ちゅうおう →（ひがし・きた・にし・きゅうけいハウス 4つ・ひみつの家・入口 の
      18か所の 出入りを 全部 たしかめた）。道具（きんのたま・かいふくのくすり・かくれた げんきのかけら）・看板・家の 人の 話・
      草むらの 戦い → つかまえる → ずかん → ニックネーム → マサキの ところへ・つり（つれないなー……／おっ！ ひいてる ひいてる！ → 戦い。
      サファリの 外は 元の 文）・ボックスが いっぱいの 文・出口の「もう おわりに する？」いいえ／はい・歩数 0 → ピンポーン → 入口。
      じてんしゃ：サファリの中・入口で 乗れる。テレポート・そらをとぶ：サファリの中は「ここでは つかえません」。
      エリアの さかいめの 矢印・セキチクの 入口の ドアが 正しい 絵（60fps版も）。
    じむきょくの 案内の 人：「サファリ ゾーンは いりぐち ふきんは どうぶつえんで…」。
    サファリの 戦い（草むら・つり）の 曲は MUSIC_KANTO_WILD_BATTLE（$08）（直さなくて よかった）。
    ポケギア：サファリの中で ひらくと「サファリゾーン」で 北の 点。上 → 19ばんすいどう、下 → サファリゾーン → セキチクシティ → 18ばんどうろ。
      セキチクから 上 → サファリゾーン → 19ばんすいどう、下 → サファリゾーン → セキチクシティ（60fps版も）。
    入口が INDOOR なので、入口から ちゅうおうに 入っても 地名の 看板は 出ない（地名が 同じ セキチクのため）。
    セキチクの 話：女の人「サファリ ゲーム もう やった？…」、事務所の 看板「いろんな ポケモン いっぱい！ サファリ ゾーンに ようこそ！」、
      ショップの つりびと「サファリ ゾーン！ と かかれた ペナントは ないのかね？」、えんちょうの まご 1回め（さいごが「…ちゃんと あけて
      くれてるわ！」）・2回め「サファリ ゾーンの えんちょう おとし なのに すごく げんきよ…」。
    ずかんの ぶんぷ：
      ラッキー（草むら）・ミニリュウ（つり）の サファリの 印が セキチクの 北の 点に 出る。
    レポート → つづきから：場所・歩数・ボール・サファリゲーム中（wStatusFlags2 bit1）・曲（$67）が そのまま（直さなくて よかった）。
    中で どくで 全部 たおれる → めのまえが まっしろ → サファリゲーム中の 印は 消える（ゲームが 自分で 消す）。
    入口：じてんしゃに 乗ったまま 入ると おりる。入口で 使うと「オーキドの ことば……」。
    なみのり：ちゅうおうの 池から 島に 上がって きんのたまを 拾えた。ひがしの $2e の 道（段差の 組み合わせ）には 水から 上がれない。
    時間の 色：朝 7時・昼 13時・夜 22時 で ちゅうおうの 色が かわり、家・入口の 中は かわらない（60fps版も）。
    地名の 看板：サファリの中で 看板が 出るときは「サファリゾーン」（入口が GATE だったときに 入口から ちゅうおうに 入って 確かめた。60fps版も）。
      サファリから セキチクに もどったときは 地名が 同じなので 看板は 出ない（元と 同じ）。
      ほかの 所から セキチクに 来ると「セキチクシティ」。セキチクの 入口の ドア（ブロック $80）は マップを 読みなおしても 入っている。
    ポケギア：サファリの中で「サファリゾーン」、セキチクシティでは「セキチクシティ」。60fps版でも ボール表示なし・すべる・アナウンスを 確かめた
  ・ボックスの 自動切りかえ：レポートを 書いたあと いまの ボックス1 を 30匹に → すぐに 音 →「ボックス１が いっぱいに なりました！」→
    「ボックス２に じどうで きりかえました！」→「レポートを かきました！」。パソコンの「ボックスを かえる」で いまの ボックスは ボックス2、
    ボックス1 は 30/30。ぜんぶ いっぱい → 「ぜんぶ いっぱいです！ パソコンで ボックスを せいり してください」が 1回だけ（歩いても 出ない）、
    ボックスは そのまま。レポートを 1回も 書いていないときは 何も 起きない。60fps版でも 切りかわる。
  ・マスターボール：セキエイの ポケモンセンターの 店員。博士から もらう 前は 元の 品ぞろえ（ハイパーボール・ゴールドスプレー…）。
    もらった あとは 一番 上に「マスターボール 10000円」（説明「ポケモンを かならず つかまえられる さいこうの ボール」）。
    3000円で「おかねが たりない ですよ！」、30000円で 1こ 買って 20000円・ボールの ポケットに マスターボール ×1。
    ほかの 店（セキチクの フレンドリィショップ）は 元のまま。60fps版でも 並ぶ。
  ・むしよけ：ききめが きれる →「スプレーの こうかが きれた」→「むしよけスプレーを つかいますか？」→ はい →「○○は むしよけスプレーを つかった！」、
    ききめ 100・1こ へった。いいえ → なにも しない。リュックに ない → 元の 文だけ。さいごに シルバースプレーを つかって いれば シルバースプレー（200）。
    リュックから ゴールドスプレー → 250・へる・おぼえる、ききめが のこって いる ときは 元の「まだ まえに つかった…」。
  ・文字の 速さ：右で ふつう → おそい → さいこう → はやい → ふつう（wOptions の 下の 3ビット 3・5・0・1）。さいこう で 看板・戦いの 文が 一度に 出る（60fps版も）。
  ・電話の 回数：「でんわ・ふつう　セレクトで　かえる」、SELECT で すくない → なし → ふつう（wOptions2 3・5・1）。A で かける のも 元のまま（60fps版も）。
    CheckPhoneCall の その先（$24:$4079）に すすむ 回数：ふつう 157・すくない 39・なし 0（同じ 300万命令の あいだ）。
  ・技を 思い出させる 人：おばあさんに 話す → はい → ピカチュウ → 一覧（でんきショック・なきごえ・しっぽをふる…、5つずつ・▼）→ あいて いる
    わざの 所に おぼえる。4つ ある ときは たたきつける → はい → たいあたりを わすれる →「1 2の…ポカン！」→ おぼえた → マップに もどる（60fps版も）。
    わざわすれの 人・本だなは 元のまま。
  ・ぶんぷの 時間帯：ホーホー ぜんぶ・よる に マーク、あさ・ひる なし。ポッポ ぜんぶ・あさ・ひる に マーク、よる なし（60fps版も）。
    カントーで 切りかえても カントーの まま。わくに「あさ」「ひる」「よる」。
  ・育て屋の 話：メタモン＋ポッポ（ちがう ID）→「まあまあ」・同じ ID →「あまり」、ポッポ＋ポッポ（オスと メス）ちがう ID →「とっても」・同じ ID →「なかが いい」、
    メタモン＋メタモン →「できそうに ないわい」。wStepsToEgg 20 →「そろそろ」、144 →「まだまだ」。そのあと 元の「…あんたの ○○ みてみるかね？」。
    １ぴき だけ・タマゴが ある ときは 元のまま（60fps版も）。
  ・セレビィと 伝説の 鳥：殿堂入り前 → 鳥は いない・ほこらは 元の 文。殿堂入り後 → うずまきじま 地下2階（9, 26）フリーザー（青）、
    イワヤマトンネル 地下1階（2, 10）サンダー（茶）、シロガネやま 2（8, 6）ファイヤー（赤）。はなす →「ギャーーッ！」→ Lv50 と 戦い →
    にげる → いない（$d836 の ビット）。もう一度 入っても いない。まけた とき（目の前が まっくら）は ビットは たたない。
    ほこら → 元の 文 →「…おや？ ほこらの おくから なにかが とびだしてきた！」→ セレビィ Lv30 → にげた あとは 元の 文だけ。
    森が さわがしい ときは 元の スクリプト（60fps版でも 3つの 鳥・セレビィ・まけた とき を 確かめた）。
  ・カントー御三家：ハナダの 家の 女の人（青）→「わたしは ここで きずついた ポケモンたちの せわを…」→ はい →「それじゃ おねがいします！」→
    「○○は フシギダネを てにいれた！」→ ニックネーム → 手もちに フシギダネ。もう一度 →「フシギダネ がんばってます？」。いいえ →「そう…… ざんねん です……」。
    手もちが 6ぴき →「フシギダネは マサキの ところへ てんそうされた！」。24ばんどうろの 男の人 → ヒトカゲ。クチバの ジュンサー（青い 絵）→
    オレンジバッジ あり → ゼニガメ、なし →「さいきん いたずら ばかりする ゼニガメを つかまえたの！…」だけ。
    3つの マップの もとの 人・看板（ハナダの 家の おじいさん・クチバの 看板・ジムの 看板）は 元のまま（60fps版でも 3人から もらえた）。
  ・わざの 威力と 命中：たいあたり 35/95、いあいぎり 50/95、なきごえ ー/100、そらをとぶ 70/95。カーソルで かわる（60fps版も）。
    カイリューに りゅうのいぶき「ドラゴン ×2」・サイコキネシス「エスパー ×1」・じしん「じめん ×0」・かみなり「でんき ×1」と 濁点が きえない（60fps版も）。
  ・わざの 効き目：ファイヤーに いわおとし ×4・じしん ×0・はっぱカッター ×1／4・みずでっぽう ×2、サンダーに たいあたり ×1・
    でんきショック ×1・そらをとぶ ×1／2・なきごえ（威力 0）は 出ない（60fps版も）。
  ・ダウジングマシン：シロガネやま 2 で かくれた 道具（14, 31）の 3つ 右 →「おッ！ マシンが はんのう してるぞ！…」→「どうぐは ひだりの ほうに あるみたいだ！」、
    道具の 上に 立つ →「あしもとに」、2つ 右・3つ 上 →「ひだりしたの ほうに」。道具の ない 所 →「…… ふぅ！ なにも はんのう しない」（60fps版も）。
  ・電話帳の 再戦の 印：ゴロウ（たんパンこぞう）・ミノル（つりびと）・エミ（ピクニックガール）の 再戦の フラグを たてる → その 行に「！」、
    シュウイチ・マイク・ゲンキ（たてて いない）は 出ない。スクロールしても 正しい 行に 出る（60fps版も）。
  ・ポケギアの 文字の 後ろ：時計・地図（道も 白）・電話帳・ラジオ・下の 文の わくが 白。女の子（町の 色が 青）でも 白（60fps版も）。
  ・前の ボール：まだ 使って いない → SELECT で リュック。リュックから モンスターボール → SELECT で モンスターボールを 投げる（10 → 8）。
    トレーナー戦（wBattleMode 2）では SELECT で なにも おきない（60fps版も）。
  ・なつき度の ハート：70 → ♥♥♡♡♡、140 → ♥♥♥♡♡、255 → ♥♥♥♥♥、0 → ♡♡♡♡♡。ページを かえても・つぎの ポケモンでも・手もち → マップ・
    戦闘の 中から 見て 戦闘に もどっても くずれない（60fps版も）。
  ・ポケギアの 今日の できごと：日〜土の 7つ ぜんぶ（はじめの 曜日を かえて）（60fps版も）。
  ・手持ちの アイコンの 色ちがい：ピカチュウ（オレンジ）・フシギダネ・リザードン（むらさき）・バタフリー・ルージュラ・ギャラドス（赤）が
    つよさの 画面の 色ちがいの 色と 同じ（元は ピカチュウが 青 など。60fps版も）。
  ・タマゴの 歩数：のこり 20・wStepCount $40 →「あと 4928ほ」、のこり 5 → 1088、のこり 1 → 64。タマゴの 文は 元のまま（60fps版も）。
  ・手持ちの 色ちがいの 星：色ちがいの ギャラドスの 行に ★、タマゴ・ふつうの ポケモンは なし。つよさの 画面から もどっても・戦闘の
    手持ちでも 出る。手持ちを とじると 町の タイル $5e は 元に もどる（60fps版も）。
  ・めざめるパワー：個体値 こうげき 15・ぼうぎょ 5・すばやさ 14・とくしゅ 3 →「めざパ こおり57」（PP の 行は 元のまま）。わざの ならびかえの あとも 出る（60fps版も）。
  ・個体値：3ページめで SELECT → たいりょく 13・こうげき 15・ぼうぎょ 5・とくこう 3・とくぼう 3・すばやさ 14、わくの 上に「こたいち」。
    つぎの ポケモン（色ちがいの ギャラドス 2・10・10・10・10、たいりょく 0）でも 個体値の まま。もう いちど SELECT で 元に もどる。
    2ページめの SELECT は わざの ならびかえ の まま（60fps版も）。
  ・相手の HP：コラッタ Lv30 に たいあたり → 58／58 → 50 → 43 → 35 → 28 と 数字が うごく（60fps版も）。
  ・手持ちの 道具：マスターボール・なし・クリティカッター、タマゴ と「やめる」では 出ない。メニューを とじても のこる（60fps版も）。
    メニューを ひらくと 道具の 名前は きえ（フィールドの わざの メニュー・戦闘の いれかえる の メニュー）、とじると もどる（60fps版も）。
  ・つり：いいつりざお 16回 → かかった 16回（入れる 前は 6回。60fps版は 10回 ぜんぶ）。サファリの 中の つりは 元の しくみの まま。
  ・きそポイント：HP 65535・こうげき 12345・ぼうぎょ 0・すばやさ 300・とくしゅ 1000 → そのとおりに 出る（とくこう・とくぼう は とくしゅ）。
    つぎの ポケモンでも きそポイントの まま、もう いちど SELECT で のうりょくに もどる（60fps版も）。
  ・つかえるわざの 命中：いあいぎり 95・なきごえ 100・いわおとし 90・じしん 100。カーソルで かわる（60fps版も）。
  ・倒した 伝説が もどる：ホウオウ・ルギア・スイクンの 戦った しるし、にげだした あと、ライコウ・エンテイが 0、ルギアは ずかんで つかまえた
    → LegendRevive の あと ホウオウ・スイクンの しるしが きえ、ルギアは そのまま、ライコウ（$f3 Lv40 2-5）・エンテイ（$f4 Lv40 10-4）が もどる。
    スズのとう 1かい → ライコウ・エンテイが はしりさって スイクンと 戦う。うずまきじま：しるしが ある と ルギアは いない、けすと いる（60fps版も）。
    （殿堂入りの 画面は テストで 出せないので、LegendRevive を スクリプトから 呼んで 確かめた。フックの バイトは 3e 76 21 00 73 cf）
  ・ジョウトの ジムリーダー 再戦：殿堂入りの あと 8人 とも「もう いちど しょうぶ する？」→「はい」→ Lv52〜58 の 手持ちで 戦いが 始まる。
    ハヤトは 最後まで 戦って 勝った ときの セリフ・戦いの あとの セリフ まで。「いいえ」→ 元の セリフ、殿堂入り まえ → 元の セリフ・わざマシン。
    RM_PARTY_FAR に かえた あとも カントーの 再戦は Lv66 の 手持ちで 始まる（60fps版も）。
  ・ひらく ときの 表示（Ver.1.2.1）：ずかんを ひらく とき、白い 画面の なかで 絵の 緑の 四角が 一瞬 見える ことが なくなり、
    白から いっぺんに ずかんの 画面に なる ことを 1フレームずつ 確かめた（外・家の中、通常版・60fps版）。ぶんぷから もどる ときも まっくらから
    いっぺんに もどる。ずかんの 一覧で カーソルを 動かすと 今までどおり その ポケモンの 色に なる（Ver.1.2.0 と 画面が 同じ）。
    手持ちの 画面（スタートメニュー・戦闘）を ひらく とき、アイコン・名前・「もちもの／…」が 同じ フレームで 出る ことを 確かめた。
    ならびかえ の あとの アイコンの 色、メニューを ひらいて とじた あとの「もちもの／…」、つかえるわざ・なまえの 画面の アイコンも 今までどおり。
  ・連れ歩き（50）：外・家の中・ポケモンセンター（回復）・ドア・つながり（29ばんどうろ ⇔ ヨシノシティ）・段差（46ばんどうろ）・
    なみのり（のる とき かくれ、おりると 出る）・野生の 戦い・ならびかえ（ギャラドスに かわる、色ちがいは あか）・ひんし（かくれる・回復で 出る）・
    タマゴ・アンノーン・レポートの あと つづきから・サファリの 入口で 確かめた。話しかけ：ふつう・ねむり（ねむりの アイコン）・
    29ばんどうろの チコリータ。60fps版でも 歩き・話しかけを 確かめた。主人公の 絵が こわれない ことを VRAM で 確かめた。
  ・ピカチュウの 表情（50）：ハート・ねむり（どく → なく）・なつき度 30〜230 で ピカチュウ版の 表の とおりの 表情が 出て、絵の 色が
    ピカチュウフルカラーと 同じ（しろ・オレンジ・ちゃいろ・くろ）、まわりの 地面の 色が かわらない、とじた あと 画面・人・字（メニュー）が
    もとどおり、ほかの ポケモンは 今までどおり 会話 ことを 通常版・60fps版で 確かめた。
  ・連れ歩き（50）：コガネシティ（人が 15人）でも 出る（おしえオヤジの 番号を 借りる）・コガネで 歩く・話しかける、
    Bダッシュの 間は かくれて 止まると また ついて くる（町・つながり）ことを 通常版・60fps版で 確かめた。
  ・ピカチュウの 表情（50）：とじた あと 色（wBGPals1・wBGPals2・画面）が ふつうの 会話の あとと 同じ（文の 色 7 だけ）、コガネ・キキョウ・
    エンジュ・ポケモンセンターで 絵の 色が 正しい ことを 通常版・60fps版で 確かめた。
  ・連れ歩き（50）の 色：フシギダネ・ヒトカゲ・ゼニガメ・ピカチュウ・チコリータ・ヒノアラシ・ワニノコ・ギャラドス（色ちがい）・リザードン・ゲンガー・
    カビゴン・アンノーン・タマゴ・カイリュー・バンギラスが 手持ちの アイコンと 同じ 色、マップを うつっても・手持ちの 画面の あとも そのまま、
    タンバシティ（岩あり）でも 同じ 色で 岩は ちゃの 色、アリゲイツ・ワニノコ・オーダイルが 青い ことを 通常版・60fps版で 確かめた。
  ・手持ちの アイコン（minis.asm）：ならびかえ の あと 入れかえた アイコンが 20フレーム ほど 前の 色で 見えて いたのを なおした
    （wOBPals2 にも 書くのは wBGPals2 の BG パレット0 の 色1 が 白（$7fff・$ffff）でも 黒でも ない とき。前は wBGPals1 と
    wBGPals2 の BG パレット0 が 同じ とき で、ならびかえの とき wBGPals1 だけ 一時 かわる ため 書かれなかった）。
    手持ちを ひらく ときは 今までどおり アイコンが 画面と いっしょに 出る ことを 通常版・60fps版で 確かめた。
  ・連れ歩き（50）の 色：アリゲイツ・ワニノコ・オーダイルの あご、トゲピー・トゲチック・パウワウ・ジュゴンの からだ が 白く、
    ヒトカゲ・ゼニガメ・ギャラドスの おなかが クリーム色 で 出る ことを 確かめた。
  ・連れ歩き（50）：絵と 色が 手持ちの アイコンと 同じ（アリゲイツ・トゲピー・トゲチック・パウワウ・ジュゴン・ヒトカゲ・ゼニガメ・ギャラドス
    ほか）、Bダッシュで 主人公の となりを いっしょに 走る（ふりかえった あとも）ことを 通常版・60fps版で 確かめた。
  ・連れ歩き（50）：Crystal Crunch と 同じ 絵（アイコン・下向き 反転）・色・2コマの 歩き・はねる・止まって 動く、夜も 暗く ならない、
    手持ちの SELECT で えらぶ（赤い ★、ならびかえで 追う、もう一度 で だれも 連れ歩かない）、えらんだ ポケモンの なまえで 会話、
    じてんしゃで ボールに もどる・おりると ボールから 出る、ピカチュウの 表情の 絵、Bダッシュ、コガネ ほか 町 を 通常版・60fps版で 確かめた。
