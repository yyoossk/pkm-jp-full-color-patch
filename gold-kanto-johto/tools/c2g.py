"""クリスタル（改造後）で変わったマップを、金の形にして 金の ROM に入れる。
   ・cwalk で集めた かたまりを、クリスタルのバンクごとに 金のバンク（$80〜）へ 1対1 で うつす（バンクの中の近いポインターを そのまま使えるように）
   ・ID（イベントフラグ・マップ・人の絵・曲・効果音・特別処理・std・エンジンフラグ）を 名前で 読みかえる
"""
import sys, re
sys.path.insert(0, '/home/claude/work/scripts')
from consts import all_tables, R
from cmaps import maplist
from maps import CMGP, GMGP, groups
from cwalk import Walk, fo, w
from near import load as loadsym_list, near

C = all_tables('pokecrystal'); G = all_tables('pokegold')
C['trainerclass'] = {n: i for i, n in enumerate(re.findall(r'trainerclass (\w+)', open(R + 'pokecrystal/constants/trainer_constants.asm').read()))}
G['trainerclass'] = {n: i for i, n in enumerate(re.findall(r'trainerclass (\w+)', open(R + 'pokegold/constants/trainer_constants.asm').read()))}
CSYM = loadsym_list('/home/claude/work/ref/crystal_jp.sym')
GJP = {}
for l in open('/home/claude/work/goldsrc/src/jp_all.inc'):
    m = re.match(r'DEF J_(\S+) EQU \$([0-9a-f]+)', l)
    if m: GJP[m.group(1)] = int(m.group(2), 16)

def inv(T, prefix):
    d = {}
    for n, v in T.items():
        if n.startswith(prefix): d.setdefault(v, n)
    return d
CMAP = {}; GMAP = {}
for gi, (gn, ms) in enumerate(groups('pokecrystal')):
    for mi, mn in enumerate(ms): CMAP[(gi + 1, mi + 1)] = mn
for gi, (gn, ms) in enumerate(groups('pokegold')):
    for mi, mn in enumerate(ms): GMAP[mn] = (gi + 1, mi + 1)
# クリスタルにしかない マップ名 → 金の かわりの マップ（必要になったら 足す）
MAPALIAS = {}
# ホームの住所（クリスタル → 金）
HOMEMAP = {0x26B2: 0x27BF}   # ObjectEvent（jumptextfaceplayer ObjectEventText）
# RAM（日本版クリスタル → 日本版金）
RAMMAP = {0xD071: 0xCF9D, 0xC2DD: 0xD165}    # wStringBuffer3・wScriptVar（rammap.py で 確かめた）

# 金で 空いていて、クリスタルでは 名前の ある 番号（クリスタル版は その 番号を 名前なしでは 使わない）
EV_POOL = sorted((set(range(0x800)) - set(v for n, v in G['event'].items() if n.startswith('EVENT_')))
                 & set(v for n, v in C['event'].items() if n.startswith('EVENT_')))
EV_EXTRA = {}

