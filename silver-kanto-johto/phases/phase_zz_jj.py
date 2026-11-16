"""（さいごに 組む：ほかの フェーズが その バンクを かえた あとで 写す）
ジョウトの ムサシと コジロウ（第48弾の のこり。ピカチュウ版の 2人）：ヤドンのいど ちか1かい・アジト ちか1かい・ラジオとう 2かい の
   ロケットだんの 場面に 2人が いて、話しかけると たたかう（トレーナー 72 の 5〜7。ジョウトの 手持ち）。たおすか、ロケットだんが
   いなく なると きえる。
   その マップの スクリプトの バンクを まるごと あいて いる バンク（$E9〜$EB）に 写して、マップの 属性の バンクを かえ、写しの
   中の ほかの マップの 所に あたらしい MapScripts（OBJECTS の callback を 足す）・イベントの 表（2人を 足す）・スクリプト・ことばを 置く。
   しるしは フラグ $BC0〜$BC2（$D785。あいて いる バイト。$D786〜$D78C は 連れ歩き）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import jptext
from gsc import fo, r16

Q = '“'
JJ, SPR_JAMES, SPR_JESSIE = 72, 0x76, 0x75
FACE = {'DOWN': 6, 'UP': 7, 'LEFT': 8, 'RIGHT': 9}
# マップ（グループ, 番号）, ロケットだんの フラグ, ムサシ (x, y, むき), コジロウ, 新しい バンク, しるし
SCENES = [((3, 32), 0x6FC, (15, 12, 'RIGHT'), (14, 12, 'RIGHT'), 0xE9, 0xBC0),
          ((3, 41), 0x6DA, (26, 2, 'RIGHT'), (26, 3, 'RIGHT'), 0xEA, 0xBC1),
          ((3, 18), 0x6CE, (13, 1, 'RIGHT'), (13, 2, 'RIGHT'), 0xEB, 0xBC2)]
TEXTS = [
    ('ムサシ' + Q + 'ちょっと　まったー！<PARA>コジロウ' + Q + 'ジョウトの　ヤドンの　シッポは<LINE>ロケットだんが　いただくぜ！<PARA>'
     'ムサシ' + Q + 'じゃまする　やつは<LINE>ここで　やっつけて　やるわ！',
     'ムサシ' + Q + 'ジョウトまで　きたのに<LINE>また　まけるなんて<……><PARA>コジロウ' + Q + 'おぼえてろよー！'),
    ('ムサシ' + Q + 'また　あんたね！<PARA>コジロウ' + Q + 'この　ひみつの　アジトは<LINE>ぜったいに　とおさないぜ！',
     'ムサシ' + Q + 'くやしいー！<PARA>コジロウ' + Q + 'なんで　いつも<LINE>こうなるんだ<……>'),
    ('ムサシ' + Q + 'ラジオとうは<LINE>ロケットだんが　いただいたわ！<PARA>コジロウ' + Q + 'サカキさまへの<LINE>だいじな　ほうそうの<CONT>'
     'じゃまは　させないぜ！<PARA>ムサシ' + Q + 'いけっ　ソーナンス！',
     'ムサシ' + Q + 'やっぱり　だめだったわ<……><PARA>コジロウ' + Q + 'こうなったら<LINE>にげるが　かちだ！'),
]
JJ_LOSE = 'ムサシ・コジロウ' + Q + '<LINE>やなかんじー！'
EXT_FLAGS = 0xD60D


def T(s): return b'\x00' + jptext.enc(s) + b'\x57'
def w(v): return bytes([v & 0xFF, v >> 8])


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    gt = fo(0x25, 0x40ED)
    for i, ((g, m), rf, jes, jam, nb, flag) in enumerate(SCENES):
        assert not any(rom[fo(nb, 0x4000):fo(nb, 0x8000)])
        hp = fo(0x25, r16(rom, gt + 2 * (g - 1))) + 9 * (m - 1); h = rom[hp:hp + 9]; ao = fo(h[0], r16(h, 3))
        sb = rom[ao + 6]; ms = r16(rom, ao + 7); ev = r16(rom, ao + 9)
        rom[fo(nb, 0x4000):fo(nb, 0x8000)] = rom[fo(sb, 0x4000):fo(sb, 0x8000)]
        # もとの MapScripts と イベントの 表を 読む
        o = fo(sb, ms); ns = rom[o]; scenes = bytes(rom[o + 1:o + 1 + 4 * ns]); o += 1 + 4 * ns
        nc = rom[o]; cbs = [bytes(rom[o + 1 + 3 * k:o + 4 + 3 * k]) for k in range(nc)]
        old_cb = [r16(c, 1) for c in cbs if c[0] == 2]; cbs = [c for c in cbs if c[0] != 2]   # もとの OBJECTS は あとで よぶ
        e = fo(sb, ev); head = bytes(rom[e:e + 2]); p = e + 2
        parts = []
        for size in (5, 8, 5):
            n = rom[p]; parts.append(bytes(rom[p:p + 1 + size * n])); p += 1 + size * n
        n = rom[p]; objs = bytes(rom[p + 1:p + 1 + 13 * n]); p += 1 + 13 * n
        ev_end = p - fo(sb, 0x4000) + 0x4000
        # 置く 所：この マップの イベントの 表の あと（写しの 中の ほかの マップの 所）
        a = ev_end; buf = bytearray(); lab = {}; fix = []
        def L(nm): lab[nm] = a + len(buf)
        def ref(nm): fix.append((len(buf), nm)); buf.extend(b'\0\0')
        jid, mid = n + 2, n + 3                                     # disappear の 番号（日本版は 人の 番号＋1）
        L('script'); buf += bytes([0x6A, 0x47, 0x4C]); ref('intro'); buf += bytes([0x53, 0x49, 0x63]); ref('lose'); buf += b'\0\0'
        buf += bytes([0x5D, JJ, 5 + i, 0x5E, 0x5F, 0x47, 0x4C]); ref('after'); buf += bytes([0x53, 0x49, 0x6D, jid, 0x6D, mid, 0x33]) + w(flag) + b'\x90'
        L('cb'); buf += bytes([0x31]) + w(rf) + bytes([0x08]); ref('cbe'); buf += bytes([0x33]) + w(flag)
        L('cbe'); buf += (b'\x03' + w(old_cb[0])) if old_cb else b'\x8F'
        L('ms'); buf += bytes([ns]) + scenes + bytes([len(cbs) + 1]) + b''.join(cbs) + b'\x02'; ref('cb')
        L('ev'); buf += head + b''.join(parts) + bytes([n + 2]) + objs
        for (x, y, f), spr in ((jes, SPR_JESSIE), (jam, SPR_JAMES)):
            buf += bytes([spr, y + 4, x + 4, FACE[f], 0, 0xFF, 0xFF, 0, 0]); ref('script'); buf += w(flag)
        intro, after = TEXTS[i]
        L('intro'); buf += T(intro); L('after'); buf += T(after); L('lose'); buf += T(JJ_LOSE)
        for off, nm in fix: buf[off] = lab[nm] & 0xFF; buf[off + 1] = lab[nm] >> 8
        assert a + len(buf) <= 0x8000
        rom[fo(nb, a):fo(nb, a) + len(buf)] = buf
        rom[ao + 6] = nb; rom[ao + 7:ao + 9] = w(lab['ms']); rom[ao + 9:ao + 11] = w(lab['ev'])
        log.append('ムサシと コジロウ %d-%d：$%02X → $%02X:$%04X〜$%04X' % (g, m, sb, nb, a, a + len(buf)))
    return rom
