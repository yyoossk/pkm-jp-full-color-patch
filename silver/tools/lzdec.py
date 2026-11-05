# ポケモン金銀クリスタルの LZ 展開（確認用）
def dec(d):
    out=bytearray(); i=0
    while True:
        b=d[i]
        if b==0xff: return bytes(out),i+1
        if (b&0xe0)==0xe0:
            cmd=(b>>2)&7; n=((b&3)<<8|d[i+1])+1; i+=2
        else:
            cmd=b>>5; n=(b&0x1f)+1; i+=1
        if cmd==0: out+=d[i:i+n]; i+=n
        elif cmd==1: out+=bytes([d[i]])*n; i+=1
        elif cmd==2:
            for k in range(n): out.append(d[i+(k&1)])
            i+=2
        elif cmd==3: out+=bytes(n)
        else:
            if d[i]&0x80: off=len(out)-1-(d[i]&0x7f); i+=1
            else: off=d[i]<<8|d[i+1]; i+=2
            for k in range(n):
                if cmd==4: out.append(out[off+k])
                elif cmd==5:
                    x=out[off+k]; out.append(int('{:08b}'.format(x)[::-1],2))
                elif cmd==6: out.append(out[off-k])
