"""第52弾：カントーの ライバル（シゲル）の 名前を 自分で きめる（金）。
   ・新しい ゲーム：オーキドの 話を クリスタル版の もの（赤の セリフ・ニドリーノ・ライバルの 名前の えらびかた）に。
     クリスタル版の 36:5867〜5B6E（コードと セリフ）を 新しい バンクの 同じ 住所へ うつして 金に 読みかえる。
     主人公の 絵は 金の 絵（トレーナーの 種類 CAL。クリスタル版の DrawIntroPlayerPic の かわり）。
     曲は クリスタル版（第53弾の 赤の オーキドの 曲）の かわりに 金の MUSIC_ROUTE_3（24・25番道路の 曲）。
   ・wGreensName の はじめの 名前 グリーン → シゲル、（主人公の 名前の 候補 サトシは gold_full の はじめで 済み）。
   ・トレーナーの 種類 $40（カントーの ライバル）の 名前は wGreensName（TB の GetTrainerName）。
   ・名前の 画面で wGreensName を きめる ときは シゲルの 人の絵（SPRITE_BLUE）。
"""
import sys
sys.path.insert(0, '/home/claude/work/scripts')
from asmx import L, CSD, GJ, GB, RX, RAM_FIX
from jpchar import encode
def fo(b, a): return b * 0x4000 + a - 0x4000

SRC = 0x36; LO, CODE_END, HI = 0x5867, 0x59A6, 0x5B6F
TXT2CRY = (0x599A, 0x59A6)
CAL = 0x0C
MUSIC_ROUTE_3 = 0x03
W_GREENS = 0xD1CD
FAR = {(0x24, 0x469E): (0x24, 0x4677),          # InitClock
       (0x01, 0x62FC): (0x01, 0x6373),          # Intro_WipeInFrontpic
       (0x01, 0x6208): (0x01, 0x6237),          # NamePlayer
       (0x01, 0x6316): (0x01, 0x638D),          # Intro_PrepTrainerPic
       (0x01, 0x62E4): (0x01, 0x635B),          # Intro_RotatePalettesLeftFrontpic
       (0x22, 0x426D): (0x01, 0x632C),          # MovePlayerPicRight
       (0x22, 0x4275): (0x01, 0x6334),          # MovePlayerPicLeft
       (0x02, 0x4C1D): (0x02, 0x51D6),          # ApplyMonOrTrainerPals
       (0x04, 0x565B): (0x04, 0x5A47),          # NamingScreen
       (0x22, 0x487D): (0x01, 0x638D)}          # DrawIntroPlayerPic（あとで 書きかえる）
HOME_EXTRA = {0x2ECB: None}                       # InitName（下で さがす）
RAM = {0xD264: 0xD10F, 0xC4F6: 0xC3F6}            # wTrainerClass、hlcoord 6,4
CHECK = {0xD4A6: 'wGreensName', 0xD066: 'wStringBuffer2', 0xCF54: 'wCurSpecies', 0xD0C8: 'wCurPartySpecies',
         0xD0E3: 'wTempMonDVs', 0xD0E4: 'wTempMonDVs', 0xCF9D: 'wMenuCursorY'}
VALUE = {0x0062, 0x0006}

def find_initname(G):
    """金の InitName（home/string.asm）：クリスタル版 $2ECB と 同じ 並び"""
    M = open('/home/claude/work/ref/crystal_kj.gbc', 'rb').read()
    pat = M[0x2ECB:0x2ECB + 24]
    import re
    # 3バイトの 命令の 引数は ちがって よい
    p = 0; rx = b''
    while p < len(pat):
        op = pat[p]; ln = L[op]
        rx += re.escape(bytes([op])) + (b'..' if ln == 3 else re.escape(bytes(pat[p + 1:p + ln])))
        p += ln
    r = [m.start() for m in re.finditer(rx[:60], G[:0x4000], re.S)]
    assert len(r) == 1, r
    return r[0]

