# 12種類の ROM を まとめて 逆アセンブルして、rgbds で 組める ソースを 作る。
#   python3 tools/disasm.py roms/ src/
# ・ROM を 16KB の バンクに わけ、中身が 同じ バンクは 1つの ファイルに まとめる（版ごとに 同じ バンクが 多い）。
# ・命令は、入口（割り込み・リセット・$0100、ほかの バンクからの farcall「ld b, バンク / ld hl, 番地 /
#   call Bankswitch」）から 流れを たどって 見つけた 所だけ。それ以外は db（データ、または 見つけられなかった 命令）。
# ・どの 版も、組み直すと 元の ROM と 1バイトも ちがわない（tools/asm.py で 確かめる）。
import os, sys, hashlib, glob, json
sys.path.insert(0, os.path.dirname(__file__))
from sm83 import decode, ENDS
from names import HOME_NAMES, BANK_NAMES

BANKSWITCH = 0x3500
BANK = 0x4000


def farcall_entries(rom):
    """ld b, bb / ld hl, aaaa / call|jp Bankswitch と ld hl, aaaa / ld b, bb / call|jp Bankswitch"""
    out = set()
    n = len(rom)
    for i in range(n - 8):
        if rom[i] == 0x06 and rom[i + 2] == 0x21 and rom[i + 5] in (0xcd, 0xc3) and rom[i + 6] == 0x00 and rom[i + 7] == 0x35:
            b, a = rom[i + 1], rom[i + 3] | rom[i + 4] << 8
        elif rom[i] == 0x21 and rom[i + 3] == 0x06 and rom[i + 5] in (0xcd, 0xc3) and rom[i + 6] == 0x00 and rom[i + 7] == 0x35:
            b, a = rom[i + 4], rom[i + 1] | rom[i + 2] << 8
        else:
            continue
        if 0 < b < n // BANK and 0x4000 <= a < 0x8000:
            out.add((b, a))
    return out


def trace(data, bank, entries):
    """data = その バンクの 16KB。entries = 番地の 集まり。→ (start: 命令の 頭の 番地 → 長さ, targets: 飛び先, home: バンク0 への 飛び先)"""
    base = 0 if bank == 0 else 0x4000
    owner = [None] * BANK          # その バイトを ふくむ 命令の 頭（オフセット）
    starts = {}
    targets = set()
    homet = set()
    todo = [a for a in entries if base <= a < base + BANK]
    while todo:
        a = todo.pop()
        while base <= a < base + BANK:
            o = a - base
            if owner[o] is not None:
                break
            d = decode(data, o)
            if d is None or o + d[1] > BANK:
                break
            if any(owner[o + k] is not None for k in range(d[1])):
                break
            fmt, n, val = d
            for k in range(n):
                owner[o + k] = o
            starts[o] = n
            op = data[o]
            tgt = None
            if 'e8' in fmt:
                tgt = a + 2 + (val - 256 if val >= 128 else val)
            elif 'a16' in fmt and (fmt.startswith('jp') or fmt.startswith('call')):
                tgt = val
            elif fmt.startswith('rst'):
                tgt = op - 0xc7
            if tgt is not None:
                if tgt < 0x4000:
                    homet.add(tgt)
                    if bank == 0:
                        targets.add(tgt); todo.append(tgt)
                elif tgt < 0x8000 and bank != 0:
                    targets.add(tgt); todo.append(tgt)
            if op in ENDS:
                break
            a += n
    return starts, targets, homet


SAME_LD = {0x40, 0x49, 0x52, 0x5b, 0x64, 0x6d, 0x7f}


def plausible(data, o, owner_starts, owner):
    """o から 命令として 読んで それらしいか（ret・jp などか、分かって いる 命令まで 正しく つづく）"""
    k = 0
    cnt = 0
    nops = 0
    while o < BANK and k < 300:
        if owner[o] is not None:
            return cnt >= 2 and o in owner_starts
        d = decode(data, o)
        if d is None or o + d[1] > BANK:
            return False
        op = data[o]
        if op in SAME_LD or op in (0x76, 0x10, 0xd9):
            return False
        if op == 0x00:
            nops += 1
            if nops >= 2:
                return False
        else:
            nops = 0
        if any(owner[o + j] is not None for j in range(1, d[1])):
            return False
        cnt += 1
        if op in ENDS:
            return cnt >= 2 or op == 0xc9 and cnt >= 1
        o += d[1]
        k += d[1]
    return False


