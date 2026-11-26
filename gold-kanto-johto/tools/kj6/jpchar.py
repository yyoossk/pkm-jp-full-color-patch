"""Japanese Gen II (Crystal JP) text codec."""
import re

KATA = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフホマミムメモヤユヨラルレロワヲンッャュョィ'
HIRA = 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんっゃゅょ'
ENC = {}
for i, c in enumerate(KATA):
    ENC[c] = 0x80 + i
for i, c in enumerate(HIRA):
    ENC[c] = 0xB1 + i
for i, c in enumerate('ガギグゲゴザジズゼゾダヂヅデド'):
    ENC[c] = 0x05 + i
for i, c in enumerate('バビブボ'):
    ENC[c] = 0x19 + i
for i, c in enumerate('がぎぐげござじずぜぞだぢづでど'):
    ENC[c] = 0x26 + i
for i, c in enumerate('ばびぶべぼ'):
    ENC[c] = 0x3A + i
for i, c in enumerate('パピプポぱぴぷぺぽ'):
    ENC[c] = 0x40 + i
ENC.update({'ー': 0xE3, '？': 0xE6, '！': 0xE7, '。': 0xE8, 'ァ': 0xE9, 'ゥ': 0xEA, 'ェ': 0xEB,
            '♂': 0xEF, '円': 0xF0, '×': 0xF1, '．': 0xF2, '／': 0xF3, 'ォ': 0xF4, '♀': 0xF5,
            '「': 0x70, '」': 0x71, '』': 0x73, '・': 0x74, '⋯': 0x75, '　': 0x7F, ' ': 0x7F,
            '…': 0x75, '?': 0xE6, '!': 0xE7,
            'ヘ': 0xCD, 'ベ': 0x3D, 'ペ': 0x47, 'リ': 0xD8})
for i, c in enumerate('0123456789'):
    ENC[c] = 0xF6 + i
CTRL = {'<LINE>': 0x4F, '<PARA>': 0x51, '<CONT>': 0x55, '<DONE>': 0x57, '<PROMPT>': 0x58,
        '<PLAYER>': 0x52, '<RIVAL>': 0x53, '<POKEMON>': 0x54, '@': 0x50, '<SCROLL>': 0x4C,
        '<NEXT>': 0x4E, '<……>': 0x56, '<USER>': 0x5A, '<TARGET>': 0x59}
DEC = {}
for k, v in ENC.items():
    DEC.setdefault(v, k)
for i, c in enumerate(KATA):
    DEC[0x80 + i] = c
for i, c in enumerate(HIRA):
    DEC[0xB1 + i] = c
DEC[0x7F] = '　'
DEC[0x75] = '…'
for k, v in CTRL.items():
    DEC[v] = k
DEC.update({0x1D: 'に　', 0x1E: 'って', 0x1F: 'を　', 0x22: 'た！', 0x23: 'こうげき', 0x24: 'は　',
            0x25: 'の　', 0x35: 'ばん　どうろ', 0x36: 'わたし', 0x37: 'ここは', 0x4A: 'が　'})


def decode(data, stop_at_end=True):
    out = []
    for b in data:
        if b == 0x50 and stop_at_end:
            out.append('@'); break
        out.append(DEC.get(b, '{%02X}' % b))
    return ''.join(out)


def encode(s):
    out = bytearray()
    i = 0
    while i < len(s):
        m = re.match(r'<[^>]+>|\{([0-9A-Fa-f]{2})\}', s[i:])
        if m:
            tok = m.group(0)
            out.append(int(m.group(1), 16) if m.group(1) else CTRL[tok])
            i += len(tok)
            continue
        c = s[i]
        if c not in ENC and c != '@':
            raise ValueError('cannot encode %r in %r' % (c, s))
        out.append(0x50 if c == '@' else ENC[c])
        i += 1
    return bytes(out)
