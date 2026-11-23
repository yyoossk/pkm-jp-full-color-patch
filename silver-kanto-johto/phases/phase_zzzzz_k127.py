"""報告の 直し（第127弾。phase_zzzz_tutor（ジムの 案内の 人）の あとに 動かす ため zzzzz。クリスタル版 カントー＆ジョウトの キットから。銀の アドレスで）
 1 外の マップの 人の絵が 組（グループ）の 読みこめる 表（$05:$465E からの ポインタ、1組 11）に なくて、主人公の 絵に なる：
   銀では 山男（25・9・10番道路）は 表に あった。かわりに すべての 外の マップを 調べたら
     組 3（3,16：銀の マップ。$25・$23 が ない）と 組 15（15,1・15,2：銀の 港。$3B・$27・$24・$A2 が ない。
     カントーを 足した ときに 表を カントーの マップ だけで 作りなおして いた）が 足りなかった
   → その 組の 外の マップで 使う 絵だけの 表に する（組 3 は 11 ちょうど、組 15 は 8）。
   組 17（フクシア）は 13 で 入らない → かざりの ポケモン 2つ（ラプラス $9C・$6B、話すと「！」だけ）を けす。
 2 ディグダのあな（2番道路側の 入口 26,84）の まわりの ブロック $0A → $7D（クチバ側 26,108 と 同じ）。
 3 画面が 反転する わざで テキストボックスに 黒い 箱：PP の ます（14〜18列・13段）の パレットを、わざを えらぶ 間だけ 6、
   えらび おわったら 7 に（$48:$4DFF・$48:$4E46 に 足す。戦闘の 画面を 作る 所 $48:$4C5E は 7）。
 4 自転車の 絵（人の絵 2、$EF:$7000、6コマ）の 上 9段を サトシの 立ちの 絵（人の絵 1、$B0:$46C0）の 上 9段に。
 5 トレーナーが かべ・段差ごしに 見つける：FacingPlayerDistance_bc（$00:$384D）を $49 の TSight（src/trainer_sight_silver.asm）へ。
 6 研究所の シゲル：銀は (7,4)・(7,5) で べつの スクリプト（$62:$4ADB・$4B63）。x＝5 でも シゲルは 主人公の 上に 来て、
   出て いく 道も 横を 通る（実際に 操作して 確かめた）→ 直さない。
 7 ジムの 案内の 人（6つの ジム、12か所、$FC）：出口の 前の 座標イベントは 下向き（出る とき）だけ。
 8 ニビの ジムへ 連れて いく 人（14,2 の (35,16)）：フラグ $AB5（使って いない）を つけ、マップの 人の コールバックで
   グレーバッジ（ENGINE $22）が あれば 消す。"""
import os, sys, re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo
import asmpatch

FB = 0x49
BOULDER = 0x22
HIDE_GYM_GUY = 0xAB5
OUT_TAB, OUT_N = 0x465E, 11


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)


def w16(v): return bytes([v & 0xFF, v >> 8])
def r16(rom, o): return rom[o] | rom[o + 1] << 8


class Free:
    def __init__(s, rom, bank, start=None):
        s.rom, s.bank = rom, bank
        if start is None:
            b = rom[fo(bank, 0x4000):fo(bank, 0x8000)]; i = 0x3FFF
            while i >= 0 and b[i] == 0: i -= 1
            start = 0x4000 + i + 3
        s.a = start
    def put(s, data):
        o = fo(s.bank, s.a); assert s.a + len(data) <= 0x8000 and not any(s.rom[o:o + len(data)]), (hex(s.bank), hex(s.a))
        s.rom[o:o + len(data)] = data; a = s.a; s.a += len(data); return a


def header(rom, g, m):
    gt = fo(0x25, 0x40ED)
    hp = fo(0x25, r16(rom, gt + 2 * (g - 1))) + 9 * (m - 1)
    h = rom[hp:hp + 9]; ao = fo(h[0], r16(h, 3))
    return h, ao


