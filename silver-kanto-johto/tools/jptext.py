"""日本版の 文字コード（ref/pokecrystal/constants/charmap.asm）"""
import re, os
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CM = {}
for l in open(os.path.join(H, 'ref/pokecrystal/constants/charmap.asm'), encoding='utf-8'):
    m = re.match(r'\s*charmap "(.+?)",\s*\$([0-9a-fA-F]+)', l)
    if m and m.group(1) not in CM: CM[m.group(1)] = int(m.group(2), 16)
for k, h in (('リ', 'り'), ('ヘ', 'へ'), ('ベ', 'べ'), ('ペ', 'ぺ')):
    if k not in CM and h in CM: CM[k] = CM[h]
INV = {}
for k, v in CM.items(): INV.setdefault(v, k)


def enc(s):
    out = []; i = 0
    while i < len(s):
        if s[i] == '<':
            j = s.index('>', i); out.append(CM[s[i:j + 1]]); i = j + 1
        else: out.append(CM[s[i]]); i += 1
    return bytes(out)


def dec(b):
    return ''.join(INV.get(x, '[%02X]' % x) for x in b)
