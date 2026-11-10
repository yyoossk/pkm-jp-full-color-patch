ポケットモンスター 金・銀（日本版）追加機能キット（クリスタル追加機能キットから移植）
==========================================================================

■ 銀（このキットは今 銀を作る設定になっている）
  元にしたROM：Pocket Monsters Gin (Japan) (Rev A)  CRC32 0AEA5383（後期版）
    初版（CRC32 BE1B928A）に当てても、後期版＋追加機能＋バグ修正と同じになる。
  銀を作るとき：src/version.inc を silver_jp.inc に、src/bf_version.inc に DEF SILVER を書く（今の状態）
  金を作るとき：src/version.inc を gold_jp.inc に、src/bf_version.inc を空にする
  銀で金とちがう所（tools/globalmap.py・genmap.py を銀で動かし、使っている所を全部照合して調べた）
    ・バンク$01：人の動きの判定 CanObjectMoveInDirection / WillObjectBumpIntoLand / WillObjectBumpIntoWater、
      道具のデータ（りゅうのキバ $6f41・ドラゴンのウロコ $6f72）、デイジーの毛づくろい（$7f07）が金より $3b 前
    ・バンク$11：PlayBattleMusic が $79ae（金は $79ec）
    ・バンク$39：_Option が $4a35（金は $4baf）
    ・それ以外の書きかえる所・空き領域・人の見た目のデータ（npc63.inc）は金と同じ
  パッチ後の CRC32（手持ちの見た目を入れる前）：通常版 FDEA91A0、60fps版 514FA701
  組み立てかた：後期版を base.gbc、初版を gin0.gbc として置いて
    export RGBDS=（rgbds 1.0.4 のフォルダ/） POKEGOLD=（pret/pokegold のフォルダ/）
    python3 check.py base.gbc
    python3 build.py feat.gbc src/features.asm src/bugfix.asm
    python3 build.py feat60.gbc src/features.asm src/bugfix.asm src/fps60.asm
    python3 mkips.py feat.gbc feat.ips gin0.gbc base.gbc feat60.gbc
    python3 mkips.py feat60.gbc feat60.ips gin0.gbc base.gbc feat.gbc
  SameBoy で確かめたこと（銀）：野生の戦闘（たおす・けいけんち・レベルアップ・わざを覚える・進化）、
    どく状態のポケモンを捕まえる、コインケース、せってい、Bダッシュ・パソコン・なまえ・わすれる・横2列、
    60fps（1フレーム1ドット）、初代ゲームボーイでの起動

■ 手持ちのポケモンの見た目（Polished Crystal から移植。src/minis.asm、今は銀のアドレス）
  ・アイコンを、約40種類の使い回しではなく ポケモンごとの絵（Polished Crystal のミニアイコン）にする。
    手持ち・名前入力・わざの画面・交換など、GetIconGFX でアイコンを読む所はぜんぶこの絵。
  ・手持ちの画面では、1匹ずつ専用の色（OBJ パレット2〜7）。色ちがいは色ちがいの色。どうぐ・メールの印は元の色。
  ・色ちがいの色は 金銀の 色ちがいの 色に そろえた（Polished Crystal の 色の ままだと ピカチュウが 青 など、
    つよさの 画面・戦闘の 色と ちがう ポケモンが いた）。gfxdata/minipals.bin は 金の キットと 同じ ファイル
    （銀の 色ちがいの 色は 金と 同じ。tools/minipals_shiny.py を pokegold で 動かしても 同じ ものに なる：55ひき 書きかえ）。
    SameBoy で確かめたこと（通常版・60fps版）：色ちがいの ピカチュウが 青 → オレンジ。フシギダネ・ミュウ・ホーホー・バタフリー・
    ミニリュウ・ワンリキー なども 金銀の 色ちがいの 色に なった。
  ・絵と色のデータは gfxdata/（クリスタルのキットと同じ。tools/mkminis.py で Polished Crystal から作り直せる）。
  クリスタルとちがう所
  ・金銀は 1MB で空きバンクがないので ROM を 2MB にのばし、バンク$40・$41 に絵、$42 に色と色の処理を置く。
    build.py は rgblink・rgbfix に -p 0 を渡す（ヘッダーの ROM の大きさも 2MB になる）。
    mkips.py は のばした所を RLE で書くので、IPS は 50KB ほど。当てると 2MB の ROM になる。
  ・色のデータ（wOBPals1・wOBPals2）は WRAM バンク0。種類番号は $de3c（バグ修正 $de38〜、60fps $de40〜 の間）。
  ・金銀の VBlank は、色を書くフレーム（hCGBPalUpdate）には 絵のコピー（Request2bpp）をしない。
    そのまま次のポケモンの絵を頼むとコピーが捨てられて、2匹目からフィールドの人の絵が出たので、
    1匹の色を書いたら DelayFrame で1フレーム待つ。
  ・初代ゲームボーイ・スーパーゲームボーイでは色を書かない（絵だけ変わる）。
  銀のアドレス：ReadMonMenuIcon $23:$676f、GetIconGFX の読み先 $23:$66b9、LoadMenuMonIcon の表 $23:$65bf、
    UpdateAnimFrame の call GetSpriteAnimFrame $23:$5086、GetSpriteOAMAttr $23:$5115、処理 $23:$7e00〜
    （金で作るときは、金のアドレスに合わせ直す）
  組み立てかた：
    python3 build.py feat.gbc src/features.asm src/bugfix.asm src/minis.asm
    python3 build.py feat60.gbc src/features.asm src/bugfix.asm src/fps60.asm src/minis.asm
  パッチ後の CRC32（ひでんわざを入れる前）：通常版 60CD2F82、60fps版 86DE0708
  SameBoy で確かめたこと：6匹（どうぐ・メール持ち、色ちがい、タマゴ）の絵と色、ならびかえ、
    手持ちの画面から戻る、戦闘中の手持ちの画面、60fps版、初代ゲームボーイでの起動

■ ひでんわざ（話しかけて使うもの）を、ポケモンが覚えていなくても使える（src/hmfield.asm）
  ・いあいぎり・なみのり・かいりき・うずしお・たきのぼり を、手持ちのポケモンが覚えていなくても
    フィールドで使える（バッジがないと使えないのは今までどおり）
  ・覚えているポケモンがいればそのポケモン、いなければ手持ちのいちばん前のポケモン（タマゴはとばす）が使う。
  ・ずつき・いわくだき は わざマシンなので、今までどおり覚えていないと使えない。
  ・そらをとぶ・フラッシュ は手持ちのメニューから使うわざなので、変わらない（覚えているポケモンが必要）。
  銀のアドレス：src/hmfield_silver.inc（tools/hmfield_find.py base.gbc で出した。金の後期版と同じ値）。
    新しい処理はバンク$3f $7e00〜（約70バイト）。くわしくは ひでんわざ_説明.txt。
  組み立てかた（ぜんぶ入り）：
    python3 build.py feat.gbc src/features.asm src/bugfix.asm src/minis.asm src/hmfield.asm
    python3 build.py feat60.gbc src/features.asm src/bugfix.asm src/fps60.asm src/minis.asm src/hmfield.asm
  パッチ後の CRC32（ぶんぷの釣りを入れる前）：通常版 70CE506A、60fps版 06F6D56D
  SameBoy で確かめたこと：わざを覚えていないヒノアラシで ワカバタウンの水に話しかけて なみのり、
    バッジがないと使えない、手持ちの先頭がタマゴのときは2匹目が使う、60fps版

■ ずかんの「ぶんぷをみる」に、つりざおで釣れる場所も出す（src/fishnest.asm）
  ・釣りの場所のマークは青。草むら・水の上で出る場所と同じ所は 今までのマーク（黒）。
  ・ボロ・いい・すごいつりざお、朝・昼・夜 のどれかで釣れる所に出す（ゲームのデータどおり）。
  ・白黒のゲームボーイでは、釣りの場所も今までと同じマーク。
  銀のアドレス：src/fishnest_silver.inc（tools/fishnest_find.py base.gbc で出した。金の後期版と同じ値）。
    釣りの場所の表 src/fishnest_maps.inc は、銀の英語版（pokesilver）で作り直しても同じだった。
    新しい処理はバンク$3f $7900〜（$1a2 バイト）。くわしくは ぶんぷの釣り_説明.txt。
  組み立てかた（ぜんぶ入り）：
    python3 build.py feat.gbc src/features.asm src/bugfix.asm src/minis.asm src/hmfield.asm src/fishnest.asm
    python3 build.py feat60.gbc src/features.asm src/bugfix.asm src/fps60.asm src/minis.asm src/hmfield.asm src/fishnest.asm
  パッチ後の CRC32（見直しの前）：通常版 5F3AC33D、60fps版 EDB6211E
  SameBoy で確かめたこと：コイキング（ジョウト・カントー、青と黒のマーク、点めつ、SELECT）、
    ポッポ（今までどおり）、60fps版

■ 見直しで直したこと（元の銀とくらべて、メニュー・図鑑・リュック・ポケギア・セーブ・戦闘・トレーナー戦・
  釣り・じてんしゃ・白黒・スーパーゲームボーイを SameBoy で一通り動かした）
  ・手持ちの見た目（minis.asm）：1匹ずつ色を書いたあと 1フレーム待っていたので、手持ちの画面ができる前に
    白い画面にアイコンだけが約12フレーム出ていた（戦闘中の「ポケモン」でよく見えた）。
    待つのをやめ、hCGBPalUpdate も立てない（手持ちの画面は アイコンのあとに SetDefaultBGPAndOBP で
    wOBPals1 → wOBPals2 を送るので、色はそこでまとめて出る）。
  ・色ちがいのギャラドスのアイコン：Polished Crystal は赤いギャラドスを別の姿にして色ちがいを金色にしているが、
    金銀では いかりのみずうみの赤いギャラドスが色ちがいなので、赤いギャラドス（gyarados_red）の色にした
    （gfxdata/minipals.bin。tools/mkminis.py も同じにした）。
  ・60fps（fps60.asm）：マップの新しい列を読むフレームでは、まん中の計算が1フレームに収まらず、
    じてんしゃ・Bダッシュで約16フレームごとに ゲームが1フレーム遅れて つかえていた。
    計算の前に LY を見て、FPS60_LY_LIMIT（110）より後なら そのフレームは補間しない。
    （120 まで遅れなし。110 は余裕を見た値。壁に着くまでのフレームが通常版と同じになることを確かめた）
  パッチ後の CRC32（ぜんぶ入り・見直し後）：通常版 1EDB1221、60fps版 4904C5C2

■ カントー・ジョウトのジムリーダーと再戦（src/rematch.asm・rematch_silver.asm。クリスタル追加機能キットの 11・金の 53）
  ・カントーのバッジが8つそろっているとき、カントーのジムリーダー8人に話しかけると「もういちど しょうぶ するか？」と聞かれ、
    「はい」なら 再戦用の手持ち（6匹・Lv66〜74・わざと持ち物つき）で戦える。何度でも戦える。
    「いいえ」・バッジがそろっていない・初めての戦いは 元のゲームのまま。
  ・殿堂入りの あと（EVENT_BEAT_ELITE_FOUR）、ジョウトの ジムリーダー 8人にも 話しかけると「もう いちど しょうぶ する？」、
    「はい」で Lv52〜58 の 手持ちと 何度でも 戦える（金と 同じ。src/rematch_johto_parties.inc）。「いいえ」・殿堂入り まえ・初めては 元の まま。
  ・アドレスは tools/rematch_find.py base.gbc src/rematch_silver.inc で作った（金の 新しい rematch_find.py。RM_PARTY_FAR 用の 値も 出る）。
    スクリプトの命令の番号は 日本版 銀の ScriptCommandTable（バンク$25:$6be4）で確かめた（クリスタル日本版と同じ）。
  ・ジョウトの 値（src/rematch_johto_silver.inc）：8人の「checkevent EVENT_BEAT_○○ / iftrue .FightDone」（イブキは「checkflag ライジングバッジ / iftrue」）の
    場所・イベントの 番号・とび先を 銀の ROM の バイトで 確かめ、ぜんぶ 金と 同じだった（ハヤト $22:$5cd6・アカネ $13:$4047・ツクシ $2c:$5410・
    マツバ $26:$6c69・ヤナギ $2d:$4c4d・ミカン $28:$6247・シジマ $2d:$784f・イブキ $2d:$531f）。
  ・手持ちの 読み方：金と 同じ RM_PARTY_FAR に した（前の 銀だけの RM_PARTY_HOOK は やめた）。ReadTrainerParty の ld a, [wOtherTrainerClass]
    （$0e:$5764）から バンク$0e の 空き $7fe0（23バイト）の 処理を 呼び、新しい スクリプト（バンク$43）から 呼ばれた ジムリーダーなら
    新しい バンクの 手持ちを 読む（元の TrainerType4 を そのまま 写した もの）。
  ・置いた所：カントーの スクリプトとセリフ $43:$4000、手持ちと読む処理 $43:$4800、ジョウトの スクリプトとセリフ $43:$5200、
    ジョウトの 手持ち $43:$5a00（$43:$5000〜$515c は せっていの とけい、$6000〜 は ボールの 絵）、負けたときのセリフのバンク $00:$3f8a
  ・SameBoy で確かめたこと（今の 作り。通常版・60fps版）：殿堂入り・バッジ・勝った イベントを たてて ジムリーダーの 前に 立つ
    （試す ROM だけ ジムの 1つめの ワープを ジムリーダーの 前に かえた）→ ハヤト「また きたのか！… もう いちど しょうぶ するか？」→ はい →
    ハヤトの 再戦（Lv52・52・53・53・54・56）。ツクシ・アカネ・マツバ・シジマ・ミカン・ヤナギ も Lv52〜56、イブキ は Lv54〜58 で 戦いに なる
    （ミカンは ジムに いる ように フラグを 消して 試した）。
    ハヤト「いいえ」→ 元の 勝った あとの 話。殿堂入り まえ → 元の 話。初めて（バッジの イベント なし）→ 元の 戦い（Lv7・9）。
    カントー：タケシ「はい」→ 再戦（Lv66〜70）で 前と 同じ。
  ・前の 作り（RM_PARTY_HOOK）で 確かめた こと：タケシの 再戦 → 6匹たおす → 負けたときのセリフ → 賞金 → 戦いのあとのセリフ → もう一度話しかけると
    また聞かれる。「いいえ」・バッジがそろっていない・グレーバッジがない は 元どおり。アンズ も 確かめた。