def trace_more(data, bank, entries):
    """trace に、「ret・jp の すぐ あと」と「番地の 表」から 見つけた 入口を 足して くりかえす"""
    base = 0 if bank == 0 else 0x4000
    entries = set(entries)
    while True:
        starts, targets, homet = trace(data, bank, entries)
        owner = [None] * BANK
        for s, n in starts.items():
            for j in range(n):
                owner[s + j] = s
        new = set()
        for s, n in starts.items():
            if data[s] in ENDS:
                o = s + n
                if o < BANK and owner[o] is None and plausible(data, o, starts, owner):
                    new.add(base + o)
        # 番地の 表（同じ バンクの 中を 指す 2バイトが 3つ 以上 つづく、まだ 分からない 所）
        o = 0
        while o < BANK - 6:
            if owner[o] is None:
                run = []
                q = o
                while q < BANK - 1 and owner[q] is None and owner[q + 1] is None:
                    v = data[q] | data[q + 1] << 8
                    if not (base <= v < base + BANK):
                        break
                    run.append(v)
                    q += 2
                if len(run) >= 3:
                    for v in run:
                        t = v - base
                        if owner[t] is None and plausible(data, t, starts, owner):
                            new.add(v)
                    o = q
                    continue
            o += 1
        new -= entries
        if not new:
            return starts, targets | (entries & set(range(base, base + BANK))), homet
        entries |= new


def hx(v, w=2):
    return '$%0*x' % (w, v)


def label(bank, a):
    if bank == 0:
        return 'Home_%04x' % a
    nm = BANK_NAMES.get((bank, a))
    return nm if nm else 'B%02x_%04x' % (bank, a)


def render(data, bank, starts, labels):
    """1つの バンクの アセンブリの 行"""
    base = 0 if bank == 0 else 0x4000
    out = []
    if bank == 0:
        out.append('SECTION "Bank $00", ROM0[$0000]\n')
    else:
        out.append('SECTION "Bank $%02x", ROMX[$4000], BANK[$%02x]\n' % (bank, bank))
    o = 0
    pend = []
    def flush():
        if pend:
            for k in range(0, len(pend), 16):
                out.append('\tdb ' + ', '.join(hx(x) for x in pend[k:k + 16]) + '\n')
            pend.clear()
    while o < BANK:
        a = base + o
        if a in labels:
            flush()
            nm = labels[a]
            extra = ''
            if bank == 0 and a in HOME_NAMES:
                extra = ' ; ' + HOME_NAMES[a]
            out.append('%s::%s\n' % (nm, extra))
        if o in starts:
            flush()
            out.append('\t' + text(data, o, a, bank, labels) + '\n')
            o += starts[o]
        else:
            pend.append(data[o])
            o += 1
    flush()
    return out


def opnd16(v, bank, labels, is_jump):
    if is_jump:
        if v < 0x4000 and v in HOME_NAMES:
            return HOME_NAMES[v]
        if bank != 0 and 0x4000 <= v < 0x8000 and v in labels:
            return labels[v]
        if bank == 0 and v < 0x4000 and v in labels:
            return labels[v]
    return hx(v, 4)


