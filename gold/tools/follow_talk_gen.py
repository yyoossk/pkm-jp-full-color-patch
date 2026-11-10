# 連れ歩きに 話しかけた ときの 会話（src/follow_talk.inc）を 作る。会話の もとは 連れ歩きキットの 会話文案.md
# 〈〉 = ポケモンの ニックネーム、/ = 次の 行、¶ = 次の ページ
EMO = {'!': 0, '?': 1, 'happy': 2, 'sad': 3, 'heart': 4, 'bolt': 5, 'sleep': 6}
T = dict(NORMAL=0, FIGHTING=1, FLYING=2, POISON=3, GROUND=4, ROCK=5, BUG=7, GHOST=8, STEEL=9,
         FIRE=0x14, WATER=0x15, GRASS=0x16, ELECTRIC=0x17, PSYCHIC=0x18, ICE=0x19, DRAGON=0x1a, DARK=0x1b)
# 金・銀の 値（pokegold の constants。クリスタルは LANDMARK_BATTLE_TOWER（$1d）が ある ので 後ろが 1つ ずれる）
LM = dict(ROUTE_29=0x02, ROUTE_30=0x04, ROUTE_31=0x05, DARK_CAVE=0x2b, SPROUT_TOWER=0x07, RUINS_OF_ALPH=0x09,
          AZALEA_TOWN=0x0c, SLOWPOKE_WELL=0x0d, ILEX_FOREST=0x0e, ROUTE_36=0x14, GOLDENROD_CITY=0x10,
          RADIO_TOWER=0x11, NATIONAL_PARK=0x13, ECRUTEAK_CITY=0x16, BURNED_TOWER=0x18, TIN_TOWER=0x17,
          ROUTE_39=0x1a, LIGHTHOUSE=0x1c, CIANWOOD_CITY=0x20, ROUTE_40=0x1d, WHIRL_ISLANDS=0x1e, ROUTE_42=0x21,
          ROUTE_15=0x4c, ROUTE_18=0x4f, LAKE_OF_RAGE=0x25, MAHOGANY_TOWN=0x23, ICE_PATH=0x27, DRAGONS_DEN=0x29,
          VICTORY_ROAD=0x57, ROUTE_1=0x2f, ROUTE_2=0x31, ROUTE_3=0x33, MT_MOON=0x34, ROCK_TUNNEL=0x41,
          DIGLETTS_CAVE=0x3d, SAFFRON_CITY=0x47, CELADON_CITY=0x46, LAVENDER_TOWN=0x44, POWER_PLANT=0x43)
MAP = dict(GOLDENROD_GYM=(0x0b, 0x03), DANCE_THEATER=(0x04, 0x05), ROCKET_B1F=(0x03, 0x29),
           ROCKET_B2F=(0x03, 0x2a), ROCKET_B3F=(0x03, 0x2b), MAHOGANY_GYM=(0x02, 0x02), MR_PSYCHIC=(0x19, 0x08))
SP = dict(BULBASAUR=1, CHARMANDER=4, SQUIRTLE=7, PIKACHU=25, RAICHU=26, CLEFAIRY=35, CLEFABLE=36, DIGLETT=50,
          DUGTRIO=51, POLIWAG=60, BELLSPROUT=69, SLOWPOKE=79, SLOWBRO=80, FARFETCHD=83, ONIX=95, KRABBY=98,
          ELECTRODE=101, TAUROS=128, MAGIKARP=129, GYARADOS=130, DITTO=132, PORYGON=137, CHIKORITA=152,
          MEGANIUM=154, CYNDAQUIL=155, TYPHLOSION=157, TOTODILE=158, FERALIGATR=160, PICHU=172, CLEFFA=173,
          AMPHAROS=181, BELLOSSOM=182, SUDOWOODO=185, UNOWN=201, STEELIX=208, HERACROSS=214, MILTANK=241,
          RAIKOU=243, ENTEI=244, SUICUNE=245, LUGIA=249, HO_OH=250, CELEBI=251, EGG=0xfd)
EV_CLEARED_SLOWPOKE_WELL = 0x2b

# (種類, ふくむ タイプ, ランドマーク, マップ, 状態, イベント, アイコン, [文])
R = []
def r(sp=None, ty=None, lm=None, mp=None, st=0, ev=None, emo='happy', texts=()):
    sps = sp if isinstance(sp, (list, tuple)) else [sp]
    lms = lm if isinstance(lm, (list, tuple)) else [lm]
    mps = mp if isinstance(mp, list) else [mp]
    for s in sps:
        for l in lms:
            for m in mps:
                R.append((s, ty, l, m, st, ev, emo, list(texts)))

