"""第64弾：金の 追加機能パッチ（リポジトリの gold/）を、カントー＆ジョウトで 使う 形で 組む → ref/kin64.gbc
   のぞく もの（クリスタル版で 入れない と 決めた キットの 機能に あたる もの）：
     safari/safari.asm（ピカチュウ版の サファリ。MOD の サファリ＝第28弾 を 使う。表示は 札の 毎フレームから MOD の 表示を 呼ぶ）、
     wild_gold.asm（殿堂入りの 前の 野生）、starters.asm（カントーの 御三家は MOD の マップで）、legends.asm の 鳥（セレビィだけ のこして Lv70 に。クリスタル版と 同じ）
   足す もの：kit/safarihud_stub.asm（SafariHUD → MOD の サファリの 表示。バンクは 移植の ときに 書く）
   つかいかた：python3 gold_kit.py（RGBDS 1.0.4 が 要る。環境変数 RGBDS）"""
import os, sys, shutil, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.environ.get('KIN64', '/home/claude/work/ref/kin64.gbc')
EXCLUDE = {'src/safari/safari.asm', 'src/wild_gold.asm', 'src/starters.asm'}
def main():
    tmp = tempfile.mkdtemp()
    src = os.path.join(REPO, 'gold'); dst = os.path.join(tmp, 'gold')
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('*.gbc', 'obj', '*.sym', '*.map'))
    shutil.copy(os.path.join(src, 'base.gbc'), dst)
    shutil.copy(os.path.join(HERE, 'kit', 'safarihud_stub.asm'), os.path.join(dst, 'src'))
    # legends.asm：鳥を のぞき、セレビィを Lv70 に
    lp = os.path.join(dst, 'src', 'legends.asm'); L = open(lp, encoding='utf-8').read()
    import re
    L = re.sub(r'\n\tlegend_copy (WI|RT|SC)', '', L)
    L = re.sub(r'\n\tlegend_bird [^\n]*', '', L)
    L = re.sub(r'Legend(WI|RT|SC)_MapScripts:\n\tdef_scene_scripts\n\tdef_callbacks\n\tcallback MAPCALLBACK_OBJECTS, Legend\w+_Callback\n\n', '', L)
    assert 'loadwildmon CELEBI, 30' in L; L = L.replace('loadwildmon CELEBI, 30', 'loadwildmon CELEBI, 70')
    open(lp, 'w', encoding='utf-8').write(L)
    sys.path.insert(0, dst); os.chdir(dst)
    import build
    files = [f for f in build.FILES if f not in EXCLUDE] + ['src/safarihud_stub.asm']
    build.build(files, 'kin64.gbc')
    shutil.copy('kin64.gbc', OUT); shutil.copy('kin64.sym', OUT.replace('.gbc', '.sym'))
    print('→', OUT)
if __name__ == '__main__': main()