■ 殿堂入りの前に、カントー・シロガネやまのポケモンを出す（data/wild_silver.txt → src/wild_silver.asm。キットの 12）
  ・python3 tools/wild_find.py base.gbc data/wild_silver.txt src/wild_silver.asm
  ・出現表のうち、45ばんどうろ（ROUTE_45）だけは 日本版 銀の表が英語版とちがっていた
    （英語版のゴマゾウ $e7 の所が 日本版はヒメグマ $d8）。日本版の ROM で調べ直して、元の表を日本版のものにした
    （足すのは 前と同じ 夜のカビゴン）。
  ・カラカラ（つながりのどうくつB1F）・ニューラ（こおりのぬけみちB1F 夜）も足す。ブーバーは もとから出るので足さない。
  ・もとから出るポケモンは 時間帯ごとに1匹も消えていない（表をくらべて確かめた）。
  ・SameBoy で確かめたこと：ピッピ・カラカラ・カビゴン・ニューラ・デルビル・ヨーギラスの「ぶんぷをみる」（夜）で、
    足した場所にマークが出る（元の銀では出ない）。
  組み立てかた（ぜんぶ入り）：
    python3 tools/rematch_find.py base.gbc src/rematch_silver.inc
    python3 tools/wild_find.py base.gbc data/wild_silver.txt src/wild_silver.asm
    python3 build.py feat.gbc src/features.asm src/bugfix.asm src/minis.asm src/hmfield.asm src/fishnest.asm src/rematch_silver.asm src/wild_silver.asm
    python3 build.py feat60.gbc src/features.asm src/bugfix.asm src/fps60.asm src/minis.asm src/hmfield.asm src/fishnest.asm src/rematch_silver.asm src/wild_silver.asm
    python3 mkips.py feat.gbc feat.ips gin0.gbc base.gbc
    python3 mkips.py feat60.gbc feat60.ips gin0.gbc base.gbc
  パッチ後の CRC32（再戦・殿堂入り前のポケモン入り）：通常版 2BFD68CB、60fps版 A1055765

■ せっていに「とけい」（src/clockopt.asm。クリスタル追加機能キットの 13）
  ・せっていの「ウインドウ」の下に「とけい」を出す。左右で あさ（4:00）・ひる（10:00）・よる（18:00）に時計を合わせる
    （曜日はそのまま、分・秒は 0。合わせ方は「時計を合わせなおす」と同じ UpdateTime → GetWeekday → wStringBuffer2 → InitTime）。
    せっていを閉じると フィールドの色も その時間になる。
  ・タイトルの「せっていを かえる」（wMapGroup = 0）では「ーー」を出して変えられない。
  ・今までの項目を1行ずつ上げ、「とけい」を15行目、「おわり」を16行目に出す。銀の せってい の項目は クリスタルと同じ8つ
    （OPT_CLOCK = 7、OPT_CANCEL = 8）。
  ・銀の せってい（_Option）はバンク$39:$4a35。項目の文字を置く「ld hl, 画面の場所」10か所・上下の移動・カーソルの場所・
    開いたときの UpdateFrame の所を、日本版 銀のコードで調べて置きかえた。
  ・バンク$39 の空きが 23バイトしかないので、本体はバンク$43:$5000 に置き、バンク$39 からは farcall で呼ぶ：
      GetOptionPointer（$4ae6）：7 = とけい は $7fe9 の farcall へ、8 = おわり は 7（元の Options_Cancel）にして元の表を引く（$7ff0）。
      カーソルの場所（$4d87〜）：farcall に置きかえ、あいた所に 開いたときの farcall（UpdateFrame もそこから farcall で呼ぶ）。
  ・SameBoy で確かめたこと：ワカバタウンの外（夜）で とけいを あさ → ひる → よる にすると、時間帯（wTimeOfDay） と
    フィールドの色が 朝・昼・夜に変わる（通常版・60fps版）。カーソルは とけい → おわり → いちばん上 と回り、上へも回る。
    タイトルの「せっていを かえる」では「ーー」のまま 左右を押しても変わらず、そのあと「つづきから」も ふつうに始まる。
  組み立てかた（ぜんぶ入り）：上の build.py の行の最後に src/clockopt.asm を足す
    python3 build.py feat.gbc src/features.asm src/bugfix.asm src/minis.asm src/hmfield.asm src/fishnest.asm src/rematch_silver.asm src/wild_silver.asm src/clockopt.asm
    python3 build.py feat60.gbc src/features.asm src/bugfix.asm src/fps60.asm src/minis.asm src/hmfield.asm src/fishnest.asm src/rematch_silver.asm src/wild_silver.asm src/clockopt.asm
  パッチ後の CRC32（とけい入り）：通常版 A3A6259B、60fps版 85D9F498
  ★ 操作を 金と同じに変えた（せっていのとけいの操作。src/clockopt.asm を 金の src/clockopt_gold.asm のアドレスを銀にしたものに 置きかえた）
  ・「おわり」は なくした（B・START で とじる）。とけいの行は「とけい　▶ひる　 せってい」。左右で「ひる」か「せってい」を選ぶ。
    「ひる」で A → ▷ になり 左右で あさ・ひる・よる。A・B で ▶ にもどる。「せってい」で A → 曜日・時・分を合わせる画面
    （RestartClock の途中 $08:$4027 から。「くるっているかも」の文はとばす）。いちばん下は とけい（下の cp 7、上の回りこみ 8）。
  ・銀のアドレス：GetOptionPointer $4ae6（頭の 3バイトを jp OptionsDispatch）、OptionsDispatch $39:$7fe9、
    Options_UpdateCursorPosition $4d79、.DownPressed $4d57、.UpPressed $4d74、おわりの文字 $4ade、開いたとき $4a70、UpdateFrame $4d2f、
    新しい処理 $43:$5000。tools/clockopt_find.py で JoyTextDelay $09fd・GetJoypad $0934・hJoyDown $ffaa・
    WaitBGMap $33ae・DelayFrame $032e を出し、WaitBGMap・DelayFrame（候補が いくつかある）は 銀のシンボルと合っていることを確かめた。
    wClockSub（とけいの行で選んでいる所）は 使われていない WRAM $dee8（$de37 は ずかんの絵の色、$de40〜$dee7 は 60fps）。
  ・SameBoy で確かめたこと（通常版・60fps版）：左右で ▶ が「あさ／ひる／よる」と「せってい」を行き来する。A → ▷、右 → ひる → よる、
    B → ▶ にもどる（とじない）。「せってい」で A → 曜日・時・分の画面、B で とりけし → もどる、A → はい →「さいせってい しました」→ もどる。
    とけいで 下 → いちばん上、上 → とけい、B・START で とじる。ほかの項目（はなしの はやさ・ウインドウ・メニューせつめい）も 左右で変わる。
    ゲームを始める前は「とけい　▶ーー」で、右・A で 何も起きない。

■ わざを覚えるとき A ボタンの連打で わざを上書きしない（src/learnno.asm。クリスタル追加機能キットの 14）
  ・レベルアップ・わざマシンで わざを覚えるときの「ほかの わざを わすれさせますか？」と「おぼえるのを あきらめますか？」の
    「はい／いいえ」を はじめから「いいえ」にする。A を連打しても 2つの質問をくり返すだけで、わざは変わらない。
  ・日本版 銀のアドレス：ForgetMove の call YesNoBox $01:$6880、LearnMove.cancel の call YesNoBox $01:$6861、
    YesNoMenuHeader $1c34、CopyMenuHeader $1b60、_YesNoBox の pop bc のあと $1c00、wMenuCursorPosition $cef3。
    新しい処理（YesNoBox_DefaultNo）は バンク$01:$7fb0。
  ・SameBoy で確かめたこと（通常版・60fps版）：4つわざを持ったピカチュウに わざマシン01 を使い、A を連打 → 2つの質問をくり返し、
    わざもわざマシンも変わらない。「わすれさせますか？」で「はい」→ わざを選んで ばくれつパンチを覚えた。
    「あきらめますか？」で「はい」→「おぼえずに おわった」で わざもわざマシンもそのまま。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/learnno.asm を足す
    python3 build.py feat.gbc src/features.asm src/bugfix.asm src/minis.asm src/hmfield.asm src/fishnest.asm src/rematch_silver.asm src/wild_silver.asm src/clockopt.asm src/learnno.asm
    python3 build.py feat60.gbc src/features.asm src/bugfix.asm src/fps60.asm src/minis.asm src/hmfield.asm src/fishnest.asm src/rematch_silver.asm src/wild_silver.asm src/clockopt.asm src/learnno.asm
  パッチ後の CRC32（わざの上書き防止入り）：通常版 2BC2262C、60fps版 93061329

■ 戦闘で投げるボールを それぞれの絵・色にする（src/ballgfx.asm。クリスタル追加機能キットの 15）
  ・ピカチュウ版フルカラー（クリスタル）と同じ絵と色：マスター＝むらさきに M、ハイパー＝黒に 黄色の H、
    スーパー＝青に 赤い もよう、モンスター＝赤。投げる・あたって開く・ゆれる・つかまえたあと残るボール・
    トレーナーにはじかれる の全部で その絵になる。ほかのボール（ぼんぐりのボールなど）は元のまま。
  ・1つのボールで色を2つ使う（上半分・下半分）。GetBallAnimPal で src/ballgfx_pals.inc の色を wOBPals1・wOBPals2 の
    パレット5（みどり）・6（あお）に入れ、ボールのパレットを 5 | $80（印）にする。BattleAnimOAMUpdate の属性を作る所で
    印があれば 上の段 = 5、下の段・開いたボール = 6（閉じたボールの右半分は 反転せずに 9・10番目のタイル）。
    PlayBattleAnim の はじめの call BattleAnimAssignPals の前に パレット5・6 を BattleObjectPals の元の色にもどす。
  ・銀のボールのアニメにも みどり・あお を使う物はない（けむり＝グレー、マスターボールのキラキラ＝ちゃいろ。
    銀の BattleAnim_ThrowPokeBall とアニメの物の表で確かめ、画面でも確かめた）。
  ・日本版 銀のアドレス（バンク$33）：LoadBattleAnimGFX の call DecompressRequest2bpp $6772、GetBallAnimPal $516c
    （BallColors $5185）、属性を作る所 $49ca、PlayBattleAnim の call BattleAnimAssignPals $40ed（BattleAnimAssignPals $47f7）。
    wCurItem $cffc、wBattleAnimTempPalette $ca21、wOBPals1 $c240・wOBPals2 $c2c0（WRAM バンク0 なので バンクの切りかえはいらない）、
    BattleObjectPals $02:$5b9f。新しい処理は $33:$7e40、絵は $43:$6000（gfxdata/balls_crystal.2bpp、圧縮なし、Request2bpp で読む）。
  ・SameBoy で確かめたこと（通常版・60fps版）：野生のコイキングに 4種類を投げ、モンスター＝赤、スーパー＝青に赤い もよう、
    ハイパー＝黒に黄色の H、マスター＝むらさき・ピンク、ヘビーボールは元のまま。トレーナーにはじかれるボールも その絵。
    はじかれたあと はっぱカッター（みどり）・みずでっぽう（あお）の色が 元の銀と同じ（パレット5・6 も元の色にもどっている）。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/ballgfx.asm を足す
  パッチ後の CRC32（ボールの絵・色入り）：通常版 AA2B4FD9、60fps版 F4E665C6

■ ずつき・いわくだきも 覚えていなくても使える（src/hmfield.asm。金のキットと同じ）
  ・ずつき（木をゆらす）・いわくだき（岩をくだく）も、その わざマシンを もらったあと（EVENT_GOT_TM02_HEADBUTT = $5f・
    EVENT_GOT_TM08_ROCK_SMASH = $4b。日本版 銀の setevent で確かめた）なら、覚えているポケモンがいなくても いちばん前のポケモンが使う。
    もらう前は 今までどおり 覚えていないと使えない（わざマシンは使うとなくなるので、リュックではなく もらったフラグで決める）。
  ・SameBoy で確かめたこと：わざを覚えていないピカチュウ1匹で、29ばんどうろの木・タンバシティの岩に話しかける。
    フラグあり →「ずつきを つかいますか？」→「ピカチュウは ずつきを つかった！」、いわくだきも 岩がくだける。
    フラグなし → 元のまま（木は何も起きない、岩は「かたそうな いわ だけど……」）。

■ 「つよさをみる」の わざのページ（2ページ目）で わざを並べかえる（src/statsmove.asm。金のキットと同じ）
  ・SELECT で始める → 上下で ▶ を動かし、A で選ぶ（▷ が残る）→ もういちど A で入れかえ（わざと PP がいっしょに動く）。
    同じわざで A・B・SELECT は 選ぶのをやめる。選んでいないときの B・SELECT で おわり。
  ・手持ちのポケモンだけ（ボックス・相手・タマゴは できない）。わざが1つのときと、戦闘中は できない。
  ・アドレスは 金と同じ（StatsScreen_LoadPage.joypad_action $14:$4d06、入口 $14:$7fe2、本体 $3f:$6e00、LoadGreenPage $14:$501a）。
    作業用の WRAM は、銀は $de3c を 手持ちの見た目で使っているので $de3b・$de3d・$de3e にした（金は $de3b〜$de3d）。
  ・SameBoy で確かめたこと：でんきショック・なきごえ・10まんボルト・でんこうせっか で SELECT → A → 下下 → A → 1つ目と3つ目が入れかわる
    （手持ちのデータの わざ と PP も）。ページを変えても 入れかえた順番のまま。戦闘中の つよさをみる では SELECT を押しても何も起きない。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/statsmove.asm を足す
  パッチ後の CRC32（ずつき・いわくだき、つよさをみるの並べかえ入り）：通常版 F2771F4B、60fps版 A7039092

■ ボールの印を赤白に（src/redballs.asm。金銀クリスタル共通。銀の値は src/redballs_silver.inc）
  ・トレーナー戦の 手持ちの数のボール（元気なポケモンのボールだけ）、野生のポケモンとの戦闘の つかまえた印、
    ずかんの一覧の つかまえた印 を、モンスターボールの赤と白にする。状態異常・ひんし・空きのボールは 元のまま黄色。
  ・アドレスは tools/redballs_find.py で 銀の ROM から出した値（金と同じだった）。
    空きは RB_HUD_FREE = $0b:$7c80（10バイト）、RB_BANK・RB_ADDR = $3f:$6f40（statsmove $3f:$6e00-$6f28 のうしろ）。
  ・src/redballs_silver.asm が src/redballs_silver.inc → src/redballs.asm の順に読みこむ。
  ・SameBoy で確かめたこと：トレーナー戦の始まりで 元気のボールが赤白、ひんし（×）・空きは黄色のまま。
    つかまえたことのあるポケモン（コイキング）との野生の戦闘で 名前の左の印が赤白、わざのアニメと HP が減ったあとも赤白のまま。
    ずかんの一覧の印が赤白、オプション（SELECT）からもどったあとも赤白。投げるボールの絵・色は 前と同じ。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/redballs_silver.asm を足す
  パッチ後の CRC32（ボールの印を赤白に 入り）：通常版 C8FE306B、60fps版 65E216D8