# 1. 状態異常
r(st=0x07, emo='sleep', texts=['〈〉は/すこし　ねむそうだ'])
r(st=0x08, emo='sad', texts=['〈〉は/ぐあいが　わるそうだ'])
r(st=0x10, emo='!', texts=['〈〉は/すこし　いたそうだ'])
r(st=0x20, emo='!', texts=['〈〉は/こおりづけに　なっている！'])
r(st=0x40, emo='bolt', texts=['〈〉は/うごきが　にぶく　なっている'])
# タマゴ（キットに ない。タマゴが 歩く ときの 文）
r(sp='EGG', emo='?', texts=['〈〉は/ときどき　うごいている……'])
# 2. ジョウト
r(sp='CHIKORITA', lm='ROUTE_29', texts=['〈〉は/はっぱを　ふりまわしている', '〈〉は/はっぱを　ぴくぴく　させている'])
r(sp='TOTODILE', lm='ROUTE_30', texts=['〈〉は/あごを　うごかしている', '〈〉は/くちを　ぱくぱく　させている'])
r(sp='CYNDAQUIL', lm='ROUTE_31', texts=['〈〉は/ひのこを　いくつか　はいた', '〈〉は/ひのこを　ひとつ　はいた……'])
r(ty='ICE', lm='DARK_CAVE', texts=['〈〉は/さむくなって　ごきげんだ'])
r(sp='BELLSPROUT', lm='SPROUT_TOWER', texts=['〈〉は/きままに　ゆらゆら　おどった', '〈〉は/ふしぎな　おどりを　おどった'])
r(sp='UNOWN', lm='RUINS_OF_ALPH', emo='?', texts=['〈〉から/ふしぎな　おとが　きこえる……', '〈〉は……/くるくる　まわりはじめた',
  '〈〉が/うなっている¶まるで　しゃべって/いるみたいだ……', 'ポケモンは/うごかない', 'ポケモンが/なにか　うたっている？'])
