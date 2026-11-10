#!/usr/bin/env python3
# 251ひき そろう版の 出現表（金 日本版）
#   キットの「かえる枠_金.txt」（どの マップの どの 枠を 何に かえるか）を、
#   この プロジェクトの 殿堂入りの 前の 書きかえ（src/wild_gold.asm）＋ 日本版の ROM の 表 に あてて、src/wild251_gold.asm を 作る。
#   （キットの wild251_gold.txt は 英語版 pokegold の 表が 元なので、日本版で 12 マップの 表が ちがって 見つからない）
#   python3 tools/wild251_jp.py base.gbc src/wild_gold.asm <かえる枠_金.txt> <pokemon_constants.asm> src/wild251_gold.asm
import re, sys
base = open(sys.argv[1], 'rb').read()
MON = {}
v = 0
for l in open(sys.argv[4]):
    l = l.split(';')[0].strip()
    m = re.match(r'const_def\s*(\S*)', l)
    if m: v = int(m.group(1).replace('$', '0x'), 0) if m.group(1) else 0; continue
    m = re.match(r'const\s+(\w+)', l)
    if m: MON[m.group(1)] = v; v += 1
T = {}; order = []
cur = None
for l in open(sys.argv[2], encoding='utf-8'):
    m = re.match(r'SECTION "wild (\w+)", ROMX\[\$(\w+)\], BANK\[\$(\w+)\]', l)
    if m: cur = m.group(1); T[cur] = [int(m.group(3), 16) * 0x4000 + int(m.group(2), 16) - 0x4000, None]; order.append(cur); continue
    if cur and l.strip().startswith('db'):
        T[cur][1] = bytearray(int(x.strip()[1:], 16) for x in l.strip()[2:].split(','))
GRP = {}
g = n = 0
for l in open(sys.argv[4].replace('pokemon_constants', 'map_constants')):
    l = l.split(';')[0].strip()
    if re.match(r'newgroup\s+\w+', l): g += 1; n = 0; continue
    m = re.match(r'map_const\s+(\w+)', l)
    if m: n += 1; GRP[m.group(1)] = (g, n)
KIT = {}
for l in open(sys.argv[3].replace('かえる枠_金.txt', 'wild251_gold.txt'), encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    mp, a, b = l.split(); KIT[mp] = bytes.fromhex(a)
SWAP = {'PHANPY': 'TEDDIURSA', 'TEDDIURSA': 'PHANPY', 'DONPHAN': 'URSARING', 'URSARING': 'DONPHAN'}
TIMES = {'朝': 0, '昼': 1, '夜': 2}
bad = 0
ok = 0
for l in open(sys.argv[3], encoding='utf-8'):
    p = l.split()
    if len(p) < 7: continue
    mp, t, slot, old, oldlv, _, new, newlv = p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]
    if mp not in T and mp in KIT and base.count(KIT[mp]) == 1:
        i = base.find(KIT[mp]); T[mp] = [i, bytearray(base[i:i + 47])]; order.append(mp)
    if mp not in T:
        g, n = GRP[mp]
        c = [i for i in range(0xa * 0x4000, 0xb * 0x4000 - 47) if base[i] == g and base[i + 1] == n and base[i + 2] in (5, 10, 15, 25) ]
        c = [i for i in c if all(base[i + 5 + 2 * k + 1] in range(1, 252) for k in range(21))]
        if mp in KIT: c = [i for i in c if base[i + 2:i + 5] == KIT[mp][2:5]]
        assert len(c) == 1, (mp, [hex(x) for x in c])
        T[mp] = [c[0], bytearray(base[c[0]:c[0] + 47])]; order.append(mp)
    # 日本版は 金・銀の ヒメグマ・リングマ と ゴマゾウ・ドンファン が 英語版と 逆（日本版の 金は ゴマゾウ・ドンファン）。
    # キットの 一覧は 英語版の 表から 作って いるので 入れかえて 読む
    old = SWAP.get(old, old); new = SWAP.get(new, new)
    i = TIMES[t] * 7 + int(slot.replace('わくめ', '')) - 1
    off = 5 + 2 * i
    tb = T[mp][1]
    if tb[off + 1] != MON[old] or tb[off] != int(oldlv[2:]):
        print('ちがう', mp, t, slot, 'ROM は', tb[off], [k for k, x in MON.items() if x == tb[off + 1]], 'キットは', old, oldlv); bad += 1
    ok += 1
    tb[off] = int(newlv[2:]); tb[off + 1] = MON[new]
out = ['; 251ひき そろう版の 出現表（src/wild_gold.asm の 殿堂入りの 前の 書きかえ ＋ キットの かえる枠_金.txt。tools/wild251_jp.py で 作った）', '']
for mp in order:
    a, tb = T[mp]
    out.append('SECTION "wild %s", ROMX[$%04x], BANK[$%02x]' % (mp, a % 0x4000 + 0x4000, a // 0x4000))
    out.append('\tdb ' + ', '.join('$%02x' % x for x in tb))
open(sys.argv[5], 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('maps', len(order), 'わく', ok, 'ちがう', bad)
