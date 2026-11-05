import subprocess,sys,os,zlib
T=os.environ.get('RGBDS','')          # rgbds 1.0.4 のフォルダ（PATH にあれば空でよい）
PG=os.environ.get('POKEGOLD','pokegold/')  # pret/pokegold のフォルダ（定数・マクロを読む）
def run(*a):
    r=subprocess.run(a,capture_output=True,text=True)
    if r.returncode: print(r.stdout,r.stderr); sys.exit(1)
    if r.stderr.strip(): print(r.stderr)
def build(asms,out,base='base.gbc',basedata=0x51aa9,hm=True):
    objs=[]
    for a in asms:
        o='obj/'+os.path.basename(a)+'.o'; os.makedirs('obj',exist_ok=True)
        run(T+'rgbasm','-I',PG,'-o',o,a); objs.append(o)
    run(T+'rgblink','-p','0','-O',base,'-n',out.replace('.gbc','.sym'),'-m',out.replace('.gbc','.map'),'-o',out,*objs)
    d=bytearray(open(out,'rb').read())
    if hm:
        for i in range(251):
            o=basedata+i*32
            d[o+30]|=0xfc   # ひでんマシン01-06
            d[o+31]|=0x01   # ひでんマシン07
    open(out,'wb').write(d)
    run(T+'rgbfix','-v','-p','0',out)   # -p 0：バンク$40〜 を使うと 2MB にのばす（1MB のままなら何も変わらない）
    print(out, hex(zlib.crc32(open(out,'rb').read())))
if __name__=='__main__':
    build(sys.argv[2:],sys.argv[1])
