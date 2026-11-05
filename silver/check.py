# 書きかえる所の元の命令が思った通りか確かめる
import sys
b=open(sys.argv[1],'rb').read()
def at(bank,a,hexs,name):
    o=a if a<0x4000 else bank*0x4000+a-0x4000
    ok=b[o:o+len(hexs)//2].hex()==hexs
    print('OK ' if ok else 'NG ',name,'%02x:%04x'%(bank,a),b[o:o+len(hexs)//2].hex(),'' if ok else 'expected '+hexs)
    return ok
r=all([
at(4,0x41ae,'3e01cd5f4237c9','walk'),
at(4,0x41db,'3e01cd5f4237c9','surf'),
at(4,0x425f,'5f1600','DoStep'),
at(4,0x6966,'a800','StartMenu MenuData'),
at(4,0x696c,'6e69','items ptr'),
at(4,0x6b0b,'3e06cd286b','exit append'),
at(4,0x6b28,'12130cc9','AppendMenuList'),
at(4,0x6dab,'21be6d110300','actions ptr'),
at(9,0x4ca2,'21bc4ccd591b','LoadHeader'),
at(9,0x4ca8,'cdc44c','GetTopCoord call'),
at(9,0x4cab,'cd0e4d','Populate call'),
at(9,0x4cbc,'40000b1113000001','MonSubmenu header'),
at(9,0x4cc4,'fac5d0','GetTopCoord'),
at(9,0x4ce1,'cd5a1a','InitCursor call'),
at(9,0x4ce4,'2110cfcbf6cd131a','Joypad'),
at(9,0x4d01,'fa14cf3d4f','Select'),
at(9,0x4d0e,'cd3d1b','PopulateMonMenu'),
at(9,0x4d2d,'21574c','GetMonMenuString'),
at(9,0x4d48,'21304c','StrPtr'),
at(9,0x4dac,'fac5d0fe082805','Cancel'),
at(9,0x4db8,'cdf34dc9','Term'),
at(9,0x4dd0,'21564c','IsFieldMove ptr'),
at(9,0x4e00,'e5d5f5','AddMonMenuItem'),
at(0x25,0x66d0,'cdfc66cd2667','HandleMap tail'),
at(0x25,0x6726,'3e01219658cf3e0321a957cfc9','HandleMapBackground'),
at(0,0x01ca,'afea1ecf','VBlank clear'),
at(0x36,0x4145,'470f1c004990','PC script'),
])
print('ALL OK' if r else 'SOME NG')