def text(data, o, a, bank, labels):
    fmt, n, val = decode(data, o)
    raw = ', '.join(hx(x) for x in data[o:o + n])
    if data[o] in (0x10, 0x76):                      # stop・halt は db（アセンブラの ちがいを さける）
        return 'db %s ; %s' % (raw, fmt)
    if data[o] in (0xea, 0xfa) and val >= 0xff00:    # ld [$ffxx] は ldh に されない よう db
        return 'db %s ; %s' % (raw, fmt.replace('a16', hx(val, 4)))
    if 'e8' in fmt:
        t = a + 2 + (val - 256 if val >= 128 else val)
        s = labels.get(t) if (bank != 0 and 0x4000 <= t < 0x8000) or (bank == 0 and t < 0x4000) else None
        return fmt.replace('e8', s if s else '@ + %d' % (t - a))
    if 'a16' in fmt:
        j = fmt.startswith('jp') or fmt.startswith('call')
        return fmt.replace('a16', opnd16(val, bank, labels, j))
    if 'n16' in fmt:
        return fmt.replace('n16', hx(val, 4))
    if 'a8' in fmt:
        return fmt.replace('a8', hx(0xff00 + val, 4))
    if 's8' in fmt:
        s = val - 256 if val >= 128 else val
        if 'sp +' in fmt:
            return 'ld hl, sp %s %d' % ('+' if s >= 0 else '-', abs(s))
        return 'add sp, %d' % s
    if 'n8' in fmt:
        return fmt.replace('n8', hx(val))
    return fmt


def main():
    romdir, outdir = sys.argv[1], sys.argv[2]
    roms = {os.path.basename(p)[:-4]: open(p, 'rb').read() for p in sorted(glob.glob(os.path.join(romdir, '*.gbc')))}
    # バンクごとの 中身 → 入口
    uniq = {}   # (bank, sha) -> {'data':, 'entries': set(), 'eds': []}
    for ed, rom in roms.items():
        fe = farcall_entries(rom)
        for b in range(len(rom) // BANK):
            data = rom[b * BANK:(b + 1) * BANK]
            h = hashlib.sha1(data).hexdigest()[:8]
            u = uniq.setdefault((b, h), {'data': data, 'entries': set(), 'eds': []})
            u['eds'].append(ed)
            if b == 0:
                u['entries'] |= {0x00, 0x08, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38, 0x40, 0x48, 0x50, 0x58, 0x60, 0x100}
                u['entries'] |= set(HOME_NAMES)
            else:
                u['entries'] |= {a for (bb, a) in fe if bb == b}
                u['entries'] |= {a for (bb, a) in BANK_NAMES if bb == b}
    os.makedirs(os.path.join(outdir, 'banks'), exist_ok=True)
    files = {}
    stat = {}
    for (b, h), u in sorted(uniq.items()):
        starts, targets, homet = trace_more(u['data'], b, u['entries'])
        base = 0 if b == 0 else 0x4000
        labels = {}
        for t in (targets | u['entries']):
            if base <= t < base + BANK:
                o = t - base
                # 命令の 途中には 名前を つけない
                if o in starts or not any(s < o < s + n for s, n in starts.items() if s > o - 3):
                    labels[t] = label(b, t)
        lines = render(u['data'], b, starts, labels)
        fn = 'banks/bank_%02x_%s.asm' % (b, h)
        with open(os.path.join(outdir, fn), 'w') as f:
            f.write('; バンク $%02x（%s）\n' % (b, '・'.join(u['eds']) if len(u['eds']) < 12 else '12種類 ぜんぶ 同じ'))
            f.writelines(lines)
        for ed in u['eds']:
            files.setdefault(ed, {})[b] = fn
        code = sum(starts.values())
        stat[fn] = code
    os.makedirs(os.path.join(outdir, 'editions'), exist_ok=True)
    for ed, fb in files.items():
        with open(os.path.join(outdir, 'editions', ed + '.asm'), 'w') as f:
            f.write('; %s\n; rgbasm -o %s.o editions/%s.asm（src の 中で）→ rgblink -o %s.gbc %s.o\n' % (ed, ed, ed, ed, ed))
            f.write('INCLUDE "include/home_names.inc"\n')
            for b in sorted(fb):
                f.write('INCLUDE "%s"\n' % fb[b])
    os.makedirs(os.path.join(outdir, 'include'), exist_ok=True)
    with open(os.path.join(outdir, 'include', 'home_names.inc'), 'w') as f:
        f.write('; ホームバンク（$0000-$3fff）の よく 使う 処理の 名前（番地は 12種類 とも 同じ）\n')
        for a, nm in sorted(HOME_NAMES.items()):
            f.write('DEF %s EQU $%04x\n' % (nm, a))
    tot = sum(stat.values())
    print('banks', len(uniq), 'code bytes', tot)


if __name__ == '__main__':
    main()
