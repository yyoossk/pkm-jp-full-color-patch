"""build_phase126.py が rgbds() だけ 使う（金の 版では MOD 側で asm を 組まない ので 呼ばれない）"""
import os
def rgbds(n): return os.path.join(os.environ.get('RGBDS', '/home/claude/rgbds-src'), n)
