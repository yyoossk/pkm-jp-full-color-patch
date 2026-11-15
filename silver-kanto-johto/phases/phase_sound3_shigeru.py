"""シゲルが 出る・去る ときの 曲を 赤と 同じ「ライバル あらわる」に（第98弾の 銀版）：
   赤フルカラーの Music_MeetRival（赤の バンク 2、$71C8）を 金銀の 音の しくみに 変えて（tools/gen1audio.py）曲に 入れる。
   赤の 4つの 鳴らしかた のうち 3つ を 別の 曲に：
     はじめから ＝ 曲 $5D、とちゅうから（Music_RivalAlternateStart）＝ $60、テンポちがい（22ばんどうろの 2かいめ）＝ $61
     （とちゅうから＋テンポちがい は とちゅうから と 同じ $60。銀の 曲の 足した 表 $3A:$7FB7 の あいて いた 番号）。
   ・スクリプト：クリスタル版の マップの シゲルの 場面（研究所・22ばんどうろ・ハナダ・サントアンヌ・ずかんの 場面）の
     playmusic MUSIC_RIVAL_ENCOUNTER／AFTER を その 曲に。
     ポケモンタワー 2F・シルフ 7F（曲が なかった）は 赤と 同じく 来る とき・戦いの あとに 鳴らす。
   （はじめ 赤の 音の しくみ 1 を そのまま 動かす 形で 作ったが、フィールドで 銀の 音の RAM と ぶつかって 固まったので この 形に）"""
import os, sys, re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps
from gsc import fo
from gen1audio import Song

AKAFC = os.environ.get('AKAFC', '/home/claude/in/aka/akafc.gbc')
MUS_RIVAL, MUS_RIVAL_AFTER = 0x1F, 0x20
DB = 0xED                                    # 曲の データ
EXT = 0x7FB7                                 # 足した 表（$5D〜$62）
IDS = {0xF0: 0x5D, 0xF1: 0x60, 0xF2: 0x61, 0xF3: 0x60}
HDR = 0x71C8
VARIANTS = {0x5D: (0x601D, 0x60B8, 0x6130), 0x60: (0x609F, 0x611A, 0x61B2), 0x61: (0x6016, 0x60B8, 0x6130)}