# 金に ない もの の かわり
ENGINE_ALIAS = {'ENGINE_PLAYER_IS_FEMALE': 'ENGINE_UNUSED_STATUSFLAGS2_3', 'ENGINE_MOBILE_SYSTEM': 'ENGINE_UNUSED_STATUSFLAGS2_3'}   # 金に 女の子は いない（いつも 立たない フラグ）
SPRITE_ALIAS = {'SPRITE_KRIS': 'SPRITE_CHRIS'}
SFX_ALIAS = {'SFX_GLASS_TING': 'SFX_SHINE', 'SFX_GLASS_TING_2': 'SFX_SHINE'}            # 金に ない 音
SPECIAL_ALIAS = {'StubbedTrainerRankings_Healings': 'UnusedCheckUnusedTwoDayTimer'}   # なにも しない（金に ない）                            # 上の フラグが 立たないので 出ない
class Xlat:
    def __init__(s):
        s.miss = []
        s.ev = inv(C['event'], 'EVENT_'); s.en = inv(C['engine'], 'ENGINE_'); s.sp = inv(C['sprite'], 'SPRITE_')
        s.mu = inv(C['music'], 'MUSIC_'); s.sf = inv(C['sfx'], 'SFX_')
        s.spc = {v: n for n, v in C['special'].items()}; s.stdn = {v: n for n, v in C['std'].items()}
        s.tc = {v: n for n, v in C['trainerclass'].items()}
        s.ts = inv(C['tileset'], 'TILESET_'); s.lm = inv(C['landmark'], 'LANDMARK_')
        s.gfree = set(range(0x800)) - set(v for n, v in G['event'].items() if n.startswith('EVENT_'))
    def _m(s, what, v, ctx):
        s.miss.append('%s %s（%s）' % (what, hex(v) if isinstance(v, int) else v, ctx)); return v
    def event(s, v, ctx=''):
        if v in (0xFFFF,): return v
        n = s.ev.get(v)
        if n is None:
            if v in s.gfree: return v     # 名前のない（MOD で使い始めた）フラグは 金でも空いている同じ番号
            if 0x800 <= v <= 0xA17: return v   # 第15弾の 土台（gold_flags.py）で 金でも 使える
            if v < 0x800:                        # 名前なしで 使っているが 金では 使われている 番号 → 空きを わりあてる
                k = ('num', v)
                if k not in EV_EXTRA: EV_EXTRA[k] = EV_POOL.pop(0)
                return EV_EXTRA[k]
            return s._m('event', v, ctx)
        g = G['event'].get(n)
        if g is None:
            # クリスタルに しか ない 名前の フラグ：金で 空いていて、クリスタル版が 名前なしで 使わない 番号を わりあてる
            g = EV_EXTRA.get(n)
            if g is None:
                g = EV_POOL.pop(0); EV_EXTRA[n] = g
        return g
    def engine(s, v, ctx=''):
        n = s.en.get(v); n = ENGINE_ALIAS.get(n, n); g = G['engine'].get(n) if n else None
        return g if g is not None else s._m('engine %s' % n, v, ctx)
    def sprite(s, v, ctx=''):
        if v >= 0xF0: return v   # SPRITE_VARS など
        if 0x67 <= v <= 0x7A: return v - 0x67 + 0x60     # クリスタル版の 新しい 人の絵（第11弾で 金に 入れる）
        if v == 0x3F: return 0x74                         # クリスタル版の サカキ（第13弾）
        n = s.sp.get(v); n = SPRITE_ALIAS.get(n, n); g = G['sprite'].get(n) if n else None
        return g if g is not None else s._m('sprite %s' % n, v, ctx)
    def music(s, v, ctx=''):
        if 0xF0 <= v <= 0xF3: return v                    # 第98弾：シゲルの 曲（赤の 音の しくみ 1。gold_opening）
        if v == 0x52: return 0x01                          # 第102弾：赤の Music_Dungeon2（金では MUSIC_TITLE の 番号。gold_hof）
        n = s.mu.get(v); g = G['music'].get(n) if n else None
        return g if g is not None else s._m('music %s' % n, v, ctx)
    def sfx(s, v, ctx=''):
        n = s.sf.get(v); n = SFX_ALIAS.get(n, n); g = G['sfx'].get(n) if n else None
        return g if g is not None else s._m('sfx %s' % n, v, ctx)
    def special(s, v, ctx=''):
        n = s.spc.get(v); n = SPECIAL_ALIAS.get(n, n); g = G['special'].get(n) if n else None
        return g if g is not None else s._m('special %s' % n, v, ctx)
    def std(s, v, ctx=''):
        n = s.stdn.get(v); g = G['std'].get(n) if n else None
        return g if g is not None else s._m('std %s' % n, v, ctx)
    def tclass(s, v, ctx=''):
        # 日本版の トレーナーの種類の番号は 1〜66 が 金と同じ（67 なぞのせいねん は 金にない）
        return v if 1 <= v <= 79 else s._m('trainerclass', v, ctx)
    def tileset(s, v, ctx=''):
        if 33 <= v <= 53: return v - 33 + 29      # クリスタル版の 新しい タイルセット（第11弾〜）→ 金 29〜
        n = s.ts.get(v); g = G['tileset'].get(n) if n else None
        return g if g is not None else s._m('tileset %s' % n, v, ctx)
    def landmark(s, v, ctx=''):
        n = s.lm.get(v); g = G['landmark'].get(n) if n else None
        return g if g is not None else s._m('landmark %s' % n, v, ctx)
    def mapid(s, gn, ctx=''):
        if tuple(gn) == (0, 0): return (0, 0)          # warp NONE（パソコンから 通信 など）
        n = CMAP.get(gn); n = MAPALIAS.get(n, n)
        g = GMAP.get(n)
        if g is None: s._m('map %s' % n, gn, ctx); return gn
        return g

