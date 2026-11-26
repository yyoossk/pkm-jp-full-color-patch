"""報告の 直し（第128弾。phase_zzzzz_k127 の あとに 動かす ため zzzzzz。クリスタル版 カントー＆ジョウトの キットから。銀の アドレスで）
 1 ポケギアで おかあさんに 電話すると「ウツギはかせが よんでいたんじゃ なかったかしら？」（ウツギはかせから ポケモンを
   もらって いない ときの 文。カントーでは いつも これ）：$36:$58D2 の 文を「げんき？ からだに きをつけて がんばってね！」に。
 2 手持ちが いっぱいで 捕まえた ポケモン：マサキに 会う 前（イベント $0835、$D713 bit5）は「だれかの パソコンへ」：
   $03:$6F2F の「ld hl, $718F / call PrintText」を $49 への farcall に。
 3 ジムの 像：赤と 同じに、バッジの 前は「<リーダー> にんてい トレーナー！ <GREEN>（シゲル）」、バッジの あとは「シゲル <PLAYER>」。
   カントーの 7つの ジムの 像の スクリプト（6つは phase_zzzz_tutor の 写しの バンク $F4〜$F9 の 方）の はじめ 4バイトを
   $49 への farsjump に。グレンジム（26,59）には 像が ない
   → 赤と 同じ (x17,y13) に 上向きで 調べる 像を 足す（イベントの 表を $63 の 空きへ 写して 作りなおす）。
 4 ニビ博物館 1F（26,77）の 化石 2つ：callasm の 前に RefreshScreen（$00:$2E3C）を よぶ（歩いた 分 ずれた BG の まま 絵を かいて、
   プテラ→カブトプス で 上に、逆で 下に ずれた）。小さな 処理は $68 の 空きに。
 5 ニビの 民家（14,3）の ニドラン：スクリプト（$A6:$7A49）の 前に faceplayer。
 8 おつきみやま：B2F（26,37）に 赤の 隠し道具 2つ（つきのいし (x18,y12) フラグ $A2C、ピーピーエイド (x33,y9) フラグ $A2D）。
   1F（26,35）の (x5,y32) の ボール（赤では わざマシン12 みずでっぽう、銀では あまいかおり）：拾うと みずでっぽうを 教える
   （phase_zzzz_tutor の KT_WaterGunBall。教えたら ボールは 消える、いいえ なら のこる）。
 9 GivePoke（$03:$6591）：手持ちが いっぱいで ボックスへ 送る とき、SRAM を 開いて いつも 指定の 持ち物（0＝なし）を 書く
   （戦いの 外の LoadEnemyMon は 最後の トレーナーの 持ち物を 入れて いた：おつきみやまの コイキングが ひみつのコハク）。
 10 自分の 部屋の ゲーム機：「ファミコンを してる！」→「ロクヨンを してる！」（$62:$7BA3）。
 11 たいあたり など：こちらの 背の 高い 絵の 上（6段目）が 動かない → src/tackle_tiles_silver.asm（6段目の タイルを ずらして かきなおす）。
 6・7（状態異常の 色）は 銀では 起きない（src/statuscolor_silver.asm は 名前の すぐ うしろの ますを さがして 色を つける。
   レベルアップの 箱も 文字化け しない。実際に 操作して 確かめた）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo
import asmpatch
from jptext import enc

FB = 0x49
BILL_FLAG_BYTE, BILL_FLAG_BIT = 0xD713, 5          # イベント $0835（マサキが 転送マシンに 入った）
PRINT_TEXT = 0x0F30
REFRESH_SCREEN = 0x2E3C
OPEN_SRAM, CLOSE_SRAM = 0x309D, 0x30AD
GREEN = 0x39
VOLCANO = 0x28                                     # ENGINE_VOLCANOBADGE
BLAINE = (0x2E, 0x02)
HID_MOON_STONE, HID_ETHER = 0xA2C, 0xA2D
MOON_STONE, ETHER = 0x08, 0x3F
STATUES = [(0x76, 0x7AF3), (0x77, 0x5ECF), (0x79, 0x6030), (0x77, 0x7781), (0x77, 0x5A13), (0x77, 0x6D40),
           (0x77, 0x69C3)]                          # ニビ・ハナダ・クチバ・タマムシ・セキチク・ヤマブキ・トキワ（元の バンク）


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


class Script:
    def __init__(s, base): s.base, s.b, s.lab, s.fix = base, bytearray(), {}, []
    def db(s, *v): s.b += bytes(v)
    def raw(s, b): s.b += bytes(b)
    def ref(s, l): s.fix.append((len(s.b), l)); s.b += b'\0\0'
    def label(s, l): s.lab[l] = s.base + len(s.b)
    def done(s):
        for at, l in s.fix:
            v = l if isinstance(l, int) else s.lab[l]
            s.b[at:at + 2] = w16(v)
        return bytes(s.b)


def header(rom, g, m):
    gt = fo(0x25, 0x40ED)
    hp = fo(0x25, r16(rom, gt + 2 * (g - 1))) + 9 * (m - 1)
    h = rom[hp:hp + 9]; ao = fo(h[0], r16(h, 3))
    return h, ao


def read_events(rom, g, m):
    h, ao = header(rom, g, m); sb = rom[ao + 6]
    o = fo(sb, r16(rom, ao + 9))
    ev = {'head': bytes(rom[o:o + 2]), 'sb': sb, 'ao': ao}; o += 2
    for k, n in (('warps', 5), ('coords', 8), ('bgs', 5), ('objs', 13)):
        c = rom[o]; ev[k] = [bytes(rom[o + 1 + n * i:o + 1 + n * (i + 1)]) for i in range(c)]; o += 1 + n * c
    ev['end'] = o
    return ev


def write_events(rom, ev, f):
    """イベントの 表を 作りなおして f（マップの スクリプトの バンク）に 置き、ポインタを かえる"""
    assert f.bank == ev['sb']
    b = bytearray(ev['head'])
    for k in ('warps', 'coords', 'bgs', 'objs'): b += bytes([len(ev[k])]) + b''.join(ev[k])
    a = f.put(bytes(b))
    rom[ev['ao'] + 9:ev['ao'] + 11] = w16(a)
    return a


def console(rom, log):
    o = fo(0x62, 0x7BA3)
    old, new = enc('ファミコンを'), enc('ロクヨンを')
    assert rom[o:o + len(old)] == old and rom.find(old, o + 1) < 0
    e = rom.index(0x57, o)
    body = bytes(rom[o:e + 1]).replace(old, new)
    rom[o:e + 1] = body + bytes(e + 1 - o - len(body))
    log.append('第128弾 10：部屋の ゲーム機「ロクヨンを してる！」（$62:$7BA3）')


def mom_phone(rom, log):
    o = fo(0x36, 0x58D2)
    head = enc('もしもし…<PARA>あら　<PLAYER><LINE>')
    expect(rom, o, (head + enc('ウツギはかせ')).hex())                     #（が　は $4A の 1文字）
    expect(rom, o + len(head) + 6, '4a' + enc('よんでいたんじゃ<CONT>なかったかしら？<DONE>').hex())
    old_end = rom.index(0x57, o)
    new = head + enc('げんき？<PARA>からだに　きをつけて<LINE>がんばってね！<DONE>')
    assert o + len(new) <= old_end + 1
    rom[o:old_end + 1] = new + bytes(old_end + 1 - o - len(new))
    log.append('第128弾 1：おかあさんの 電話（ポケモンを もらう 前の 文）$36:$58D2')


def transfer(rom, log):
    at = fo(3, 0x6F2F)
    expect(rom, at, '21 8f 71 cd 30 0f')
    src = fo(3, 0x718F); end = rom.index(0x58, src)              # <PROMPT>（ここで 文が おわる）まで
    orig = bytes(rom[src:end + 1])
    masaki = enc('は　マサキの　ところへ')
    assert masaki in orig, orig.hex(' ')
    someone = orig.replace(masaki, enc('は　だれかの　パソコンへ'))
    f = Free(rom, FB)
    tb = f.put(orig); ts = f.put(someone)
    code = bytes([0x21]) + w16(tb) + bytes([0xFA]) + w16(BILL_FLAG_BYTE) + bytes([0xCB, 0x47 | BILL_FLAG_BIT << 3]) + \
        bytes([0x20, 0x03, 0x21]) + w16(ts) + bytes([0xC3]) + w16(PRINT_TEXT)
    r = f.put(code)
    rom[at:at + 6] = bytes([0x3E, FB, 0x21]) + w16(r) + bytes([0xCF])
    log.append('第128弾 2：ボックスへ 送った 文（マサキに 会う 前は だれかの パソコンへ）$03:$6F2F → $%02X:$%04X' % (FB, r))


def statues(rom, log):
    city = bytes.fromhex('00 50 01 9d cf 00 7f 54 0b 9f 57')
    expect(rom, fo(0x36, 0x4B19), city.hex())
    tr = bytes.fromhex('00 50 01 a8 cf 00 7f') + enc('にんてい') + bytes([0x7F, 0x5D, 0xE7, 0x4F])
    expect(rom, fo(0x36, 0x4B24), (tr + bytes([0x52, 0x57])).hex())
    expect(rom, fo(0x36, 0x44FA), '42 00 47 4c 19 4b 53 49 90')            # GymStatue1（std $27）
    expect(rom, fo(0x36, 0x4503), '42 00 47 4c 19 4b 54 4c 24 4b 53 49 90')  # GymStatue2（std $28）
    f = Free(rom, FB); s = Script(f.a)
    for k, tail in (('1', [GREEN]), ('2', [GREEN, 0x7F, 0x52])):
        s.label('k' + k); s.db(0x42, 0x00, 0x47, 0x4C); s.ref('city'); s.db(0x54, 0x4C); s.ref('t' + k)
        s.db(0x53, 0x49, 0x90)
        s.label('t' + k); s.raw(tr + bytes(tail) + b'\x57')
    s.label('city'); s.raw(city)
    # 6つの ジムは phase_zzzz_tutor が スクリプトの バンクを $F4〜$F9 に 写した（ハナダ・タマムシ・ヤマブキ・ニビは 写しの 方が、
    # クチバ・トキワは farsjump で 元の バンクの 方が 動く）→ 元と 写しの 両方を かえる
    found = []
    for b0, p0 in STATUES:
        o0 = fo(b0, p0)
        copies = [nb for nb in range(0xF4, 0xFA) if rom[fo(nb, p0):fo(nb, p0) + 8] == rom[o0:o0 + 8]]
        found.append((b0, p0, copies))
    log.append('   像：' + ' '.join('$%02X:$%04X%s' % (b, p, ''.join('・$%02X' % c for c in cs)) for b, p, cs in found))
    stubs = []
    for b, p, cs in found:
        o = fo(b, p)
        assert rom[o] == 0x34 and rom[o + 2] == 0 and rom[o + 3] == 0x09 and rom[o + 6:o + 8] == b'\x0c\x27', rom[o:o + 8].hex(' ')
        bt = fo(b, r16(rom, o + 4))
        assert rom[bt] == 0x43 and rom[bt + 3] == 0x01 and rom[bt + 4:bt + 6] == b'\x0c\x28', rom[bt:bt + 6].hex(' ')
        stubs.append(((b, p), rom[o + 1], (rom[bt + 1], rom[bt + 2])))
        for c in cs: assert rom[fo(c, r16(rom, o + 4)):fo(c, r16(rom, o + 4)) + 6] == rom[bt:bt + 6]
    stubs.append(('cinnabar', VOLCANO, BLAINE))
    for i, (bp, flag, (cl, ci)) in enumerate(stubs):
        s.label('s%d' % i); s.db(0x43, cl, ci, 0x01, 0x34, flag, 0x00, 0x09); s.ref('k2'); s.db(0x03); s.ref('k1')
    blob = s.done(); assert f.put(blob) == s.base
    for i, (bp, flag, ci) in enumerate(stubs):
        if bp == 'cinnabar': continue
        b, p, cs = found[i]
        for bb in [b] + cs: rom[fo(bb, p):fo(bb, p) + 4] = bytes([0x04, FB]) + w16(s.lab['s%d' % i])
    # グレンジム：像を 足す
    ev = read_events(rom, 26, 59); sb = ev['sb']
    assert sb == 0x63 and not any((x[0], x[1]) == (13, 17) for x in ev['bgs'])
    h, ao = header(rom, 26, 59); assert (rom[ao + 1], rom[ao + 2]) == (9, 10)
    f2 = Free(rom, sb)
    stub = f2.put(bytes([0x04, FB]) + w16(s.lab['s%d' % (len(stubs) - 1)]))
    ev['bgs'].append(bytes([13, 17, 0x01]) + w16(stub))                   # BGEVENT_UP
    ea = write_events(rom, ev, f2)
    log.append('第128弾 3：ジムの 像（シゲル・主人公）$%02X:$%04X、グレンジムの 像 (x17,y13)（イベント $%02X:$%04X）'
               % (FB, s.base, sb, ea))


def fossils(rom, log):
    ev = read_events(rom, 26, 77); sb = ev['sb']
    f = Free(rom, 0x68); n = 0
    for b in ev['bgs']:
        o = fo(sb, r16(b, 3))
        if rom[o] != 0x0E or rom[o + 1] != 0x68: continue                   # callasm
        ca = r16(rom, o + 2); r = fo(0x68, ca)
        if rom[r] != 0x3E or rom[r + 1] not in (0x8D, 0x8E): continue       # ld a, KABUTOPS / AERODACTYL
        st = f.put(bytes([0xCD]) + w16(REFRESH_SCREEN) + bytes([0xC3]) + w16(ca))
        rom[o + 2:o + 4] = w16(st); n += 1
    assert n == 2, n
    log.append('第128弾 4：博物館の 化石 2つ RefreshScreen（$68）')


def nidoran(rom, log):
    ev = read_events(rom, 14, 3); sb = ev['sb']
    ob = [i for i, o in enumerate(ev['objs']) if o[0] == 0x83]
    assert len(ob) == 1 and sb == 0xA6
    o = ev['objs'][ob[0]]; p = r16(o, 9)
    expect(rom, fo(sb, p), '47 4c 5d 7a 83 20 00 53 49 90')
    f = Free(rom, sb)
    new = f.put(bytes([0x6A, 0x03]) + w16(p))                             # faceplayer ; sjump
    # 表の 中の その 人の ポインタだけ かえる
    h, ao = header(rom, 14, 3); q = fo(sb, r16(rom, ao + 9)) + 2
    q += 1 + 5 * rom[q]; q += 1 + 8 * rom[q]; q += 1 + 5 * rom[q]
    oo = q + 1 + 13 * ob[0]; assert rom[oo] == 0x83
    rom[oo + 9:oo + 11] = w16(new)
    log.append('第128弾 5：ニビの ニドラン faceplayer（$%02X:$%04X）' % (sb, new))


def givepoke(rom, log):
    o = fo(3, 0x6591)
    expect(rom, o, 'fa fc cf a7 28 06 fa fc cf ea 31 ad fa fe cf ea 43 d1 ea df d0')
    # $659D（.done）へは 手持ちに 入った とき（$03:$6558・$656A の jr）も とんで くるので そこは そのまま。
    # $6591〜$659C（12 バイト）を farcall $49 ＋ nop に：ld a,1 / call OpenSRAM / ld a,[wCurItem] / ld [sBoxMon1Item],a /
    # jp CloseSRAM（持ち物が 0 でも 書く）
    f = Free(rom, FB)
    h = f.put(bytes([0x3E, 0x01, 0xCD]) + w16(OPEN_SRAM) + bytes.fromhex('fafccf ea31ad') + bytes([0xC3]) + w16(CLOSE_SRAM))
    rom[o:o + 12] = bytes([0x3E, FB, 0x21]) + w16(h) + bytes([0xCF]) + bytes(6)
    log.append('第128弾 9：GivePoke（ボックスへ 送る ポケモンの 持ち物）$03:$6591 → $%02X:$%04X' % (FB, h))


def mtmoon(rom, ctx, log):
    # B2F：隠し道具 2つ
    ev = read_events(rom, 26, 37); sb = ev['sb']
    have = {(x[0], x[1]) for x in ev['bgs']}
    f = Free(rom, sb)
    for (x, y), it, fl in (((18, 12), MOON_STONE, HID_MOON_STONE), ((33, 9), ETHER, HID_ETHER)):
        assert (y, x) not in have
        d = f.put(w16(fl) + bytes([it]))
        ev['bgs'].append(bytes([y, x, 0x07]) + w16(d))                    # BGEVENT_ITEM
    ea = write_events(rom, ev, f)
    # 1F：(x5,y32) の ボール → KT_WaterGunBall
    ev1 = read_events(rom, 26, 35); sb1 = ev1['sb']
    hit = [i for i, o in enumerate(ev1['objs']) if (o[2] - 4, o[1] - 4) == (5, 32)]
    assert len(hit) == 1
    o = ev1['objs'][hit[0]]
    assert o[0] == 0x54 and o[7] == 0x01 and r16(o, 11) == 0x805, o.hex(' ')
    expect(rom, fo(sb1, r16(o, 9)), 'cb 01')                               # TM12（あまいかおり）
    wg = ctx['kt_watergun']
    st = 0x7FFC                                                           # $7A の さいご（$7FFA の sjump の あと）
    assert sb1 == 0x7A and rom[fo(sb1, 0x7FFA)] == 0x66 and not any(rom[fo(sb1, 0x7FFB):fo(sb1, 0x8000)])
    rom[fo(sb1, st):fo(sb1, st) + 4] = bytes([0x04, 0xFC]) + w16(wg)       # farsjump KT_WaterGunBall
    h, ao = header(rom, 26, 35); q = fo(sb1, r16(rom, ao + 9)) + 2
    q += 1 + 5 * rom[q]; q += 1 + 8 * rom[q]; q += 1 + 5 * rom[q]
    oo = q + 1 + 13 * hit[0]; assert rom[oo:oo + 13] == o
    rom[oo + 7] = 0x00                                                    # OBJECTTYPE_SCRIPT
    rom[oo + 9:oo + 11] = w16(st)
    log.append('第128弾 8：おつきみやま B2F 隠し道具 2つ（イベント $%02X:$%04X）、1F の ボール → $FC:$%04X' % (sb, ea, wg))


def tackle(rom, log):
    o32, oh = fo(0x32, 0x4E1E), fo(0x33, 0x4166)
    expect(rom, o32, 'c3 20 7e')                                          # 第126弾 → TS_Customs1
    expect(rom, oh, 'cd 2e 3c cd b1 41')                                  # PushLYOverrides / BattleAnimRequestPals
    f32 = Free(rom, 0x32); fm = Free(rom, FB)
    src = open(os.path.join(H, 'src', 'tackle_tiles_silver.asm'), encoding='utf-8').read()
    defs = 'DEF CODE32 EQU $%04X\nDEF CODEM EQU $%04X\nDEF BANKM EQU $%02X\nDEF OLD1 EQU $7E20\n' % (f32.a, fm.a, FB)
    before = bytes(rom)
    asmpatch.overlay(rom, defs + src)
    d = [i for i in range(len(rom)) if rom[i] != before[i]]
    assert all(fo(0x32, f32.a) <= i < fo(0x33, 0x4000) or fo(FB, fm.a) <= i < fo(FB + 1, 0x4000) for i in d)
    # 入口の 番地（セクションの 先頭）
    nt = f32.a; tt_setup = fm.a
    assert rom[fo(0x32, nt)] == 0xFE and rom[fo(0x32, nt) + 1] == 0x43       # cp LOW(rSCX)
    # TT_Hook は main の 中：ラベルが いるので 2回目に sym を 読む かわりに、ソースの 順で さがす
    hook = find_hook(rom, fm.a)
    rom[o32 + 1:o32 + 3] = w16(nt)
    rom[oh:oh + 6] = bytes([0x3E, FB, 0x21]) + w16(hook) + bytes([0xCF])
    log.append('第128弾 11：たいあたりの 6段目 $32:$%04X、$%02X:$%04X（TT_Hook $%04X）' % (nt, FB, tt_setup, hook))


def levelup_box(rom, log):
    o1, o2 = fo(0x0F, 0x6EA0), fo(0x0F, 0x6EC3)
    expect(rom, o1, 'af ea 53 ce 3e 1f cd 05 2e 21 a9 c3 06 0a 0e 09 cd c1 0e 21 d3 c3')
    expect(rom, o2, 'cd 26 0a cd 20 31 af ea 53 ce')
    expect(rom, fo(0x48, 0x4C5E), '21 df cd 3e 07 22 22 22 22 77')        # StatusColor_BattleLayout（第127弾で 7）
    f = Free(rom, 0x48)
    src = open(os.path.join(H, 'src', 'levelup_box_silver.asm'), encoding='utf-8').read()
    before = bytes(rom)
    asmpatch.overlay(rom, 'DEF BOX_ADDR EQU $%04X\n' % f.a + src)
    d = [i for i in range(len(rom)) if rom[i] != before[i]]
    assert d and min(d) >= fo(0x48, f.a) and max(d) < fo(0x49, 0x4000)
    pre = f.a
    post = pre + bytes(rom[fo(0x48, pre):fo(0x48, pre) + 0x40]).index(bytes.fromhex('cd 26 0a cd 20 31'))
    rom[o1:o1 + 19] = bytes([0x3E, 0x48, 0x21]) + w16(pre) + bytes([0xCF, 0x18, 0x0B]) + bytes(11)
    rom[o2:o2 + 6] = bytes([0x3E, 0x48, 0x21]) + w16(post) + bytes([0xCF])
    log.append('第128弾 7：レベルアップの 箱 $0F:$6EA0・$6EC3 → $48:$%04X・$%04X' % (pre, post))


def vram_bank1(rom, log):
    # 状態異常の 色（src/statuscolor_silver.asm）の VRAM バンク1 への 書きこみ：SC_AttrRun・SC_MakeGlyphs は rVBK を 1 に
    # した まま 1バイトずつ SC_WriteVRAM（di〜ei）を よんで いた。あいだで VBlank が 来ると、BG マップの 転送が バンク1
    # （属性）に タイルを 書いて、下の 文の 箱などが 化けた（レベルアップの 箱の あとで 見つけた）。
    # → バンク1 を えらぶのは di〜ei の 中だけに する SC_WriteVRAM1 を 足して、その 2つから よぶ。
    o = fo(0x48, 0x4B8B); expect(rom, o, '3e 01 e0 4f 78 cd d3 4d 0d 20 fa af e0 4f')        # SC_AttrRun
    g = fo(0x48, 0x4DA8); expect(rom, g, 'af e0 4f cd c9 4d 13 13 4f 3e 01 e0 4f 79 cd d3 4d af cd d3 4d')  # MakeGlyphs.row
    f = Free(rom, 0x48)
    w1 = f.put(bytes.fromhex('c5 4f f3 3e 01 e0 4f f0 41 e6 02 20 fa 71 af e0 4f fb 23 79 c1 c9'))
    rom[o:o + 4] = bytes(4); rom[o + 6:o + 8] = w16(w1)
    rom[g + 9:g + 13] = bytes(4); rom[g + 15:g + 17] = w16(w1); rom[g + 19:g + 21] = w16(w1)
    log.append('第128弾 7：状態異常の 色の VRAM バンク1 の 書きこみ（SC_WriteVRAM1 $48:$%04X）' % w1)


def find_hook(rom, start):
    # TT_Hook：call PushLYOverrides（cd 2e 3c）の あと ld a,[wTTState]（fa 93 c7）
    o = fo(FB, start); b = bytes(rom[o:o + 0x400])
    i = b.find(bytes.fromhex('cd 2e 3c fa 93 c7'))
    assert i >= 0 and b.find(bytes.fromhex('cd 2e 3c fa 93 c7'), i + 1) < 0
    return start + i


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    console(rom, log)
    mom_phone(rom, log)
    transfer(rom, log)
    statues(rom, log)
    fossils(rom, log)
    nidoran(rom, log)
    givepoke(rom, log)
    mtmoon(rom, ctx, log)
    tackle(rom, log)
    levelup_box(rom, log)
    vram_bank1(rom, log)
    return rom