r(ty='FIRE', lm='AZALEA_TOWN', texts=['ポケモンは/あつくて　ごきげんだ！'])
r(sp=['SLOWPOKE', 'SLOWBRO'], lm='SLOWPOKE_WELL', ev=EV_CLEARED_SLOWPOKE_WELL, texts=['〈〉は/とても　うれしそうだ'])
r(sp=['SLOWPOKE', 'SLOWBRO'], lm='SLOWPOKE_WELL', emo='sad', texts=['ポケモンは/なんだか　かなしそうだ'])
r(ty='FIRE', lm='SLOWPOKE_WELL', emo='sad', texts=['ポケモンは/じめんの　みずが　いやみたいだ¶〈〉は/ぬれて　ごきげんななめだ……'])
r(ty='WATER', lm='SLOWPOKE_WELL', texts=['〈〉は/うれしそうに　はねまわっている！'])
r(sp='FARFETCHD', lm='ILEX_FOREST', texts=['〈〉は/とても　うれしそうだ'])
r(sp='CELEBI', lm='ILEX_FOREST', emo='heart', texts=['〈〉は/たのしそうに　おどった！', '〈〉は/うつくしく　おどった！'])
r(sp='HERACROSS', lm=['ILEX_FOREST', 'ROUTE_2'], texts=['〈〉は/きに　しがみついている！'])
r(sp='SUDOWOODO', lm='ROUTE_36', emo='?', texts=['〈〉は/ぴくりとも　うごかない……¶きの　まねを/しているようだ！'])
r(sp='CLEFAIRY', lm='GOLDENROD_CITY', mp=MAP['GOLDENROD_GYM'], texts=['〈〉は/ゆびを　ふって　おどっている！'])
r(ty='ELECTRIC', lm='RADIO_TOWER', emo='bolt', texts=['〈〉は/びりびり　きているようだ！'])
r(ty='GHOST', lm='RADIO_TOWER', emo='?', texts=['〈〉は/なにかを　けいかいしている……'])
r(ty='BUG', lm='NATIONAL_PARK', texts=['〈〉は/すこし　こうふん　している'])
r(sp='PICHU', lm='ECRUTEAK_CITY', mp=MAP['DANCE_THEATER'], texts=['〈〉は/まいこはんと　いっしょに　おどった！'])
r(sp='BELLOSSOM', lm='ECRUTEAK_CITY', mp=MAP['DANCE_THEATER'], texts=['〈〉は/まいこはんより　じょうずに/おどった！'])
r(sp=['RAIKOU', 'ENTEI', 'SUICUNE'], lm='BURNED_TOWER', emo='!', texts=['〈〉は/おおきな　こえで　ほえた！'])
r(sp='HO_OH', lm='BURNED_TOWER', emo='!', texts=['〈〉の　こえで/とうが　ゆれた！'])
r(sp='HO_OH', lm='TIN_TOWER', emo='!', texts=['〈〉は/そらを　みあげて　さけんでいる！'])
r(sp='TAUROS', lm='ROUTE_39', emo='!', texts=['〈〉は/とつぜん　ほえた！'])
r(sp='MILTANK', lm='ROUTE_39', texts=['〈〉は　うれしくて/ころがり　はじめた'])
r(sp='AMPHAROS', lm='LIGHTHOUSE', texts=['〈〉は　アカリちゃんと/いっしょに　ひかった！'])
r(sp='KRABBY', lm='CIANWOOD_CITY', texts=['〈〉は/よこに　あるいた！'])
r(sp='POLIWAG', lm=['ROUTE_40', 'WHIRL_ISLANDS'], texts=['〈〉は/おなかを　ゆらした'])
r(sp='LUGIA', lm='WHIRL_ISLANDS', emo='!', texts=['〈〉は　ながい　からだを/うごかして　おおきく　ほえた！'])
r(ty='WATER', lm='WHIRL_ISLANDS', texts=['〈〉は/ぬれて　うれしそうだ！'])
r(ty='ROCK', lm='ROUTE_42', texts=['〈〉は/やまを　みあげている¶のぼるのが/たのしみな　ようだ'])
r(sp='MAGIKARP', lm='LAKE_OF_RAGE', texts=['〈〉は/いつもより　はねている！'])
r(sp='GYARADOS', lm='LAKE_OF_RAGE', texts=['〈〉は/とても　うれしそうだ'])
r(sp='ELECTRODE', lm='MAHOGANY_TOWN', mp=[MAP['ROCKET_B1F'], MAP['ROCKET_B2F'], MAP['ROCKET_B3F']], emo='!', texts=['〈〉は/ふるえている！'])
ICE_T = ['わっ！　つめたい　かぜが/ふいた！¶でも　うれしそう？', '〈〉は/さむくて　ごきげんだ！', '〈〉は　さむくて/うれしそうに　よろこんでいる！']
GRASS_T = ['〈〉は/さむくて　ごきげんななめだ……', '〈〉は　さむくて/からだを　ちぢめた……']
r(ty='ICE', lm='ICE_PATH', texts=ICE_T)
r(ty='GRASS', lm='ICE_PATH', emo='sad', texts=GRASS_T)
r(ty='ICE', lm='MAHOGANY_TOWN', mp=MAP['MAHOGANY_GYM'], texts=ICE_T)
r(ty='GRASS', lm='MAHOGANY_TOWN', mp=MAP['MAHOGANY_GYM'], emo='sad', texts=GRASS_T)
r(ty='DRAGON', lm='DRAGONS_DEN', emo='!', texts=['〈〉は/とつぜん　ほえた！', '〈〉は/こうふん　している！', '〈〉は/とつぜん　とおぼえした！',
  '〈〉は/じっと　あなたを　みつめている', '〈〉は/ちいさく　うなっている'])
r(sp='MEGANIUM', lm='VICTORY_ROAD', emo='!', texts=['〈〉は　くびを　ふって/かけごえを　あげた！'])
r(sp='TYPHLOSION', lm='VICTORY_ROAD', emo='!', texts=['〈〉は　ほのおを/ふいて　さけんだ！'])
r(sp='FERALIGATR', lm='VICTORY_ROAD', emo='!', texts=['〈〉は　うでを/ふりまわして　さけんでいる！'])
# 3. カントー
r(sp='BULBASAUR', lm='ROUTE_1', texts=['〈〉は/つるを　くねくね　させた！', '〈〉は/つるを　ぴしっと　ならした！'])
r(sp='CHARMANDER', lm='ROUTE_2', texts=['〈〉は/しっぽの　ほのおを　もやした！'])
r(sp=['PICHU', 'PIKACHU', 'RAICHU'], lm=['ROUTE_2', 'POWER_PLANT'], emo='heart', texts=['〈〉は/たのしく　おどった！', '〈〉は　うれしくて/おどりだした！'])
r(sp='SQUIRTLE', lm='ROUTE_3', emo='sad', texts=['〈〉は　ころんで/ちょっと　くやしそうだ！'])
r(sp=['CLEFFA', 'CLEFAIRY', 'CLEFABLE'], lm='MT_MOON', texts=['〈〉は/そらを　みあげている！', '〈〉は/とつぜん　おどりだした！'])
r(sp=['ONIX', 'STEELIX'], lm='ROCK_TUNNEL', texts=['〈〉は　たのしそうに/じめんに　もぐっている！'])
r(ty='ROCK', lm='ROCK_TUNNEL', texts=['〈〉は　たのしそうに/ころがっている！', '〈〉は/いわを　けずりはじめた！', '〈〉は　たのしそうに/いわを　ぶつけている！',
  '〈〉は　じめんを/たたいて　ならしはじめた！'])
