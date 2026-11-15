"""カントーから きた 主人公（カントーの チャンピオン、マサラの お母さん）に あわせた ジョウトの ことば（第49弾の 銀版）：
   ・ウツギ はかせ：くれる ポケモンは ジョウトでの パートナー。ポケモンじいさんの あと（ずかんは オーキドが ジョウトでも
     つかえるように した）、たびの まえ（マサラの お母さん）、ふねの チケット（もう もって いるので さきに とってから わたす）。
   ・じょしゅ：主人公は つかまえかたを しって いる。ワカバの 女の人。お母さんの はじめての 電話。
   ・「3ねんほど まえ」→「つい この まえ」（ロケットだんを つぶした 子ども）。
   ことばは $E8 に おき、もとの 文の 所を farwritetext の スクリプトに して よぶ 命令を scall・sjump に かえる。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import jptext
from gsc import fo

CB, CA = 0xE8, 0x4E40
Q = '“'
S_S_TICKET = 0x44


def T(s): return b'\x00' + jptext.enc(s) + b'\x57'


TEXTS = {
    (0x13, 0x68BD): 'ウツギ' + Q + 'やあ　<PLAYER>くん<LINE>まっていたよ！<PARA>きょう　きみを　よんだのは<LINE>おねがいが　あるからなんだ！<PARA>'
                    'ぼくの　しりあいにね<LINE><POKEMON>じいさん　という<PARA>へんな　モノを　みつけてきては<LINE>だいはっけん！　って　おおさわぎする<CONT>'
                    'おじいさんが　いるんだよ<PARA>で　さっきね<LINE>こんどこそ　ほんものですぞ！<CONT>って　メールが　きたんだ<PARA>'
                    'きに　なるんだけど<LINE>ぼくも　じょしゅも　<POKEMON>の<CONT>けんきゅうで　いそがしくてね<CONT>かわりに　いってきてほしいんだ<PARA>'
                    'もちろん　ジョウトでの<LINE>パートナーとなる　<POKEMON>を<CONT>あげるよ<PARA>さいきん　みつけたばかりの<LINE>'
                    'めずらしい　<POKEMON>　だよ<CONT>さあ　えらんでよ！',
    (0x13, 0x6C46): 'ウツギ' + Q + 'え？　オーキドはかせが<LINE><POKEMON>ずかんを　ジョウトでも<CONT>つかえるように　してくれた！？<PARA>'
                    'さすが　オーキドはかせ　だね！<LINE>カントーの　チャンピオンの<CONT><PLAYER>くん　なら<PARA>'
                    'ジョウトの　ずかんも<LINE>きっと　すぐに　うまるよ！<PARA>'
                    '<POKEMON>も　なついてるようだし<LINE>ジョウトの　<POKEMON>ジムにも<CONT>ちょうせん　してみたら　どうかな？<PARA>'
                    'ここからだと　キキョウシティの<LINE><POKEMON>ジムが　いちばん　ちかいよ',
    (0x13, 0x6D1C): '<……>　<PLAYER>くん<LINE>ジョウトの　たびも<CONT>ながく　なると　おもう<PARA>'
                    'マサラの　おかあさんにも<LINE>れんらく　しておくんだよ',
    (0x13, 0x704E): 'ウツギ' + Q + 'やあ　<PLAYER>くん<LINE>まっていたよ！<PARA>きょう　きみを　よんだのは<LINE>あげたいものが　あるからなんだ！<PARA>'
                    'ほら！<LINE>ふねのチケット<PARA>これで　いつでも<LINE>カントーに　かえれるね！',
    (0x13, 0x7209): '<PLAYER>くん　なら<LINE>つかいかたは　わかってますよね！<PARA>ジョウトの　<POKEMON>も<LINE>どんどん　つかまえて　くださいね！',
    (0x35, 0x412E): 'まって！<LINE>ウツギはかせが<CONT>きみを　まってるわよ！<PARA>さきに　けんきゅうじょへ<LINE>いってらっしゃい！',
    (0x35, 0x4187): 'あら　<PLAYER>くん！<LINE>また　でかけるの？<PARA>きを　つけて<LINE>いってらっしゃい！',
    (0x36, 0x5949): 'もしもし…<PARA><……>　<PLAYER>？<LINE>オーキドはかせから　きいたわ<CONT>ジョウトに　ついたのね！<PARA>'
                    'おかねとかって　どうするの？<LINE>おかあさん　ちょきんしてあげようか？',
}
REPLACE = [(0x22, 0x6A37, '3ねんほど　まえ', 'つい　この　まえ')]
TICKET = (0x13, 0x6745)


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    a = CA; n = 0
    for (b, t), s in TEXTS.items():
        new = T(s); assert not any(rom[fo(CB, a):fo(CB, a) + len(new)]); rom[fo(CB, a):fo(CB, a) + len(new)] = new
        o = fo(b, t); assert rom[o] == 0x00; old_len = rom.index(0x57, o) - o + 1
        seg = range(fo(b, 0x4000), fo(b, 0x8000) - 2)
        refs = [k for k in seg if rom[k] in (0x4C, 0x51, 0x52) and rom[k + 1] == t & 0xFF and rom[k + 2] == t >> 8]
        kinds = {rom[k] for k in refs}; assert len(kinds) == 1 and refs, (hex(b), hex(t), kinds)
        kind = kinds.pop()
        far = bytes([0x4B, CB, a & 0xFF, a >> 8])
        stub = {0x4C: far + b'\x90', 0x51: b'\x6A\x47' + far + b'\x53\x49\x90', 0x52: b'\x47' + far + b'\x53\x49\x90'}[kind]
        assert len(stub) <= old_len
        rom[o:o + len(stub)] = stub
        for k in refs: rom[k] = 0x00 if kind == 0x4C else 0x03          # scall / sjump
        a += len(new); n += len(refs)
    for b, t, x, y in REPLACE:
        o = fo(b, t); e = rom.index(0x57, o); ex, ey = jptext.enc(x), jptext.enc(y); assert len(ex) == len(ey)
        i = rom.find(ex, o, e); assert i > 0; rom[i:i + len(ey)] = ey
    # ウツギの ふねの チケット：もって いる チケットを さきに とる（ことばの 所の あとに スクリプト）
    o = fo(*TICKET); assert rom[o:o + 3] == bytes([0x9D, S_S_TICKET, 1])
    st = 0x704E + 5; p = fo(0x13, st)
    rom[p:p + 7] = bytes([0x20, S_S_TICKET, 1, 0x9D, S_S_TICKET, 1, 0x90])
    rom[o:o + 3] = bytes([0x00, st & 0xFF, st >> 8])
    log.append('ジョウトの ことば %d（よぶ 所 %d、$%02X:$%04X〜$%04X）・ふねの チケット' % (len(TEXTS), n, CB, CA, a))
    return rom
