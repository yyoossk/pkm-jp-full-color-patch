"""クリスタル版（完成 ROM）の カントーを 銀へ 写す。

  決まり：
   ・クリスタル版の バンク $60〜$7C（この MOD が 足した もの）は 銀の 同じ バンクへ そのまま 写す。
   ・日本版クリスタルの もとの バンク b（$60 より 下）に ある データ（マップ・スクリプト・セリフ・動き など）は、
     使う 所だけ 銀の バンク b+$80 の 同じ アドレスへ 写す。だから 同じバンクの ポインタは そのまま 使える。
     3バイトの ポインタ（バンク つき）の バンクだけ 読みかえる。
   ・写した スクリプトの 命令・フラグ・special・std・マップ・どうぐ・人の絵・曲 などは 銀の 番号へ 読みかえる。
   ・読みかえられない ものは log に 書いて、あとで 1つずつ 直す。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gsc, cscript, cmaps, xlat
from gsc import fo, r16

MOD_LO, MOD_HI = 0x60, 0x7C           # この MOD の バンク（そのまま 写す）
EXT_FLAG_BASE = 0x800                  # 銀で 足す イベントフラグ（クリスタルに しか ない もの）
CR_HOME = {}                           # クリスタルの ホーム（バンク0）の スクリプト → 銀の アドレス（あとで 足す）


def cb(b):
    """クリスタルの バンク → 銀の バンク"""
    if b == 0: return 0
    if MOD_LO <= b <= 0x7F: return b
    if b < MOD_LO: return b + 0x80
    return b                               # $80〜（追加機能キットの バンク）は 銀では 別に 作る


# setval 0 / waitsfx（3バイト）
SPECIAL_SUB = {'CheckMobileAdapterStatusSpecial': bytes([0x15, 0x00, 0x85]),
               'StubbedTrainerRankings_Healings': bytes([0x85, 0x85, 0x85])}


class Port:
    def __init__(s, silver, cmod, log):
        s.s = silver; s.c = cmod; s.log = log
        s.T = xlat.Tables()
        s.CM = cmaps.CMaps(cmod)
        s.SM = gsc.Maps(silver, gsc.PG + '/constants/map_constants.asm')
        s.done = set()            # 読みかえ 済みの 銀の 位置
        s.seen_script = set(); s.seen_text = set(); s.seen_move = set()
        s.copied = set()          # 写した クリスタルの 位置
        s.ext_flags = {}          # クリスタルの フラグ → 銀の フラグ（足した もの）
        s.todo = {}
        s.ram = {}; s.ram_pos = []  # 使って いる WRAM の アドレス（読みかえる）
        s.trainers = set()        # カントーで 使う (クラス, 番号)（クリスタルの 番号）
        s.force = {}              # クリスタルの フラグ → 銀の フラグ（シーンに 使う バイトは まとめて 動かす）

    def note(s, kind, msg):
        s.todo.setdefault(kind, set()).add(msg)

    # ---------- 写す
    def copy(s, b, a, n):
        """クリスタル b:a から n バイトを 銀へ（$60 より 下の バンクだけ。上は もう 写して ある）"""
        if b >= MOD_LO: return
        src = fo(b, a); dst = fo(cb(b), a)
        for i in range(n):
            if src + i in s.copied: continue
            s.copied.add(src + i); s.s[dst + i] = s.c[src + i]

    def dst(s, b, a): return fo(cb(b), a)

    def put16(s, o, v):
        s.s[o] = v & 0xff; s.s[o + 1] = v >> 8

    def once(s, o):
        if o in s.done: return False
        s.done.add(o); return True

    # ---------- 番号の 読みかえ
    def x_flag(s, v):
        if v == 0xFFFF or v == 0: return v
        if v in s.force: return s.force[v]
        n = xlat.inv(s.T.c_ev).get(v)
        if v >= 0x800:                                     # この MOD が 足した フラグ（第15弾）
            return v
        if n and n in s.T.g_ev: return s.T.g_ev[n]
        if v not in s.ext_flags:
            s.ext_flags[v] = EXT_FLAG_BASE + 0x400 + len(s.ext_flags)   # $C00〜（クリスタルだけの フラグ）
        return s.ext_flags[v]

    def x_named(s, cd, gd, v, kind):
        if isinstance(cd, list):
            if v < len(cd) and cd[v] in gd: return gd.index(cd[v])
            s.note(kind, '%s %s' % (hex(v), cd[v] if v < len(cd) else '?')); return v
        n = xlat.inv(cd).get(v)
        if n in gd: return gd[n]
        s.note(kind, '%s %s' % (hex(v), n)); return v

    def x_map(s, g, m):
        if (g, m) == (0, 0) or g == 0xFF or m == 0xFF: return g, m
        if g == 26 and m > cmaps.G26_JP: return 26, m - cmaps.G26_JP + len(s.SM.groups[25][1])
        n = s.CM.name.get((g, m))
        if n in s.SM.id: return s.SM.id[n]
        s.note('map', '%d:%d %s' % (g, m, n)); return g, m

    def x_sprite(s, v):
        if v == 0 or v >= 0x67: return v                   # $67〜 は この MOD の 2つめの 表（第14弾など）→ 銀にも 同じ 表を 作る
        if v >= 0x80: return v                             # 変わる 人の絵（SPRITE_VARS）
        return s.x_named(s.T.c_spr, s.T.g_spr, v, 'sprite')

    def x_item(s, v):
        if v == 0 or v >= 0xBF: return v                 # わざマシン・ひでんマシンは 同じ 番号
        return s.x_named(s.T.c_item, s.T.g_item, v, 'item')

    def x_trclass(s, v):
        if v >= 0x44: return v                             # この MOD の クラス（第10弾）→ 銀にも 足す
        return s.x_named(s.T.c_tc, s.T.g_tc, v, 'trainerclass')

    # ---------- スクリプト
    def script(s, b, a):
        stack = [(b, a)]
        while stack:
            b, a = stack.pop()
            while True:
                if b >= 0x80:
                    s.note('kitbank', 'script %02X:%04X' % (b, a)); break
                if a < 0x4000:
                    s.note('home', 'script %02X:%04X' % (b, a)); break
                if (b, a) in s.seen_script: break
                s.seen_script.add((b, a))
                try:
                    op, name, args, ln, end = cscript.decode(s.c, b, a)
                except ValueError as e:
                    s.note('bad', str(e)); break
                s.copy(b, a, ln)
                d = s.dst(b, a)
                if op == 0x5d: s.trainers.add((args[0][1], args[1][1]))
                if s.once(d):
                    if op not in cscript.SILVER_OP: s.note('op', '%s @ %02X:%04X' % (name, b, a))
                    else: s.s[d] = cscript.SILVER_OP[op]
                    if op == 0x9f: s.note('op', 'swarm @ %02X:%04X' % (b, a))
                for f, v, p in args:
                    q = d + (p - fo(b, a))
                    if not s.once(q):
                        if f == 'p': stack.append((b, v))
                        elif f == 'F': stack.append(v)
                        continue
                    s.arg(f, v, q, b, stack)
                a += ln
                if end: break

    def arg(s, f, v, q, b, stack):
        if f == 'p': stack.append((b, v))
        elif f == 'F': s.s[q] = cb(v[0]); stack.append(v)
        elif f == 't': s.text(b, v)
        elif f == 'T': s.s[q] = cb(v[0]); s.text(*v)
        elif f == 'm': s.movement(b, v)
        elif f == 'E': s.put16(q, s.x_flag(v))
        elif f == 'G':
            if xlat.inv(s.T.c_eng).get(v) == 'ENGINE_PLAYER_IS_FEMALE':     # 銀の 主人公は いつも 男の子 → いつも 0 の フラグ
                s.put16(q, s.T.g_eng['ENGINE_UNUSED_STATUSFLAGS2_3'])
            else: s.put16(q, s.x_named(s.T.c_eng, s.T.g_eng, v, 'engineflag'))
        elif f == 'S':
            r = s.x_named(s.T.c_special, s.T.g_special, v, 'special')
            cs = s.T.c_special; nm = cs[v] if isinstance(cs, list) and v < len(cs) else None
            if nm in SPECIAL_SUB:                     # 銀に ない 特別な 処理（モバイル・つうしん の 記録）→ 同じ 長さの 命令
                s.s[q - 1:q + 2] = SPECIAL_SUB[nm]
            else:
                if nm not in s.T.g_special: s.note('special_at', '%s %s' % (hex(v), getattr(s, 'curmap', '?')))
                s.put16(q, r)
        elif f == 'D': s.put16(q, s.x_named(s.T.c_std, s.T.g_std, v, 'std'))
        elif f == 'M':
            g, m = s.x_map(v & 0xff, v >> 8); s.s[q] = g; s.s[q + 1] = m
        elif f == 'I': s.s[q] = s.x_item(v)
        elif f == 'P': s.s[q] = s.x_sprite(v)
        elif f == 'Q': s.put16(q, s.x_named(s.T.c_mus, s.T.g_mus, v, 'music'))
        elif f == 'Y': s.put16(q, s.x_named(s.T.c_sfx, s.T.g_sfx, v, 'sfx'))
        elif f == 'L': s.s[q] = s.x_trclass(v)
        elif f == 'A': s.s[q] = cb(v[0]); s.note('asm', 'callasm %02X:%04X' % v)
        elif f == 'X': s.s[q] = cb(v[0]); s.note('far', 'data %02X:%04X' % v)
        elif f in 'RUN': s.note('data', '%s %02X:%04X' % (f, b, v))
        elif f == 'w' and 0xC000 <= v < 0xE000:
            s.ram.setdefault(v, set()).add('script'); s.ram_pos.append((v, q))

    # ---------- テキスト
    def text(s, b, a):
        if a < 0x4000: s.note('home', 'text %02X:%04X' % (b, a)); return
        if b >= 0x80: s.note('kitbank', 'text %02X:%04X' % (b, a)); return
        while True:
            if (b, a) in s.seen_text: return
            s.seen_text.add((b, a))
            o = fo(b, a); c = s.c[o]
            if c == 0x00:                                         # 文字（@ まで。<DONE>・<PROMPT> で 終わり）
                n = 1
                while s.c[o + n] not in (0x50, 0x57, 0x58): n += 1
                term = s.c[o + n]; s.copy(b, a, n + 1); a += n + 1
                if term != 0x50: return
                continue
            ln = {0x01: 3, 0x02: 4, 0x03: 3, 0x04: 5, 0x05: 1, 0x06: 1, 0x07: 1, 0x09: 4, 0x0a: 1, 0x0b: 1, 0x0c: 2,
                  0x0d: 1, 0x0e: 1, 0x0f: 1, 0x10: 1, 0x11: 1, 0x12: 1, 0x13: 1, 0x14: 2, 0x15: 1, 0x16: 4}.get(c)
            if c == 0x50: s.copy(b, a, 1); return
            if c == 0x08: s.copy(b, a, 1); s.note('textasm', '%02X:%04X' % (b, a)); return
            if ln is None: s.note('badtext', '%02X:%04X %02X' % (b, a, c)); return
            s.copy(b, a, ln)
            if c == 0x16:
                fa = r16(s.c, o + 1); fb = s.c[o + 3]
                q = s.dst(b, a) + 3
                if s.once(q): s.s[q] = cb(fb)
                s.text(fb, fa)
            elif c in (0x01, 0x02, 0x09):
                s.ram.setdefault(r16(s.c, o + 1), set()).add('text%02X' % c)
                s.ram_pos.append((r16(s.c, o + 1), s.dst(b, a) + 1))
            a += ln

    def movement(s, b, a):
        if (b, a) in s.seen_move: return
        s.seen_move.add((b, a)); o = fo(b, a); n = 0
        while True:
            c = s.c[o + n]; n += 1
            if c in (0x4f, 0x55): n += 1
            if c in (0x47, 0x4a, 0x4b): break
            if n > 400: s.note('badmove', '%02X:%04X' % (b, a)); break
        s.copy(b, a, n)

    # ---------- マップ
    def map(s, k):
        """クリスタル版の マップ k を 写して、銀の ヘッダー（9バイト）を 返す"""
        CM = s.CM; c = s.c; s.curmap = CM.name.get(k, str(k))
        h = CM.header(k); at = CM.attributes(k)
        ab, aa = h['attr_bank'], h['attr']
        n_at = 12 + 12 * len(at['conns'])
        s.copy(ab, aa, n_at)
        ao = s.dst(ab, aa)
        if s.once(ao):
            s.s[ao + 3] = cb(at['blocks_bank']); s.s[ao + 6] = cb(at['scripts_bank'])
            p = ao + 12
            for cn in at['conns']:
                g, m = s.x_map(cn['group'], cn['map']); s.s[p] = g; s.s[p + 1] = m
                s.put16(p + 4, cn['dst'] - 0x100); s.put16(p + 10, cn['window'] - 0x100)   # wOverworldMap：クリスタル $C800 → 銀 $C700
                p += 12
        s.copy(at['blocks_bank'], at['blocks'], at['width'] * at['height'])
        sb = at['scripts_bank']
        sc, cbs, so, se = cmaps.map_scripts(c, sb, at['scripts'])
        s.copy(sb, at['scripts'], se - so)
        for x in sc: s.script(sb, x)
        for t, x in cbs: s.script(sb, x)
        ev = CM.events(k)
        s.copy(sb, at['events'], ev['end'] - ev['off'])
        eo = s.dst(sb, at['events'])
        p = eo + 2 + 1
        for w in ev['warps']:
            if s.once(p):
                g, m = s.x_map(w[3], w[4]); s.s[p + 3] = g; s.s[p + 4] = m
            p += 5
        p += 1
        for cdv in ev['coords']:
            s.script(sb, cdv[4] | cdv[5] << 8); p += 8
        p += 1
        for g_ in ev['bgs']:
            x, y, f, lo, hi = g_; ptr = lo | hi << 8
            if f <= 4: s.script(sb, ptr)
            elif f in (5, 6):
                s.copy(sb, ptr, 4); q = s.dst(sb, ptr)
                if s.once(q): s.put16(q, s.x_flag(r16(c, fo(sb, ptr))))
                s.script(sb, r16(c, fo(sb, ptr) + 2))
            elif f == 7:
                s.copy(sb, ptr, 3); q = s.dst(sb, ptr)
                if s.once(q):
                    s.put16(q, s.x_flag(r16(c, fo(sb, ptr)))); s.s[q + 2] = s.x_item(c[fo(sb, ptr) + 2])
            p += 5
        p += 1
        for ob in ev['objects']:
            if s.once(p):
                s.s[p] = s.x_sprite(ob[0])
                fl = ob[11] | ob[12] << 8; s.put16(p + 11, s.x_flag(fl))
            typ = ob[7] & 0x0f; ptr = ob[9] | ob[10] << 8
            if typ == 0 and ptr == 0x26B2: s.put16(p + 9, 0x27BF)       # ObjectEvent（ホーム）
            elif typ == 0 and ptr: s.script(sb, ptr)
            elif typ == 1:
                s.copy(sb, ptr, 2); q = s.dst(sb, ptr)
                if s.once(q): s.s[q] = s.x_item(c[fo(sb, ptr)])
            elif typ == 2:
                s.copy(sb, ptr, 14); q = s.dst(sb, ptr); o = fo(sb, ptr)
                s.trainers.add((c[o + 2], c[o + 3]))
                if s.once(q):
                    s.put16(q, s.x_flag(r16(c, o))); s.s[q + 2] = s.x_trclass(c[o + 2])
                for i in (4, 6, 8):
                    v = r16(c, o + i)
                    if v: s.text(sb, v)
                v = r16(c, o + 10)
                if v: s.script(sb, v)
            p += 13
        return bytes([cb(ab), h['tileset'], h['env']]) + aa.to_bytes(2, 'little') + bytes(
            [h['landmark'], h['music'], h['palette'], h['fish']])
