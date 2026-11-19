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
FPS60 = os.environ.get('FPS60', '1') == '1'
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
    if FPS60: files.append('src/fps60.asm')       # 60fps（キットの 4-3：60fps も 入れる）
    build.build(files, 'kin64.gbc')
    if FPS60: move_fps60_home('kin64.gbc')
    shutil.copy('kin64.gbc', OUT); shutil.copy('kin64.sym', OUT.replace('.gbc', '.sym'))
    print('→', OUT)
def move_fps60_home(path):
    """60fps の VBlank の 入口（ホーム $3FA0〜$3FB4、21バイト）は 移植の HFI（$3FA0〜）と かさなる。
       rst の あいだの 使われていない 所（$0019・$0021・$0039・$0051。$18・$20・$38 は rst $38、$50 は reti で、
       その うしろへは 流れて こない）に 4つに 分けて 置き、VBlank の フック（$01CA call $3FA0）を $0019 へ。"""
    g = bytearray(open(path, 'rb').read())
    code = bytes.fromhex('afea1ecffa40dea7c8f09ff53e3fd7cd0068f1d7c9')
    assert bytes(g[0x3FA0:0x3FB5]) == code and bytes(g[0x1CA:0x1CE]) == bytes([0xCD, 0xA0, 0x3F, 0x00])
    for a in (0x19, 0x21, 0x39, 0x51): assert not any(g[a:a + 7])
    def jr(fr, to): return bytes([0x18, (to - (fr + 2)) & 0xFF])
    g[0x19:0x19 + 6] = code[0:4] + jr(0x19 + 4, 0x21)               # xor a / ld [wVBlankOccurred], a
    g[0x21:0x21 + 7] = code[4:9] + jr(0x21 + 5, 0x39)               # ld a, [wFps60Flag] / and a / ret z
    g[0x39:0x39 + 7] = code[9:14] + jr(0x39 + 5, 0x51)              # ldh a, [hROMBank] / push af / ld a, BANK
    g[0x51:0x51 + 7] = code[14:21]                                  # rst $10 / call Fps60_Restore / pop af / rst $10 / ret
    g[0x3FA0:0x3FB5] = bytes(21)
    g[0x1CB] = 0x19; g[0x1CC] = 0x00
    open(path, 'wb').write(g)


if __name__ == '__main__': main()
