import sys,pickle,align as A
A.load('/home/claude/work/rom/kin1.gbc')
rom,ram=pickle.load(open('/home/claude/work/tools/jpsym.pkl','rb'))
n=int(sys.argv[2]) if len(sys.argv)>2 and sys.argv[2].isdigit() else 24
for name in [x for x in sys.argv[1:] if not x.isdigit()]:
    if name in ram: print(name,'RAM EN %04x JP %04x'%(A.SYM[name][1],ram[name])); continue
    if name not in A.SYM: print(name,'NOSYM'); continue
    eb,ea=A.SYM[name]; eo=A.off(eb,ea)
    if name in rom:
        jb,ja=rom[name]; jo=A.off(jb,ja)
        print('%-40s EN %02x:%04x JP %02x:%04x'%(name,eb,ea,jb,ja)); print('  EN',A.EN[eo:eo+n].hex()); print('  JP',A.JP[jo:jo+n].hex())
    else:
        print('%-40s EN %02x:%04x JP ?'%(name,eb,ea)); print('  EN',A.EN[eo:eo+n].hex())
