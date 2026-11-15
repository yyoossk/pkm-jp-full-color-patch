"""「ポケットモンスター 銀 カントー＆ジョウト」の 組み立て

  roms/gin0.gbc  … ポケットモンスター銀 初期版（CRC32 BE1B928A）
  roms/gin1.gbc  … ポケットモンスター銀 後期版（CRC32 0AEA5383）   ← できあがりの もと
  rgbds 1.0.4 の rgbasm・rgblink・rgbfix（PATH に あるか 環境変数 RGBDS に フォルダ。さいごに /）

  python3 build.py
    → build/銀カントー＆ジョウト.gbc と build/ポケットモンスター 銀 カントー＆ジョウト.ips
      IPS は 初期版・後期版の どちらに 当てても 同じ ROM に なる（当てて CRC32 を 確かめる）

  手順
    1. ../silver（銀 追加機能パッチ Ver.1.5.1）を build/kit に 写し、src/ の この MOD の ファイルで 上書きして、
       buildlist_mod.txt の 機能と 60fps で 組む（クリスタル版の 第64弾に あたる 所。README の 4-3）
    2. phases/ の 第○弾の スクリプトを 順に 当てる（クリスタル版の フェーズ一覧の 順）
    3. 2つの 元の ROM から 1つの IPS を 作り、両方に 当てて 確かめる
"""
import os, sys, shutil, subprocess, zlib, importlib.util
H = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(H, 'build')
CRC = {'gin0': 0xBE1B928A, 'gin1': 0x0AEA5383}
NAME = 'ポケットモンスター 銀 カントー＆ジョウト'


def crc(b): return zlib.crc32(b) & 0xffffffff


def roms():
    r = {}
    for k in ('gin0', 'gin1'):
        p = os.path.join(H, 'roms', k + '.gbc')
        d = open(p, 'rb').read()
        assert crc(d) == CRC[k], '%s の CRC32 が ちがう: %08X' % (p, crc(d))
        r[k] = d
    return r


def stage1(base):
    """銀 追加機能パッチの ソースで 機能と 60fps を 組む"""
    kit = os.path.join(B, 'kit')
    if os.path.exists(kit): shutil.rmtree(kit)
    shutil.copytree(os.path.join(H, '..', 'silver'), kit,
                    ignore=shutil.ignore_patterns('*.gbc', '*.sym', '*.map', 'obj', '*.ips'))
    for f in os.listdir(os.path.join(H, 'src')):           # この MOD の ファイルで 上書き
        shutil.copy(os.path.join(H, 'src', f), os.path.join(kit, 'src', f))
    open(os.path.join(kit, 'base.gbc'), 'wb').write(base)
    asms = ['src/fps60.asm'] + open(os.path.join(H, 'buildlist_mod.txt')).read().split()
    env = dict(os.environ, POKEGOLD='pokegold/')
    r = subprocess.run(['python3', 'build.py', 'stage1.gbc'] + asms, cwd=kit, env=env, capture_output=True, text=True)
    print(r.stdout.strip())
    assert r.returncode == 0, r.stderr
    shutil.copy(os.path.join(kit, 'stage1.sym'), os.path.join(B, 'stage1.sym'))
    return bytearray(open(os.path.join(kit, 'stage1.gbc'), 'rb').read())


def phases(rom):
    """phases/phaseNN.py の apply(rom, ctx) を 番号の 順に よぶ"""
    d = os.path.join(H, 'phases')
    if not os.path.isdir(d): return rom
    ctx = {'H': H, 'B': B, 'sym': os.path.join(B, 'stage1.sym')}
    for f in sorted(x for x in os.listdir(d) if x.startswith('phase') and x.endswith('.py')):
        spec = importlib.util.spec_from_file_location(f[:-3], os.path.join(d, f))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        rom = m.apply(rom, ctx)
        print(f, '%08X' % crc(rom))
    return rom


def fix_header(rom):
    """ヘッダーの チェックサムと 全体の チェックサムを 計算しなおす（rgbfix -v と 同じ）"""
    c = 0
    for i in range(0x134, 0x14D): c = (c - rom[i] - 1) & 0xff
    rom[0x14D] = c
    s = (sum(rom) - rom[0x14E] - rom[0x14F]) & 0xffff
    rom[0x14E], rom[0x14F] = s >> 8, s & 0xff


def main():
    os.makedirs(B, exist_ok=True)
    r = roms()
    rom = stage1(r['gin1'])
    rom = phases(rom)
    fix_header(rom)
    out = os.path.join(B, '銀カントー＆ジョウト.gbc')
    open(out, 'wb').write(rom)
    sys.path.insert(0, os.path.join(H, '..', 'silver'))
    from mkips import ips, apply
    p = ips([r['gin0'], r['gin1']], bytes(rom))
    for k in ('gin0', 'gin1'):
        a = apply(r[k], p)
        assert a == bytes(rom), k + ' に 当てた ものが ちがう'
        print(k, 'に 当てた CRC32 %08X' % crc(a))
    open(os.path.join(B, NAME + '.ips'), 'wb').write(p)
    print('IPS', len(p), 'バイト / できあがり', len(rom), 'バイト CRC32 %08X' % crc(rom))


if __name__ == '__main__':
    main()
