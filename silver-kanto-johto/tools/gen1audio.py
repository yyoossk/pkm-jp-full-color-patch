"""Gen I (Red) music / sound effects (binary, one ROM bank) -> Gen II (Crystal) audio engine data."""


def _cmd_len(b, ch, sfx):
    """(length in bytes, kind) of the Gen I command b on channel ch (0-7)"""
    if sfx:
        if b == 0x10: return 2, 'sweep'
        if 0x20 <= b < 0x30: return (3 if ch == 7 else 4), 'sfxnote'
    if b < 0xC0:
        if ch % 4 == 3 and b >= 0xB0: return 2, 'drum'
        return 1, 'note'
    if b < 0xD0: return 1, 'rest'
    if b < 0xE0: return (1 if ch % 4 == 3 else 2), 'notetype'
    if b < 0xE8: return 1, 'octave'
    return {0xE8: (1, 'perfect'), 0xEA: (3, 'vibrato'), 0xEB: (3, 'slide'), 0xEC: (2, 'duty'), 0xED: (3, 'tempo'),
            0xEE: (2, 'stereo'), 0xEF: (2, 'unk'), 0xF0: (2, 'volume'), 0xF8: (1, 'exec'), 0xFC: (2, 'dutypat'),
            0xFD: (3, 'call'), 0xFE: (4, 'loop'), 0xFF: (1, 'ret')}[b]


class Song:
    """convert one Gen I header (music or sfx) from bank `bank` of `rom`"""
    def __init__(s, rom, bank, hdr, drums=None, kit=0):
        s.rom = rom; s.bank = bank; s.drums = drums or {}; s.kit = kit
        def rd(a): return rom[bank * 0x4000 + a - 0x4000]
        s.rd = rd
        n = (rd(hdr) >> 6) + 1
        s.chans = [(rd(hdr + 3 * i) & 7, rd(hdr + 3 * i + 1) | rd(hdr + 3 * i + 2) << 8) for i in range(n)]
        s.ins = {}                                                # gen1 address -> (channel, bytes)
        for ch, a in s.chans:
            s._walk(ch, a)

    def _walk(s, ch, a):
        sfx = ch >= 4; todo = [a]
        while todo:
            a = todo.pop()
            while a not in s.ins:
                b = s.rd(a); n, k = _cmd_len(b, ch, sfx)
                raw = bytes(s.rd(a + i) for i in range(n))
                s.ins[a] = (ch, raw, k)
                if k == 'call':
                    todo.append(raw[1] | raw[2] << 8)
                if k == 'loop':
                    t = raw[2] | raw[3] << 8; todo.append(t)
                    if raw[1] == 0: break                             # infinite loop: no fallthrough
                if k == 'ret': break
                if k == 'exec': sfx = False
                a += n

    def _conv(s, ch, raw, k):
        b = raw[0]
        if k == 'note': return bytes([((b >> 4) + 1) << 4 | (b & 15)])
        if k == 'drum':
            inst = raw[1]; kn = s.drums[inst]
            return bytes([kn << 4 | (b & 15)])
        if k == 'rest': return bytes([b & 15])
        if k == 'notetype': return bytes([0xD8, b & 15]) + raw[1:]
        if k == 'octave': return bytes([b - 0x10])
        if k == 'perfect': return bytes([0xE6, 0x00, 0x01])
        if k == 'vibrato': return bytes([0xE1]) + raw[1:]
        if k == 'slide':
            p = raw[2]; return bytes([0xE0, raw[1], (p & 0xF0) | (((p & 15) + 1) % 12)])
        if k == 'duty': return bytes([0xDB, raw[1]])
        if k == 'tempo': return bytes([0xDA]) + raw[1:]
        if k == 'stereo': return bytes([0xEF, raw[1]])
        if k == 'unk': return b''
        if k == 'volume': return bytes([0xE5, raw[1]])
        if k == 'dutypat': return bytes([0xDE, raw[1]])
        if k == 'sweep': return bytes([0xDD, raw[1]])
        if k == 'sfxnote': return raw
        if k == 'ret': return b'\xff'
        raise ValueError(k)

    def build(s, base):
        """Gen II bytes placed at `base` (address in the target bank): (header address, data)"""
        out = bytearray(); lab = {}; fix = []
        nhdr = 3 * len(s.chans)
        pre = {}
        for ch, a in s.chans:
            if ch == 3: pre[a] = bytes([0xE3, s.kit])               # music noise channel: drum kit
        for a in sorted(s.ins):
            ch, raw, k = s.ins[a]
            if a in pre:
                lab[('pre', a)] = base + nhdr + len(out); out += pre[a]
            lab[a] = base + nhdr + len(out)
            if k == 'call':
                out += b'\xfe'; fix.append((len(out), raw[1] | raw[2] << 8)); out += b'\0\0'
            elif k == 'loop':
                out += bytes([0xFD, raw[1]]); fix.append((len(out), raw[2] | raw[3] << 8)); out += b'\0\0'
            else:
                out += s._conv(ch, raw, k)
        for o, t in fix:
            v = lab[t]; out[o] = v & 0xFF; out[o + 1] = v >> 8
        hdr = bytearray()
        for i, (ch, a) in enumerate(s.chans):
            v = lab[('pre', a)] if ('pre', a) in lab else lab[a]
            hdr += bytes([((len(s.chans) - 1) << 6 if i == 0 else 0) | ch, v & 0xFF, v >> 8])
        return base, bytes(hdr + out)