■ ずかんとパソコンの絵をカラフルに（src/picpal.asm。金銀クリスタル共通。銀の値は src/picpal_silver.inc）
  ・ずかんの一覧（緑1色）と パソコンで ポケモンを選ぶ画面（オレンジ1色）の ポケモンの絵を、手持ちと同じように
    白い背景に そのポケモンの色（色ちがいも）で出す。見たことがないポケモンの ？ は 緑のまま。白黒のゲームボーイでは 今までと同じ。
  ・アドレスは tools/picpal_find.py で 銀の ROM から出した値（金と同じだった）。空きは
    PP_CGB_FREE = $02:$7c00、PP_HOME_DEX = $00:$3fe0、PP_HOME_PC = $00:$3f94、WRAM は $de37・$de3f。
    ホームの空きが足りないので、再戦の「負けたときのセリフのバンク」（RM_BANK0_FREE）を $3fe0 から $3f8a へうつした。
  ・src/picpal_silver.asm が src/picpal_silver.inc → src/picpal.asm の順に読みこむ。
  ・SameBoy で確かめたこと：ずかんの一覧で カーソルを動かすと そのポケモンの色になる（見ただけのベイリーフも色つき、見ていない所は 緑の ？）。
    説明のページ・オプション・けんさく から もどっても 同じ色。パソコンの あずける・つれていく で それぞれの色、
    色ちがいのギャラドスは 赤、「やめる」では 絵が消える、ようすをみる から もどっても 同じ色。
    戦闘・ボールの印・手持ち・白黒／スーパーゲームボーイの ずかんは 前と同じ。タケシとの再戦で 負けたときのセリフも 前と同じ。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/picpal_silver.asm を足す

■ フィールドのボール・回復の機械・肌の色（src/fieldcolors.asm。金銀クリスタル共通。銀の値は src/fieldcolors_silver.inc）
  ・フィールドの道具のボール（SPRITE_POKE_BALL）は ピカチュウ版の道具のボールと同じ（上が赤・下が白。黒い帯はない）。
  ・ウツギ研究所の机の上の3つのボールだけ、使われていない SPRITE_UNUSED_GUY（$3f）を 研究所のボールの絵
    （黒い帯とボタンのあるモンスターボール）にして、3つの object_event のスプライトを $3f にした。
    どちらも 下の2枚だけ PAL_OW_EMOTE にして 下を白にする。
  ・ポケモンセンターの回復の機械の上のボールを赤と白にする。フィールドの人の肌の色を 31,19,10 → 31,24,17 にする。
  ・アドレスは tools/fieldcolors_find.py で パッチを入れる前の 銀の ROM から出した値（金と同じだった）。
    FC_FREE = $01:$7fc8（50バイト。$7fb0〜$7fc2 は わざの上書き防止）、FC_LABGFX = $3f:$7f00（64バイト。$3f:$7e00〜$7e73 は ひでんわざ）。
  ・src/fieldcolors_silver.asm が src/fieldcolors_silver.inc → src/fieldcolors.asm の順に読みこむ。
  ・SameBoy で確かめたこと：研究所の3つのボールが 赤・黒い帯とボタン・白。話しかけると 元のとおり ヒノアラシを選べて、選んだボールは消える。
    道具のボール（グループ25・3番のマップ）は 上が赤・下が白で帯なし、外に出て入り直しても同じ。
    ポケモンセンターで回復すると 機械の上のボールが赤と白（光る線は白）。ジョーイさん・研究所の助手・主人公の肌が薄い肌色。
    ほかの人の色・草むらで足がかくれるのは 前と同じ。通常版・60fps版とも同じ。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/fieldcolors_silver.asm を足す

■ ルギア・ホウオウの専用わざ（src/sigmove.asm。金銀クリスタル共通。銀の値は src/sigmove_silver.inc）
  ・ルギア・ホウオウは 両方 レベル40 で出てきて、専用わざ（エアロブラスト・せいなるほのお）を 覚えている。
    （銀は ルギアが 40、ホウオウが 70 だった。レベル70 だと 専用わざは 押し出されて 覚えていなかった）
  ・レベルアップで覚える わざの表に「レベル60 で 専用わざ」を足した。もう つかまえている ルギア・ホウオウも レベル60 で 覚えられる。
  ・アドレスは tools/sigmove_find.py で パッチを入れる前の 銀の ROM から出した値：EvosAttacksPointers の ルギア $10:$6b4f・ホウオウ $10:$6b51。
    出てくるときの レベルの所は 金と銀の両方の 行がある（checkver で分かれている）ので、銀が通る所を選んだ：
    ルギア $2d:$4536（元から 40）、ホウオウ $29:$6e52（70 → 40）。
  ・バンク$10 は おわりに 6バイトしか空きがない。元の ルギア（$7fba）・ホウオウ（$7fd0）・セレビィ（$7fe6）の表と おわりの空きは
    つながっている（$7fba〜$7fff の 70バイト）ので、新しい ルギア・ホウオウの表（48バイト）を $7fba から置き、
    セレビィの表（中身は そのまま 20バイト）を $7fea に うつして、3つの ポインタを 書きかえた（src/sigmove_silver.asm）。
  ・SameBoy で確かめたこと：うずまきじまの ルギア・スズのとうの ホウオウの スクリプトを そのまま動かして 両方 レベル40。
    ルギア：エアロブラスト・しんぴのまもり・かぜおこし・じこさいせい、ホウオウ：せいなるほのお・しんぴのまもり・かぜおこし・じこさいせい
    （元の銀の ホウオウは レベル70：じこさいせい・だいもんじ・にほんばれ・スピードスター）。
    レベル59 の ルギア・ホウオウ（専用わざなし）に ふしぎなアメ → レベル60 で「あたらしく エアロブラスト（せいなるほのお）を おぼえた！」。
    わざが 4つのときは「おぼえたい……！」から いつもの わすれる画面（わざの上書き防止で いいえ が先）。
    もう 覚えているときは 何も出ない。元のゲームでは 何も覚えない。通常版・60fps版とも同じ。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/sigmove_silver.asm を足す

■ サファリゾーン（ピカチュウ版フルカラーパッチと同じ。src/safari/safari_silver.asm。金の src/safari/safari.asm を銀にしたもの）
  ・セキチクシティの 北の 入口から 入れる。入口・ちゅうおう・ひがし・きた・にし・きゅうけいハウス 4つ・ひみつの家 の 10マップ。
    遊び方・出るポケモン・つり・戦い（ボール・エサ・いし・にげる）は 金と同じ（くわしくは サファリゾーン_説明.txt）。
  ・銀のアドレス：src/jp_all_silver.inc（英語版 pokesilver のラベル → 日本版 銀のアドレス。金の src/jp_all.inc と同じ形）を作った。
    金と銀の アドレスは、サファリで使う バンク（$00・$02・$03・$04・$09・$0f・$25・$32・$33・$36・$3f）では 同じ。
    フックの所の 元の命令（ld a, [wLinkMode]・call CheckWildEncounterCooldown・cp BATTLETYPE_DEBUG・ld a, [wTilePermissions] など）が
    銀の ROM でも 同じことを 確かめた。tools/safari_gen.py の 出力も 金と同じ（銀の タイルセットの表 $05:$562b も 同じ）。
  ・銀で 変えた所：
    - マップ・スクリプト・文章は バンク$44、タイルセット・ブロックは バンク$45（銀は $43 を 再戦・とけい・ボールの絵で 使っている）。
    - えさ・いしの アニメの部品の表は $33:$7fc0（銀は $33:$7e40〜 に 投げるボールの絵の処理）。
    - 投げるボール：銀は ballgfx.asm（クリスタル追加機能キットの移植）なので、そこに 5つめの サファリボール（wCurItem = $b3）を足した
      （絵は gfxdata/pikaballs.2bpp の5つめ、色は gfxdata/pikaballs.pal の5つめ。金の tools/pikaballs_make.py で 作ったもの）。
    - セキチクシティの マップの 北の入口の かべ（ブロック$7d、$2a:$65f1 の x9・y1）を ドアのブロック$80 にした
      （金の zip には この所がなく、ドアが 出なかった・入れなかった）。
    - 空きは どこも 銀の ROM で 0 なのを確かめ、ほかのパッチと 重ならない（.map で確かめた）。
  ・SameBoy で確かめたこと（通常版・60fps版）：
    セキチクの ドア・看板（めいぶつ！ サファリ ゲーム！）→ 入口で 500円 → ボール30こ・502歩 → ちゅうおうへ。スタートメニューに「502/500」「ボール 30こ」。
    草むらで サファリの戦い：ボール（サファリボールの絵・色、はずれる／ゆれて でる／つかまえる → ニックネーム）、エサ（たべてる）、
    いし（おこってる）、にげだす、にげる（うまく にげきれた！）。最後の ボール → アナウンス → 入口。歩数 0 → アナウンス → 入口。
    入口に もどる →「もう おわりに する？」。つり：ボロ＝コイキング5、いい＝トサキント／ニョロモ10・つれないことも、すごい＝コイキングなど。
    きゅうけいハウス 4つ・ひみつの家・ひがし・きた・にし の 絵。ふつうの戦いの 投げるボールは 前と同じ（前の ROM と 画面が 同じ）。
    （ひがしの 段差の 組み合わせは 金で 確かめたものと 同じ処理で、銀では 歩いて 試していない）
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/safari/safari_silver.asm を足す（60fps版も同じ）
  ★ 改良（金の 新しい版に合わせた。src/safari/safari_silver.asm に 同じ 変更を 入れた）
  ・中の 曲：ピカチュウ版の サファリゾーンの 曲（MUSIC_SAFARI_ZONE_PK = $5d。_PlayMusic の ld hl, Music $3a:$4b39 を call に、表 $3a:$7fb7）。
  ・アナウンスの 音：ピカチュウ版の SFX_Safari_Zone_PA（SFX_SAFARI_ZONE_PA = $bc。_PlaySFX の ld hl, SFX $3a:$4c78 を call に、表 $3a:$7fc8）。
    曲・音の データは バンク$45（$7900・$7a00）。
  ・戦いの 始まりに 手もちの ボールを 出さない（BattleStart_TrainerHuds $0b:$50e4 → $0b:$7d00）。
  ・にげだした ポケモンが 右へ すべって 消える（SlideBattlePicOut $0f:$534a を $0f:$7fc0 から 呼ぶ）。
  ・あなぬけのヒモ・あなをほる：サファリゲーム中は さいごの ポケモンセンターの 前へ（farscall Script_AbortBugContest $03:$4d5c を かえる）。
  ・ずかんの ぶんぷ（カントー）：サファリの ポケモンを セキチクシティに（src/fishnest.asm を 金の 新しい版に。src/safari/safari_nest.inc は safari_gen.py が 作る）。
  ・ポケギアの 地図：サファリの中は「サファリゾーン」（farcall GetLandmarkName $24:$501d を かえる）。
  ・どの アドレスも 銀の シンボルで 金と同じことを確かめた（Music $3a:$506e・SFX $3a:$525e・SlideBattlePicOut・GetLandmarkName $24:$6498・
    Script_AbortBugContest $04:$64e8）。フックの 元の命令も 同じ。空きは どこも 0。
  ・SameBoy で確かめたこと（通常版・60fps版）：サファリの中で 曲の番号 $5d。歩数 0 → 曲が とまって 630Hz・510Hz の 音 →「アナウンス『ピンポーン！」。
    戦いの 始まりに 手もちの ボールなし（トレーナー戦の ボールは 前と同じ）。にげだした モンジャラが 右へ すべって 消える。
    あなぬけのヒモ → セキチクの ポケモンセンターの 前、サファリゲームは おわり（スタートメニューの 歩数も 消える）。
    ずかんの ぶんぷ（カントー）：ラッキー → セキチクに マーク、ミニリュウ → セキチクに 青い マーク。
    ポケギアの 地図：サファリの中「サファリゾーン」、セキチクシティでは「セキチクシティ」。
  ・地名の 看板（PlaceMapNameSign）：金銀には マップに 入ったときの 地名の 看板が ない（クリスタルで 足されたもの）ので、銀では 直す所はない。
    （英語版 pokegold にも PlaceMapNameSign は なく、銀の ROM の GetLandmarkName を 呼ぶ所は ポケギア・ラジオ・電話・
    スクリプトの getcurlandmarkname だけ）。ポケギアの 地図は サファリの中（ちゅうおう・きゅうけいハウス）で「サファリゾーン」、
    入口・セキチクシティで「セキチクシティ」（通常版・60fps版で 確かめた）。
  ・つりの 文（サファリの中だけ ピカチュウ版）：つれない「つれないなー……」、つれた「おっ！ ひいてる ひいてる！」。
    Script_NotEvenANibble $03:$5299（writetext RodNothingText $5329 / sjump の 6バイト）→ farsjump SafariFishNibbleScript、
    Script_NotEvenANibble2 $03:$52a2 → sjump $5299、Script_GotABite の writetext RodBiteText $03:$52c6 から → farsjump SafariFishBiteScript
    （PutTheRodAway $03:$530b）。銀の ROM の バイトで 金と 同じことを 確かめた。サファリの外の つりは 元の文（つれないなあ……／お！ ひいてる！ひいてる！）。
  ・ボックスが いっぱい：ピカチュウ版の「ボックスに あずけている ポケモンが いっぱいなので つかえません！」。ボールは へらない。
    くらべる数は 30（日本版。MONS_PER_BOX = 20 は 使わない）。銀の ほかの 所（ボックスの自動切りかえ など）も 30。
  ・じてんしゃ・テレポート（確かめただけ）：サファリの 外の マップ（CAVE）で じてんしゃに 乗れる、そらをとぶ・テレポートは「ここでは つかえません」。
    入口（GATE）でも じてんしゃに 乗れる（金銀の しくみ）。
  ・時間で 色を かえる（外の 4つ だけ）：safari_header に パレットの 引数（外の 4つ PALETTE_AUTO、ほかは PALETTE_DAY）。
    SafariMapPals で wTimeOfDayPal（銀も $d55b）& 3 → 朝 .morn・昼 .outdoor・夜 .nite（表は 金の 値）。家の中・入口は いつも 同じ。
  ・入口の 見出しの 環境を GATE → INDOOR（じてんしゃで 入ると おりる、入口で 使うと「オーキドの ことば…」）。
  ・SameBoy で確かめたこと（通常版・60fps版）：
    朝 7時・昼 13時・夜 22時 で ちゅうおうの 色が かわる（入口・きゅうけいハウスは かわらない）。
    ちゅうおうで レポート →（リセット）→ つづきから：場所・歩数（300）・ボール（25）・サファリゲーム中・曲（$5d）が もどり、歩くと 歩数が へる。
    手もちを ぜんぶ どく・HP 1 に して 歩く → ちからつきた → めのまえが まっしろ → サファリゲームの しるしが 消える（家へ）。
    セキチクから じてんしゃで 入口に 入ると おりる。入口で じてんしゃを 使うと「オーキドの ことば……」。
    なみのり：ちゅうおうの 池から 島に 上がれる（きんのたまも とれた）。島の 上の ふちから 水へは 歩いて 出られない
    （ふちで A →「なみのりを つかいますか？」→ はい なら 水に 出られる。出られないと 島から もどれないので これで よい）。
  ・セキチクの「サファリゾーンが しまっている」話を かえた（金と同じ）。日本版 銀にも text_far（$16）は ない（金と同じ）。
    元より 短い 3つは 元の 場所に ピカチュウ版の 文（safari_gen.py の INPLACE。銀の 場所も 金と同じ $36:$70e1・$36:$7155・$2d:$5d48）。
    えんちょうの まごは スクリプトの 頭 $2d:$63b3（faceplayer / opentext / checkevent $00d9 … 金と同じ）を farsjump SafariGranddaughterScript に。
  ・ポケギアの 地図・ずかんの ぶんぷ：サファリを セキチクの 北の 点（x 100・y 120。銀の Landmarks $24:$64b6 の セキチクは x 100・y 132）に。
    GetLandmarkCoords $24:$6489 → jp SafariLandmarkCoords（$24:$7f40）。fishnest.asm の FISHNEST_EXTRA_LANDMARK = $5f。
  ・SameBoy で確かめたこと：女の人「サファリ ゲーム もう やった？ あそこでしか とれない めずらしい ポケモンも いるよ！」、
    ショップの つりびと「サファリ ゾーン！ と かかれた ペナントは ないのかね？ ちょうちんは？ カレンダーも ないのか！」、
    まご 1回め（さいごの 段が「サファリゾーンは かかりの ひとたちが ちゃんと あけて くれてるわ！」）、
    2回め「サファリ ゾーンの えんちょう おとし なのに すごく げんきよ でも……」。
    ポケギア：ちゅうおうでは セキチクの 北の 点に 自分の アイコン・「サファリゾーン」、入口・セキチクでは セキチクの 点。
    ずかんの ぶんぷ（カントー）：ラッキー・ミニリュウ（つり）の サファリの マークが セキチクの 北の 点に。
  ・セキチクの サファリゾーン じむきょく（銀も 中に だれも いない。(17,7)）に 案内の 人（ピカチュウ版 0x1a8e6 の 文）。
    SafariZoneMainOffice_MapAttributes（銀も $25:$61b5）の +6〜+10 を バンク$44 の SafariOffice_MapScripts・_MapEvents（$44:$7b00）に。
  ・ポケギアの 地図：サファリの 点（$5f）を カーソルで 選べる（GetLandmarkCoords は $5f だけ 別の 座標）。
    ひらいた とき .LoadLandmark $24:$4cd4、カーソルの 上下 $24:$4f90・$4f9d（.done_dpad $4fa8）、wPokegearMapCursorLandmark $c5d7・
    wPokegearMapPlayerIconLandmark $c5d8（どれも 銀と 金で 同じ）。
  ・SameBoy で確かめたこと：草むら・つりの サファリの 戦いの メニューで wMusicID = $08（MUSIC_KANTO_WILD_BATTLE）。
    じむきょくの 人「サファリ ゾーンは いりぐち ふきんは どうぶつえんで おくに いくと ポケモンが とりほうだいの サファリ ゲームじゃ」。
    ポケギア：サファリの中で ひらくと「サファリゾーン」（セキチクの 北の 点）、上 → 19ばん すいどう、下 → セキチクシティ。
    セキチクで ひらいて 上 →「サファリゾーン」→ 上 →「19ばん すいどう」、下で もどり、セキチクの 下は 18ばん どうろ。
  ・セキチクの 入口の ドア：FuchsiaCity_Blocks（$2a:$65f1）+1×20+9 の $7d → $80 が ROM に 入っている（金の 新しい版と 同じ 書き方
    J_FuchsiaCity_Blocks に した）。ワカバから セキチクへ 来て、ドアから 入口に 入れることを 確かめた。

