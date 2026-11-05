import sys,re
j=open('/home/claude/work/rom/kin1.gbc','rb').read()
pat=sys.argv[1].replace(' ','')
rx=re.compile(b''.join(b'.' if pat[i:i+2]=='??' else re.escape(bytes.fromhex(pat[i:i+2])) for i in range(0,len(pat),2)),re.S)
n=int(sys.argv[2]) if len(sys.argv)>2 else 8
for m in rx.finditer(j):
    s=m.start(); print('%02x:%04x'%(s//0x4000,s%0x4000+(0x4000 if s>=0x4000 else 0)), j[s:s+len(pat)//2+n].hex())
