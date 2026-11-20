#!/usr/bin/env python3
"""ブログ用 HTML（画像入り）：ポケットモンスター金 カントー＆ジョウト
   python3 mkhtml_gold.py 手本.html 画像の フォルダ 完成.gbc 出力.html
   手本：金銀移植キットの「ブログ参考/ポケットモンスター クリスタル カントー＆ジョウト_ブログ用.html」。
   ・追加機能の 節（説明と 画像）は 手本の まま 使い、「クリスタル 追加機能パッチ」を「金 追加機能パッチ」に、
     金で ちがう 所（メニュー・つよさの 画面の ハート・バグ修正の 一覧 など）を 書きかえる。
   ・この パッチの オリジナルの 節の 画像は 金の ROM で とった もの（画像の フォルダ）。見出し画像も ここで 作る。
   ・色は 金の 色（手本の 青を 金色に）。"""
import base64, io, re, sys, zlib, hashlib
from PIL import Image, ImageDraw, ImageFont

REF = open(sys.argv[1], encoding='utf-8').read()
IMGD = sys.argv[2].rstrip('/') + '/'
ROM = open(sys.argv[3], 'rb').read()
OUT = sys.argv[4]
NAME = 'ポケットモンスター金 カントー＆ジョウト'
CRC = '%08X' % zlib.crc32(ROM); SHA = hashlib.sha1(ROM).hexdigest()
HISTORY = [('2026/11/20', '1.0.1', ['タイトル画面のメニューから B で戻ると、画面がこわれて先に進めなかったのを直しました（オープニングを飛ばしてタイトル画面にもどります）']),
           ('2026/11/19', '1.0.0', ['初回リリース'])]

COL = {'#0e3a66': '#5a3a06', '#1565a6': '#8a5a08', '#2b7bb9': '#b8860b', '#3d6480': '#7a5a1a', '#8cc8e6': '#e0c070',
       '#9ad8f5': '#f5d77a', '#eaf7fd': '#fdf6e3', '#f3fbfe': '#fffaf0'}
H2S = 'margin:36px 0 12px;padding:10px 14px;font-size:21px;color:#fff;background:linear-gradient(90deg,#0e3a66,#2b7bb9);border-radius:6px;border-left:8px solid #9ad8f5;'
H3S = 'margin:24px 0 8px;padding:4px 0 4px 10px;font-size:18px;color:#0e3a66;border-left:5px solid #2b7bb9;border-bottom:1px dashed #8cc8e6;'
def H2(t): return f'<h2 style="{H2S}">{t}</h2>'
def H3(t): return f'<h3 style="{H3S}">{t}</h3>'
def P(t): return f'<p style="line-height:1.85;margin:8px 0;">{t}</p>'
def UL(items): return '<ul style="line-height:1.85;margin:6px 0 10px;">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
def BOX(t): return f'<div style="border:2px solid #2b7bb9;background:#eaf7fd;border-radius:8px;padding:10px 14px;margin:12px 0;line-height:1.85;">{t}</div>'


def uri(path, scale=2):
    im = Image.open(IMGD + path).convert('RGB')
    if scale != 1: im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


def IMG(*paths, cap=None):
    imgs = ''.join(f'<img src="{uri(p)}" alt="" width="320" height="288" style="width:320px;max-width:100%;height:auto;image-rendering:pixelated;border:3px solid #8cc8e6;border-radius:4px;background:#000;" />' for p in paths)
    c = f'<div style="text-align:center;font-size:13px;color:#3d6480;margin:-4px 0 10px;">{cap}</div>' if cap else ''
    return f'<div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:12px 0;">{imgs}</div>' + c