■ ボックスの自動切りかえ（src/autobox.asm。金銀クリスタル共通。銀は src/autobox_silver.asm）
  ・フィールドで いまの ボックスが 30匹なら、次の あいている ボックスに 切りかえて レポートを 書く（ピカチュウ版フルカラーと 同じ 文）。
    ぜんぶ いっぱいなら「ポケモン ボックスが ぜんぶ いっぱいです！ パソコンで ボックスを せいり してください」（1回だけ）。
    レポートを 1回も 書いていないとき・ちがう 人の レポートが あるときは しない。
  ・銀の 値：フック CheckTimeEvents.do_daily の farcall CheckPhoneCall $25:$6890（金と同じ）、処理は $46:$4000、
    WRAM は $dee9・$deea（$de40〜$dee7 は 60fps、$dee8 は せっていの とけい）、sBoxCount = SRAM バンク1 $ad10、
    ボックス1〜9 の 表は GetBoxCount.BoxBankAddresses（$38:$7dd9）と 同じ（金と同じ）。
  ・SameBoy で確かめたこと（通常版・60fps版）：レポートを 書いたあと いまの ボックス（1）を 30匹に すると、1歩で 音 →
    「ボックス１が いっぱいに…」→「ボックス２に じどうで きりかえました」→「レポートを かきました」。
    ボックス1 の 場所に 30匹で 書かれ、いまの ボックスは 2（0匹）。ぜんぶ いっぱいでは 文が 1回だけ 出て、ボックスは そのまま。
    レポートを 書く前は 何も 起きない。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/autobox_silver.asm を足す

■ マスターボールを売る（src/masterball.asm。金と同じ。銀の値は src/masterball_silver.asm）
  ・ウツギ博士から マスターボールを もらった あと（EVENT_GOT_MASTER_BALL_FROM_ELM）だけ、セキエイこうげんの ショップの 一番上に
    マスターボール（10000円）が 並ぶ。
  ・銀の 値：GetMart $05:$5d9e（22バイト、金と同じ 並び）、Marts $05:$65ea（$22 店）、MartIndigoPlateau $05:$6746（品ぞろえも 同じ）、
    イベント $007c（ProfElmScript $13:$64f9 の checkevent。wEventFlags $d7aa）は 金と同じ。
    ItemAttributes だけ ちがって $01:$6b58（MASTER_BALL の 値段 0円 → 10000円）。処理と 表は $46:$4200。
  ・SameBoy で確かめたこと（通常版・60fps版）：もらう前は 元の 品ぞろえ（ハイパーボールから）。もらった あとは 一番上に マスターボール 10000円、
    100000円 → 1こ 買うと 90000円、もう 1こ で 80000円、ボールの ポケットに マスターボール 2こ。
    5000円 では「おかねが たりない ですよ！」で 買えず、お金も そのまま。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/masterball_silver.asm を足す

■ むしよけを もう一度 つかう（src/repelask.asm。金と同じ。銀の値は src/repelask_silver.asm）
  ・むしよけの ききめが きれたとき、リュックに のこりが あれば「○○を つかいますか？」と きく。はい で その場で つかう。
    きく ものは さいごに つかった むしよけ（なければ むしよけスプレー → シルバースプレー → ゴールドスプレー の じゅん）。
  ・銀の 値：DoRepelStep の フック $25:$6b14、RepelWoreOffText $04:$7a79、UseRepel $03:$787c（17バイト）、
    PrintText $0f30・CheckItem $304b・TossItem $3025 は 金と同じ。WRAM は $deeb・$deec（$dee9・$deea は ボックスの 自動切りかえ）。
    処理は $47:$4000。
  ・SameBoy で確かめたこと（通常版・60fps版）：むしよけスプレー 3こ → 「むしよけスプレーを つかいますか？」→ はい →
    「むしよけスプレーを つかった！」、のこり 2こ・ききめ 100歩。いいえ → つかわない（ききめ 0・3こ の まま）。
    さいごに ゴールドスプレーを つかって いれば ゴールドを きく（ききめ 250歩）。シルバーと ゴールドだけ なら シルバー（200歩）。
    リュックに 1こも なければ 元の 文だけ。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/repelask_silver.asm を足す

■ 文字の速さ さいこう（src/textspeed.asm。金と同じ。銀の値は src/textspeed_silver.asm）
  ・せっていの「はなしの はやさ」に「さいこう」（文字が 待たずに 一度に 出る）を 足す。さいこう・はやい・ふつう・おそい を 左右で。
  ・銀の 値：Options_TextSpeed は $39:$4b05（金は $4c7f。銀は _Option から 前に ずれている）。文字の 場所は せっていの とけいで
    1行 上げた 所（hlcoord 11, 3 の 1行 上。金と同じ）。処理は $47:$4200。
  ・SameBoy で確かめたこと（通常版・60fps版）：右で ふつう → おそい → さいこう → はやい → ふつう、左で その 逆。
    むしよけの 文が 出きるまで：さいこう 17フレーム、はやい 29、ふつう 53、おそい 77（さいこうは 1文字ずつ 待たない）。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/textspeed_silver.asm を足す

■ 電話の回数（src/phonefreq.asm。金と同じ。銀の値は src/phonefreq_silver.asm）
  ・ポケギアの 電話の 画面の 下に「ちゃくしん・ふつう　セレクト　かえる」。SELECT で ふつう → すこし（4分の1）→ なし。
    （はじめは 金と 同じ「でんわ・すくない　セレクトで　かえる」だったが、日本版は 濁点を 1行 上（10行め）に かくので、
      4人めの 行と かさなって いた：4人めに カーソルが あると「でんわ」の 濁点が きえ、しょくぎょうの 6文字めが「セレクトで」の
      濁点に かわる。濁点の ない ことばに かえて 直した。金の src/phonefreq.asm も 同じ）
    とまるのは ふつうの 電話（再戦・ポケモンじまん など）だけ。話の 中で かかってくる 電話は とまらない。レポートに 書かれる。
  ・銀の 値：CheckPhoneCall $24:$4074、PokegearPhone_Joypad $24:$50cf、.Phone の call $24:$4dc3、UpdateDisplayList $5241、
    CheckStandingOnEntrance $170d、Random $305e、PlaySFX $3d45、wOptions2 $d1b0（ビット 1・2）は 金と同じ。
    バンク$24 の 空き $7fb0（サファリの 地図の 場所 $7f40〜$7faa の あと）。処理は $47:$4400。
  ・SameBoy で確かめたこと（通常版・60fps版）：電話の 画面で SELECT → すこし（wOptions2 = 3）→ なし（5）→ ふつう（1）。
    4人めに つりびと・ピクニックガール などを ならべて カーソルを 4人めに しても、名前・しょくぎょう・カーソル が くずれない。
    ほかの 画面に 行って もどっても 同じ 文字。かかってくる 回数（4分の1・なし）は 長く 歩いて 数えては いない（金で 確かめた 処理と 同じ バイト）。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/phonefreq_silver.asm を足す

■ 技を思い出させる人（src/moverelearn.asm。金と同じ。銀は src/moverelearn_silver.asm）
  ・フスベシティの わざわすれの いえに、わざを おもいださせて くれる おばあさん（5, 4）を 置く。お金は いらない。
    いまの レベルまでに レベルで おぼえる わざの うち、おぼえて いない わざを 一覧で えらぶ。タマゴは えらべない。
  ・銀の 値：MoveDeletersHouse_MapAttributes $25:$5d29、元の スクリプト $2d:$5d05（special MoveDeletion = $21、本だな jumpstd $0001、
    人は 1人）、EvosAttacksPointers $10:$695f、SelectMonFromParty $14:$4000 は 金と同じ。
    LearnMove だけ ちがって $01:$67ae（金は $67e9）。src/moverelearn_silver.asm は 金の ファイルの jp_all.inc を jp_all_silver.inc に、
    LearnMove と 置き場所（$47:$4800）を かえた もの。
  ・SameBoy で確かめたこと（通常版・60fps版）：おばあさん → はい → ヒノアラシ（Lv20）→ にらみつける → 4つ ある → はい →
    えんまくを わすれて「にらみつけるを おぼえた！」→「また いつでも おいでなさいね」→ マップに もどる。
    ピカチュウ：なきごえ・しっぽをふる・かげぶんしん・たたきつける・やめる。ルギア：エアロブラスト・しんぴのまもり・じこさいせい。
    タマゴ：「タマゴは まだ わざを おもいだせないよ」。わざわすれの 人は 元のまま（たいあたりを わすれさせた）。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/moverelearn_silver.asm を足す

■ 技教えの人（src/movetutor.asm・movetutor_compat.inc。金と同じ。銀は src/movetutor_silver.asm）
  ・殿堂入りの あと、コインケースを もっていれば、水よう日・土よう日に コガネシティの ゲームコーナーの 前（12, 22）に 出る。
    コイン 4000まいで かえんほうしゃ・10まんボルト・れいとうビーム の どれかを 1回（その日は もう 出ない）。おぼえられる ポケモンは クリスタルと 同じ。
  ・銀の 値：GoldenrodCity_MapAttributes $25:$4ec5、コガネの スクリプト・イベント $34:$4000〜$44ee（callback $4003、元の callback $4005
    = setflag $0045・$0015、人の 数 $4437 = 14人、ロケット団の 見はりは 8人め = wMapObjects の 9番）、
    殿堂入り イベント $0044（HallOfFame の setevent）、special DisplayCoinCaseBalance $4e（SpecialsPointers $03:$4239）、
    wDailyFlags2 $d92f の ビット 6、KnowsMove $03:$7f70 は 金と同じ。LearnMove だけ $01:$67ae。
    コガネの 写しと 処理は バンク$48（写し $4000〜$44ed、処理 $5000）。
  ・銀で 直した 所：コインケースを さがす CheckItem に wNumKeyItems を わたして いたのを wNumItems に した。
    wNumKeyItems だと どうぐの 2つ組（番号・数）として 見てしまい、たいせつなものの 並びに よっては コインケースが 見つからず 出なかった
    （wNumItems を わたすと どうぐの 種類で たいせつなものの ポケットを 見る）。金の src/movetutor.asm も 同じ。
  ・SameBoy で確かめたこと（通常版・60fps版）：殿堂入り・コインケース・水よう日／土よう日：見はりの 場所に 人が 出る。
    月よう日・殿堂入り 前：出ない（見はりの まま）。話す → はい → コイン 9999まい → はい → かえんほうしゃ／10まんボルト／れいとうビーム／やめる。
    かえんほうしゃ → ピカチュウ →「その ポケモンには おしえられんのう」→ また えらぶ → B →「そ そんな……」（コインは そのまま）。
    10まんボルト → ピカチュウ → たいあたりを わすれて おぼえた → コイン 5999まい →「ワハハ！ さらばじゃ！」→ 消える。
    wDailyFlags2 の ビット 6 が たつ。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/movetutor_silver.asm を足す

■ ぶんぷの時間帯（src/nesttime.asm。金と同じ。銀の値は src/nesttime_silver.asm）
  ・ずかんの すみかの 画面で START を おすと、ぜんぶ → あさ → ひる → よる と 切りかわり、その 時間に 出る 場所だけ マークする。
    わくの 右に「あさ」「ひる」「よる」。カントーを 見て いた ときは カントーの まま。
  ・銀の 値：FindNest .FindGrass $0a:$6655、Pokedex_GetArea $24:$5da5（くりかえし $5e02・見出し $5eb6・.right $5e4b）は 金と同じ。
    空きは $0a:$7fc9・$24:$7f1c（サファリの 地図の 場所 $7f40 の 前）・$24:$7fde（電話の回数の あと）。
    WRAM は $deed・$deee。処理は $47:$4600。
  ・SameBoy で確かめたこと（通常版）：ポッポ：ぜんぶ・あさ・ひる は マーク、よる は なし。ホーホー：あさ・ひる なし、よる だけ マーク。
    カントーの 画面でも START で 切りかわる。ジョウトに もどっても 時間帯は そのまま。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/nesttime_silver.asm を足す

