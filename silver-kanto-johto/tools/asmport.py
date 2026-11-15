"""日本版クリスタル用の アセンブリ（この MOD が 書いた もの）を 銀の アドレスへ 読みかえる 道具。
   ・命令を たどって、ホーム（$0000-$3FFF）の 呼び出し・WRAM・HRAM・farcall の 先を 集める
   ・ホームの 関数は、命令の 並び（アドレスを 伏せた もの）が 同じ 所を 銀の ROM0 から さがす
   ・同じ 長さの まま 書きかえる"""
import re
from gsc import fo, r16

L3 = {0x01, 0x11, 0x21, 0x31, 0x08, 0xC2, 0xC3, 0xC4, 0xCA, 0xCC, 0xCD, 0xD2, 0xD4, 0xDA, 0xDC, 0xEA, 0xFA}
L2 = {0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E, 0x18, 0x20, 0x28, 0x30, 0x38, 0xC6, 0xCE, 0xD6, 0xDE,
      0xE0, 0xE6, 0xE8, 0xEE, 0xF0, 0xF6, 0xF8, 0xFE, 0xCB}
JR = {0x18, 0x20, 0x28, 0x30, 0x38}
JP = {0xC2, 0xC3, 0xCA, 0xD2, 0xDA}
CALL = {0xC4, 0xCC, 0xCD, 0xD4, 0xDC}
END = {0xC9, 0xD9, 0xE9, 0xC3, 0x18}          # ret reti jp(hl) jp jr（無条件）


def ilen(op): return 3 if op in L3 else 2 if op in L2 else 1


def norm(rom, o, n=24):
    """命令の 並び（アドレス・WRAM を 伏せる）"""
    out = []; i = 0
    while i < n:
        op = rom[o + i]; L = ilen(op); out.append(op)
        if L == 3: out += ['*', '*']
        elif L == 2: out.append('*' if op in (0xE0, 0xF0) or op in JR else rom[o + i + 1])
        i += L
        if op in (0xC9, 0xD9, 0xE9) or op in (0xC3,): break
    return tuple(out)


class Home:
    """クリスタルの ホームの 関数 → 銀の ホームの 関数"""
    def __init__(s, c, g):
        s.c = c; s.g = g; s.cache = {}
        s.index = {}
        for a in range(0x100, 0x4000):
            for n in (24, 16, 10):
                s.index.setdefault((n, norm(g, a, n)), []).append(a)

    def find(s, a):
        if a in s.cache: return s.cache[a]
        r = None
        for n in (24, 16, 10):
            hits = s.index.get((n, norm(s.c, a, n)), [])
            if len(hits) == 1: r = hits[0]; break
            if len(hits) > 1:
                # 前の 命令も 見る
                best = [h for h in hits if s.g[h - 1] == s.c[a - 1]]
                if len(best) == 1: r = best[0]; break
        s.cache[a] = r
        return r


def walk(rom, bank, addr, limit=4000):
    """関数を たどる → [(位置, op, 長さ)]"""
    seen = set(); out = []; st = [addr]
    while st:
        a = st.pop()
        while True:
            if a in seen or not (0x4000 <= a < 0x8000): break
            seen.add(a); o = fo(bank, a); op = rom[o]; L = ilen(op)
            out.append((a, op, L))
            if op in JR:
                d = rom[o + 1]; t = a + 2 + (d - 256 if d > 127 else d)
                st.append(t)
                if op == 0x18: break
            elif op in JP:
                t = r16(rom, o + 1)
                if 0x4000 <= t < 0x8000: st.append(t)
                if op == 0xC3: break
            elif op in (0xC9, 0xD9, 0xE9):
                break
            elif op in CALL:
                t = r16(rom, o + 1)
                if 0x4000 <= t < 0x8000: st.append(t)
            a += L
            if len(seen) > limit: break
    return sorted(out)


