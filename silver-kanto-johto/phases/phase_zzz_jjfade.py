"""ムサシと コジロウが 戦いの あと 急に 消えない（第103弾の 銀版）：ピカチュウ版と 同じく、最後の ことばの あと 画面が 暗く なって
   から いなく なる（special FadeOutToBlack / ReloadSpritesNoPalettes / disappear ×2 / pause 15 / FadeInFromBlack）。
   カントー（$79〜$7B：おつきみやま・アジト・タワー・シルフ）は 暗く なる 間 ムサシと コジロウの 曲（$39）、そのあと マップの 曲。
   ジョウト（$E9〜$EB：phase_zz_jj）も。disappear・disappear・setevent（7バイト）を $E8:$5A00〜 への farsjump に。
   （phase_zz_jj の あとに 組む）"""
import os, sys, re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

SP_FADEOUT, SP_FADEIN, SP_RELOADSPR = 0x2F, 0x31, 0x32
MUSIC_JJ = 0x39
CB, CA = 0xE8, 0x5A00
KANTO, JOHTO = (0x79, 0x7A, 0x7B), (0xE9, 0xEA, 0xEB)


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    pat = re.compile(rb'\x5d\x48.\x5e\x5f\x47\x4c..\x53\x49\x6d(.)\x6d(.)\x33(..)\x90', re.S)
    a = CA; n = 0
    assert not any(rom[fo(CB, CA):fo(CB, CA) + 0x100])
    for b in KANTO + JOHTO:
        s = fo(b, 0x4000)
        for m in pat.finditer(rom, s, s + 0x4000):
            o1, o2, ev = m.group(1)[0], m.group(2)[0], m.group(3)
            kanto = b in KANTO
            code = bytearray()
            if kanto: code += bytes([0x7E, MUSIC_JJ, 0x00])
            code += bytes([0x0F, SP_FADEOUT, 0, 0x0F, SP_RELOADSPR, 0, 0x6D, o1, 0x6D, o2, 0x8A, 15, 0x0F, SP_FADEIN, 0, 0x33]) + ev
            if kanto: code += b'\x81'
            code += b'\x90'
            rom[fo(CB, a):fo(CB, a) + len(code)] = code
            d = m.start(1) - 1
            rom[d:d + 7] = bytes([0x04, CB, a & 0xFF, a >> 8, 0, 0, 0])
            a += len(code); n += 1
    assert n == 7, n
    log.append('ムサシと コジロウ：暗く なって から 消える（%d か所、$%02X:$%04X〜$%04X）' % (n, CB, CA, a))
    return rom
