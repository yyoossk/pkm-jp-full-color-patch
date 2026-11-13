# ポケットモンスター金 追加機能パッチ を 組み立てる
#   つかいかた：python3 build.py
#   ・このフォルダに 元の ROM（ポケットモンスター金 後期版。CRC32 4EF7F2A5）を base.gbc の 名前で おく
#   ・RGBDS 1.0.4 の rgbasm・rgblink・rgbfix を PATH に 入れる（または 環境変数 RGBDS に その フォルダ）
#   ・できる もの：kin.gbc（通常版）・kin60.gbc（60fps版）、kin251.gbc・kin251_60.gbc（251ひき そろう版の 通常版・60fps版）
import subprocess,sys,os,zlib
T=os.environ.get('RGBDS','')
if T and not T.endswith('/'): T+='/'
HERE=os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
FILES=[
    'src/features.asm',
    'src/bugfix.asm',
    'src/minis.asm',
    'src/hmfield.asm',
    'src/fishnest.asm',
    'src/rematch_gold.asm',
    'src/wild_gold.asm',
    'src/clockopt_gold.asm',
    'src/learnmove.asm',
    'src/pikaballs.asm',
    'src/statsmove.asm',
    'src/redballs.asm',
    'src/picpal.asm',
    'src/fieldcolors.asm',
    'src/safari/safari.asm',
    'src/sigmove_gold.asm',
    'src/autobox.asm',
    'src/masterball.asm',
    'src/repelask.asm',
    'src/textspeed.asm',
    'src/phonefreq.asm',
    'src/moverelearn.asm',
    'src/movetutor.asm',
    'src/nesttime.asm',
    'src/kurtbulk.asm',
    'src/daycarehint.asm',
    'src/legends.asm',
    'src/starters.asm',
    'src/movepower.asm',
    'src/phonemark.asm',
    'src/itemfinder.asm',
    'src/pokegearwhite.asm',
    'src/quickball.asm',
    'src/hearts.asm',
    'src/gearday.asm',
    'src/eggsteps.asm',
    'src/partyshiny.asm',
    'src/mapsign.asm',
    'src/hpower.asm',
    'src/dvview.asm',
    'src/enemyhp_gold.asm',
    'src/partyitem.asm',
    'src/fishbite.asm',
    'src/moveacc.asm',
    'src/legendrevive.asm',
    'src/contestpc.asm',
    'src/monmenu_fix.asm',
    'src/follow_gold.asm',
    'src/prizetm_gold.asm',
    'src/statuscolor_gold.asm',
    'src/dexinfo_gold.asm','src/tmshop.asm','src/daycareout.asm','src/eggfast.asm']
# 251ひき そろう版：野生・ショップ・ずかんの 文字の ファイルを かえて、edition251_gold.asm を 足す
FILES251=[{'src/wild_gold.asm':'src/wild251_gold.asm','src/masterball.asm':'src/masterball251.asm',
           'src/dexinfo_gold.asm':'src/dexinfo251_gold.asm'}.get(f,f) for f in FILES]+['src/edition251_gold.asm']
EXPECT={'kin.gbc':0x84575E8A,'kin60.gbc':0xDA69765C,   # Ver.1.5.0 ＋ イベントの follow の 直し（まだ リリースして いない）
        'kin251.gbc':0xD8DABBEA,'kin251_60.gbc':0xCEC13AB1}   # Ver.1.5.0 の 251ひき そろう版
def run(*a):
    r=subprocess.run(a,capture_output=True,text=True)
    if r.returncode: print(r.stdout,r.stderr); sys.exit(1)
def build(asms,out,base='base.gbc',basedata=0x51aa9):
    objs=[]
    os.makedirs('obj',exist_ok=True)
    for a in asms:
        o='obj/'+os.path.basename(a)+'.o'
        run(T+'rgbasm','-I','pokegold/','-o',o,a); objs.append(o)
    run(T+'rgblink','-O',base,'-n',out.replace('.gbc','.sym'),'-m',out.replace('.gbc','.map'),'-o',out,*objs)
    d=bytearray(open(out,'rb').read())
    for i in range(251):                 # すべての ポケモンが ひでんマシンを おぼえる
        o=basedata+i*32
        d[o+30]|=0xfc
        d[o+31]|=0x01
    open(out,'wb').write(d)
    run(T+'rgbfix','-v','-p','0',out)
    c=zlib.crc32(open(out,'rb').read())
    print(out,'%08X'%c,'OK' if c==EXPECT.get(out) else '（リリースと ちがう）')
if __name__=='__main__':
    if not os.path.exists('base.gbc'): sys.exit('base.gbc（ポケットモンスター金 後期版）を おいてください')
    if zlib.crc32(open('base.gbc','rb').read())!=0x4EF7F2A5: print('注意：base.gbc の CRC32 が 4EF7F2A5（後期版）では ありません')
    build(FILES,'kin.gbc')
    build(FILES+['src/fps60.asm'],'kin60.gbc')
    build(FILES251,'kin251.gbc')
    build(FILES251+['src/fps60.asm'],'kin251_60.gbc')