class Emit:
    """クリスタルのバンク → 金のバンク。かたまりを 同じ アドレスの 並びで 詰める"""
    def __init__(s, rom, first_bank=0x80):
        s.rom = rom; s.X = Xlat(); s.bankmap = {}; s.next_bank = first_bank; s.fill = {}; s.loc = {}
        s.homemiss = []; s.blk = {}; s.pending = []
    def gbank(s, cb):
        if cb not in s.bankmap:
            s.bankmap[cb] = s.next_bank; s.fill[s.next_bank] = 0x4000; s.next_bank += 1
        return s.bankmap[cb]
    def place(s, key, blob):
        if key in s.loc: return s.loc[key]
        cb = blob['bank']; gb = s.gbank(cb)
        a = s.fill[gb]; n = len(blob['data'])
        if a + n > 0x8000: raise Exception('バンクがいっぱい %02X' % gb)
        s.loc[key] = (gb, a); s.fill[gb] = a + n
        return s.loc[key]
    def ptr(s, cbank, a, ctx):
        """クリスタルの (bank, addr) → 金の (bank, addr)"""
        if a < 0x4000:
            if a in HOMEMAP: return (0, HOMEMAP[a])
            hit = near(CSYM, 0, a)
            if hit and hit[1] == 0 and hit[0] in GJP: return (0, GJP[hit[0]])
            s.homemiss.append('%04X %s（%s）' % (a, hit, ctx)); return (0, a)
        key = (cbank, a)
        if key in s.loc: return s.loc[key]
        s.homemiss.append('未配置 %02X:%04X（%s）' % (cbank, a, ctx)); return (s.gbank(cbank), a)

    def write_all(s, blobs):
        for k, b in blobs.items(): s.place(k, b)
        for k, b in blobs.items(): s.write(k, b)
    def write(s, key, b):
        gb, ga = s.loc[key]; data = bytearray(b['data']); X = s.X; ctx = '%s %02X:%04X' % (b['kind'], b['bank'], b['addr'])
        for off, t, sem, name in b['fix']:
            if t == 'dw':
                v = data[off] | data[off + 1] << 8; nv = v
                if sem == 'event_flag': nv = X.event(v, ctx)
                elif sem == 'engine_flag': nv = X.engine(v, ctx)
                elif sem in ('music_pointer', 'music'): nv = X.music(v, ctx)
                elif sem == 'sound_pointer': nv = X.sfx(v, ctx)
                elif sem == 'special': nv = X.special(v, ctx)
                elif sem == 'std': nv = X.std(v, ctx)
                elif sem == 'cry_id': nv = v
                elif sem in ('ram', 'address'):
                    nv = RAMMAP.get(v)
                    if nv is None:
                        import asmx
                        nv = asmx.RAM_FIX.get(v)
                        if nv is None and v >= 0xFF80 and (v & 0xFF) in asmx.HRAM: nv = 0xFF00 | asmx.HRAM[v & 0xFF]
                        if nv is None:
                            gv, nm = asmx.RX.x(v)
                            nv = gv if gv is not None else X._m('RAM %s' % nm, v, ctx)
                elif 'pointer' in sem or sem == 'data':
                    if v not in (0, 0xFFFF): nv = s.ptr(b['bank'], v, ctx)[1]
                data[off] = nv & 0xFF; data[off + 1] = nv >> 8
            elif t == 'map_id':
                g, n = X.mapid((data[off], data[off + 1]), ctx); data[off] = g; data[off + 1] = n
            elif t == 'dba':
                bb, aa = data[off], data[off + 1] | data[off + 2] << 8
                nb, na = s.ptr(bb, aa, ctx); data[off] = nb; data[off + 1] = na & 0xFF; data[off + 2] = na >> 8
            elif t == 'db':
                if sem == 'sprite': data[off] = X.sprite(data[off], ctx)
                elif sem == 'trainer_group': data[off] = X.tclass(data[off], ctx)
                elif sem == 'opcode':
                    nv = {0x9F: 0x9E, 0xA0: 0x9F, 0xA1: 0xA0, 0xA2: 0xA1}.get(data[off])   # swarm・halloffame・credits・warpfacing
                    if nv is None: X._m('命令 %02X %s' % (data[off], name), data[off], ctx)
                    else: data[off] = nv
        o = gb * 0x4000 + ga - 0x4000
        s.rom[o:o + len(data)] = data

