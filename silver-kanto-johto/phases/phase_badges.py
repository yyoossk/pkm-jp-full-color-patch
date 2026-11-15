"""ロケットだんの コガネ・ラジオとうの 事件は ジョウトの バッジの かずだけで きめる（第82弾の 銀版）：
   主人公は カントーの バッジ 8こを もって いるので、VAR_BADGES（ジョウト＋カントー）では 6・7 に ならず 物語が とまる。
   ジムリーダーの「ロケットだんを うごかす」所（ifequal 7 / ifequal 6 / end、7か所）を、ジョウトの バッジ（wJohtoBadges $D56F）だけ
   かぞえてから に する。本体 $E8:$5200。"""
import os, sys, re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

CB, CA = 0xE8, 0x5200
W_JOHTO, COUNTSETBITS, W_NUMSETBITS, W_SCRIPTVAR = 0xD56F, 0x3504, 0xD143, 0xD165


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    assert rom[COUNTSETBITS:COUNTSETBITS + 1] and not any(rom[fo(CB, CA):fo(CB, CA) + 0x100])
    sites = []
    for m in re.finditer(rb'\x1c\x07\x00(..)', bytes(rom[:0x100000]), re.S):
        bank = m.start() // 0x4000; ta = m.group(1)[0] | m.group(1)[1] << 8
        if not 0x4000 <= ta < 0x8000: continue
        t = fo(bank, ta); x = rom[t:t + 9]
        if x[0] == 6 and x[1] == 7 and x[4] == 6 and x[5] == 6 and x[8] == 0x90:
            sites.append((bank, ta, x[2] | x[3] << 8, x[6] | x[7] << 8))
    assert len(sites) == 7, sites
    w = lambda v: bytes([v & 0xFF, v >> 8])
    cnt = CA
    blob = bytes([0x21]) + w(W_JOHTO) + bytes([0x06, 0x01, 0xCD]) + w(COUNTSETBITS) + bytes([0xFA]) + w(W_NUMSETBITS) + \
        bytes([0xEA]) + w(W_SCRIPTVAR) + bytes([0xC9])
    for bank, ta, rt, gt in sites:
        base = CA + len(blob); r_at = base + 13; g_at = r_at + 4
        blob += bytes([0x0E, CB]) + w(cnt) + bytes([0x06, 7]) + w(r_at) + bytes([0x06, 6]) + w(g_at) + bytes([0x90, 0x04, bank]) + \
            w(rt) + bytes([0x04, bank]) + w(gt)
        t = fo(bank, ta); rom[t:t + 4] = bytes([0x04, CB]) + w(base)
    rom[fo(CB, CA):fo(CB, CA) + len(blob)] = blob
    log.append('ロケットだんの 事件：ジョウトの バッジだけ かぞえる（%d か所、$%02X:$%04X）' % (len(sites), CB, CA))
    return rom
