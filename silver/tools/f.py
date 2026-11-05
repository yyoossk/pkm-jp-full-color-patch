# f.py LABEL PATTERN [range]  … LABEL の JP の位置から PATTERN（16進、?? は何でも）を探す
import sys,pickle,re,align as A
A.load('/home/claude/work/rom/kin1.gbc')
rom,ram=pickle.load(open('/home/claude/work/tools/jpsym.pkl','rb'))
lab,pat=sys.argv[1],sys.argv[2].replace(' ','')
rng=int(sys.argv[3],0) if len(sys.argv)>3 else 0x200
jb,ja=rom[lab]; jo=A.off(jb,ja)
rx=re.compile(b''.join(b'.' if pat[i:i+2]=='??' else re.escape(bytes.fromhex(pat[i:i+2])) for i in range(0,len(pat),2)),re.S)
for m in rx.finditer(A.JP,jo,jo+rng):
    o=m.start(); print('%02x:%04x +%d'%(jb,ja+o-jo,o-jo), A.JP[o:o+len(pat)//2+6].hex())