■ ガンテツのボールをまとめて作る（src/kurtbulk.asm。金と同じ。銀の値は src/kurtbulk_silver.asm）
  ・ぼんぐりを えらぶと その 色の ぼんぐりを リュックに ある だけ ぜんぶ わたし、次の日に その 数だけ ボールを くれる。
  ・銀の 値：SelectApricornForKurt $03:$45d1、Kurt_SelectApricorn $09:$4ba1、Script_giveitem の ld [wItemQuantityChange], a
    $25:$764f、TossItem $3025、KURTS_HOUSE（8, 4）、wKurtCount $d7a0（wEventFlags の 前の 空き）は 金と同じ。
    バンク$25 の 空き $7fc0（通常版・60fps版とも 空き）。処理は $48:$5400。
  ・SameBoy で確かめたこと（通常版・60fps版）：あかぼんぐり 5こ・あおぼんぐり 2こ → あかを えらぶ → あかが リュックから
    なくなる（wKurtCount = 5）→「ボールに するまで 1にちほど…」→ 次の日（wDailyFlags1 の ビット0 を 消して 入りなおす）→
    「レベルボールを もらった！」、ボールの ポケットに レベルボール 5こ。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/kurtbulk_silver.asm を足す

■ 育て屋の話（src/daycarehint.asm。金と同じ。銀の値は src/daycarehint_silver.asm）
  ・中の おじいさんが、2ひき あずけて タマゴが まだ ない とき、ひきとるか きく 前に なかの よさ（4だんかい）と
    「タマゴが そろそろ…」／「まだまだ じゃな」を いう。
  ・銀の 値：DayCareMan .AskWithdrawMon $05:$6d06、GetBreedMon1LevelGrowth $03:$696e、CheckBreedmonCompatibility $05:$78e9、
    wDayCareMan $dbd4・wDayCareLady $dc01・wStepsToEgg $dc02・wBreedingCompatibility $d143・wBreedMon2 $dc10 は 金と同じ。
    処理は $48:$5600。
  ・SameBoy で確かめたこと（通常版・60fps版）：メタモン＋ポッポ（ちがう ID）→「まあまあ」、同じ ID →「あまり」、
    ポッポ ♂＋♀（ちがう ID）→「とっても」、同じ ID →「なかが いい」、メタモン＋メタモン →「できそうに ないわい」。
    wStepsToEgg 20 →「そろそろ」、144 →「まだまだ」。1ぴき だけ なら 何も いわない。そのあと 元の「なんだ もう きたのかい」に つづく。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/daycarehint_silver.asm を足す

■ セレビィと伝説の鳥（src/legends.asm。金と同じ。銀の値は src/legends_silver.asm）
  ・殿堂入りの あと 1回だけ：セレビィ Lv30（ウバメのもりの ほこらを しらべる）、フリーザー（うずまきじま 地下2階）・
    サンダー（イワヤマトンネル 地下1階）・ファイヤー（シロガネやま 2）Lv50。会ったかは wLegendFlags（$d7a1）の ビット。
  ・銀の 値（銀の バイトで 確かめた。ぜんぶ 金と同じ）：ウバメのもり（バンク$28）の ほこらの bg_event の スクリプトの 場所 $60d3
    （元は $5dd7 の jumptext $608d）、空き $28:$7ffb。
    うずまきじま 地下2階 $2d:$44b2〜$44fb（人 3つ → 鳥は 5番）、イワヤマトンネル 地下1階 $2f:$6ecf〜$6f20（人 3つ → 5番）、
    シロガネやま 2 $2d:$45ad〜$45d1（人 0 → 2番）。MapAttributes $25:$5ae9・$5c51・$5b0d。AddSpriteGFX $05:$41c7・LoadUsedSpritesGFX $05:$41f8。
    写す 所に ほかの パッチは ない（通常版・60fps版の .map で 確かめた）。写しと 処理は バンク$49（本体 $6000）。
  ・SameBoy で確かめたこと（通常版・60fps版）：殿堂入りの あと 3つの マップに 鳥が 出る → はなす →「ギャーーッ！」→
    フリーザー・サンダー・ファイヤーと 戦う。にげると 鳥が 消えて wLegendFlags の ビットが たつ（ファイヤー：$08）。
    殿堂入り 前は 出ない。
    セレビィ：ほこらを しらべる →「ウバメのもりの ほこら……」→「…おや？ ほこらの おくから なにかが とびだしてきた！」→ セレビィと 戦う
    → にげると wLegendFlags の ビット0。もう 一度 しらべると 元の 文だけ。殿堂入り 前も 元の 文だけ。
    （ほこらの 前へは、試す ROM だけ ウバメのもりの 1つめの ワープの 場所を ほこらの 前に かえて 行った）
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/legends_silver.asm を足す

■ わざの威力と命中（src/movepower.asm。金と同じ。銀の値は src/movepower_silver.asm）
  ・戦闘で わざを えらぶ とき、右下の わくに PP・いりょく・めいちゅう と、相手への 効き目（×4・×2・×1・×1／2・×1／4・×0）・タイプを 出す。
    命中は ％、威力 0・1 は「ー」で 効き目も 出さない。（金の 新しい src/movepower.asm に 入れかえ。「タイプ／」の 文字は やめた）
  ・銀の 値：MoveInfoBox の さいごの 9バイト（ld hl, $c4ef / ld a, $2a / call Predef / ret）は 銀では $0f:$65df
    （金は $65e4。銀は ここが 5バイト 前）。Predef $2e05・PrintNum $31f9・PlaceString $0f46・wPlayerMoveStruct $caef は 金と同じ。
    効き目：TypeMatchups $0d:$4cfd・wEnemyMonType1 $d0ff・2 $d100・GetFarByte $30e4 は 金と同じ。処理は $48:$5800。
  ・SameBoy で確かめたこと（通常版・60fps版）：ヒノアラシ：たいあたり 35/95・ひのこ 40/100・えんまく ー/100・でんこうせっか 40/100。
    効き目：ファイヤーに たいあたり ×1・ひのこ ×1／2・えんまく なし、フリーザーに ひのこ ×2、サンダーに ひのこ ×1。
    「いりょく」の よこに 出て いた 濁点（「わざタイプ」の 濁点の のこり）を 直した 新しい src/movepower.asm に 入れかえ、出なく なった。
    さらに 金の 新しい src/movepower.asm に 入れかえ：タイプを いちばん 下の 行に かくと 上の 行の 命中の 数と 濁点が かさなって
    「ドラゴン」→「トラコン」「エスパー」→「エスハー」に なって いた。わくの 中を 上から PP・タイプと 効き目・いりょく・めいちゅう に した
    （タイプの 濁点は PP の 左の 空いた 所に 出る）。銀で：サイコキネシス「エスパー ×1」・りゅうのいかり「ドラゴン ×1」が 濁点も 正しく 出る。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/movepower_silver.asm を足す

■ カントー御三家（src/starters.asm・starters_texts.inc・starters_jenny.inc・tools/starters_gen.py。金と同じ。銀の値は src/starters_silver.asm）
  ・フシギダネ・ヒトカゲ・ゼニガメ（Lv10）を ピカチュウフルカラーと 同じ 人・同じ 文・同じ 色（青）で もらえる。
    フシギダネ：ハナダの こうかんの 話の 家の 女の人、ヒトカゲ：24ばんどうろの 北の はしの 男の人、ゼニガメ：クチバの ジュンサー（オレンジバッジ）。
  ・銀の 値（銀の バイトで 確かめた。ぜんぶ 金と同じ）：ハナダの 家 $28:$6efe〜$6fb4（人 4、人の 数 $6f7f）、
    24ばんどうろ $35:$779c〜$79f8（人 1、$79ea）、クチバシティ $35:$6df6〜$71b7（人 6、$7168）、MapAttributes $25:$5d7d・$56f9・$55f1、
    OverworldSprites $05:$47b0（SPRITE_OLD_LINK_RECEPTIONIST $58 は 使われて いない）、クチバの 外の 絵の 表 $05:$46df の 9番め = SPRITE_BIKER。
    文と ジュンサーの 絵は tools/starters_gen.py を ピカチュウフルカラーの ROM で 動かして 作りなおし、金と 同じ ものに なった。
    もらった ことは $d7a1 の ビット 4〜6。写す 所に ほかの パッチは ない（.map で 確かめた）。
    置き場所：クチバの 写しは バンク$47（$6df6〜・表 $7c00）、ハナダ・24ばんどうろの 写しと 本体・絵は バンク$4a（$48 は 技教えの人などが 使う）。
  ・SameBoy で確かめたこと（通常版・60fps版）：ハナダ：はなす → はい →「それじゃ おねがいします！」→「フシギダネを てにいれた！」→ ニックネーム いいえ →
    もう一度 はなすと「フシギダネ がんばってます？」。いいえ →「そう…… ざんねん です……」で もらわない。
    クチバ：ジュンサー（青）が 出る。オレンジバッジ あり → はい →「まかせたわ！…」→「ゼニガメを てにいれた！」→「ゼニガメ げんきで やっている？」。
    バッジ なし →「さいきん いたずら ばかりする ゼニガメを つかまえたの！… このこを まかせたいんだけど……」だけ。
    24ばんどうろ：はい →「それじゃ おねがい するよ！」→「ヒトカゲを てにいれた！」→「あのときの ヒトカゲ そだってる？」。
    いいえ →「そうか…… じゃ どこに にがそうかな……」。
    （24ばんどうろへは、試す ROM だけ ハナダシティの 1つめの ワープの 場所を 北の はしに かえて 行った）
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/starters_silver.asm を足す

■ ダウジングマシンの方向（src/itemfinder.asm。金と同じ。銀の値は src/itemfinder_silver.asm）
  ・はんのう した とき、元の 文の あとに「どうぐは　ひだりの　ほうに／あるみたいだ！」のように 方向を 出す。
  ・銀の 値：ItemFinder の farcall $04:$67e0、.Script_FoundSomething の writetext $04:$6815（4c 23 68 49 90）、
    元の 文 $04:$6823（38バイト）、GetMapScriptsBank $2cec・GetFarByte $30e4・GetFarWord $30f8・EventFlagAction $2eeb は 金と同じ。
    WRAM は $def5〜$def8（$deeb〜$deee は ほかの 機能）。処理は $48:$5a00。
  ・SameBoy で確かめたこと（通常版・60fps版）：シロガネやま 2 の 入口（かくれた 道具が 3つ ひだり）→「おッ！ マシンが はんのう してるぞ！
    ちかくに どうぐが うまってる！」→「どうぐは ひだりの ほうに あるみたいだ！」。ガンテツの 家（道具 なし）→「…… なんにも はんのう しない」。
    （ひだり 以外の 方向は 銀では 試して いない。方向を きめる 処理は 金と 同じ）
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/itemfinder_silver.asm を足す

■ 電話帳の再戦の印（src/phonemark.asm。金と同じ。銀の値は src/phonemark_silver.asm）
  ・電話で「また 戦おう」と いって きた トレーナーの 行の 右はし（x 18）に「！」。戦うと 消える。
  ・銀の 値：PokegearPhone_UpdateDisplayList の call PokegearPhone_UpdateCursor $24:$5283、UpdateCursor $5220、wPhoneList $d98c、
    wPokegearPhoneScrollPosition $c5d2 は 金と同じ。バンク$24 の 空き $7fe8（ぶんぷの時間帯の あと）。
    再戦の イベントの 番号（ジャック $0260〜エリン $029e）は 銀の ROM の トレーナーの スクリプトで checkevent・setevent が
    1つずつ ある ことを 確かめて 金と 同じ。処理は $48:$5c00。
  ・SameBoy で確かめたこと（通常版・60fps版）：ゴロウ（$0274）と エミ（$029e）の イベントを たてる → その 2人の 行だけ「！」。
    スクロール しても 合う。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/phonemark_silver.asm を足す

■ ポケギアの文字の後ろを白に（src/pokegearwhite.asm。金と同じ。銀の値は src/pokegearwhite_silver.asm）
  ・ポケギアの 文字の 後ろ（うすい 黄緑 RGB 28,31,20）を 白に する。時計・電話帳・ラジオ・下の 文の わく・地名の わく。
    地図の 道も 同じ 色なので 白に なる（ずかんの「ぶんぷ」・そらをとぶ の 地図も 同じ）。
  ・銀の 値：PokegearPals は 銀も $02:$7af4（「fc 53 b5 56 ad 35 00 00 fc 53 e0 03 …」は ROM に 1か所）。6組 とも 色0 が $53fc で 金と同じ。
  ・SameBoy で確かめたこと（通常版・60fps版）：元の 銀と くらべて、時計・地図・電話帳・ラジオの 黄緑が 白に なった。
    ずかんの ぶんぷの 地図も 白。（そらをとぶ の 地図は 同じ 色の 表なので 試して いない）
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/pokegearwhite_silver.asm を足す

■ 前のボールをすぐ投げる（src/quickball.asm。金と同じ。銀の値は src/quickball_silver.asm）
  ・野生の 戦闘の メニューで SELECT を おすと、前に 使った ボールを リュックを ひらかずに 投げる。ない ときは リュックを ひらく。
  ・銀の 値：BattleMenuHeader の MenuData $09:$4e9f・CommonBattleMenu の call _2DMenu $09:$4e8a・BattleMenu .next $0f:$5fe5・
    BattleMenu_Pack $0f:$600b・.got_item $0f:$6046・.UseItem $0f:$6071、空き $09:$7fcf・$0f:$7fc8 は 金と同じ。
    WRAM は $def9・$defa（$def5〜$def8 は ダウジング）。処理は $48:$5e00。
  ・SameBoy で確かめたこと（通常版・60fps版）：ファイヤーとの 戦闘で、まだ 使って いない → SELECT で リュックが ひらく →
    モンスターボールを 使う（20 → 19、おぼえる）→ つぎの ターンに SELECT → リュックを ひらかずに モンスターボールを 投げる（19 → 18）。
    （トレーナー戦で なにも しない ことは 銀では 試して いない）
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/quickball_silver.asm を足す

■ なつき度のハート（src/hearts.asm。金と同じ。銀の値は src/hearts_silver.asm）
  ・つよさの 画面の 1ページめに「なつきど」と ハート 5こ（（なつき度＋50）÷51 こ ぬりつぶし）。
  ・銀の 値：LoadPinkPage の さいごの call WaitBGMap $14:$4f8e、空き $14:$7fc8、wTempMonHappiness $d020、wAttrmap $cccd は 金と同じ。
    処理は $48:$6000。
  ・SameBoy で確かめたこと（通常版・60fps版）：ヒノアラシ（なつき度 70）→ ♥♥♡♡♡、ピカチュウ（255）→ ♥♥♥♥♥。
    2・3ページ（わざ・のうりょく）に かえても くずれない。ほかの ポケモンに かえても 出る。手もちの 画面に もどっても ふつう。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/hearts_silver.asm を足す

