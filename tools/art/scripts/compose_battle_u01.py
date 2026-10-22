"""Compose approved independent art at V05 board anchors; preview only."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];O=R/'ImageReview/batches/battle-u01';O.mkdir(parents=True,exist_ok=True)
reg={a['id']:a for a in json.loads((R/'docs/design/art-inventory/developer-asset-registry.json').read_text(encoding='utf-8'))['items']};deps={}
def asset(k):
 a=reg[k];assert a['productionEligible'];p=R/a['paths']['png'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'];deps[k]=a['paths']['png'];return Image.open(p).convert('RGBA')
def text(im,xy,s,size=24,color='#F1EEE2',anchor='lm',title=False):
 f=ImageFont.truetype(str(R/'Assets/UI/fonts/q01'/('SourceHanSerifSC-Regular.otf' if title else 'SourceHanSansSC-Regular.otf')),size);ImageDraw.Draw(im).text(xy,s,font=f,fill=color,anchor=anchor)
def fit(im,k,box):
 a=ImageOps.contain(asset(k),box[2:],Image.Resampling.LANCZOS);im.alpha_composite(a,(box[0]+(box[2]-a.width)//2,box[1]+box[3]-a.height))
def paste(im,k,xy,size=None):
 a=asset(k)
 if size:a=a.resize(size,Image.Resampling.LANCZOS)
 im.alpha_composite(a,xy)
def nine(im,k,box):
 a=asset(k);w,h=box[2:];l,b,r,t=reg[k]['spec']['slice'];sx=[0,l,a.width-r,a.width];sy=[0,t,a.height-b,a.height];dx=[0,l,w-r,w];dy=[0,t,h-b,h]
 for x in range(3):
  for y in range(3):im.alpha_composite(a.crop((sx[x],sy[y],sx[x+1],sy[y+1])).resize((dx[x+1]-dx[x],dy[y+1]-dy[y]),Image.Resampling.LANCZOS),(box[0]+dx[x],box[1]+dy[y]))
frame=asset('border_card_attack_ornate_c04');sp=reg['border_card_attack_ornate_c04']['spec'];w=sp['window'];card=Image.new('RGBA',frame.size)
card.alpha_composite(ImageOps.fit(asset('card_attack_dushubiji_illustration_v02'),(w['width'],w['height'])),(w['x'],w['y']));card.putalpha(Image.open(R/sp['windowMask']).convert('L'));card.alpha_composite(frame)
# Render text at actual display size, not baked source font sizes.
card=card.resize((144,192),Image.Resampling.LANCZOS);text(card,(76,31),'读书笔记',13,'#252F32',anchor='mm',title=True)
for y,s in [(136,'造成8点伤害'),(151,'翻开：标记邻牌'),(165,'共鸣')]:text(card,(72,y),s,11,'#252F32','mm')
for boss in [False,True]:
 im=asset('bg_battle_empty_a01');im=ImageOps.fit(im,(1920,1080));d=ImageDraw.Draw(im)
 shade=Image.new('RGBA',im.size);ImageDraw.Draw(shade).rectangle((0,76,1080,1080),fill=(24,34,37,110));im.alpha_composite(shade)
 fit(im,'enemy_memory_devourer_phase3_s02' if boss else 'enemy_chaos_slime_etching_b01',(1260,145,480,300))
 fit(im,'portrait_scholar_etching_b01',(1180,750,285,330))
 d=ImageDraw.Draw(im);d.rectangle((0,0,1920,76),fill='#252F32');text(im,(48,38),'记忆勇者',32,title=True);text(im,(360,38),'第一章  /  记忆回廊',22)
 text(im,(1510,38),'金币 50     牌库 10',23);paste(im,'btn_secondary_normal_b03',(1615,88),(285,50));text(im,(1757,113),'旅途手记 · 暂停',21,'#252F32','mm')
 text(im,(304,111),'记忆牌阵',18);text(im,(940,111),'翻牌推进敌人行动',16,anchor='rm')
 text(im,(84,145),'遗物',18,anchor='mm');text(im,(84,235),'暂无',16,anchor='mm')
 for i in range(16):
  x=304+(i%4)*164;y=132+(i//4)*212
  if i==6:im.alpha_composite(card,(x,y))
  else:paste(im,'cardback_universal_ornate_c03',(x,y),(144,192))
  if i==7:paste(im,'badge_mark_paper_b03',(x+79,y+9),(60,25));text(im,(x+109,y+21),'×1',16,'#252F32','mm')
 text(im,(304,982),'正面 1 / 1',18);text(im,(940,982),'点击正面牌查看详情',16,anchor='rm');d=ImageDraw.Draw(im);d.line((274,1008,970,1008),fill='#657174')
 text(im,(274,1045),'抽牌 4   弃牌 0   消耗 0   记忆 1',21);paste(im,'btn_secondary_normal_b03',(778,1025),(192,34));text(im,(874,1042),'重新铺满 +2',16,'#252F32','mm')
 paste(im,'hud_enemy_base_a03',(1206,456))
 name='记忆吞噬者' if boss else '混乱史莱姆';hp='54 / 180' if boss else '35 / 35';threshold=8 if boss else 10;value=6 if boss else 1
 text(im,(1242,492),name,32,title=True);text(im,(1835,492),'第三阶段' if boss else '普通敌人',18,anchor='rm')
 text(im,(1242,531),'生命',16);text(im,(1835,531),hp,21,anchor='rm');nine(im,'hud_health_track_a03',(1242,545,590,12));paste(im,'hud_health_fill_a03',(1243,547),(int(588*(.3 if boss else 1)),8))
 text(im,(1242,579),'行动条',23);text(im,(1350,579),f'距行动 {threshold-value} 点',17);text(im,(1835,579),f'{value} / {threshold}',22,anchor='rm')
 for j in range(threshold):nine(im,'hud_action_filled_a03' if j<value else 'hud_action_empty_a03',(1242+j*(590//threshold),598,590//threshold-5,28))
 fit(im,'icon_intent_attack_etching_b01',(1242,637,30,30));text(im,(1288,654),'下次行动',16);text(im,(1390,654),f'攻击 {16 if boss else 6}',25);text(im,(1830,654),'行动条满时执行',15,anchor='rm')
 paste(im,'hud_player_base_a03',(1480,864));text(im,(1516,903),'学者',29,'#252F32',title=True);text(im,(1806,903),'触类旁通',15,'#48575A','rm')
 nine(im,'hud_health_track_a03',(1516,929,290,12));paste(im,'hud_health_fill_a03',(1517,931),(288,8));text(im,(1660,956),'60 / 60',20,'#252F32','mm');text(im,(1516,988),'格挡 0',20,'#252F32');text(im,(1806,1014),'持续能力：暂无',15,'#48575A','rm')
 im.convert('RGB').save(O/('boss_phase3.png' if boss else 'normal.png'))
(O/'assets.json').write_text(json.dumps({'status':'pending-review','productionEligible':False,'canvas':[1920,1080],'dependencies':deps,'outputs':['normal.png','boss_phase3.png']},ensure_ascii=False,indent=2),encoding='utf-8')