def header():
    W, H = 1280, 720
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    c1, c2 = (150, 104, 20), (70, 40, 10)
    for x in range(W):
        t = x / W; d.line([(x, 0), (x, H)], fill=tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3)))
    F = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
    f1, f2 = ImageFont.truetype(F, 62), ImageFont.truetype(F, 28)
    def ctext(y, s, f, fill, stroke=0, sc=None):
        w = d.textlength(s, font=f); d.text(((W - w) / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc)
    ctext(30, NAME, f1, (255, 255, 255), 5, (40, 24, 6))
    ctext(118, 'サトシになって マサラタウンから旅立ち、カントー、そしてジョウトへ', f2, (255, 226, 140))
    t = Image.open(IMGD + 'title.png').convert('RGB').resize((480, 432), Image.NEAREST)
    bx = Image.new('RGB', (488, 440), 'white'); bx.paste(t, (4, 4)); im.paste(bx, (28, 178))
    for k, s in enumerate(['PalletTown', 'PewterCity', 'CeruleanCity', 'NewBarkTown', 'GoldenrodCity', 'EcruteakCity']):
        a = Image.open(IMGD + s + '.png').convert('RGB').resize((224, 202), Image.NEAREST)
        fr = Image.new('RGB', (232, 210), (255, 255, 255)); fr.paste(a, (4, 4)); im.paste(fr, (546 + (k % 3) * 240, 184 + (k // 3) * 222))
    ctext(652, '151匹・第二世代・追加機能・60fps', f2, (255, 255, 255))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=90)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


# ---- 手本の「追加した機能」の 節
a = REF.index('追加した機能（「クリスタル 追加機能パッチ」から）</h2>'); a = REF.index('<h3', a)
b = REF.index('<h2', a)
secs = {}
for m in re.finditer(r'<h3[^>]*>(\d+)\. (.*?)</h3>(.*?)(?=<h3|\Z)', REF[a:b], re.S):
    secs[int(m.group(1))] = [m.group(2), m.group(3)]
assert len(secs) == 49, len(secs)
assert secs[49][0] == '元のゲームのバグ修正'
IMGRE = r'<div style="display:flex.*?</div>(<div style="text-align:center;font-size:13px;color:#3d6480;[^"]*">.*?</div>)?'
def setsec(n, html, title=None):
    if title: secs[n][0] = title
    secs[n][1] = html

setsec(2, P('スタートメニューに「<b>パソコン</b>」を足しました。どこでもポケモンセンターのパソコン（ボックス・じぶん・オーキド など）が使えます。'
            'メニューの ならびは、ずかん・ポケモン・リュック・ポケギア・パソコン・主人公の名前・レポート・せってい です。メニューは B か START で閉じられます。')
       + IMG('menu_pc.png'))
t3 = re.sub(IMGRE, '', secs[3][1], flags=re.S); setsec(3, t3 + IMG('party_sub.png'))
t28 = secs[28][1]; m28 = re.search(IMGRE, t28, re.S)
setsec(28, t28[:m28.start()] + IMG('stats1.png', cap='なつき度のハート（タイプが2つのポケモンも、2つめのタイプが見えます）') + t28[m28.end():])

BUGS = [('バトル', 'ほろびのうた・まきびしでHPが0になっても倒れない／追加効果100%のわざが1/256で効果なし／はらだいこ／いかりのいでんしのこんらんが長く続く／'
                 'メタルパウダー／かなしばり＋ポイントアップでわるあがきにならない／おいうちで倒れたポケモンの状態異常／こんらんの自分へのダメージ／'
                 'みがわりを壊したあとにぼうぎょを下げる／攻撃して能力を上げるわざ／りゅうのキバ／スケッチ／最大HP3以下のポケモンとの入れかえで止まる／'
                 'まひ・やけどの能力ダウン／アイスバッジ／野生のテレポート／ライバルの個体値'),
        ('捕獲', 'へんしん中を捕まえるとメタモンになる／状態異常で捕まえやすくならない／最大HP342以上の計算／持たせた道具の効果／ムーンボール／ラブラブボール／'
                 'スピードボール／パークボールのアニメ／つかまえかたを見せる人で止まる'),
        ('コンピューターの作戦', 'くろいまなざし／テクスチャー2／にほんばれ／あとから効くわざ／あくむ／みらいよち／タイプの調べ方／道具の使い方'),
        ('その他', 'ポケモン（人）の上で釣りができる・なみのりで乗れる／ハナダジムの水で釣りができる／育て屋でけいけんちが減る／レベル1のけいけんち／'
                   '5けたのけいけんちの表示／HPバーの動き／戦闘の始まりの画面／トレーナーの見た目と色／ロケット団の戦闘の曲／スロットの音／にげる音／'
                   '進化の石の表示／殿堂入り200回の表示／デイジーの毛づくろい／コイキングの長さ／ツボツボのマニア／アンノーンのタマゴ／'
                   'セーブしていない殿堂入りでボックスがこわれる／せっていを開いた瞬間の左右／エンディングのあとのわざ選び／'
                   'アルフのいせきの研究所の屋根の色／ヤドンのいどの石のタイル／港のじゅうたんのタイル／スクリプト・マップ・アニメの作りのバグ')]
TD = 'padding:6px 8px;border:1px solid #8cc8e6;'
setsec(49, P('元のゲームにあったバグ（70か所ほど）を直しています。')
       + f'<div style="overflow-x:auto;"><table style="border-collapse:collapse;margin:8px 0 12px;font-size:15px;"><tr><th style="{TD}background:#2b7bb9;color:#fff;">分類</th><th style="{TD}background:#2b7bb9;color:#fff;">直したバグ</th></tr>'
       + ''.join(f'<tr><td style="{TD}white-space:nowrap;vertical-align:top;">{k}</td><td style="{TD}">{v}</td></tr>' for k, v in BUGS) + '</table></div>'
       + P('※ コインケースのバグは、このゲームではもともと起きないので、そのままです。'))
for n in secs:
    for k in range(2):
        secs[n][k] = secs[n][k].replace('クリスタル 追加機能パッチ', '金 追加機能パッチ')
KEEP = list(range(1, 50))
left = [n for n in KEEP if 'クリスタル' in secs[n][1] or 'クリスタル' in secs[n][0]]
assert not left, [(n, secs[n][0]) for n in left]

o = ['<meta charset="utf-8" />', '<div style="font-size:16px;color:#333;max-width:760px;margin:0 auto;">']
o.append(f'<div style="text-align:center;margin:0 0 16px;"><img src="{header()}" alt="{NAME}" style="width:100%;max-width:760px;height:auto;border-radius:8px;" /></div>')
o.append(P('『ポケットモンスター金』を、<b>サトシ</b>になって マサラタウンから旅立つ物語に作りかえたパッチです。'
           'カントーでは初代ポケモンシリーズ（赤・緑・青・ピカチュウ）のストーリーをたどり、<b>カントーで151匹すべて</b>ゲットできるようにしました。'
           'カントーで殿堂入りしたあとは、船でワカバタウンへ渡って、ジョウトで金の物語が始まります。ジョウトでは<b>第二世代のポケモンをすべて</b>ゲットできるようにしました。'))
o.append(P('さらに「金 追加機能パッチ」の機能（Bボタンダッシュ・連れ歩き・<b>60fps</b> など）と、元のゲームのバグ修正も入っています。'))
o.append(BOX('<b>ゲームボーイカラー専用です</b><br />パッチを当てたファイルは、拡張子を <b>.gbc</b> にして、<b>ゲームボーイカラーのコア（モード）</b>で起動してください。<br />'
             'パッチを当てると ROM は <b>4MB</b>（4,194,304 バイト・<b>MBC30</b>）になります。<b>4MB の MBC30 に対応したエミュレーター</b>で遊んでください。<br />'
             '<b>動くもの</b>：SameBoy（動作を確かめています）・mGBA・BGB・VBA-M（2.1.5 以降）・Pizza Boy GBC Pro（5.4.5 以降）・RetroArch の SameBoy コア／mGBA コア など<br />'
             '<b>動かないもの</b>：gambatte（RetroArch の gambatte コアや、gambatte を使う中華エミュレーター機をふくむ）・ゲームボーイカラー本体＋エバードライブなどのフラッシュカート（MBC30 の 4MB に対応したカートリッジでないと動きません）<br />'
             '対応していないものでは、著作権の画面のあと オープニングに進まずに止まります。'))

orig = []   # (見出し, html)
def OS(title, html): orig.append((title, html))
OS('サトシになって マサラタウンから旅立つ',
   P('オープニングとタイトル画面は初代ポケモンシリーズ（ゲンガーとニドリーノ・ヒトカゲ）です。主人公の名前は自由に決められて、「サトシ」も選べます。ライバルはシゲルで、名前も自分で決められます。')
   + P('さいしょから始めると、初代シリーズと同じく 自分の部屋のゲーム機の前から始まります。パソコンには キズぐすりが1こ入っています。')
   + IMG('title.png', 'PalletTown.png'))
OS('カントーは初代ポケモンシリーズのストーリー',
   UL(['町・道路・ダンジョンは初代シリーズのマップです（トキワのもり・おつきみやま・サントアンヌ号・ロケット団のアジト・ポケモンタワー・シルフカンパニー・ふたごじま・ポケモンやしき・ハナダのどうくつ など）。',
       'ジムリーダー・トレーナー・四天王・チャンピオンも、初代シリーズと同じ手持ちとセリフです。',
       'ポケモンタワーでは、シルフスコープがないと「ゆうれい」が出てきます。',
       'シゲルが出てくるときは、初代シリーズと同じシゲルの曲（ライバルあらわる）が流れます。',
       'カントーの町や道路も、ジョウトと同じく朝・昼・夜で色が変わります。',
       'カントーで殿堂入りすると、初代シリーズの殿堂入りとスタッフロールが流れます。'])
   + IMG('PewterCity.png', 'CeruleanCity.png') + IMG('CeladonCity.png', 'LavenderTown.png'))
OS('ムサシとコジロウ',
   P('ロケット団の<b>ムサシとコジロウ</b>が、『ピカチュウ』のようにカントーの行く先々で勝負をしかけてきます。マップの上の絵とバトルの絵は「ポケットモンスターピカチュウフルカラー」と同じです。'
     'バトルの絵は2人を塗り分けていて、<b>コジロウは青紫の髪、ムサシは赤紫の髪</b>、2人とも肌色と白い服です。')
   + P('ジョウトでも、ヤドンのいど・いかりのみずうみのアジト・ラジオとうのロケット団の場面に登場します。') + IMG('musashi.png', cap='ヤドンのいどのムサシとコジロウ'))
OS('カントーで151匹すべてゲットできる',
   P('カントーの野生・つり・もらうポケモンなどを見直して、<b>カントーだけで151匹すべて</b>ゲットできるようにしました。第二世代のポケモンはカントーには出ません。'
     'ピカチュウは赤・緑・青と同じ場所に出ます。'))
OS('フシギダネ・ヒトカゲ・ゼニガメがもらえる',
   P('『ピカチュウ』と同じ人・同じ話で、フシギダネ（ハナダシティの家の女の人）・ヒトカゲ（24ばんどうろ）・ゼニガメ（クチバシティのジュンサー）がもらえます。'))
OS('タマムシのゲームコーナーの景品',
   P('ポケモンの景品は『ピカチュウ』と同じです（ケーシィ・ロコン・プクリン、「つぎへ」でストライク・カイロス・ポリゴン）。わざマシンの景品も初代シリーズと同じです。') + IMG('prize.png'))
def _osec(n):
    m = re.search(r'<h3[^>]*>%d\. (.*?)</h3>(.*?)(?=<h3|<h2)' % n, REF[REF.index('>このパッチのオリジナル</h2>'):], re.S)
    t, h = m.group(1), m.group(2)
    for a2, b2 in (('クリスタルのわざマシン', '金のわざマシン'), ('クリスタルのもの', '金のもの'), ('クリスタルでは', '金では'),
                   ('クリスタルのポケモン', '金のポケモン'), ('クリスタルと同じ', '元の『金』と同じ'), ('クリスタルのまま', '金のまま'),
                   ('クリスタルにも', '金にも'), ('クリスタル', '金')):
        h = h.replace(a2, b2)
    return t, h
for _n in (17, 18): OS(*_osec(_n))
OS('殿堂入りしたら船でジョウトへ',
   P('カントーで殿堂入りすると、オーキドはかせから船のチケットがもらえます。はじめての船はクチバからワカバタウンへ向かい、ジョウトの物語が始まります（2回目からはアサギシティ行きです）。'
     'ワカバタウンの家は金の主人公「ゴールド」の家です。手持ちのポケモンは、カントーからそのまま連れて行けます。')
   + IMG('NewBarkTown.png', 'GoldenrodCity.png'))
OS('ジョウトでは第二世代のポケモンをすべてゲットできる',
   P('ジョウトの野生・つり・ずつき・いわくだき・むしとり大会・もらうポケモン・景品・交換は第二世代のポケモンだけにして、<b>ジョウトで第二世代のポケモンをすべて</b>ゲットできるようにしました'
     '（『銀』にしか出ないポケモンも、ジョウトのどこかで手に入ります）。第一世代から進化するポケモン（クロバット・ハガネールなど）は、カントーから連れてきて進化させます。'
     'いかりのみずうみの赤いギャラドスはそのままです。')
   + IMG('EcruteakCity.png'))
OS('ジョウトの御三家は3匹ともらえる', P('ウツギはかせのところで1匹えらぶと、のこりの2匹ももらえます。'))
OS('通信交換で進化するポケモンはレベル37で進化',
   P('ユンゲラー・ゴーリキー・ゴローン・ゴースト・ニョロゾ（ニョロトノ）・シードラ・イワーク・ストライク・ポリゴンは、レベル37になると進化します。ヤドンは おうじゃのしるし を持たせてレベル37以上でレベルが上がるとヤドキングに進化します。'))
OS('セレビィ', P('ジョウトで殿堂入りしたあと、ウバメのもりのほこらで<b>レベル70</b>のセレビィに会えます。つかまえなかったとき（負けた・たおした・にげた）は、つぎの殿堂入りのあとにまた会えます。'))
OS('ジョウトは3年後の物語',
   P('ジョウトの物語は、サトシがカントーのチャンピオンになってから3年後です。ワタル・四天王・ライバル・オーキドはかせなどのセリフを、「カントーのチャンピオンのサトシ」に合わせて作りなおしています。'))
OS('リニアが走る（ヤマブキシティに駅）',
   P('ジョウトで殿堂入りしたあと、コガネシティとヤマブキシティをむすぶリニアが走りはじめます。ヤマブキシティに駅の入口を作りました。'
     'リニアのていきけんは、元の『金』と同じく ヤマブキのモノマネむすめに「なくしたピッピにんぎょう」を届けるともらえます。'))
OS('カントーのジムリーダーと再戦',
   P('ジョウトで殿堂入りしたあと、カントーのジムリーダーに話しかけると再戦できます。セキチクジムはアンズ、トキワジムはシゲル、カツラはふたごじまにいます。'
     'ジムリーダーは3年ぶりに会うサトシに話しかけてきます。2回目からは「また しょうぶ しよう」という短いセリフになります。'))
OS('シロガネやまのゴールド', P('ジョウトで殿堂入りしたあと、シロガネやまの奥では 金の主人公「<b>ゴールド</b>」が待っています。') + IMG('gold_talk.png', 'gold_battle.png'))
OS('サファリゾーン（初代シリーズ）',
   P('セキチクシティの北のサファリゾーンは初代シリーズと同じです（500円でサファリボール30こ・500歩、ボール・エサ・いし・にげる）。ひみつの家でなみのりのひでんマシン、きんのいればで かいりきのひでんマシンがもらえます。'
     '中を歩いているあいだは、画面の下に残りの歩数とボールの数をいつも表示します。'))

o.append(BOX('<b>ここが変わります（まとめ）</b><ul style="margin:4px 0 0;padding-left:1.4em;">' + ''.join(f'<li>{t}</li>' for t, _ in orig)
             + ''.join(f'<li>{secs[n][0]}</li>' for n in KEEP) + '</ul>'))

# バグ報告（手本と 同じ 形。値は この パッチ）
i = REF.index('バグ報告をする前に確認してください'); i = REF.rindex('<div', 0, REF.rindex('<div', 0, i))
j = REF.index('ギガファイル便にアップロードしたリンク）</div></div>', i) + len('ギガファイル便にアップロードしたリンク）</div></div>')
bug = REF[i:j]
RCRC = re.search(r'CRC32：([0-9A-F]{8})', REF).group(1)
assert bug.count(RCRC) == 2 and bug.count('ポケットモンスター クリスタル カントー＆ジョウト.ips') == 1
bug = bug.replace(RCRC, CRC).replace('ポケットモンスター クリスタル カントー＆ジョウト.ips', NAME + '.ips')
o.append(bug)

o.append(H2('あらすじ'))
o.append(P('マサラタウンに住む少年<b>サトシ</b>は、オーキドはかせからはじめてのポケモンをもらい、ライバルの<b>シゲル</b>と競いながらカントー地方の旅に出ます。'))
o.append(P('トキワのもり・おつきみやま・ハナダ・クチバ……と町をめぐってジムリーダーに勝ち、バッジを集めていきます。行く先々では、ロケット団の<b>ムサシとコジロウ</b>が待ちかまえています。'
           'タマムシのゲームコーナーの地下にあるロケット団のアジト、ポケモンタワーのゆうれい、ヤマブキのシルフカンパニーと、ロケット団のたくらみをくじきながら、8つのバッジをそろえて セキエイこうげんのポケモンリーグへ。'
           '四天王とチャンピオンになったシゲルに勝てば、殿堂入りです。'))
o.append(P('殿堂入りのあと、オーキドはかせから<b>船のチケット</b>をもらったサトシは、クチバから船に乗って ジョウト地方のワカバタウンへ。物語はカントーのチャンピオンになってから<b>3年後</b>です。'
           'ウツギはかせのもとで ジョウトのポケモンと出会い、新しいライバルや よみがえったロケット団、伝説のポケモンをめぐる ジョウトの冒険が始まります。'))
o.append(P('ジョウトでも殿堂入りすると、リニアが走りはじめ、3年ぶりのカントーのジムリーダーとの再戦、ウバメのもりのセレビィ、そしてシロガネやまで待つ<b>ゴールド</b>との戦いが待っています。'))

o.append(H2('このパッチのオリジナル'))
for k, (t, h) in enumerate(orig, 1):
    o.append(H3('%d. %s' % (k, t))); o.append(h)
o.append(H2('追加した機能（「金 追加機能パッチ」から）'))
o.append(P('「金 追加機能パッチ」の機能（251匹そろう版をのぞく）が入っています。画面の写真の一部は、同じ機能のクリスタル版のものです。'))
for k, n in enumerate(KEEP, 1):
    o.append(H3('%d. %s' % (k, secs[n][0]))); o.append(secs[n][1])
o.append(BOX('<b>60fpsについて</b><br />このパッチは、フィールドを歩くときの動きを1ドットずつ（60fps）にしています。歩く・走る（Bダッシュ）・自転車・なみのり、外・建物の中のどれでもなめらかに動きます。ゲームの速さ・タイミングは元のままです。'))

# 遊び方（手本から、元の ROM・名前・値を この パッチに）
i = REF.index('>遊び方（パッチの当て方）</h2>'); i = REF.rindex('<h2', 0, i)
j = REF.index('>確認用の値（パッチを当てたあとのROM）</h2>'); j = REF.rindex('<h2', 0, j)
howto = REF[i:j]
howto = howto.replace('『ポケットモンスター クリスタル』', '『ポケットモンスター金』')
howto = howto.replace('「ポケットモンスター クリスタル カントー＆ジョウト_リリース.zip」', f'「{NAME}_リリース.zip」')
mt = re.search(r'<tr[^>]*><td[^>]*>ポケットモンスター クリスタル</td>.*?</tr>', howto, re.S); assert mt, 'CRC の 表'
row = mt.group(0)
r1 = row.replace('ポケットモンスター クリスタル', 'ポケットモンスター金（初期版）').replace('270C4ECC', '524478D4').replace('2,097,152 バイト（2MB）', '1,048,576 バイト（1MB）')
r2 = row.replace('ポケットモンスター クリスタル', 'ポケットモンスター金（後期版）').replace('270C4ECC', '4EF7F2A5').replace('2,097,152 バイト（2MB）', '1,048,576 バイト（1MB）')
howto = howto.replace(row, r1 + r2)
howto = howto.replace('ポケットモンスター クリスタル カントー＆ジョウト', NAME)
howto = howto.replace('違うときは、吸い出しをやり直してください。', '初期版・後期版のどちらでも使えます（パッチを当てると、どちらも同じROMになります）。違うときは、吸い出しをやり直してください。')
howto = howto.replace('元の『クリスタル』とちがうので、元の『クリスタル』のセーブデータでは遊べません', '元の『金』とちがうので、元の『金』のセーブデータでは遊べません')
for bad in ('クリスタル', '270C4ECC', '2,097,152'): assert bad not in howto, bad
o.append(howto)

o.append(H2('確認用の値（パッチを当てたあとのROM）'))
o.append(f'<div style="font-family:monospace;font-size:14px;word-break:break-all;overflow-wrap:anywhere;background:#f3fbfe;border:1px solid #8cc8e6;border-radius:4px;padding:6px 8px;margin:4px 0 10px;">CRC32：{CRC}<br />SHA-1：{SHA}<br />サイズ：4,194,304 バイト</div>')
o.append(H2('注意事項'))
o.append(UL(['バトルの計算のバグを直しているので、パッチを当てていないカートリッジ・ROMとの通信対戦では、結果がずれることがあります。',
             'エミュレーターの「ステートセーブ」は、パッチの版をまたいで使わないでください（画面がくずれたり止まったりすることがあります）。ゲームの中の「レポート」でのセーブは、そのまま使えます。',
             'パッチは自己責任で使ってください。元のROMは、必ずコピーを残しておいてください。']))
o.append('<div style="border:2px solid #c0392b;background:#fff3f0;border-radius:8px;padding:10px 14px;margin:12px 0;line-height:1.85;"><b>不具合を見つけたら</b><br />'
         'どの端末（パソコン・Android・iPhone・中華エミュレーター機など）とエミュレーターを使って、どの場所で、何をしたときに起きたかを、コメントで教えてください。できれば画面の写真や動画もあると助かります。</div>')
o.append(H2('更新履歴'))
o.append(f'<div style="overflow-x:auto;"><table style="border-collapse:collapse;margin:8px 0 12px;font-size:15px;"><tr><th style="{TD}background:#2b7bb9;color:#fff;">日付</th><th style="{TD}background:#2b7bb9;color:#fff;">内容</th></tr>'
         + ''.join(f'<tr><td style="{TD}white-space:nowrap;vertical-align:top;">{d}</td><td style="{TD}">Ver.{v}'
                   + ('　' + items[0] if len(items) == 1 else '<ul style="margin:4px 0 0;padding-left:1.4em;">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>')
                   + '</td></tr>' for d, v, items in HISTORY) + '</table></div>')
i = REF.index('>クレジット</h2>'); i = REF.rindex('<h2', 0, i)
cred = REF[i:REF.rindex('</div>')]
cred = cred.replace('pret/pokecrystal（逆アセンブル）', 'pret/pokegold・pret/pokecrystal（逆アセンブル）')
cred = cred.replace('サファリゾーンのバトル：サファリゾーン入りのクリスタル改造ROM', 'サファリゾーンのバトル：サファリゾーン入りの改造ROM')
cred = cred.replace('</ul>', '<li>もとにしたパッチ：ポケットモンスター クリスタル カントー＆ジョウト</li></ul>', 1)
o.append(cred)
o.append('</div>')
html = '\n'.join(o) + '\n'
DRIVE = 'https://drive.google.com/drive/folders/1F6hFvKp835elROuIJ6M7XStGfC9iq2z6'
GH = 'https://github.com/yyoossk/pkm-jp-full-color-patch/releases/tag/v2.0'
html = re.sub(r'https://drive\.google\.com/drive/folders/[A-Za-z0-9_-]+(\?usp=drive_link)?', DRIVE, html)
html = html.replace('https://github.com/yyoossk/pkm-jp-full-color-patch/releases', GH)
for k, v in COL.items(): html = html.replace(k, v)
body = re.sub(r'data:image/[a-z]+;base64,[A-Za-z0-9+/=]+', '', html)
for bad in ('日本語', '日本版', '海外版', '欧州版', '移植', 'ヒビキ', '『赤』どおり', '赤どおり'):
    assert bad not in body, bad
open(OUT, 'w', encoding='utf-8').write(html)
print(OUT, len(html), CRC)
