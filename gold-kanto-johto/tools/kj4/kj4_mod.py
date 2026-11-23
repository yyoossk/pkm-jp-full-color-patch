"""crystal_kj4.gbc：kj3 に 第126弾の MOD 側（スクリプト・文）の 直しだけを 当てる。
   2 ゲートの グレーバッジの 確認（来た 向きへ 押し戻す・見張りは 話すだけ）、3 26番道路の エリートトレーナー（<RIVAL> → <GREEN>）。
   1 たいあたり・4 人に ついて行く・5 パソコン・6 ニドラン は 金の エンジンの 所なので gold_p126.py（金の ROM に 直接）。
   使いかた：MODROOT=… python3 kj4_mod.py kj3.gbc kj4.gbc"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_phase126 as P
from lib import fix_checksum
rom = bytearray(open(sys.argv[1], 'rb').read()); log = []
P.gate(rom, log); P.route26(rom, log)
fix_checksum(rom); open(sys.argv[2], 'wb').write(rom); print('\n'.join(log))