def events(rom, g, m):
    h, ao = header(rom, g, m); sb = rom[ao + 6]
    o = fo(sb, r16(rom, ao + 9)) + 2
    warps = [rom[o + 1 + 5 * i:o + 6 + 5 * i] for i in range(rom[o])]; o += 1 + 5 * rom[o]
    coords = [rom[o + 1 + 8 * i:o + 9 + 8 * i] for i in range(rom[o])]; o += 1 + 8 * rom[o]
    o += 1 + 5 * rom[o]
    objs = [o + 1 + 13 * i for i in range(rom[o])]
    return dict(sb=sb, ao=ao, h=h, warps=warps, coords=coords, objs=objs)


def all_maps(rom):
    # 組の マップの 数：組の ヘッダーの 表（$25:$40ED）の ポインタの 差（組 26 は 148）から。そこから ワープでも たどる
    gt = fo(0x25, 0x40ED); ptr = [r16(rom, gt + 2 * g) for g in range(26)]
    S = set()
    for g in range(26):
        nxt = sorted(x for x in ptr if x > ptr[g])
        n = (nxt[0] - ptr[g]) // 9 if nxt and g < 25 else 148
        S |= {(g + 1, m) for m in range(1, n + 1)}
    seen = set(); todo = list(S)
    while todo:
        k = todo.pop()
        if k in seen: continue
        try: e = events(rom, *k)
        except Exception: continue
        seen.add(k)
        for w in e['warps']:
            if (w[3], w[4]) not in seen: todo.append((w[3], w[4]))
    return seen


def outdoor_lists(rom, log):
    from collections import Counter, defaultdict
    need = defaultdict(Counter)
    maps = all_maps(rom)
    for (g, m) in sorted(maps):
        h, ao = header(rom, g, m)
        if h[2] not in (1, 2): continue
        for o in events(rom, g, m)['objs']:
            if 0 < rom[o] < 0xF0: need[g][rom[o]] += 1
    fixed = []
    for g in sorted(need):
        p = fo(5, r16(rom, fo(5, OUT_TAB) + 2 * (g - 1)))
        lst = list(rom[p:p + OUT_N])
        miss = [s for s in need[g] if s not in lst]
        if not miss: continue
        if g == 17:
            log.append('第127弾 1：組 17（フクシア）は %d の 絵 → 入らない %s（fuchsia() で 消す）' % (len(need[g]), [hex(s) for s in miss]))
            continue
        keep = [s for s in lst if s in need[g]]
        new = keep + [s for s, n in need[g].most_common() if s not in keep]
        assert len(new) <= OUT_N, (g, new)
        # 表が ほかの 組と 同じ 所を 指して いないか
        shared = [g2 for g2 in range(1, 27) if g2 != g and r16(rom, fo(5, OUT_TAB) + 2 * (g2 - 1)) == r16(rom, fo(5, OUT_TAB) + 2 * (g - 1))]
        assert not shared, (g, shared)
        rom[p:p + OUT_N] = bytes(new + [0] * (OUT_N - len(new)))
        fixed.append(g)
        log.append('第127弾 1：組 %d の 外の 人の絵 %s → %s' % (g, bytes(lst).hex(' '), bytes(new).hex(' ')))
    assert fixed == [3, 15], fixed


def fuchsia(rom, log):
    """フクシア（17,5）は 人の絵が 13 で、外の マップの 表（11）に 入らない ラプラス（$9C）と $6B が 主人公の 絵に なって いた。
    2匹とも 話すと「！」だけの かざり（道具・話の すすみ には かかわらない）なので、マップの 人の 終わりの 2つを けす。"""
    h, ao = header(rom, 17, 5); sb = rom[ao + 6]
    o = fo(sb, r16(rom, ao + 9)) + 2
    o += 1 + 5 * rom[o]; o += 1 + 8 * rom[o]; o += 1 + 5 * rom[o]
    n = rom[o]; last = [rom[o + 1 + 13 * i] for i in range(n)][-2:]
    assert last == [0x9C, 0x6B], [hex(x) for x in last]
    rom[o] = n - 2
    log.append('第127弾 1：フクシアの かざりの ポケモン 2つ（$9C・$6B）を けす（人 %d → %d）' % (n, n - 2))


