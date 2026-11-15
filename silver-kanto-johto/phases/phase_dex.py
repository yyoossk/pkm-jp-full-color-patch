"""ずかんの ぶんぷ（第100弾と その あとの ぶんぷの フリーズの 直しの 銀版）：
   ・ぶんぷは 主人公の いる 地方の 地図で ひらく。カントーは いつでも、ジョウトは 着いて から（ふねで ワカバに 着いた しるし＝
     クリスタル版の $34C、銀では $D773 ビット4）。もとの 銀は いつも ジョウトで、カントーは 殿堂入りの あと だけ だった。
     銀の .left・.right（$24:$5E3A〜）を 書きかえ、.LeftRightInput（$24:$5E2F）の とび先を なおす。
     はじめの 地方（$24:$5DFE の xor a / call GetAndPlaceNest）→ $24 の 空き の 小さな 処理 → $47 で いまの 地方を しらべる。
   ・追加機能キットの「ぶんぷの 時間帯」（$47:$4600 NestTime_Input）：START で 作りなおした あと、見て いた 地方
     （1 カントー・2 ジョウト）に もどす（.right・.left を 新しい 番地で よぶ）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

B = 0x24
INIT, LRI, LEFT, BLK_END = 0x5DFE, 0x5E2F, 0x5E3A, 0x5E61
GETNEST, CLEARSPRITES, HWY = 0x5EC0, 0x30BB, 0xD4
ARRIVED, ARRIVED_MASK = 0xD773, 0x10
KB, KA = 0x47, 0x4B40                     # $47 の 空き
NT = 0x4600
W_NESTTIME, W_NESTKANTO, HJOYPRESSED = 0xDEED, 0xDEEE, 0xA9
GETWORLDMAPLOCATION, KANTO_LANDMARK = 0x2D44, 0x2E


def w(v): return bytes([v & 0xFF, v >> 8])


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    at = lambda a: fo(B, a)
    assert rom[at(INIT):at(INIT) + 4] == bytes.fromhex('afcdc05e')
    assert rom[at(LRI):at(LRI) + 11] == bytes.fromhex('7ee62020067ee6102012c9')
    assert rom[at(LEFT):at(BLK_END)] == bytes.fromhex(
        'f0d4fe90c8cdbb303e90e0d4afcdc05ec9fa64d5cb77c8f0d4a7c8cdbb30afe0d43e01cdc05ec9')
    left = b'\xfa' + w(ARRIVED) + bytes([0xE6, ARRIVED_MASK, 0xC8]) + bytes([0xF0, HWY, 0xFE, 0x90, 0xC8, 0xCD]) + w(CLEARSPRITES) + \
        bytes([0x3E, 0x90, 0xE0, HWY, 0xAF, 0xC3]) + w(GETNEST)
    right_at = LEFT + len(left)
    right = bytes([0xF0, HWY, 0xA7, 0xC8, 0xCD]) + w(CLEARSPRITES) + bytes([0xAF, 0xE0, HWY, 0x3E, 0x01, 0xC3]) + w(GETNEST)
    kanto = right_at + 4
    blk = left + right; assert LEFT + len(blk) <= BLK_END
    rom[at(LEFT):at(BLK_END)] = blk + bytes(BLK_END - LEFT - len(blk))
    rom[at(LRI) + 9] = right_at - (LRI + 10)
    # はじめの 地方：$47 で しらべて キャリー＝カントー
    k = bytes([0xFA, 0xC6, 0xD9, 0x47, 0xFA, 0xC7, 0xD9, 0x4F, 0xCD]) + w(GETWORLDMAPLOCATION) + bytes([0xFE, KANTO_LANDMARK, 0x3F, 0xC9])
    assert not any(rom[fo(KB, KA):fo(KB, KA) + 0x60]); rom[fo(KB, KA):fo(KB, KA) + len(k)] = k
    stub = bytes([0x3E, KB, 0x21]) + w(KA) + bytes([0xCF, 0xDA]) + w(kanto) + bytes([0xAF, 0xC3]) + w(GETNEST)
    s = rom[fo(B, 0x4000):fo(B, 0x8000)]; sa = 0x4000 + len(s.rstrip(b'\0')) + 1
    assert sa + len(stub) <= 0x8000; rom[at(sa):at(sa) + len(stub)] = stub
    rom[at(INIT):at(INIT) + 4] = b'\xcd' + w(sa) + b'\x00'
    # ぶんぷの 時間帯（キット）
    o = fo(KB, NT); assert rom[o:o + 16] == bytes.fromhex('faeedea7280aafeaeede3e24214b5ecf')
    n2 = KA + len(k)
    c = bytearray(b'\xfa' + w(W_NESTKANTO) + b'\xa7\x28\x00'); jz = len(c) - 1
    c += b'\xf5\xaf\xea' + w(W_NESTKANTO) + b'\xf1\x3d\x21' + w(right_at) + b'\x28\x03\x21' + w(LEFT) + bytes([0x3E, B, 0xCF])
    inp = len(c)
    c += bytes([0xF0, HJOYPRESSED, 0xE6, 0x08, 0xC8, 0xFA]) + w(W_NESTTIME) + b'\x3c\xe6\x03\xea' + w(W_NESTTIME)
    c += bytes([0xF0, HWY, 0xA7, 0x3E, 0x01, 0x28, 0x01, 0x3C, 0xEA]) + w(W_NESTKANTO) + b'\xcd' + w(CLEARSPRITES) + b'\x37\xc9'
    c[jz] = inp - (jz + 1)
    rom[fo(KB, n2):fo(KB, n2) + len(c)] = c
    assert rom[o + 16:o + 0x2D] == bytes.fromhex('f0a9e608c8faedde3ce603eaeddef0d4a72005'
                                                 '3e01eaeedecdbb3037c9')[:0x2D - 16]
    rom[o:o + 3] = b'\xc3' + w(n2)
    log.append('ずかんの ぶんぷ：いる 地方で ひらく・ジョウトは 着いて から（.right $24:$%04X）、時間帯の 切りかえで 地方を たもつ（$47:$%04X）' % (right_at, n2))
    return rom