def emit_map(E, W, at, cname, chdr, crom, grom, gmaps, cmaps_by_name):
    """at: cwalk.map の結果。gmaps: 金のマップ一覧（名前→dict）"""
    X = E.X; gname = MAPALIAS.get(cname, cname)
    if gname not in gmaps: X._m('金にないマップ', cname, cname); return
    gm = gmaps[gname]
    cb = at['scbank']; gb = E.gbank(cb)
    def alloc(n, bank):
        a = E.fill[bank]
        if a + n > 0x8000: raise Exception('バンクがいっぱい %02X' % bank)
        E.fill[bank] = a + n; return a
    # ブロック
    nblk = at['h'] * at['w']; bo = fo(at['blkbank'], at['blk'])
    bgb = E.gbank(at['blkbank']); ba = alloc(nblk, bgb)
    grom[bgb * 0x4000 + ba - 0x4000: bgb * 0x4000 + ba - 0x4000 + nblk] = crom[bo:bo + nblk]
    E.blk[cname] = (bgb, ba)
    # スクリプトの見出し
    sh = bytearray([len(at['scenes'])])
    for p in at['scenes']: sh += E.ptr(cb, p, cname + ' scene')[1].to_bytes(2, 'little') + b'\0\0'
    sh.append(len(at['callbacks']))
    for t, p in at['callbacks']: sh += bytes([t]) + E.ptr(cb, p, cname + ' cb')[1].to_bytes(2, 'little')
    sa = alloc(len(sh), gb); grom[gb * 0x4000 + sa - 0x4000:gb * 0x4000 + sa - 0x4000 + len(sh)] = sh
    # イベント
    ev = bytearray(at['ev0']); ev.append(len(at['warps']))
    for wv in at['warps']:
        g, n = X.mapid((wv[3], wv[4]), cname + ' warp'); ev += wv[:3] + bytes([g, n])
    ev.append(len(at['coords']))
    for c in at['coords']: ev += c[:4] + E.ptr(cb, w(c, 4), cname + ' coord')[1].to_bytes(2, 'little') + c[6:8]
    ev.append(len(at['bgs']))
    for g_ in at['bgs']: ev += g_[:3] + E.ptr(cb, w(g_, 3), cname + ' bg')[1].to_bytes(2, 'little')
    ev.append(len(at['objs']))
    for ob in at['objs']:
        ob = bytearray(ob); ob[0] = X.sprite(ob[0], cname + ' obj')
        p = w(ob, 9); ob[9:11] = E.ptr(cb, p, cname + ' obj')[1].to_bytes(2, 'little')
        fl = w(ob, 11); ob[11:13] = X.event(fl, cname + ' obj').to_bytes(2, 'little')
        ev += ob
    ea = alloc(len(ev), gb); grom[gb * 0x4000 + ea - 0x4000:gb * 0x4000 + ea - 0x4000 + len(ev)] = ev
    E.pending.append((cname, gm, at, gb, sa, ea, bgb, ba, chdr))

def finish_maps(E, crom, grom, cmaps_by_name, gmaps):
    """属性（つながり込み）を書いて、金のマップの見出しを書きかえる。つながりは 相手のブロックの住所で計算しなおす"""
    X = E.X
    for cname, gm, at, gb, sa, ea, bgb, ba, chdr in E.pending:
        attr = bytearray([at['border'], at['h'], at['w'], bgb]) + ba.to_bytes(2, 'little') + bytes([gb]) + sa.to_bytes(2, 'little') + ea.to_bytes(2, 'little') + bytes([at['conn']])
        con = at['connections']
        for i in range(0, len(con), 12):
            c = bytearray(con[i:i + 12])
            cn = CMAP.get((c[0], c[1])); g, n = X.mapid((c[0], c[1]), cname + ' conn'); c[0], c[1] = g, n
            strip = w(c, 2)
            # 相手のブロック：クリスタルの住所 → 金の住所
            cm = cmaps_by_name.get(cn)
            if cm is not None:
                A = crom[cm['attr']:cm['attr'] + 12]; cblk = w(A, 4)
                if cn in E.blk: gblk = E.blk[cn][1]
                else:
                    gmn = gmaps.get(MAPALIAS.get(cn, cn))
                    gblk = w(grom[gmn['attr']:gmn['attr'] + 12], 4) if gmn else cblk
                    # 金の元のブロックを使う：大きさが ちがえば 要注意
                    gA = grom[gmn['attr']:gmn['attr'] + 3] if gmn else None
                    if gA and (gA[1], gA[2]) != (A[1], A[2]): X._m('つながり先の大きさがちがう', cn, cname)
                c[2:4] = (gblk + strip - cblk).to_bytes(2, 'little')
            # wOverworldMapBlocks：クリスタル $C800 → 金 $C700（つながりの 書きこみ先と 窓）
            for k in (4, 10): c[k:k + 2] = (w(c, k) - 0x100).to_bytes(2, 'little')
            attr += c
        aa = E.fill[gb]; E.fill[gb] += len(attr)
        grom[gb * 0x4000 + aa - 0x4000:gb * 0x4000 + aa - 0x4000 + len(attr)] = attr
        h = gm['hdr']; ch = crom[chdr:chdr + 9]
        grom[h] = gb; grom[h + 3] = aa & 0xFF; grom[h + 4] = aa >> 8
        grom[h + 1] = X.tileset(ch[1], cname); grom[h + 2] = ch[2]
        grom[h + 5] = X.landmark(ch[5], cname); grom[h + 6] = X.music(ch[6], cname); grom[h + 7] = ch[7]; grom[h + 8] = ch[8]
