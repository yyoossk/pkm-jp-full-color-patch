"""crystal_kj5.gbc：kj4 に 第127弾の MOD 側（スクリプト・マップ）の 直しを 当てる。
   2 ディグダのあな ニビ側の ボーダー、6 研究所の シゲル、8 ニビの ジムへ 連れて いく 人。
   7 ジムの 技教えの 呼び止め は この MOD（kj4）に 第122弾の ジムの 技教えが ない ので 当てはまらない。
   1 山男・3 PP の 色・4 自転車・5 トレーナーの 見つかり方 は 金の エンジンの 所なので gold_p127.py。
   使いかた：MODROOT=… python3 kj5_mod.py kj4.gbc kj5.gbc"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules.setdefault("mapdb", __import__("mapdb"))
import build_phase127 as P
from lib import fix_checksum
rom = bytearray(open(sys.argv[1], 'rb').read()); log = []
P.diglett(rom, log); P.lab_rival(rom, log)
P.FREE_BANK = 0x67                 # 8：ニビシティの スクリプトの バンク（$8E に 移すと 金の バンクの わりあてが ずれて あふれる）
P.pewter_guy(rom, log)
fix_checksum(rom); open(sys.argv[2], 'wb').write(rom); print('\n'.join(log))