def diglett(rom, log):
    h, a2 = header(rom, 26, 84); h, a1 = header(rom, 26, 108)
    assert rom[a2] == 0x0A and rom[a1] == 0x7D and rom[a2 + 1:a2 + 3] == rom[a1 + 1:a1 + 3] == b'\x04\x04'
    rom[a2] = 0x7D
    log.append('第127弾 2：ディグダのあな 2番道路側（26,84）の まわり $0A → $7D')


def pp_attr(rom, log):
    expect(rom, fo(0x48, 0x4C5E), '21 df cd 3e 06 22 22 22 22 77')
    rom[fo(0x48, 0x4C62)] = 0x07                                     # 戦闘の 画面：7
    expect(rom, fo(0x48, 0x4DFF), 'c5 21 b2 c4 cd')                  # StatusColor_PP
    expect(rom, fo(0x48, 0x4E46), '11 06 01 af cd')                  # StatusColor_PPReset
    f = Free(rom, 0x48)
    setp = f.put(bytes([0xC5, 0xD5, 0xE5,
                        0x21, 0xDF, 0xCD, 0x06, 0x05, 0x22, 0x05, 0x20, 0xFC, 0x4F,
                        0xF0, 0x4F, 0xF5, 0x3E, 0x01, 0xE0, 0x4F,
                        0x21, 0xAE, 0x99, 0x06, 0x05,
                        0xF0, 0x41, 0xE6, 0x02, 0x20, 0xFA, 0x71, 0x23, 0x05, 0x20, 0xF5,
                        0xF1, 0xE0, 0x4F, 0xE1, 0xD1, 0xC1, 0xC9]))
    pp = f.put(bytes([0x3E, 0x06, 0xCD]) + w16(setp) + bytes([0xC5, 0x21, 0xB2, 0xC4, 0xC3, 0x03, 0x4E]))
    rs = f.put(bytes([0x3E, 0x07, 0xCD]) + w16(setp) + bytes([0x11, 0x06, 0x01, 0xC3, 0x49, 0x4E]))
    rom[fo(0x48, 0x4DFF):fo(0x48, 0x4DFF) + 3] = bytes([0xC3]) + w16(pp)
    rom[fo(0x48, 0x4E46):fo(0x48, 0x4E46) + 3] = bytes([0xC3]) + w16(rs)
    log.append('第127弾 3：PP の ますの 色 $48:%04X（えらぶ 間 6、えらんだら 7）' % setp)