■ ポケギアの今日のできごと（src/gearday.asm。金と同じ。銀の値は src/gearday_silver.asm）
  ・時計の 画面の 下の 文を、曜日きょうだいの いる 場所と、むしとりたいかい（火・木・土）・ラプラス（金）に する。
  ・銀の 値：PokegearClock_Init の ld hl, PokegearPressButtonText / call PrintText $24:$4e5f、GetWeekday $351b は 金と同じ。処理は $48:$6200。
  ・SameBoy で確かめたこと（通常版・60fps版）：wStartDay を かえて 日〜土の 7つ ぜんぶ（37・40・29ばんどうろ、いかりのみずうみ、36・32ばんどうろ、
    フスベシティ。火・木・土 は むしとりたいかい、金 は ラプラス）。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/gearday_silver.asm を足す

■ タマゴの歩数（src/eggsteps.asm。金と同じ。銀の値は src/eggsteps_silver.asm）
  ・タマゴの つよさの 画面に「あと ○○ほ」（歩数 ＝ $80 − wStepCount（0 なら 256）＋（のこりの 回数 − 1）× 256）。
  ・銀の 値：EggStatsScreen .picked の あとの call WaitBGMap $14:$51bf、wTempMonHappiness $d020、wStepCount $d983 は 金と同じ。処理は $48:$6400。
  ・SameBoy で確かめたこと（通常版・60fps版）：のこり 5回・wStepCount $40 →「あと 1088ほ」、1回・$7f →「あと 1ほ」、1回・$00 →「あと 128ほ」。
    もどった あとも ふつう。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/eggsteps_silver.asm を足す

■ 手持ちの色ちがいの星（src/partyshiny.asm。金と同じ。銀の値は src/partyshiny_silver.asm）
  ・手持ちの 画面で 色ちがいの 名前の 右上（「：Ｌ」の 上）に ★。タマゴは なし。★の 絵は 背景の タイル $5e。
  ・銀の 値：PlacePartyNicknames .end の ld de, .CancelString / call PlaceString / ret $14:$40be、wPartyMon1DVs $da05 は 金と同じ。処理は $48:$6600。
  ・SameBoy で確かめたこと（通常版・60fps版）：色ちがいの ピカチュウ・ミュウに ★、ほかと タマゴは なし。手持ちの 画面を とじた あとの 町も ふつう。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/eggsteps_silver.asm・src/partyshiny_silver.asm を足す

■ 場所の名前の札（src/mapsign.asm。金と同じ。銀の値は src/mapsign_silver.asm。わくの 絵 gfxdata/map_entry_sign.2bpp）
  ・クリスタルと 同じ 札：ちがう 場所（ランドマーク）に 入ると、歩く ループの 2回めで 画面の 下 4行に 札を 出し、
    118フレーム（クリスタルの 59回×2フレーム）で いっぺんに 消す（すべる 動きは なし。クリスタルも なし）。
    わくの 絵・色（31,31,16／31,31,16／14,9,0／0,0,0）・名前の まん中 よせ も クリスタルと 同じ。
    つながりで 歩いて 入る・その場で むきを かえる いがいの イベント（メニュー・話しかける など）で すぐ 消す。
    出て いる 間に べつの 場所に 入ったら その 名前に かわる。白黒の ゲームボーイでは 出さない（クリスタルと 同じ）。
  ・銀の 値：アドレスは 金と 同じ。WRAM は $defb〜$defd と wMSState $def2（$def9・$defa は 前のボール）。
    hCGB $ffe8・wBGPals2 の パレット7 $c2b8。処理は $48:$4600（大きく なったので $6800 から うつした）。
  ・SameBoy で確かめたこと（通常版・60fps版）：34ばん どうろ・コガネシティ・ワカバタウン・30／36／39ばん どうろ・
    マダツボミのとう・ハナダシティ で まん中に 出る。マップが 出てから 2回めの ループで 出て、ちょうど 118フレームで 消える。
    ワカバタウン → 29ばんどうろ を 歩いて こえると「29ばん どうろ」、出て いる 間に もどると「ワカバタウン」に かわる。
    スタートメニューを ひらくと すぐ 消え、メニューの わくは 白に もどる。白黒の ゲームボーイでは 出ない。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/mapsign_silver.asm を足す

■ めざめるパワー（src/hpower.asm。金と同じ。銀の値は src/hpower_silver.asm）
  ・つよさの 画面の わざの ページで、めざめるパワーの 所に タイプと 威力（めざパ　くさ69）。
  ・銀の 値：LoadGreenPage の farcall LoadStatsScreenPals $14:$5089、LoadStatsScreenPals $02:$5241、GetTypeName $14:$4a87 は 金と同じ。処理は $48:$6b00。
  ・SameBoy で確かめたこと（通常版・60fps版）：個体値 $fe $dc の ヒノアラシ →「めざパ　ドラゴン68」（計算と 同じ）。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/hpower_silver.asm を足す

■ 個体値・きそポイント（src/dvview.asm。金と同じ。銀の値は src/dvview_silver.asm）
  ・つよさの 画面の 3ページめで SELECT を おすたびに のうりょく → 個体値（たいりょく も）→ きそポイント（0〜65535・5けた）→ のうりょく。
    きそポイントの とき：わくの 上の 線に「きそポイント」、4行めに「たいりょく」。とくこう・とくぼう は どちらも とくしゅ。
  ・銀の 値：.joypad_loop の call GetJoypad $14:$4ce2、LoadBluePage の farcall LoadStatsScreenPals $14:$50d8、空き $14:$7fd1、
    wTempMon の きそポイント $d010（大きい ほうが 先）は 金と同じ。WRAM は $defe。処理は $48:$6c00、きそポイントの 処理は $48:$6f00。
  ・SameBoy で確かめたこと（通常版・60fps版）：個体値 $fe $dc → たいりょく 10・こうげき 15・ぼうぎょ 14・とくこう 12・とくぼう 12・すばやさ 13。
    きそポイント（HP 65535・こうげき 1234・ぼうぎょ 0・すばやさ 300・とくしゅ 9999 に した）→ たいりょく 65535・こうげき 1234・ぼうぎょ 0・
    とくこう 9999・とくぼう 9999・すばやさ 300。もう 1回 で のうりょく に もどる。ページを かえても くずれない。
  ・きそポイントの「たいりょく」の 数は x15〜19（ほかの 5つは わくの 中の x14〜18）。x14 からだと 65535 のように 5けたの とき
    「たいりょく65535」と 字と 数が くっついて いた（クリスタルで 直した のと 同じ）。dvview.asm は 金と 同じ ファイルなので 金も 直る。
    確かめたこと（通常版・60fps版）：たいりょく 65535・こうげき 12345 → 「たいりょく　65535」と あいだが あく。
    個体値・のうりょくの ページ、もどした あとは 元のまま。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/dvview_silver.asm を足す

■ 相手のHPの数字（src/enemyhp.asm。金と同じ。銀の値は src/enemyhp_silver.asm）
  ・相手の HP バーの 下に「32／ 32」。HP が へる とき 数字も うごく。
  ・銀の 値：DrawEnemyHUD の farcall DrawEnemyHUDBorder $0f:$5eb1、HPBarAnim_UpdateHPRemaining の and a / ret z / cp 1 / jr z（a7 c8 fe 01 28 05）$03:$5a57 は 金と同じ。
    処理は $48:$6d00。
  ・SameBoy で確かめたこと（通常版・60fps版）：ファイヤー「155／155」。つった メノクラゲに たいあたり → 30 → 25 → 24 → 23 … と へって いく。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/enemyhp_silver.asm を足す

■ 手持ちの道具の名前（src/partyitem.asm。金と同じ。銀の値は src/partyitem_silver.asm）
  ・手持ちの 画面で カーソルの ポケモンの 道具を「もちもの／○○」。
  ・銀の 値：AnimSeq_PartyMon の ld a, [wMenuCursorY] $23:$52ed、空き $23:$7f80、GetItemName $360a は 金と同じ。wPILast は $d7a2（金と同じ）。処理は $48:$6e00。
  ・SameBoy で確かめたこと（通常版・60fps版）：ヒノアラシ「もちもの／きのみジュース」、ピカチュウ「たべのこし」、ギャラドス「なし」。カーソルを うごかすと かわる。
  ・金の 新しい src/partyitem.asm に 入れかえ：右に 出る メニューを ひらくと「もちもの／な」が わくの 左に はみ出して いた。
    LoadMenuHeader の call CopyMenuHeader（$1b59）を ROM0 の 空き（使われて いない DummyEndPredef の nop 16こ $2dd2。銀も 同じ）に つないで、
    手持ちの 画面の メニューから ひらく ときは 先に けす。処理は $48:$7300 に うつした（大きく なったので）。
    銀で：メニューを ひらくと「やめる」だけ、とじると「もちもの／たべのこし」に もどる、カーソルを うごかすと かわる（通常版・60fps版）。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/partyitem_silver.asm を足す

■ つりでかならずかかる（src/fishbite.asm。金と同じ。銀の値は src/fishbite_silver.asm）
  ・Fish.Fish の jr nc, .no_bite（30 1f。銀も $24:$68e5）を nop 2つに。
  ・SameBoy で確かめたこと（通常版・60fps版）：ボロのつりざおで 6回 つって 6回 とも かかった（元の 銀は 6回 中 2回）。60fps版も 4回 中 4回。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/fishbite_silver.asm を足す

■ つかえるわざの命中（src/moveacc.asm。金と同じ。銀の値は src/moveacc_silver.asm）
  ・手持ちの「つかえるわざ」の 画面で、「タイプ／○○　いりょく／ ○○」の 上の 行に「めいちゅう／ 95」（命中は ×100÷255 を 四捨五入）。
  ・銀の 値：PlaceMoveData の hlcoord 1, 14 / ld a, PRINTMOVEDESCRIPTION / call Predef（21 b9 c4 3e 11 cd 05 2e）$04:$76a8、
    Moves $10:$5c6c、wCurSpecies $ce54 は 金と同じ。処理は $48:$7000。
  ・SameBoy で確かめたこと（通常版・60fps版）：たいあたり 95・ひのこ 100・えんまく 100・でんこうせっか 100。カーソルを うごかすと かわる。
    とじた あとも ふつう。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/moveacc_silver.asm を足す

■ 倒した伝説がもどる（src/legendrevive.asm。金と同じ。銀の値は src/legendrevive_silver.asm）
  ・殿堂入りの とき、倒した（にげた）けど ずかんで つかまえて いない ホウオウ・ルギア・ライコウ・エンテイ・スイクンを もとに もどして から レポート。
  ・銀の 値：HallOfFame の farcall SaveGameData $21:$65f1（3e 05 21 f5 4b cf。バグ修正を 入れた あとも 同じ）、
    EVENT_FOUGHT_HO_OH $317（checkevent $29:$6e1c・setevent $29:$6e3b）・EVENT_FOUGHT_LUGIA $318（$2d:$4500・$451f）・
    EVENT_RELEASED_THE_BEASTS $7b、wRoamMon1 $dc90、InitRoamMons（$0a:$688a）の 値（レベル 40・42ばんどうろ・37ばんどうろ・38ばんどうろ）は 金と同じ。
    処理は $48:$7100。
  ・SameBoy で確かめたこと（通常版・60fps版）：ホウオウ・ルギアと 戦った あと・ライコウたちが いない（しゅるい 0）・ずかんで ルギアと ライコウだけ
    つかまえた ことに して 殿堂入りの へやに 入る → 殿堂入りで ホウオウの イベントだけ きえる（ルギアは のこる）、エンテイ（37ばんどうろ）・
    スイクン（38ばんどうろ）が レベル 40 で もどり、ライコウは もどらない。もどした 値が レポート（SRAM の バンク1 と 3）にも 書かれて いる。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/legendrevive_silver.asm を足す

■ 2列のメニューの カーソル（src/monmenu_fix.asm。金と同じ。銀の値は src/monmenu_fix_silver.asm）
  ・手持ちの 2列の メニューで 項目が 奇数の とき、いちばん 下の 右の 空いた 所に カーソルが 行けて いたのを、左に もどす。
  ・銀の 値：2DMenu の ループの call _2DMenuInterpretJoypad $09:$4166、空き $09:$7fd9（前のボールの 処理の あと）、wMonSubmenuCount $d0c5 は 金と同じ。
    処理は $48:$7200。
  ・SameBoy で確かめたこと（通常版・60fps版）：ギャラドス（9項目）の メニューで「もどる」から 右 → 元の 銀は 空いた 所に カーソルが 行ったが、
    直した あとは「もどる」の まま。右の 列から 下 でも「もどる」に もどる。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/monmenu_fix_silver.asm を足す

■ バグ修正 10（わるあがき）の とび先（src/bugfix.asm）
  ・かなしばり中の わるあがき の 修正（10）の さいごの とび先 .force_struggle を IF DEF(SILVER) で 分けた。
    金は J_MoveSelectionScreen__force_struggle（$0f:$64b8）。銀も 銀の ROM で 確かめると $0f:$64b8（ld hl, BattleText_MonHasNoMovesLeft）。
  ・前の 銀は jp $64b9 で 命令の とちゅうに とんで いたので、この バグ修正が 銀では こわれて いた（下を 見て）。
  ・SameBoy で確かめたこと（通常版・60fps版）：ファイヤーとの 戦闘で 1つめの わざを かなしばり、2つめの わざを PP 0（ポイントアップ 3回）に して「たたかう」
    → 元の 銀は わざの 画面が 出て すすめない。前の 銀（$64b9）は「ナ1エラー」「や」と 文字化けした。
    直した あとは「ヒノアラシは だすことの できる わざが ない！」と 出て わるあがき に なり、戦闘が つづく。