def apply(g, M, PB, TB, log):
    G = bytes(g)
    g[fo(PB, LO):fo(PB, HI)] = M[fo(SRC, LO):fo(SRC, HI)]
    initname = find_initname(G)
    p = LO
    while p < CODE_END:
        o = fo(SRC, p); d = fo(PB, p); op = M[o]; ln = L[op]
        if ln == 3 and op != 0x31:
            v = M[o + 1] | M[o + 2] << 8; nv = v
            if op == 0x21 and M[o - 2] == 0x3E and M[o + 3] == 0xCF:
                nb, nv = FAR[(M[o - 1], v)]; g[d - 1] = nb
            elif v in VALUE: nv = v
            elif v < 0x4000:
                if v == 0x2ECB: nv = initname
                elif v == 0x1041: nv = 0x0F30   # PrintText
                else:
                    nm = CSD.get((0, v)); assert nm and GB.get(nm, 0) == 0, (hex(v), nm); nv = GJ[nm]
            elif v < 0x8000: assert LO <= v < HI, hex(v)
            elif 0xC000 <= v < 0xE000:
                if v in RAM: nv = RAM[v]
                elif v in RAM_FIX: nv = RAM_FIX[v]
                else:
                    nv, nm = RX.x(v); assert nm.split('+')[0] == CHECK[v], (hex(v), nm)
            g[d + 1] = nv & 0xFF; g[d + 2] = nv >> 8
        p += ln
    # 曲
    o = fo(PB, 0x5873); assert g[o:o + 3] == bytes([0x11, 0x62, 0x00]); g[o + 1] = MUSIC_ROUTE_3
    # 主人公の 絵（5916〜5921：DrawIntroPlayerPic → ShowTrainerPic(CAL)）
    o = fo(PB, 0x5916); assert M[fo(SRC, 0x591A):fo(SRC, 0x591D)] == bytes([0x3E, 0x22, 0x21])
    g[o:o + 12] = bytes([0x3E, CAL, 0xC3, 0xFD, 0x58]) + bytes(7)
    # 金の OakSpeech（01:5FB3）→ ここへ
    o = fo(0x01, 0x5FB3); assert G[o:o + 3] == bytes([0x3E, 0x24, 0x21])
    g[o:o + 7] = bytes([0x3E, PB, 0x21, LO & 0xFF, LO >> 8, 0xCF, 0xC9])
    # はじめの 名前
    o = fo(0x01, 0x5D82); assert G[o:o + 5] == encode('グリーン@'); g[o:o + 5] = encode('シゲル@') + b'\x50'
    # トレーナーの 名前（TB の GetTrainerName 5918）
    o = fo(TB, 0x5918); assert g[o:o + 3] == bytes([0x79, 0xFE, 0x0C])
    sa = 0x54F0; st = fo(TB, sa); assert not any(g[st:st + 0x21])      # 手持ちの 所（〜$5510）の あき
    g[st:st + 16] = bytes([0x79, 0xFE, 0x40, 0x21, W_GREENS & 0xFF, W_GREENS >> 8, 0xCA, 0x50, 0x59,
                           0x79, 0xFE, 0x0C, 0xC3, 0x1B, 0x59, 0x00])
    g[o:o + 3] = bytes([0xC3, sa & 0xFF, sa >> 8])
    # 名前の 画面の 人の絵（04:5B28 ld de,$43C0）→ HFI で バンク 7E の 本体（a・hl・フラグは そのまま）
    import gold_hfi
    o = fo(0x04, 0x5B28); assert G[o:o + 3] == bytes([0x11, 0xC0, 0x43])
    D = 0xC5D0   # wNamingScreenDestinationPointer
    body = bytes([0xF5, 0x11, 0xC0, 0x43, 0xFA, D & 0xFF, D >> 8, 0xFE, W_GREENS & 0xFF, 0x20, 0x0A,
                  0xFA, (D + 1) & 0xFF, (D + 1) >> 8, 0xFE, W_GREENS >> 8, 0x20, 0x03, 0x11, 0x40, 0x48, 0xF1, 0xC9])
    t = gold_hfi.put(g, body); st = gold_hfi.stub(g, 0x04, t)
    g[o:o + 3] = bytes([0xCD, st & 255, st >> 8])
    log.append('第52弾：オーキドの 話 %02X:%04X、InitName %04X、トレーナーの 名前 %02X:%04X' % (PB, LO, initname, TB, sa))