def bike(rom, log):
    def px(g):
        P = [[0] * 16 for _ in range(16)]
        for t, (dx, dy) in enumerate(((0, 0), (8, 0), (0, 8), (8, 8))):
            d = rom[g + t * 16:g + t * 16 + 16]
            for y in range(8):
                lo, hi = d[2 * y], d[2 * y + 1]
                for x in range(8): P[dy + y][dx + x] = ((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1)
        return P
    def enc(P):
        out = bytearray()
        for dx, dy in ((0, 0), (8, 0), (0, 8), (8, 8)):
            for y in range(8):
                lo = hi = 0
                for x in range(8):
                    v = P[dy + y][dx + x]; lo |= (v & 1) << (7 - x); hi |= (v >> 1) << (7 - x)
                out += bytes([lo, hi])
        return out
    t = fo(5, 0x47B0)
    expect(rom, t, 'c0 46 c0 b0 01 00'); expect(rom, t + 6, '00 70 c0 ef 01 00')
    walk, bk = fo(0xB0, 0x46C0), fo(0xEF, 0x7000)
    out = bytearray()
    for f in range(6):
        s = px(walk + (f % 3) * 64); k = px(bk + f * 64)
        out += enc([s[y][:] if y < 9 else k[y][:] for y in range(16)])
    rom[bk:bk + 384] = out
    log.append('第127弾 4：自転車の 絵（$EF:$7000）の 頭を サトシに')


def trainer_sight(rom, log):
    expect(rom, 0x384D, 'd5 cd 55 38 42 4b d1 c9')
    assert not any(rom[fo(FB, 0x4660):fo(FB, 0x4700)])
    asmpatch.overlay(rom, open(os.path.join(H, 'src', 'trainer_sight_silver.asm'), encoding='utf-8').read())
    rom[0x384D:0x3855] = bytes([0x3E, FB, 0x21, 0x60, 0x46, 0xCF, 0xC9, 0x00])
    log.append('第127弾 5：トレーナーの 見つけかた $49:$4660')


def gym_doors(rom, log):
    f = Free(rom, FB)
    maps = all_maps(rom)
    targets = {}
    for (g, m) in maps:
        e = events(rom, g, m)
        for c in e['coords']:
            p = c[4] | c[5] << 8; o = fo(e['sb'], p)
            if rom[o] != 0x04 or rom[o + 1] != 0xFC: continue                 # farsjump $FC:…（ジムの スクリプト）
            p = r16(rom, o + 2); o = fo(0xFC, p)
            if rom[o] == 0x34 and rom[o + 2] == 0x00 and rom[o + 3] == 0x08 and rom[o + 6] == 0x31:
                targets[(0xFC, p)] = (g, m)
    assert len(targets) == 12, targets
    for (b, p) in sorted(targets):
        o = fo(b, p)
        badge = rom[o + 1]; skip = rom[o + 4] | rom[o + 5] << 8
        base = f.a
        blob = bytearray([0x1C, 0x09, 0x06, 0x01]) + b'\0\0'            # readvar VAR_FACING ; ifequal UP, .up
        blob += bytes([0x34, badge, 0x00, 0x08]) + b'\0\0'                # checkflag badge ; iffalse .nb
        blob += bytes([0x04, b]) + w16(p + 6)                            # farsjump（バッジ あり：つづき）
        nb = base + len(blob); blob += bytes([0x04, b]) + w16(skip)      # .nb：farsjump（バッジ なし）
        up = base + len(blob); blob += bytes([0x90])                     # .up：end
        blob[4:6] = w16(up); blob[10:12] = w16(nb)
        assert f.put(bytes(blob)) == base
        rom[o:o + 4] = bytes([0x04, FB]) + w16(base)
    log.append('第127弾 7：ジムの 出口の 前 %d か所（出る ときだけ）' % len(targets))


def pewter_guy(rom, log):
    e = events(rom, 14, 2); sb = e['sb']; ao = e['ao']
    gy = [o for o in e['objs'] if (rom[o + 2] - 4, rom[o + 1] - 4) == (35, 16)]
    assert len(gy) == 1, gy
    o = gy[0]
    assert rom[o + 11:o + 13] == b'\xff\xff'
    rom[o + 11:o + 13] = w16(HIDE_GYM_GUY)
    # マップの スクリプト（シーン・コールバック）を 写して、人の コールバック（2）を 足す
    ms = fo(sb, r16(rom, ao + 7))
    ns = rom[ms]; scenes = bytes(rom[ms:ms + 1 + 4 * ns]); q = ms + 1 + 4 * ns
    nc = rom[q]; cbs = bytes(rom[q + 1:q + 1 + 3 * nc])
    assert all(cbs[3 * i] != 2 for i in range(nc)), cbs.hex()
    f = Free(rom, sb)
    cb = f.a
    s = bytearray([0x34]) + w16(BOULDER) + bytes([0x08]) + b'\0\0'       # checkflag ENGINE_BOULDER ; iffalse .show
    s += bytes([0x33]) + w16(HIDE_GYM_GUY) + bytes([0x8F])               # setevent ; endcallback
    show = cb + len(s); s += bytes([0x32]) + w16(HIDE_GYM_GUY) + bytes([0x8F])
    s[4:6] = w16(show)
    assert f.put(bytes(s)) == cb
    new = f.put(scenes + bytes([nc + 1]) + cbs + bytes([2]) + w16(cb))
    rom[ao + 7:ao + 9] = w16(new)
    log.append('第127弾 8：ニビの ジムへ 連れて いく 人 フラグ $%03X（コールバック %02X:%04X）' % (HIDE_GYM_GUY, sb, cb))


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    fuchsia(rom, log)
    outdoor_lists(rom, log)
    diglett(rom, log)
    pp_attr(rom, log)
    bike(rom, log)
    trainer_sight(rom, log)
    gym_doors(rom, log)
    pewter_guy(rom, log)
    return rom