■ ぶんぷを とじる とき 黒い 画面を はさまない（src/dexarea.asm。銀の 値は src/dexarea.asm の 中。src/dexarea_silver.asm で 読みこむ）
  ・元の ゲームは ぶんぷを B で とじると、画面を 黒く して（約 20コマ）から ずかんの 説明に もどる。
    ぶんぷを 出した まま 説明の 画面を WRAM に かき、ポケモンの 絵を のばして おき（GetMonFrontpic の 行き先を SRAM の $a000 そのものに。
    VRAM は さわらない）、さいごに LCD を 切って 絵・タイル・色の わりあて・色を いっぺんに 書いて LCD を つける。
  ・銀の 値：.Area の Pokedex_GetArea の あと（call Pokedex_BlackOutBG〜ret の 34バイト）$10:$4264、Pokedex_RedisplayDexEntry $42cc・
    GetSelectedMon $4a7d・LoadSelectedMonTiles $5170・BlackOutBG $5140、GetSGBLayout $34e5・DmgToCgbBGPals $0c4a・DmgToCgbObjPal0 $0c8f・
    UpdateCGBPals $0bcc・DisableLCD $0432・EnableLCD $0454・OpenSRAM $309d・CloseSRAM $30ad・GetBaseData $39dd・Predef $2e05（GetMonFrontpic は $3c）、
    wTempSpecies $d143・wCurPartySpecies $cffe・wFirstUnownSeen $dbd3・wUnownLetter $d110・hCGB $ffe8・hBGMapMode $ffd6・hWY $ffd4。処理は $48:$7500。
    白黒の ゲームボーイ（hCGB = 0）は 元の とおり。
  ・SameBoy で確かめたこと（通常版・60fps版）：B の あと 11コマ ぶんぷの まま → 白 3コマ（LCD を 切って いる 間）→ 説明の 画面
    （元は 黒 20コマ）。説明の 画面は 元の 銀と 1ドットも 同じ。カントー・START の あと でも 同じ。一覧に もどる・ほかの ポケモン・
    フィールドに もどっても ふつう。白黒（DMG）でも 元の 銀と 同じ 画面。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/dexarea_silver.asm を足す

■ 前のボールをすぐ投げる で 画面が 白く ならない（src/quickball.asm）
  ・SELECT で 投げると、リュックを とじた ときと 同じ「戦闘の 画面の かきなおし」（_ReturnToBattle_UseBall。さいしょに ClearBGPalettes で
    画面ぜんたいが 白く なる）を して いた（約 40コマ 白い 画面）。リュックを ひらいて いないので かきなおさない ように した。
  ・_ReturnToBattle_UseBall の はじめの call ClearBGPalettes（$09:$7665）を QB_RetCheck（$09:$7fe8）に：
    SELECT で 投げて いる とき（wQuickBall = 2。QB_Decide で たて、QB_Remember で もどす）は かきなおさずに もどる（むしとり大会の パークボールと 同じ）。
  ・SameBoy で確かめたこと（通常版・60fps版）：SELECT → すぐ「ゴールドは モンスターボールを つかった！」→ 投げる → つかまえた／にげた まで ふつう。
    リュックから 投げる ときは 元の とおり。

■ むしとり大会の ポケモンを パソコンへ（src/contestpc.asm。クリスタルの src/contestpc_crystal.asm を 金銀に した もの。銀の 値は src/contestpc_silver.asm）
  ・2匹めを つかまえて「ポケモンを いれかえる？」→ はい なら 前の ポケモン、いいえ なら つかまえた ポケモンを
    「○○を パソコンに おくりますか？」→ はい で ボックスへ、いいえ なら 元の まま にがす。
    いまの ボックスが いっぱい（30匹）なら 次の あいて いる ボックスへ（下の「むしとり大会と 重さの 修正キット」）。
    ぜんぶ いっぱいなら「ボックスが いっぱいなので パソコンに おくれません！」で 元の まま。ニックネームは きかない。
  ・金銀は つかまえた 場所・時間を おぼえないので、クリスタルの SetBoxMonCaughtData・しぜんこうえん の 場所 は ない
    （pret/pokegold の CheckPartyFullAfterContest.TryAddToBox と 同じ：wContestMon → wBufferMon 32バイト、wPlayerName → wBufferMonOT、
    farcall InsertPokemonIntoBox、名前 → sBoxMonNicknames）。WRAM の バンクを 切りかえないので、前の ポケモンを よけるのは CopyBytes。
  ・銀の 値：BugContest_SetCaughtContestMon（$03:$6a4d）の lb bc, 14, 12 / call PlaceYesNoBox / ret c（01 0c 0e cd f1 1b d8）$03:$6a62、
    .generatestats $03:$6a7c、InsertPokemonIntoBox $14:$59a7、CopyBytes $30d6・PlaceYesNoBox $1bf1・PrintText $0f30・GetPokemonName $35e0・
    GetBaseData $39dd・OpenSRAM $309d・CloseSRAM $30ad、sBoxCount $ad10・sBoxMonNicknames $b1a4、wContestMon $dc5d・wBufferMon $cf2d・
    wBufferMonOT $cf27・wCurPartyMon $cfff・wPlayerName $d1b5・wTempEnemyMonSpecies $d0df・wNamedObjectIndex $d143・wCurPartySpecies $cffe・
    wCurSpecies $ce54・wStringBuffer1 $cf87。よける 所は 使われていない WRAM $d740〜$d76f。処理は $48:$7700。
  ・SameBoy で確かめたこと（通常版・60fps版）：大会の 中で 前に ビードルを つかまえた ことに して キャタピーを つかまえる →
    いれかえる はい・おくる はい → ボックスに ビードル（名前 ビードル、おや は 主人公）、大会の ポケモンは キャタピー。
    はい・いいえ → ボックスは 0匹、キャタピー。いいえ・はい → ボックスに キャタピー、大会の ポケモンは ビードル。
    いいえ・いいえ → ボックス 0匹、ビードル。ボックス 30匹 → 「ボックスが いっぱいなので…」、ボックスは 30匹の まま。
    どれも 戦いの あと フィールドに もどって 大会が つづく。
  組み立てかた（ぜんぶ入り）：build.py の行の最後に src/contestpc_silver.asm を足す

■ ずかん・手持ちの画面を ひらく ときの 表示（src/picpal.asm・src/minis.asm・src/partyitem.asm。金銀クリスタル共通の 修正を 銀に 入れた）
  1. ずかんを ひらく とき、白い 画面の なかで 絵の ところ だけ 先に 色が ついて 見えた
     → picpal.asm を 入れかえ（PicPal_PushIfShown：パレット0 が wBGPals1 と wBGPals2 で 同じで、まっくら でない とき だけ うつす）。
       picpal.asm が 大きく なったので、銀の PP_CGB_FREE を $02:$7c00 → $02:$7e40 に うつした（$7c60〜$7e37 は サファリの 色）。
  2. 手持ちの アイコンの 色を wOBPals2 にも 書くのは、BG パレット0 が wBGPals1（$c200）と wBGPals2（$c280）で 同じ とき だけに した
     （src/minis.asm。銀は hCGBPalUpdate を 立てないので もとから アイコン だけ 先に 出る ことは なかったが、同じ 作りに した）。
  3.「もちもの／…」が 4〜5コマ おくれて 出た → partyitem.asm を 入れかえ、PI_TEXT_HOOK を 決めた：
     PlacePartyMenuText（$14:$4403）の おわり「cd 46 0f / f1 ea ab d1 c9」の f1 から 5バイト（$14:$4436）を jp に して PartyItem を 呼ぶ。
     バンク$14 に 空きが ないので、つなぎは ROM0 の GetDexNumber（$3a93。どこからも 呼ばれない）に 置いた（PI_TEXT_STUB_ROM0。
     partyitem.asm に ROM0 に 置く 分かれ道を 足した）。wOptions は $d1ab。
  ・SameBoy で確かめたこと（通常版・60fps版、1コマずつ）：ずかん → 白から いっぺんに 一覧が 出る。手持ち（フィールド・戦闘）→ 画面と
    いっしょに「もちもの／○○」が 出る。カーソルを うごかすと かわる。ぶんぷから もどる・カントー・白黒（DMG）・パソコンの あずける画面も 前と 同じ。

■ 全ポケモンの連れ歩き（src/follow.asm・follow_talk.inc・follow_talk_data.inc・follow_pika.inc・follow_pika_data.inc・follow_data.inc。
  金銀連れ歩きキットの クリスタルで 入れた もの（follow_crystal.asm）を 金銀の しくみに した もの）
  ・ピカチュウ方式は 入って いなかったので、ユーザーに たずねて クリスタルと 同じく この 連れ歩きを 直接 入れた
    （ピカチュウも この しくみで 歩き、話しかけると ピカチュウフルカラーと 同じ 表情の 絵）。
  ・えらんだ ポケモン（はじめは 1匹目。手持ちの 画面で SELECT・赤い ★）が 主人公の 後ろを 歩く。タマゴも 歩く。
    ひんし・じてんしゃ・なみのり など では ボールに もどる。ドアから 出た あとは 1歩 歩くと 出る。白黒の ゲームボーイでは 出さない。
  ・正面は 手持ちの アイコンと 同じ 絵と 色、後ろ・横は 向きの ある 歩行グラフィック。夜でも 暗く しない。
  ・話しかけると ふりむいて 鳴き、気持ちの アイコンと 会話（会話文案.md）。ピカチュウは 表情の 絵（文章なし）。
  ・金銀で クリスタルと ちがう 所
    ・金銀の 人の 絵の 表は 外の マップで いっぱい なので、連れ歩きの 絵は 金銀が 使わない VRAM バンク1 に 置く
      （止まり $8660・歩き $8e60・白い したじき $8000）。InitSprite の パレットの and %111 を and %1111 に して、
      連れ歩きの オブジェクトの OBJECT_PALETTE の ビット3 で OAM の バンク1 を 出す。人の 絵の 表は かえないので、
      つながりで 人の 絵が 読みなおされる ことも ない。
    ・金銀の マップの 人は 2番から なので、連れ歩きは いつも 1番の マップオブジェクト。
    ・変数は セーブの 使われていない 所（$d786〜$d78c）、えらんだ 番号は $d7a3（レポートに 書かれる）。
    ・ピカチュウの 表情の 絵は 画面で 使って いない BG の 色を かりるが、3（みず）・4（きいろ）は かりない
      （タイルの アニメが 画面の 色に じかに 書くので、夜に 絵の 白が 紺色に なった）。
    ・つながりで 1フレーム 消えて いた（29ばんどうろ の 人を 出し入れする マップの スクリプトが、連れ歩きを 作る 前に
      スプライトを 並べなおして いた）→ 連れ歩きの オブジェクトを マップの コールバックより 先に 作る。
  ・SameBoy で確かめたこと（通常版・60fps版）：後ろを 歩く・ドア・つながり（ワカバ → 29ばんどうろ。1フレームずつ：
    消えない・はなれない・正面を 向かない・画面が 止まらない）・Bダッシュ・話しかけ・ピカチュウの 表情の 絵（夜も）・
    SELECT（★・だれも 連れ歩かない）・ならびかえ・ひんし／じてんしゃで ボール・タマゴ・ポケギアの あと・
    イベントで 人に ついて いく（29ばんどうろの つかまえかた）の あと もどる。
    歩く 速さ：通常版は 1歩 16フレームの まま。60fps版は 連れ歩きの オブジェクトが 1つ ふえる ぶん、
    3歩に 1回 ほど 17フレームに なる（歩きはじめの 処理が 2フレームに 入りきらない。連れ歩き なしは 16フレーム）。
  ・クレジット（公開する ときは ブログ用 HTML の クレジットに 書く。金銀連れ歩きキットの クレジット.txt）

■ あわせて 直した もの（金銀連れ歩きキットの「あわせて直したもの」）
  ・手持ちの ならびかえで アイコンの 色が 一瞬 おかしく なる（src/minis.asm の Minis_SetIconPal の おわり）。
  ・相手の HP の 数字で HP バーの 線が とぎれる（src/enemyhp.asm の EH_LINE_BELOW。銀の けす 所 8か所は src/enemyhp_silver.asm）。

■ クリスタル追加機能キットの 2・51〜57
  2. スタートメニューの ならびを ずかん・ポケモン・リュック・ポケギア・パソコン・主人公の名前・レポート・せってい に
     （src/features.asm。ポケギアの あとの $04:$6aed と とじる の $04:$6b0b。とじる は むしとり大会中 だけ）。
  51. 16この バッジの あと、四天王・ワタル・ライバルが 強く なる（src/league.asm・league_parties.inc。src/rematch_silver.asm で
      RM_LEAGUE。銀：wJohtoBadges $d56f・wKantoBadges $d570・wOtherTrainerID $d10d。手持ちは $43:$4a40）。
      確かめ：セキエイの ライバル（RIVAL2 の 4）が バッジ 16こ で Lv70〜75（たべのこし つき）、15こ では 元の Lv45〜50。
  52. 景品の わざマシンに わざの 名前（src/prizetm_silver.asm）。銀は コガネ（$13）・タマムシ（$27）の バンクに 空きが ないので、
      スクリプトの loadmenu / verticalmenu（4バイト）を callasm に して 新しい バンク（$43:$4f00）で メニューを 出す。
  53. サファリゾーンで 歩数と ボールを いつも 表示（src/safari/safari_silver.asm の SafariHUD）。銀には PlaceMapNameSign が
      ないので、場所の 名前の 札（mapsign.asm）の 札が 出て いない ときの 処理（MS_IDLE）から よぶ。文字の 絵は 札と 同じく
      VRAM バンク1 に 写す。
  54. そだてやで 今の レベルも おしえる（src/daycarehint.asm の DH_LEVEL。銀：おばあさん $05:$6d5a・GetBreedMon2LevelGrowth $6989・
      名前 $dbd5・$dc04）。
  55・56. 状態異常の 文字の 色・のこりの PP の 色（src/statuscolor_silver.asm。redballs.asm の RB_STATUSCOLOR・movepower.asm の MP_PPCOLOR）。
      金銀の 戦闘の わくは 状態異常が 名前の すぐ うしろに 出るので、PlaceNonFaintStatus（$14:$543c）を predef $21 に して、
      predef の 表の $21 を 新しい 処理（元と 同じ 文字を かいて から、その 行の 色を もどして 状態異常の ますに 色）に した。
      わざを えらび おわった あと PP の 色を 黒に もどす のは ParsePlayerAction（$0f:$4411）からの farcall。
  57. ずかんの タイプ・種族値・進化の ページ（src/dexinfo_silver.asm。SELECT。つかまえた ポケモン だけ）。
      銀の ずかんの 説明の 画面は クリスタルと 同じ 作り・同じ 場所（$10:$41b2・$4222・$42d2）。ボタンは $10:$41d9〜$41e5 を
      farcall に した（バンク$10 に 空きが ないので）。ページは $deeb・$deec。
  確かめたこと（SameBoy、通常版・60fps版）：メニューの ならびと パソコン、ライバルの 手持ち、コガネ・タマムシの 景品の メニューと
    えらんだ あと、サファリの 表示（メニューの あとも もどる・サファリを 出ると 消える）、そだてやの おじいさん・おばあさん、
    戦闘の 5種類の 状態異常（自分・相手）と PP の 黄・赤、わざの あとの 文が 黒、手持ちの 画面の 5種類と ★、
    ずかんの ページ（SELECT で 2・3ページ → 説明に もどる・ぶんぷ から もどる・B で もどる）。

