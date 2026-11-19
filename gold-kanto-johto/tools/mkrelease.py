"""リリース用の IPS：金の 初期版・後期版の どちらに 当てても out/gold_full.gbc と 同じ ROM に なる 1つの パッチ。
   「初期版と ちがう 所」と「後期版と ちがう 所」を 両方 書く（README 4-4）。元より 大きい 所（1MB〜4MB）は ぜんぶ 書く
   （0 の 続く 所は RLE）。最後の 1バイトも 書くので、当てた あとの 大きさは 4MB に そろう。
   python3 mkrelease.py 完成.gbc 初期版.gbc 後期版.gbc 出力.ips"""
import sys, zlib
sys.path.insert(0, __import__('os').path.dirname(__file__))
import ips as IPS


def make(final, roms):
    n = len(final)
    diff = bytearray(n)
    for i in range(n):
        if any(i >= len(r) or r[i] != final[i] for r in roms): diff[i] = 1
    diff[n - 1] = 1
    out = bytearray(b'PATCH')
    i = 0
    while i < n:
        if not diff[i]: i += 1; continue
        j = i
        while j < n and diff[j] and j - i < 0xFFFF: j += 1
        s = i
        while s < j:
            if s == 0x454F46:                      # "EOF" と 読まれる 住所からは はじめない
                s -= 1
            # 同じ バイトが 続く 所は RLE
            k = s
            while k < j and final[k] == final[s] and k - s < 0xFFFF: k += 1
            if k - s >= 9:
                out += s.to_bytes(3, 'big') + b'\0\0' + (k - s).to_bytes(2, 'big') + bytes([final[s]]); s = k; continue
            e = s
            while e < j and e - s < 0xFFFF:
                if e + 9 <= j and len(set(final[e:e + 9])) == 1: break
                e += 1
            if e == s: e = s + 1
            out += s.to_bytes(3, 'big') + (e - s).to_bytes(2, 'big') + final[s:e]; s = e
        i = j
    out += b'EOF'
    return bytes(out)


if __name__ == '__main__':
    fin, early, late, op = sys.argv[1:5]
    final = open(fin, 'rb').read(); E = open(early, 'rb').read(); L = open(late, 'rb').read()
    p = make(final, [E, L]); open(op, 'wb').write(p)
    for nm, r in (('初期版', E), ('後期版', L)):
        o = IPS.apply(r, p); assert o == final, nm
        print(nm, '→ %08X' % zlib.crc32(o), len(o))
    print('IPS', len(p), 'バイト')
