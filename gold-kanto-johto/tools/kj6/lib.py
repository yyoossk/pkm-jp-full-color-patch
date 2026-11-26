"""Common helpers for the Satoshi MOD (JP Crystal): paths, symbols, map structures, script assembler, IPS."""
import re, os
SC = os.environ.get('MODROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # project root (parent of tools/)
PC = SC + '/ref/pokecrystal'
PR = SC + '/ref/pokered'
US_ROM = PC + '/pokecrystal.gbc'
JP_BASE = SC + '/crystal/Pocket Monsters - Crystal Version (Japan).gbc'
MODBANK = 0x78


def fo(bank, addr):
    return addr if addr < 0x4000 else bank * 0x4000 + (addr - 0x4000)


def loadsym(path=PC + '/pokecrystal.sym'):
    d = {}
    for l in open(path):
        m = re.match(r'([0-9a-fA-F]+):([0-9a-fA-F]+) (\S+)', l)
        if m:
            d[m.group(3)] = (int(m.group(1), 16), int(m.group(2), 16))
    return d


def load_consts(path):
    d = {}
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*const\s+(\w+)\s*;\s*([0-9a-fA-F]+)', line)
        if m:
            d[m.group(1)] = int(m.group(2), 16)
    return d


def ips(orig, new):
    out = bytearray(b'PATCH')
    i, n = 0, len(new)
    while i < n:
        if orig[i] == new[i]:
            i += 1; continue
        j = i
        while j < n and j - i < 0xFFFF and (orig[j] != new[j] or (j + 1 < n and orig[j + 1] != new[j + 1] and j + 1 - i < 0xFFFF)):
            j += 1
        if i == 0x454F46:
            i -= 1
        out += i.to_bytes(3, 'big') + (j - i).to_bytes(2, 'big') + new[i:j]
        i = j
    out += b'EOF'
    return bytes(out)


def fix_checksum(rom):
    s = (sum(rom) - rom[0x14E] - rom[0x14F]) & 0xFFFF
    rom[0x14E], rom[0x14F] = s >> 8, s & 0xFF


class US:
    _inst = None

    def __init__(s):
        s.us = open(US_ROM, 'rb').read()
        s.S = loadsym()
        b, a = s.S['MapGroupPointers']
        s.mgp = fo(b, a); s.bank = b

    @classmethod
    def get(cls):
        if cls._inst is None:
            cls._inst = US()
        return cls._inst

    def groups(s):
        return [fo(s.bank, s.us[s.mgp + 2 * g] | s.us[s.mgp + 2 * g + 1] << 8) for g in range(26)]


def hdr_index(name):
    u = US.get()
    b, a = u.S[name + '_MapAttributes']
    G = u.groups(); p = G[0]
    while p < G[0] + 9 * 400:
        if u.us[p] == b and (u.us[p + 3] | u.us[p + 4] << 8) == a:
            return p
        p += 9
    raise KeyError(name)


def mapid(name):
    u = US.get(); G = u.groups(); h = hdr_index(name)
    for g in range(len(G)):
        if G[g] <= h and (g + 1 == len(G) or h < G[g + 1]):
            return g + 1, (h - G[g]) // 9 + 1


def attrs(rom, hdr):
    b = rom[hdr]; a = rom[hdr + 3] | rom[hdr + 4] << 8
    o = fo(b, a)
    r = rom[o:o + 12]
    return dict(attr_off=o, border=r[0], h=r[1], w=r[2], blkbank=r[3], blk=r[4] | r[5] << 8,
                scbank=r[6], scripts=r[7] | r[8] << 8, events=r[9] | r[10] << 8, conn=r[11])


def parse_events(rom, bank, addr):
    o = fo(bank, addr)
    p = o + 2
    ev = {'start': o}
    n = rom[p]; p += 1; ev['warps'] = [(p + 5 * i, bytes(rom[p + 5 * i:p + 5 * i + 5])) for i in range(n)]; p += 5 * n
    n = rom[p]; p += 1; ev['coords'] = [(p + 8 * i, bytes(rom[p + 8 * i:p + 8 * i + 8])) for i in range(n)]; p += 8 * n
    n = rom[p]; p += 1; ev['bgs'] = [(p + 5 * i, bytes(rom[p + 5 * i:p + 5 * i + 5])) for i in range(n)]; p += 5 * n
    ev['obj_count_off'] = p
    n = rom[p]; p += 1; ev['objs'] = [(p + 13 * i, bytes(rom[p + 13 * i:p + 13 * i + 13])) for i in range(n)]; p += 13 * n
    ev['end'] = p
    return ev


def bank_free_tail(rom, b):
    s = b * 0x4000; e = s + 0x4000; i = e
    while i > s and rom[i - 1] == 0:
        i -= 1
    return i, e - i


class Asm:
    """JP Crystal script assembler (JP opcode = US opcode, minus 1 for US >= 0x53; US 0x52 farjumptext does not exist)"""
    def __init__(s, base):
        s.base = base; s.b = bytearray(); s.labels = {}; s.fix = []
    def here(s): return s.base + len(s.b)
    def label(s, n): s.labels[n] = s.here()
    def db(s, *v): s.b += bytes(v)
    def dw(s, v):
        if isinstance(v, str):
            s.fix.append((len(s.b), v)); s.b += b'\0\0'
        else:
            s.b += bytes([v & 0xFF, v >> 8])
    def raw(s, data): s.b += data
    def done(s):
        for off, n in s.fix:
            a = s.labels[n]; s.b[off] = a & 0xFF; s.b[off + 1] = a >> 8
        return bytes(s.b)
    def text(s, t):
        from jpchar import encode
        s.raw(encode(t))
    # commands
    def scall(s, l): s.db(0x00); s.dw(l)
    def sjump(s, l): s.db(0x03); s.dw(l)
    def farsjump(s, b, l): s.db(0x04, b); s.dw(l)
    def iffalse(s, l): s.db(0x08); s.dw(l)
    def iftrue(s, l): s.db(0x09); s.dw(l)
    def jumpstd(s, n): s.db(0x0C); s.dw(n)
    def special(s, n): s.db(0x0F); s.dw(n)
    def setmapscene(s, g, n, sc): s.db(0x12, g, n, sc)
    def checkscene(s): s.db(0x13)
    def setscene(s, n): s.db(0x14, n)
    def givepoke(s, sp, lv): s.db(0x2D, sp, lv, 0x00, 0x00)
    def checkevent(s, e): s.db(0x31); s.dw(e)
    def clearevent(s, e): s.db(0x32); s.dw(e)
    def setevent(s, e): s.db(0x33); s.dw(e)
    def checkflag(s, f): s.db(0x34); s.dw(f)
    def setflag(s, f): s.db(0x36); s.dw(f)
    def warp(s, g, n, x, y): s.db(0x3C, g, n, x, y)
    def getmonname(s, sp): s.db(0x40, sp, 0x00)
    def opentext(s): s.db(0x47)
    def reanchormap(s): s.db(0x48, 0x00)
    def closetext(s): s.db(0x49)
    def farwritetext(s, b, a): s.db(0x4B, b, a & 0xFF, a >> 8)
    def writetext(s, l): s.db(0x4C); s.dw(l)
    def yesorno(s): s.db(0x4E)
    def jumptextfaceplayer(s, l): s.db(0x51); s.dw(l)
    def jumptext(s, l): s.db(0x52); s.dw(l)   # JP has no farjumptext (US 0x52)
    def waitbutton(s): s.db(0x53)
    def promptbutton(s): s.db(0x54)
    def pokepic(s, sp): s.db(0x55, sp)
    def closepokepic(s): s.db(0x56)
    def loadtrainer(s, c, i): s.db(0x5D, c, i)
    def startbattle(s): s.db(0x5E)
    def reloadmapafterbattle(s): s.db(0x5F)
    def winlosstext(s, w, l): s.db(0x63); s.dw(w); s.dw(l)
    def endifjustbattled(s): s.db(0x65)
    def applymovement(s, o, l): s.db(0x68, o); s.dw(l)
    def faceplayer(s): s.db(0x6A)
    def disappear(s, o): s.db(0x6D, o)
    def appear(s, o): s.db(0x6E, o)
    def showemote(s, e, o, t): s.db(0x74, e, o, t)
    def turnobject(s, o, d): s.db(0x75, o, d)
    def playmusic(s, m): s.db(0x7E); s.dw(m)
    def dontrestartmapmusic(s): s.db(0x82)
    def cry(s, sp): s.db(0x83, sp, 0x00)
    def playsound(s, snd): s.db(0x84); s.dw(snd)
    def waitsfx(s): s.db(0x85)
    def pause(s, n): s.db(0x8A, n)
    def sdefer(s, l): s.db(0x8C); s.dw(l)
    def endcallback(s): s.db(0x8F)
    def end(s): s.db(0x90)
    def verbosegiveitem(s, item, n=1): s.db(0x9D, item, n)
    def halloffame(s): s.db(0xA0)
    def ifequal(s, v, l): s.db(0x06, v); s.dw(l)
    def ifnotequal(s, v, l): s.db(0x07, v); s.dw(l)
    def callasm(s, b, a): s.db(0x0E, b); s.dw(a)
    def readmem(s, a): s.db(0x19); s.dw(a)
    def checkitem(s, i): s.db(0x21, i)
    def givecoins(s, n): s.db(0x25); s.dw(n)
    def loadwildmon(s, sp, lv): s.db(0x5C, sp, lv)
    def changeblock(s, x, y, b): s.db(0x79, x, y, b)
    def refreshmap(s): s.db(0x7B)
    def earthquake(s, n): s.db(0x77, n)
    def elevator(s, l): s.db(0x94); s.dw(l)
    def endifjustbattled2(s): s.db(0x65)

# phase 17 additions
def _asm_more():
    A = Asm
    A.reloadmap = lambda s: s.db(0x7A)
    A.playmapmusic = lambda s: s.db(0x81)
    A.setlasttalked = lambda s, o: s.db(0x67, o)
    A.moveobject = lambda s, o, x, y: s.db(0x71, o, x, y)
    A.loadvar = lambda s, v, n: s.db(0x1E, v, n)
    A.faceobject = lambda s, a_, b_: s.db(0x6B, a_, b_)
    A.writemem = lambda s, ad: (s.db(0x1A), s.dw(ad))
    A.loadmem = lambda s, ad, v: (s.db(0x1B), s.dw(ad), s.db(v))
    A.dontrestartmapmusic = lambda s: s.db(0x82)
    A.farsjump = lambda s, b, l: (s.db(0x04, b), s.dw(l))
    A.farscall = lambda s, b, l: (s.db(0x01, b), s.dw(l))
    A.checkflag = lambda s, f: (s.db(0x34), s.dw(f))
    A.setflag = lambda s, f: (s.db(0x36), s.dw(f))
    A.iftrue = lambda s, l: (s.db(0x09), s.dw(l))
    A.special = lambda s, n: (s.db(0x0F), s.dw(n))
    A.musicfadeout = lambda s, m, n: (s.db(0x80), s.dw(m), s.db(n))
_asm_more()
Asm.variablesprite = lambda s, i, spr: s.db(0x6C, i, spr)