■ むしとり大会と 重さの 修正キット（クリスタルで 直した ものを 銀に）
  1. むしとり大会中に ボックスが いっぱいでも おくれる（src/contestpc.asm の ContestPC_Send。銀の 値は src/contestpc_silver.asm）。
     いまの ボックスが いっぱい（30匹）なら、次の あいて いる ボックス（いまの 次から じゅんに。9 の 次は 1）へ 直接 おくる
     （「○○を ボックス２に おくりました！」）。ぜんぶ いっぱいなら 今までどおり「ボックスが いっぱいなので…」。
     大会中は レポートを 書けないので ボックスは 切りかえない。大会の あと フィールドで いつもの 自動切りかえ（autobox）が 動く。
     戦いの 中なので SaveBox・LoadBox（wBoxPartialData が 戦いの データと 同じ 所）は 使わず、SRAM から SRAM へ 1バイトずつ 写す
     （ContestPC_BoxCopy：sBox → いまの ボックスの 場所、おくる ボックス → sBox、入れる、sBox → おくる ボックス、いまの ボックス → sBox）。
     銀の 値：wCurBox $d8af、sBox $ad10（SRAM バンク1）、ボックス 1つ $54a バイト、ボックスの 場所は GetBoxCount.BoxBankAddresses
     （$38:$7dd9。バンク2 $a000・$a54a・$aa94・$afde・$b528・$ba72、バンク3 $a000・$a54a・$aa94）、写す 間の バンクは wStringBuffer2（$cf92）＋4・＋5、
     ボックスの 数字と "@" は GetPokemonName の あとに wStringBuffer2 へ。「ボ」は $1c。
  2. 人の 多い 所で 重いのを 直す
     (1) フィールドの ボールの 色（src/fieldcolors.asm の FC_END_HOOK）：OAM 1枚 ごとの call を やめて、その 人の OAM を 書きおえた あと
         （InitSprite の さいごの ld a, c / ldh [hUsedSpriteIndex], a、銀 $01:$5a20 の 79 e0 bf）で ボールの 下の 2枚を まとめて なおす。
         銀：FC_hUsedSpriteIndex $ffbf・FC_wShadowOAM $c300。.addsprite（$01:$5a14）は 元の まま。処理が 少し 大きく なったので
         FC_FREE を $01:$7fc3 に（$7fc3〜$7ffd）。
     (2) 60fps（src/fps60.asm）：銀は 前から まん中の 計算・VBlank で もどす 所の OAM の ループを call なしで 書いて いたので、そのまま。
     (3) 連れ歩きの 白い したじき（src/follow.asm の Fw_FixOAM）：OAM が もう いっぱい（hUsedSpriteIndex ≧ $a0）なら OAM の 中を さがさない。
         向きの 色だけは 連れ歩きの オブジェクトの 向き（Fw_FaceClass）で 見る。
  確かめたこと（SameBoy）：
    ・結果発表の ゲート（グループ10・17番。大会の 人 10人は 銀の イベントフラグ 1824〜1833 を 0。マップの データで 調べた）で
      5マス 歩く フレーム数（キーを おして から 5マスめ まで。12回の 平均。元の 銀は 92.5）：
        通常版 連れ歩き なし 93.5 → 93.1、あり 95.0 → 93.5。60fps版 なし 95.9 → 95.5、あり 97.8 → 97.1。
      60fps版で ゲートを 歩く 間の SCX は、前は 2ドットずつ（まん中を 出せない フレーム）の 所が 多かったが、直した あとは ほぼ 1ドットずつ。
      ワカバ（人が 少ない 所）は 連れ歩き なしで 1ドットずつ（前と 同じ）。
    ・人が 出て いる（直す 前と 同じ 人が 同じ 所に。OAM 40枚）、道具の ボール（くらやみのほらあな）・研究所の ボールの 見た目と
      OAM の 色が 前と 同じ、ゲートで 連れ歩きが 向きを かえた ときの 色。
    ・大会：sBox 30匹・ボックス2 0匹で「いれかえる？ はい → おくる はい」（ビードルが ボックス2へ、大会の ポケモンは キャタピー）、
      「いいえ → はい」（キャタピーが ボックス2へ、大会は ビードル）。どちらも sBox は 30匹の まま、いまの ボックスの 場所も sBox と 同じ。
      ぜんぶ いっぱいなら「ボックスが いっぱいなので…」。大会が おわって フィールドに もどると「ボックス１が いっぱいに なりました！
      ボックス２に じどうで きりかえました」（レポートが ある とき）。通常版・60fps版とも。

■ 手持ちの 画面の 状態異常の 文字（Ver.1.3.0 の あとに 直した もの）
  ・1匹目を 連れ歩いて いて その ポケモンが ねむり だと、手持ちの 画面で「ねむり」の「む」が べつの 文字に なって いた。
    状態異常の 文字（hlcoord 8〜10, 0 ＋ 2行 × 番号）は 色ちがいの ★（8, 0）・連れ歩きの ★（9, 0）の ますに かさなる。
    StatusColor_Party は ★の ますの 色を のこすので、その ますだけ バンク1 の 印が なく、バンク0 の タイル $76 が 出て いた
    （どく・やけど・こおり も まん中の 文字だけ HP の 赤の パレットに なって いた）。
    → StatusColor_PartyGlyph（src/statuscolor_silver.asm）で 文字の 3ます の 色を 1ます目と そろえる。
  ・状態異常の ある ポケモンを SELECT で 連れ歩くと、まん中の 文字が ★に なって いた（「ま★」）。
    → Fw_PartyMark（src/follow.asm）は 空いた ます（$7f）か ★の ますにだけ ★を 書く（状態異常の 文字が 出て いる ときは
      元の ゲームの 色ちがいの ★と 同じく 文字が かつ）。
  ・確かめ（通常版・60fps版）：戦闘の 入れかえ・フィールドの 手持ちで ねむり・どく・やけど・こおり・まひ、SELECT で ねむり／まひ の
    ポケモン → ほかの ポケモン（赤い ★ が 出る）。

■ 場所の 名前の 札が 白く なる ことが あった（Ver.1.3.1 の あとに 直した もの）
  ・マップに 入った ときの フェードの さいごが 札を 出した あとに なると（うずまきじま 地下2階に 殿堂入りの あと 入った とき など）、
    画面の 色が まとめて 書きなおされて パレット7 が 白に もどり、札が 白く なって いた。
    → src/mapsign.asm：札が 出て いる 間 まいフレーム、パレット7 の 色0 の 上の バイト（$43）を 見て、ちがえば クリスタルの 色を 書きなおす。
  ・確かめ（通常版・60fps版）：うずまきじま 地下2階（28, 9）に 入った とき 黄色の 札（前は 白）、イワヤマトンネル・シロガネやま・ウバメのもり・
    29ばんどうろ も 黄色、スタートメニューを ひらくと 札が 消えて メニューの わくは 白い まま。60fps 版で 1ドットずつ 動く。
  ・殿堂入りの あとの フリーザー・サンダー・ファイヤー：銀は 連れ歩きが マップオブジェクト 1番、鳥は 5番・5番・2番 なので ぶつからない。
    3羽とも 連れ歩き あり・なしで 出て、はなすと 戦闘に なる ことを 確かめた。

■ 金（ここから下は金で作ったときの説明）

元にしたROM：Pocket Monsters Kin (Japan) (Rev 1)  CRC32 4EF7F2A5（後期版）
  初版（CRC32 524478D4）に当てても、後期版＋追加機能と同じになるようにパッチを作る。

■ 入っている機能（クリスタルと同じ）
  1. Bボタンダッシュ（なみのりも速く）
  2. スタートメニューの「とじる」→「パソコン」（むしとり大会中は「とじる」のまま）
  3. 手持ちのポケモンを選ぶと「なまえ」（何も入れなければそのまま）
  4. 手持ちのポケモンを選ぶと「わすれる」（ひでんわざもOK、わざ1つのときは不可）
  5. 手持ちメニューが9項目以上なら横2列
  6. ひでんマシン01〜07を全ポケモンが覚えられる（build.py で基本データを書きかえ）
  7. 60fps（別の版。フィールドの移動だけ、速さ・タイミングは元のまま）
  8. オリジナルのバグ修正（src/bugfix.asm。通常版・60fps版の両方に入る）

■ ファイル
  src/gold_jp.inc   日本版 金のアドレス一覧（pret/pokegold を組み立てて、命令の並びで照合して調べた）
  src/version.inc   使うアドレス一覧を選ぶ（銀を作るときは silver_jp.inc に替える）
  src/features.asm  1〜5
  src/fps60.asm     7
  src/charmap_jp.inc 文字コード
  src/bugfix.asm    8（オリジナルのバグ修正）
  src/jp_all.inc    英語版 pokegold の全ラベル → 日本版 金のアドレス（自動生成。J_名前 / JB_名前）
  bf/               バグ修正で使う定数・データ（pg.inc は pokegold の定数を読みこむ。-I に pokegold を指定）
  tools/            アドレスを調べた道具（align.py / globalmap.py / genmap.py / npc2.py など）
  build.py          組み立て（rgbds 1.0.4）
  check.py          書きかえる所の元の命令が思った通りか確かめる
  mkips.py          IPS を作る（元のROMを何本でも渡せる。どれに当てても同じ結果になる）

  組み立てかた：後期版を base.gbc、初版を kin0.gbc として置いて
    python3 check.py base.gbc
    python3 build.py feat.gbc src/features.asm src/bugfix.asm
    python3 build.py feat60.gbc src/features.asm src/bugfix.asm src/fps60.asm
    （build.py の rgbasm に -I で pret/pokegold のフォルダを渡している）
    python3 mkips.py feat.gbc feat.ips kin0.gbc base.gbc feat60.gbc
    python3 mkips.py feat60.gbc feat60.ips kin0.gbc base.gbc feat.gbc

■ クリスタルとちがう所
  ・金銀はバンク4・9の空きが少ないので、表だけをバンク4（$7f58〜）・9（$7f34〜）に置き、
    処理はホーム（$0068〜$00ff、$3f10〜$3fff）に置いた。なまえ・わすれる の本体と 60fps の本体はバンク$3f（$6100〜、$6800〜）。
  ・金銀のスタートメニューには むしとり大会用の別のメニューが無い（項目の作り方で分けている）。
  ・金銀の HandleMapBackground には PlaceMapNameSign が無い。
  ・60fps の作業用メモリ：金銀はスタックが WRAM バンク1（$dfff から下）にあるので、
    クリスタルのように WRAM バンク2 に切りかえるとスタックがずれて止まる。
    日本版 金のゲームデータの後ろの使われていない所 $de40〜$dee7 を使う（初代ゲームボーイでも動く）。
  ・farcall は 6バイト（ld a / ld hl / rst $08）。英語版のラベルからずらして位置を出すときは注意。

■ 確かめたこと（SameBoy で）
  ・Bダッシュ：歩き 1マス16フレーム → 8フレーム。なみのり 16 → 8フレーム
  ・パソコン：マサキのパソコン などが開き、閉じるとフィールドにもどる。大会中は「とじる」
  ・なまえ：変えた名前が手持ちに出る。何も入れないと元のまま
  ・わすれる：なみのり（ひでんわざ）を忘れ、わざとPPが詰まる。わざ1つは「ひとつしかおぼえていない」。
    やめる・いいえ で元のまま
  ・手持ちメニュー 11項目で横2列、選んだ項目が正しく動く。7項目は今までどおり1列
  ・60fps：1フレームに1ドットずつ動く（自転車・ダッシュは2ドット）。マスを進むフレームは元と同じ。
    マップのつなぎ目・戦闘のあと・メニューを開いたときもずれない。初代ゲームボーイでも起動する

■ オリジナルのバグ修正（pret/pokecrystal と pret/pokegold の docs/bugs_and_glitches.md の番号）
  直したもの：
   0 ほろびのうた・まきびしで HP0 のまま倒れない / 1・3 こうげき・ぼうぎょが 1024 を超えると回る
   2 メタルパウダー / 4 追加効果100%でも 1/256 で出ない / 5 はらだいこ / 6 いかりのいでんし
   7 こんらんの自分へのダメージ / 8 さんせい等が みがわり の後に ぼうぎょ を下げる / 9 カウンター・ミラーコート
   10 かなしばり＋ポイントアップ で わるあがき にならない / 11 おいうち で倒れたポケモンの状態異常
   12 ロックオン・こころのめ / 13〜15・58 ふくろだたき / 16 プレゼント / 17 おんがえし・やつあたり
   18 りゅうのウロコ→ドラゴンのキバ / 19 最大HP4未満で入れかえると止まる / 20 自分の能力を上げる攻撃わざ
   21 スケッチ / 22 へんしん中を捕まえると メタモン / 23 レベル1の経験値 / 24 つかまえかた の説明で止まる
   25 状態異常と捕まえやすさ / 26 ムーンボール / 27 ラブラブボール / 28 スピードボール / 30 最大HP342以上
   31 まひ・やけど の能力ダウン / 32 アイスバッジ / 33〜43 AI / 44 テレポート / 45 ライバルの個体値
   46 HELD_CATCH_CHANCE / 47 エンディング後のわざ選び / 48 LoadMetatiles / 49 なみのり と マップのつなぎ目
   50 泳ぐNPC / 51 NPC の上で釣り / 52 育て屋の経験値 / 54 港のタイル / 55 アルフの遺跡の研究所の屋根の色
   56 ヤドンの井戸の石 / 57 アンノーンのタマゴ / 59・60 HPバー / 61 パークボール / 62 戦闘の始まりの画面
   63 NPC の見た目・色 / 65 スロットの音 / 66 ロケット団の曲 / 67 ぶつかる音 / 68 図鑑の鳴き声（回避策）
   69 にげる音 / 70 5けたの経験値 / 71・72 進化の石の表示 / 73 殿堂入り200回 / 75 デイジーの毛づくろい
   76 いかりのみずうみのコイキング / 78 コイキングの長さの計算 / 82 マニア / 84 ScriptCall / 86・87 野生のポケモン
   88 TryObjectEvent / 89 ReadObjectEvents / 91 BattleAnimCmd_ClearObjs / 92 せってい
   G2 セーブなしで殿堂入り / G5 NPC の上で なみのり / G6 ハナダジムで釣り
  日本版 金にはないので直していないもの：
   29 ヘビーボール（日本版は表の作りがちがい、バグがない） / 53 戦闘の「…」（金銀は直っている）
   64 たいあたり のアニメ（クリスタルだけ） / 74 イブキのわざマシン（クリスタルだけ）
   77 コイキングの長さのフィート・インチの変換（日本版は mm のまま） / 79 親の名前は5文字まで（日本版は5文字）
   85 LoadSpriteGFX（金銀は作りがちがう） / 90 ClearWRAM（金銀は WRAM のバンクを使わない）
   G1 コインケース（日本版は「…まい<DONE>」が文字の中にあって起きない。
      done を TX_END に替えると、黒いかたまりが出て メッセージが閉じなくなるので、直さない）
   G3 ラッキーナンバーのボックス10〜14（日本版は9ボックス） / G4・G7 英語の文章だけのバグ
  直していないもの：
   80 CheckOwnMonAnywhere（金銀ではどこからも使われていない） / 81 phonecall 命令（使われていない）
   83 セーブ中に電源を切ったとき（docs でも「かんたんで正確な直し方はない」）
  ※ 対戦の計算を直したので、直していないカートリッジ・ROM との通信対戦では、ずれることがある。
