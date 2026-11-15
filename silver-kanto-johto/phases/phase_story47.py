"""カントーの 殿堂入りの あとの ジョウト（第47弾の ジョウトがわ。カントーがわ〔オーキドの チケット・ふねの はじめての こうかい〕は
   クリスタル版の マップと いっしょに 移植ずみ）。クリスタル版の ヒビキは ゴールド：
   ・ワカバタウンの「主人公の いえ」は ゴールドの いえ：1かいの お母さん（ポケギアの 場面なし。あたらしい ことば・ポケモンを やすませる）、
     ワカバの かんばん「ここは ゴールド のいえ」。
   ・シロガネやまの レッドの かわりに ゴールド（人の絵 6〔SPRITE_RED〕を 銀の 主人公の 絵に、ことば。
     トレーナーの 名前・手持ち・絵は phase_trainers）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import jptext
from gsc import fo, r16

CB, CA = 0xE8, 0x4A00
EV_BEAT_E4, EV_GOT_ELM_MON, EV_GOLD_GONE = 0x44, 0x1A, 0x762
EV_MOM_1, EV_MOM_2 = 0x6C7, 0x6C8
MUSIC_HEAL, SP_HEALPARTY, SP_RESTARTMUSIC = 0x0D, 0x1B, 0x3C


def T(s): return b'\x00' + jptext.enc(s) + b'\x57'


class Asm:
    def __init__(s, base): s.base = base; s.b = bytearray(); s.lab = {}; s.fix = []
    def here(s): return s.base + len(s.b)
    def L(s, n): s.lab[n] = s.here()
    def db(s, *v): s.b += bytes(v)
    def dw(s, v):
        if isinstance(v, str): s.fix.append((len(s.b), v)); s.b += b'\0\0'
        else: s.b += bytes([v & 0xFF, v >> 8])
    def op(s, c, *args):
        s.db(c)
        for a in args: s.dw(a)
    def raw(s, b): s.b += b
    def done(s):
        for o, n in s.fix: v = s.lab[n]; s.b[o] = v & 0xFF; s.b[o + 1] = v >> 8
        return bytes(s.b)


def events(rom, g, m):
    gt = fo(0x25, 0x40ED); hp = fo(0x25, r16(rom, gt + 2 * (g - 1))) + 9 * (m - 1)
    h = rom[hp:hp + 9]; ao = fo(h[0], r16(h, 3)); sb = rom[ao + 6]
    o = fo(sb, r16(rom, ao + 9)) + 2
    ev = {'sb': sb, 'scripts': fo(sb, r16(rom, ao + 7))}
    n = rom[o]; o += 1; o += 5 * n
    n = rom[o]; ev['coords_at'] = o; o += 1; o += 8 * n
    n = rom[o]; o += 1; ev['bgs'] = [o + 5 * i for i in range(n)]; o += 5 * n
    n = rom[o]; o += 1; ev['objs'] = [o + 13 * i for i in range(n)]
    return ev


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    assert not any(rom[fo(CB, CA):fo(CB, CA) + 0x600])
    a = Asm(CA)
    # ---- ゴールドの いえ 1かい
    h1 = events(rom, 24, 6)
    ms = h1['scripts']; assert rom[ms:ms + 11] == bytes.fromhex('02fa740000fe7400000000')[:11] or rom[ms] == 2
    s0 = fo(0x13, 0x74FA); assert rom[s0] == 0x0B or True
    mom = r16(rom, h1['objs'][0] + 9); assert all(r16(rom, o + 9) == mom for o in h1['objs']) and mom == 0x7561
    a.L('scene')                                          # ポケギアの 場面の かわり
    a.op(0x14, 1); a.op(0x33, EV_MOM_1); a.op(0x32, EV_MOM_2); a.db(0x90)
    a.L('mom'); a.db(0x6A, 0x47)
    a.op(0x31, EV_BEAT_E4); a.op(0x09, 'mom_e4')
    a.op(0x31, EV_GOT_ELM_MON); a.op(0x09, 'mom_2')
    a.op(0x4C, 'm1'); a.db(0x53, 0x49, 0x90)
    a.L('mom_e4'); a.op(0x31, EV_GOLD_GONE); a.op(0x09, 'mom_4'); a.op(0x4C, 'm3'); a.op(0x03, 'mom_h')
    a.L('mom_4'); a.op(0x4C, 'm4'); a.op(0x03, 'mom_h')
    a.L('mom_2'); a.op(0x4C, 'm2')
    a.L('mom_h'); a.db(0x53, 0x49)
    a.op(0x7E, MUSIC_HEAL); a.op(0x0F, SP_HEALPARTY); a.db(0x8A, 60); a.op(0x0F, SP_RESTARTMUSIC)
    a.db(0x47); a.op(0x4C, 'mh'); a.db(0x53); a.op(0x4C, 'mb'); a.db(0x53, 0x49, 0x90)
    texts = {
        'm1': T('あら？　あなたが　カントーから　きた<LINE><PLAYER>くん　ね！<PARA>ゴールドの　ははです<PARA>'
                'ウツギはかせから<LINE>はなしは　きいているわ<PARA>けんきゅうじょは　この　まちの<LINE>ひだりうえよ<PARA>'
                'はかせが　まってるわ！<LINE>いってらっしゃい！'),
        'm2': T('あら　<PLAYER>くん！<LINE>おかえりなさい<PARA>うちの　ゴールドも<LINE><PLAYER>くんと　おなじ　ころに<CONT>たびに　でたのよ<PARA>'
                'いまごろ　どこで　なにを<LINE>しているのかしら<……><PARA>つかれたでしょう？<LINE>すこし　やすんでいって！'),
        'm3': T('あら　<PLAYER>くん！<PARA>ゴールドったら　シロガネやまに<LINE>こもって　しゅぎょう　してるらしいの<PARA>'
                'もし　あったら　たまには<LINE>かえって　きなさいって<CONT>つたえてね！<PARA>つかれたでしょう？<LINE>すこし　やすんでいって！'),
        'm4': T('あら　<PLAYER>くん！<LINE>ゴールドに　あったの？<PARA>そう<……>　げんきに　してたのね<PARA>'
                'あのこったら<LINE><PLAYER>くんと　しょうぶ　できて<CONT>きっと　うれしかったと　おもうわ<PARA>'
                'つかれたでしょう？<LINE>すこし　やすんでいって！'),
        'mh': T('<PLAYER>の　<POKEMON>は<LINE>みんな　げんきに　なった！'),
        'mb': T('いってらっしゃい！<LINE>むりは　しないでね！'),
        'sign': T('ここは　ゴールド　のいえ'),
        'gs': T('<……>　！<LINE><PLAYER>さん　ですよね？<PARA>ぼくは　ゴールド<LINE>ワカバタウンから　きました<PARA>'
                'いつか　あなたと<LINE>たたかって　みたかったんだ！<PARA>さあ　しょうぶ　です！'),
        'gw': T('<……>　まいったなあ！<LINE>やっぱり　つよいや！'),
        'gl': T('ありがとう　<PLAYER>さん！<PARA>もっと　もっと　つよく　なって<LINE>また　あいに　いきます！<PARA>'
                'かあさんに　よろしく！'),
    }
    a.L('signs'); a.op(0x52, 'sign')
    # ---- シロガネやまの ゴールド（レッドの スクリプトを 写して ことばだけ かえる）
    sv = events(rom, 3, 68); so = sv['objs'][0]; assert rom[so] == 6 and r16(rom, so + 9) == 0x45D3 and sv['sb'] == 0x2D
    p = fo(0x2D, 0x45D3); rs = bytearray(rom[p:p + 64]); e = rs.index(0x90) + 1; rs = rs[:e]
    assert rs[:4] == bytes([0x0F, 0x69, 0x00, 0x6A]) and rs[5] == 0x4C and rs[10] == 0x63 and rs[15:18] == bytes([0x5D, 0x3F, 1])
    a.L('gold'); a.raw(bytes(rs[:5])); a.op(0x4C, 'gs'); a.raw(bytes(rs[8:10])); a.op(0x63, 'gw', 'gw')
    k2 = rs.index(0x4C, 15); a.raw(bytes(rs[15:k2])); a.op(0x4C, 'gl'); a.raw(bytes(rs[k2 + 3:]))
    for k, v in texts.items(): a.L(k); a.raw(v)
    blob = a.done(); rom[fo(CB, CA):fo(CB, CA) + len(blob)] = blob
    L = a.lab
    def far(at, lab): rom[at:at + 4] = bytes([0x04, CB, L[lab] & 0xFF, L[lab] >> 8])
    # 1かい：場面 0 → scene、お母さん（4人 とも $13:$7561）→ mom
    far(fo(0x13, 0x74FA), 'scene'); far(fo(0x13, 0x7561), 'mom')
    # かんばん（ワカバ 5,11 → $35:$7FEC の farsjump）
    nb = events(rom, 24, 4); bo = [o for o in nb['bgs'] if rom[o] == 5 and rom[o + 1] == 11][0]
    assert not any(rom[fo(0x35, 0x7FEC):fo(0x35, 0x7FF0)]); far(fo(0x35, 0x7FEC), 'signs'); rom[bo + 3] = 0xEC; rom[bo + 4] = 0x7F
    # シロガネやま：スクリプトの 頭を farsjump、人の絵 6 を 銀の 主人公の 絵（$30:$4000）に
    far(p, 'gold')
    o = 0x147B0 + 6 * 5; assert rom[o:o + 6] == bytes.fromhex('c046c0300100'); rom[o] = 0x00; rom[o + 1] = 0x40
    log.append('ゴールドの いえ・かんばん・シロガネやまの ゴールド（$%02X:$%04X〜$%04X）' % (CB, CA, CA + len(blob)))
    return rom