r(sp=['DIGLETT', 'DUGTRIO'], lm='DIGLETTS_CAVE', texts=['〈〉は　からだを/のばして　くつろいでいる！'])
r(ty='PSYCHIC', lm='SAFFRON_CITY', mp=MAP['MR_PSYCHIC'], emo='?', texts=['……　……　……　……¶〈〉は/だまって　うなずいた！'])
r(sp='PORYGON', lm='CELADON_CITY', emo='?', texts=['〈〉は/なにか　つぶやいた……'])
r(sp='DITTO', lm='ROUTE_15', emo='?', texts=['……おや？　〈〉の/すがたは……/かわらなかった！'])
r(ty='FLYING', lm='ROUTE_18', texts=['〈〉は/ゆうがに　そらを　とんでいる！'])
r(ty='GHOST', lm='LAVENDER_TOWN', texts=['〈〉は　たのしそうに/ゆらゆら　ゆれている'])
# 4. ふつう（さいご）
r(texts=['〈〉は/あなたと　いっしょで　うれしそうだ！'])

def enc(t):
    """文 → db の 行"""
    out = []
    line = 0
    first = True
    buf = ''
    def flush():
        nonlocal buf
        if buf:
            out.append('db "%s"' % buf)
            buf = ''
    i = 0
    started = False
    while i < len(t):
        if t.startswith('〈〉', i):
            flush()
            out.append('db $01\n\tdw wPartyMonNicknames')
            out.append('db $00')
            started = True
            i += 2
            continue
        if not started:
            out.append('db $00')
            started = True
        c = t[i]
        if c == '/':
            flush()
            out.append('db $4f' if line == 0 else 'db $55')
            line += 1
        elif c == '¶':
            flush()
            out.append('db $51')
            line = 0
        else:
            buf += c
        i += 1
    flush()
    out.append('db $57')
    return out

lines = ['; tools/follow_talk_gen.py で 作る（手で 書きかえない）。会話の もとは 連れ歩きキットの 会話文案.md',
         '; 表：種類（0 = どれでも）、タイプ（$ff = どれでも）、ランドマーク（$ff）、マップ（グループ・番号。0, 0 = どれでも）、',
         ';     状態（0 = どれでも）、イベントフラグ（$ffff = 見ない。立って いる とき だけ）、アイコン、文の 表',
         'FollowerTalkTable:']
texts = {}
for k, (s, ty, l, m, st, ev, emo, tx) in enumerate(R):
    key = tuple(tx)
    if key not in texts:
        texts[key] = 'FwTexts_Default' if k == len(R) - 1 else 'FwTexts_%d' % len(texts)
    lines.append('\tdb %d, $%02x, $%02x, $%02x, $%02x, $%02x' % (
        SP[s] if s else 0, T[ty] if ty else 0xff, LM[l] if l else 0xff,
        m[0] if m else 0, m[1] if m else 0, st))
    lines.append('\tdw $%04x' % (ev if ev is not None else 0xffff))
    lines.append('\tdb %d' % EMO[emo])
    lines.append('\tdw %s' % texts[key])
lines.append('\tdb $fe ; おわり')
lines.append('DEF FW_TALK_ROW EQU 11')
lines.append('')
for key, lab in texts.items():
    lines.append('%s:' % lab)
    lines.append('\tdb %d' % len(key))
    for j in range(len(key)):
        lines.append('\tdw %s_%d' % (lab, j))
for key, lab in texts.items():
    for j, t in enumerate(key):
        lines.append('%s_%d: ; %s' % (lab, j, t))
        for l in enc(t):
            lines.append('\t' + l)
open('src/follow_talk_data.inc', 'w').write('\n'.join(lines) + '\n')
print(len(R), 'rows', len(texts), 'text sets')