# 手で しらべた ホームの 関数（クリスタル → 銀）
HOME_EXTRA = {0x1D07: 0x1B60, 0x31C2: 0x33C6, 0x3037: 0x30D6}   # 3037 FarCopyWRAM → CopyBytes（銀の 色は WRAM0）
# 手で しらべた WRAM・HRAM（クリスタル → 銀）
WRAM_EXTRA = {
    0xD067: 0xCF93, 0xD068: 0xCF94, 0xD069: 0xCF95, 0xD06A: 0xCF96, 0xD21C: 0xD0C6, 0xD833: 0xD7A3,
    0xDC3F: 0xD989, 0xDC40: 0xD98A, 0xDC41: 0xD98B, 0xDC9D: 0xD9E8, 0xDCA6: 0xD9F1, 0xDCA7: 0xD9F2,
    0xDE3E: 0xDB89, 0xDE3F: 0xDB8A, 0xDE4C: 0xDB97, 0xDE89: 0xDBD4, 0xDE8A: 0xDBD5, 0xDBC3: 0xD90D,
    0xD841: 0xD566, 0xFFAD: 0xFFAF, 0xFFC6: 0xFFC8, 0xFFC7: 0xFFC9, 0xFFC8: 0xFFCA,
}
C_EXT_LO, C_EXT_HI, EXT_DELTA = 0xDA01, 0xDA65, 0xD901 - 0xD60D


class Translator:
    def __init__(s, cmod, corig, silver, wm, Hm, log):
        s.c = cmod; s.co = corig; s.g = silver; s.wm = dict(wm); s.wm.update(WRAM_EXTRA); s.Hm = Hm
        s.log = log; s.unres = {}
        s.fidx = None

    def far(s, b, a):
        """クリスタルの 関数 b:a → 銀の (バンク, アドレス)"""
        if s.fidx is None:
            g = bytes(s.g[:0x100000]) + bytes(64); s.fidx = {}
            for o in range(0x4000, 0x100000): s.fidx.setdefault(norm(g, o, 16), []).append(o)
        o = fo(b, a); hits = s.fidx.get(norm(s.co, o, 16), [])
        if len(hits) > 1:
            same = [h for h in hits if h // 0x4000 == b]
            hits = same or [h for h in hits if s.g[h - 1] == s.co[o - 1]] or hits
        if len(hits) != 1: return None
        h = hits[0]; return h // 0x4000, h % 0x4000 + 0x4000

    def wram(s, v):
        if v in s.wm: return s.wm[v]
        if C_EXT_LO <= v < C_EXT_HI: return v - EXT_DELTA
        if 0xC3A0 <= v < 0xC508: return v                    # タイルマップ（同じ）
        return None

    def routine(s, rom, b, a, name):
        un = []
        db = b + 0x80 if b < 0x60 else b                    # 銀での バンク（port.cb と 同じ）
        for pos, op, L in walk(s.c, b, a):
            o = fo(b, pos); d = fo(db, pos) - o             # rom への 書きこみは o + d
            if L == 3:
                v = r16(s.c, o + 1)
                if (op in CALL or op in JP) and v < 0x4000:
                    t = HOME_EXTRA.get(v) or s.Hm.find(v)
                    if t: rom[o + d + 1] = t & 0xff; rom[o + d + 2] = t >> 8
                    else: un.append('home %04X' % v)
                elif op in (0x01, 0x11, 0x21, 0xEA, 0xFA) and 0xC000 <= v < 0xE000:
                    t = s.wram(v)
                    if t: rom[o + d + 1] = t & 0xff; rom[o + d + 2] = t >> 8
                    else: un.append('wram %04X' % v)
            elif op == 0xE0 and s.c[o + 1] == 0x70 and getattr(s, 'nosvbk', False):
                rom[o + d] = 0x00; rom[o + d + 1] = 0x00            # ldh [rSVBK],a を 消す（銀は スタックが $DFxx）
            elif op in (0xE0, 0xF0) and s.c[o + 1] >= 0x80:
                v = 0xFF00 + s.c[o + 1]; t = s.wram(v)
                if t: rom[o + d + 1] = t & 0xff
                else: un.append('hram %04X' % v)
            elif op == 0xCF and s.c[o - 5] == 0x3E and s.c[o - 3] == 0x21:
                fb, fa = s.c[o - 4], r16(s.c, o - 2)
                if fb >= 0x60: continue
                t = s.far(fb, fa)
                if t: rom[o + d - 4] = t[0]; rom[o + d - 2] = t[1] & 0xff; rom[o + d - 1] = t[1] >> 8
                else: un.append('far %02X:%04X' % (fb, fa))
        if un: s.unres[name] = sorted(set(un))
