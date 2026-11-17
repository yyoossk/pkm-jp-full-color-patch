"""たおれた ときと「そらをとぶ」で 出る 場所（SpawnPoints $05:$5286〜、4バイト：グループ・マップ・x・y）を、
   カントーの 町は クリスタル版の MOD と 同じに（赤の マップの ポケモンセンターの 前）。
   銀の 表は 金銀の カントーの マップの 位置の ままで、たとえば クチバで たおれると センターの 前では なく
   (x9, y6)（赤の マップでは 町の まん中の あたり）に 出て いた。
   表の ならびは クリスタルと 銀で 同じ。クリスタルの もとの 表と MOD の 表で ちがう 所だけ、銀の マップ番号に 読みかえて 書く。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port

S_TAB, C_TAB, N = 0x5286, 0x5346, 28        # 銀・クリスタルの $05 の 表（どちらも 28 こ。0 ＝ 家）


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    P = port.Port(rom, cmod, log)
    so = 5 * 0x4000 + S_TAB - 0x4000; co = 5 * 0x4000 + C_TAB - 0x4000
    assert rom[so + 4 * N] == 0xFF and corig[co + 4 * N] == 0xFF
    assert tuple(rom[so + 4 * 7:so + 4 * 8]) == (12, 3, 9, 6)      # クチバ
    n = 0
    for i in range(1, N):
        c, m = cmod[co + 4 * i:co + 4 * i + 4], corig[co + 4 * i:co + 4 * i + 4]
        if c == m: continue
        g, mm = P.x_map(c[0], c[1])
        rom[so + 4 * i:so + 4 * i + 4] = bytes([g, mm, c[2], c[3]]); n += 1
        log.append('  とぶ・たおれた ときの 場所 %d：%d:%d (x%d,y%d) → %d:%d (x%d,y%d)' % (i, m[0], m[1], m[2], m[3], g, mm, c[2], c[3]))
    log.append('とぶ・たおれた ときの 場所：カントー %d か所を クリスタル版の MOD と 同じに' % n)
    return rom