def w(v): return bytes([v & 0xFF, v >> 8])


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    corig = open(cmaps.CORIG, 'rb').read()
    J = bytearray(open(AKAFC, 'rb').read())
    assert J[fo(2, HDR):fo(2, HDR) + 9] == bytes.fromhex('801d6001b860023061')
    assert not any(rom[fo(DB, 0x4000):fo(DB, 0x8000)])
    a = 0x4000
    for mid, (c1, c2, c3) in VARIANTS.items():
        K = bytearray(J); K[fo(2, HDR):fo(2, HDR) + 9] = bytes([0x80]) + w(c1) + b'\x01' + w(c2) + b'\x02' + w(c3)
        song = Song(bytes(K), 2, HDR, {9: 2, 10: 3, 11: 4, 12: 5, 13: 6}, 1)
        h, data = song.build(a); assert a + len(data) <= 0x8000
        rom[fo(DB, a):fo(DB, a) + len(data)] = data; a += len(data)
        t = fo(0x3A, EXT) + 3 * (mid - 0x5D)
        assert rom[t:t + 3] == rom[fo(0x3A, 0x506E):fo(0x3A, 0x506E) + 3], hex(mid)    # あいて いた（曲 0 と 同じ）
        rom[t:t + 3] = bytes([DB]) + w(h)
    # スクリプト
    def pm(bank):
        s_ = rom[fo(bank, 0x4000):fo(bank, 0x8000)]; out = []
        for m in re.finditer(rb'\x7e([\x1f\x20])\x00', s_):
            i = fo(bank, 0x4000) + m.start()
            if corig[i:i + 3] == m.group(0): continue
            out.append((0x4000 + m.start(), m.group(1)[0]))
        return out
    plan = {}
    for x, v in pm(0x62): plan[(0x62, x)] = 0xF0 if v == MUS_RIVAL else 0xF1
    for x, v in pm(0x61): plan[(0x61, x)] = 0xF0 if v == MUS_RIVAL else 0xF1
    for x, v in pm(0x6F): plan[(0x6F, x)] = 0xF1
    r22 = pm(0x72); assert len(r22) == 8, r22
    for k, (x, v) in enumerate(r22):
        plan[(0x72, x)] = {(False, MUS_RIVAL): 0xF0, (False, MUS_RIVAL_AFTER): 0xF1, (True, MUS_RIVAL): 0xF2, (True, MUS_RIVAL_AFTER): 0xF3}[(k >= 4, v)]
    def tail(bank):
        s_ = rom[fo(bank, 0x4000):fo(bank, 0x8000)]; return 0x4000 + len(s_.rstrip(b'\0')) + 2
    for (b, x), v in sorted(plan.items()):
        rom[fo(b, x) + 1] = IDS[v]
    # シルフ 7F・ポケモンタワー 2F（$7A・$7B）：あたらしい かたまりは $7B の 空き
    SB, TB = 0x7A, 0x7B
    f7b = tail(TB) + 6
    def put(data):
        nonlocal f7b
        x = f7b; rom[fo(TB, x):fo(TB, x) + len(data)] = data; f7b += len(data); assert f7b <= 0x8000; return x
    def after_block(bank, at):
        o = fo(bank, at); seg = rom[o:o + 14]
        assert seg[0:2] == b'\x47\x4c' and seg[4:6] == b'\x53\x49' and seg[6] == 0x6D and seg[8] == 0x33 and seg[11] == 0x90, seg.hex()
        t = seg[2] | seg[3] << 8
        blk = bytes([0x7E, IDS[0xF1], 0]) + b'\x47\x4b' + bytes([bank]) + w(t) + b'\x53\x49' + bytes(seg[6:11]) + b'\x81\x90'
        x = put(blk); rom[o:o + 4] = bytes([0x04, TB]) + w(x)
    seg = rom[fo(SB, 0x4000):fo(SB, 0x8000)]
    hits = [m.start() for m in re.finditer(rb'\x68\x0a..\x03\xa2\x66', seg, re.S)]; assert len(hits) == 2, hits
    f7a = tail(SB)
    for h in hits:
        o = fo(SB, 0x4000) + h; cp = bytes(rom[o:o + 7])
        ca = f7a; rom[fo(SB, ca):fo(SB, ca) + 7] = cp; f7a += 7; assert f7a <= 0x8000
        na = put(bytes([0x7E, IDS[0xF0], 0]) + b'\x04' + bytes([SB]) + w(ca))
        rom[o:o + 7] = bytes([0x04, TB]) + w(na) + b'\x00\x00\x00'
    k = seg.find(bytes.fromhex('5e5f474c306a')); assert k > 0 and seg.find(bytes.fromhex('5e5f474c306a'), k + 1) < 0
    after_block(SB, 0x4000 + k + 2)
    seg = rom[fo(TB, 0x4000):fo(TB, 0x8000)]
    k = seg.find(bytes.fromhex('6a474caf73534963')); assert k > 0
    o = fo(TB, 0x4000) + k
    na = put(b'\x6a' + bytes([0x7E, IDS[0xF0], 0]) + b'\x47\x4c\xaf\x73\x03' + w(0x4000 + k + 5))
    rom[o:o + 3] = b'\x03' + w(na)
    k = seg.find(bytes.fromhex('5e5f474c3874')); assert k > 0
    after_block(TB, 0x4000 + k + 2)
    log.append('シゲルの 曲（赤の Music_MeetRival → 曲 $5D・$60・$61、$%02X:$4000〜$%04X）：スクリプト %d か所・シルフ・タワー' % (DB, a, len(plan)))
    return rom
