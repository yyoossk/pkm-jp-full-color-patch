import subprocess,sys,os,zlib
T=''  # rgbds 1.0.4 を PATH に入れておく
def run(*a): 
    r=subprocess.run(a,capture_output=True,text=True)
    if r.returncode: print(r.stdout,r.stderr); sys.exit(1)
    if r.stderr.strip(): print(r.stderr)
def build(asms,out,hm=True):
    objs=[]
    for a in asms:
        o='obj/'+os.path.basename(a)+'.o'; os.makedirs('obj',exist_ok=True)
        run(T+'rgbasm','-I',os.environ.get('POKECRYSTAL','pokecrystal/'),'-o',o,a); objs.append(o)   # サファリゾーンは pret/pokecrystal の 定数・マクロを読む
    run(T+'rgblink','-O','base.gbc','-n',out.replace('.gbc','.sym'),'-m',out.replace('.gbc','.map'),'-o',out,*objs)
    d=bytearray(open(out,'rb').read())
    if hm:
        BD=0x514ba
        for i in range(251):
            o=BD+i*32
            d[o+30]|=0xfc   # ひでんマシン01-06
            d[o+31]|=0x01   # ひでんマシン07
    open(out,'wb').write(d)
    run(T+'rgbfix','-v',out)
    print(out, hex(zlib.crc32(open(out,'rb').read())))
if __name__=='__main__':
    build(sys.argv[2:],sys.argv[1])
