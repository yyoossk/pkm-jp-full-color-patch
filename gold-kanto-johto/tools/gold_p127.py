"""第127弾（報告の 直し）キットの 金版：エンジンの 所。
   MOD 側（kj5/make_kj5.sh → crystal_kj5.gbc、c2g で 金へ）：2 ディグダのあな ニビ側の ボーダー、6 研究所の シゲル、
   8 ニビの ジムへ 連れて いく 人（フラグ $A20 → c2g が 金の 空きの うしろから わりあてる）。
   4 自転車の 絵：gold_player.py（bike_head）。
   ここは 金の ROM に 直接：
    5 トレーナーの 見つかり方：FacingPlayerDistance_bc（00:384D）→ farcall 7E の TSight（asm127/trainer_sight_gold.asm）。
   当てはまらない もの：1 山男（金は マップの 人から 人の絵の 表を 作る：gold_sprites.py）、
    7 ジムの 技教えの 呼び止め・3 PP の 色 は gold_p127 の 説明（作業メモ）を 見る。
"""
import os, re, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
import gold_hfi
RGBDS = os.environ.get('RGBDS', '/home/claude/rgbds-src')
def fo(b, a): return b * 0x4000 + a - 0x4000
def w16(v): return bytes([v & 0xFF, v >> 8])


def expect(g, o, h):
    b = bytes.fromhex(h.replace(' ', '')); assert bytes(g[o:o + len(b)]) == b, (hex(o), g[o:o + len(b)].hex(' '), h); return b


def assemble(asm, bank, addr):
    with tempfile.TemporaryDirectory() as d:
        open(d + '/in.gbc', 'wb').write(bytes((bank + 1) * 0x4000))
        subprocess.run([RGBDS + '/rgbasm', '-D', 'CODE_BANK=$%X' % bank, '-D', 'CODE_ADDR=$%X' % addr, '-o', d + '/a.o', os.path.join(HERE, 'asm127', asm)], check=True)
        subprocess.run([RGBDS + '/rgblink', '-O', d + '/in.gbc', '-o', d + '/out.gbc', '-n', d + '/out.sym', d + '/a.o'], check=True)
        new = open(d + '/out.gbc', 'rb').read()
        sym = {l.split()[1]: int(l.split()[0].split(':')[1], 16) for l in open(d + '/out.sym') if re.match(r'[0-9a-f]+:[0-9a-f]+ ', l)}
    o = fo(bank, addr); e = len(new)
    while e > o and new[e - 1] == 0: e -= 1
    return new[o:e], sym


def trainer_sight(g, log):
    expect(g, 0x384D, 'd5 cd 55 38 42 4b d1 c9')
    a = gold_hfi.here()
    code, sym = assemble('trainer_sight_gold.asm', gold_hfi.EB, a)
    assert gold_hfi.put(g, code) == a and sym['TSight'] == a
    g[0x384D:0x3855] = bytes([0x3E, gold_hfi.EB, 0x21]) + w16(a) + bytes([0xCF, 0xC9, 0x00])
    log.append('第127弾 5 トレーナーの 見つかり方：00:384D → %02X:%04X' % (gold_hfi.EB, a))


# ---- 3 画面が 反転する わざで テキストボックスに 黒い 箱：金の 追加機能パッチの PP の 色（バンク $49、statuscolor_gold.asm）も
#  PP の ます（14〜18列, 13段）が 戦い の あいだ ずっと 6本目。画面の 反転は 0〜6本目を かえるので 白が 黒に なった。
#  ますの パレットを わざを えらぶ 間（StatusColor_PPBody）だけ 6本目、えらび おわったら（StatusColor_PPReset）7本目に
#  （属性マップと VRAM の 両方）。戦いの 画面を つくる 所（StatusColor_BattleLayout）では 7本目。
SC = 0x49
def tail(g, b):
    B = g[b * 0x4000:(b + 1) * 0x4000]; e = len(B)
    while e and B[e - 1] == 0: e -= 1
    return 0x4000 + e + 2


def pp_attr(g, log):
    o = fo(SC, 0x413E); expect(g, o, '21 e9 cc 3e 05 22 22 77 21 df cd 3e 06 22 22 22 22 77')
    g[o + 12] = 0x07
    expect(g, fo(SC, 0x41F8), 'c5 21 b2 c4 cd')
    expect(g, fo(SC, 0x423F), '11 06 01 af cd')
    a = tail(g, SC)
    def put(b):
        nonlocal a
        o_ = fo(SC, a); assert a + len(b) <= 0x8000 and not any(g[o_:o_ + len(b)]); g[o_:o_ + len(b)] = b; r = a; a += len(b); return r
    setp = put(bytes([0xC5, 0xD5, 0xE5,
                      0x21, 0xDF, 0xCD, 0x06, 0x05, 0x22, 0x05, 0x20, 0xFC, 0x4F,     # 属性マップ（CDDF ＝ CCCD + 13×20 + 14）
                      0xF0, 0x4F, 0xF5, 0x3E, 0x01, 0xE0, 0x4F,                         # VRAM バンク 1
                      0x21, 0xAE, 0x99, 0x06, 0x05,                                     # 9800 + 13×32 + 14
                      0xF3, 0xF0, 0x41, 0xE6, 0x02, 0x28, 0x03, 0xFB, 0x18, 0xF6,       # di / モード 0・1 まで（割りこみで ずれない ように）
                      0x71, 0xFB, 0x23, 0x05, 0x20, 0xF0,
                      0xF1, 0xE0, 0x4F, 0xE1, 0xD1, 0xC1, 0xC9]))
    pp = put(bytes([0x3E, 0x06, 0xCD]) + w16(setp) + bytes([0xC5, 0x21, 0xB2, 0xC4, 0xC3]) + w16(0x41FC))
    rs = put(bytes([0x3E, 0x07, 0xCD]) + w16(setp) + bytes([0x11, 0x06, 0x01, 0xC3]) + w16(0x4242))
    g[fo(SC, 0x41F8):fo(SC, 0x41F8) + 3] = bytes([0xC3]) + w16(pp)
    g[fo(SC, 0x423F):fo(SC, 0x423F) + 3] = bytes([0xC3]) + w16(rs)
    log.append('第127弾 3 PP の ますの パレット：%02X:%04X（えらぶ 間 6・おわったら 7）' % (SC, setp))


def apply(g, log):
    trainer_sight(g, log)
    pp_attr(g, log)
