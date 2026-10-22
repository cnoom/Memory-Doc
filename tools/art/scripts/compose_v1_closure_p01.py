"""Upgrade flow preview assembled from approved assets; not game implementation."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3]; B=R/'ImageReview/batches/v1-closure-p01'; B.mkdir(parents=True,exist_ok=True)
reg={a['id']:a for a in json.loads((R/'docs/design/art-inventory/developer-asset-registry.json').read_text(encoding='utf-8'))['items']}; deps={}
def asset(i):
 a=reg[i]; p=R/a['paths']['png']; assert a['productionEligible'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'];deps[i]=a['paths']['png'];return Image.open(p).convert('RGBA')
def panel(w,h):
 im=asset('panel_paper_a03'); o=Image.new('RGBA',(w,h)); xs=[0,32,224,256];ys=xs;dx=[0,32,w-32,w];dy=[0,32,h-32,h]
 for i in range(3):
  for j in range(3):o.alpha_composite(im.crop((xs[i],ys[j],xs[i+1],ys[j+1])).resize((dx[i+1]-dx[i],dy[j+1]-dy[j]),Image.Resampling.LANCZOS),(dx[i],dy[j]))
 return o
def txt(im,x,y,s,n=25,c='#252F32',anchor='lm'):
 ImageDraw.Draw(im).text((x,y),s,font=ImageFont.truetype(str(R/'ImageReview/batches/fonts-q01'/('SourceHanSerifSC-Regular.otf' if n>=32 else 'SourceHanSansSC-Regular.otf')),n),fill=c,anchor=anchor)
def btn(im,x,y,w,s,disabled=False,secondary=False):
 a=asset('btn_'+('secondary' if secondary else 'primary')+'_'+('disabled' if disabled else 'normal')+'_b03');h=round(w*112/640);im.alpha_composite(a.resize((w,h),Image.Resampling.LANCZOS),(x,y));txt(im,x+w/2,y+h/2,s,24,'#485356' if disabled or secondary else '#F1EEE2','mm')

outputs=[]
def save(im,name):
 im.convert('RGB').save(B/(name+'.png'));outputs.append(name)
def base(title,bg='bg_map_i04'):
 im=asset(bg);im.alpha_composite(Image.new('RGBA',im.size,(0,0,0,95)));im.alpha_composite(panel(1640,920),(140,90));txt(im,220,160,title,42);return im
def fitpaste(im,aid,box):
 a=ImageOps.contain(asset(aid),(box[2],box[3]),Image.Resampling.LANCZOS);im.alpha_composite(a,(box[0]+(box[2]-a.width)//2,box[1]+(box[3]-a.height)//2))
def lines(im,x,y,ss,size=27,gap=43,color='#252F32'):
 for j,s in enumerate(ss):txt(im,x,y+j*gap,s,size,color)
def tabs(im,current):
 for i,label in enumerate(['个人信息','当前卡组','遗物']):btn(im,230+i*340,225,300,label,secondary=label!=current)
 btn(im,1450,135,250,'返回',secondary=True)
def card(aid,name,lines_,skill=False):
 fid='border_card_skill_ornate_c05' if skill else 'border_card_attack_ornate_c04';f=asset(fid);s=reg[fid]['spec'];w=s['window'];o=Image.new('RGBA',f.size)
 o.alpha_composite(ImageOps.fit(asset(aid),(w['width'],w['height']),method=Image.Resampling.LANCZOS),(w['x'],w['y']))
 o.putalpha(Image.open(R/s['windowMask']).convert('L'));o.alpha_composite(f)
 t=s['textSafe']['title'];txt(o,t['x']+t['width']/2,t['y']+t['height']/2,name,72,anchor='mm')
 for j,line in enumerate(lines_):txt(o,480,900+j*64,line,48,anchor='mm')
 return o
starters=[('打击',4,'card_attack_daji_etching_b01',['造成6点伤害'],False),('格挡',4,'card_skill_gedang_etching_b01',['获得6点格挡'],True),('笔记',1,'card_attack_biji_etching_b01',['造成6点伤害','[共鸣]'],False),('读书笔记',1,'card_attack_dushubiji_illustration_v02',['造成8点伤害','[翻开] 标记相邻','1张背面牌','[共鸣]'],False)]
cards=[card(aid,n,l,sk) for n,c,aid,l,sk in starters]
for victory in [True,False]:
 im=base('旅途结算','bg_battle_empty_a01')
 fitpaste(im,'ornament_memory_ring_b03',(260,265,420,420))
 txt(im,470,750,'学者',36,anchor='mm')
 txt(im,1060,285,'胜利' if victory else '失败',64,'#355C67' if victory else '#8D3D35')
 stats=[('到达章节','第1章 · 通关' if victory else '第1章 · 败于精英节点'),('击败敌人','4' if victory else '2'),('获得金币','110' if victory else '65'),('剩余生命','28 / 60' if victory else '0 / 60')]
 for j,(k,v) in enumerate(stats):txt(im,900,435+j*88,k,29);txt(im,1630,435+j*88,v,29,anchor='rm')
 btn(im,870,880,360,'返回主菜单',secondary=True);btn(im,1330,880,360,'再来一局');save(im,'victory' if victory else 'defeat')

im=base('选择角色','bg_main_menu_h03');fitpaste(im,'portrait_scholar_etching_b01',(225,260,430,580))
txt(im,760,255,'学者',48);txt(im,760,322,'初始生命 60 / 60',29)
txt(im,760,395,'触类旁通',33);lines(im,760,447,['每获得一张卡牌，有25%概率附加[共鸣]。','已带[共鸣]的卡牌不会重复附加。'],27)
txt(im,760,555,'初始牌库 · 10张',30)
for i,((name,count,aid,_,_),c) in enumerate(zip(starters,cards)):
 x=760+i*225;im.alpha_composite(c.resize((180,240),Image.Resampling.LANCZOS),(x,590));txt(im,x+90,862,f'{name} ×{count}',23,anchor='mm')
btn(im,225,915,320,'返回',secondary=True);btn(im,1320,915,360,'开始旅途');save(im,'character_select')

im=base('旅途详情');tabs(im,'个人信息');fitpaste(im,'portrait_scholar_etching_b01',(235,330,390,525))
txt(im,760,355,'学者',45)
lines(im,760,425,['生命 52 / 60      金币 50','第一章 · 记忆回廊','当前卡组 10张      已持有遗物 2件'],29,58)
txt(im,760,640,'角色被动 · 触类旁通',31)
lines(im,760,700,['每获得一张卡牌，有25%概率为其附加[共鸣]。','带[共鸣]的卡牌可以与其他[共鸣]卡牌匹配。','已带[共鸣]时不重复附加。'],26)
save(im,'journey_profile')

for empty in [False,True]:
 im=base('旅途详情');tabs(im,'当前卡组')
 txt(im,230,325,'牌库10张 · 按相同状态分组',26)
 btn(im,230,365,210,'全部',secondary=empty);btn(im,460,365,210,'攻击',secondary=True);btn(im,690,365,210,'技能',secondary=True);btn(im,920,365,210,'能力',secondary=not empty)
 if empty:
  txt(im,960,585,'没有符合筛选条件的卡牌',36,anchor='mm');btn(im,800,680,320,'清除筛选',secondary=True)
 else:
  for i,c in enumerate(cards):
   x=230+i*245;im.alpha_composite(c.resize((220,293),Image.Resampling.LANCZOS),(x,465));txt(im,x+110,800,f'{starters[i][0]} ×{starters[i][1]}',22,anchor='mm')
  ImageDraw.Draw(im).rounded_rectangle((958,459,1187,764),radius=8,outline='#648891',width=3)
  ImageDraw.Draw(im).line((1250,440,1250,910),fill='#87918A',width=2)
  txt(im,1310,485,'读书笔记',32);lines(im,1310,555,['普通 · 攻击','牌库中共1张','造成8点伤害','[翻开] 标记相邻','1张背面牌','[共鸣]'],25,43)
  txt(im,230,910,'数量按牌库单份统计。',23,'#48575A')
 save(im,'journey_cards_empty' if empty else 'journey_cards')

for empty in [False,True]:
 im=base('旅途详情');tabs(im,'遗物');txt(im,230,330,'已持有遗物 · '+('0件' if empty else '2件'),28)
 if empty:txt(im,960,560,'尚未获得遗物',38,anchor='mm')
 else:
  for x,aid,name in [(260,'relic_memory_crystal_etching_e01','记忆水晶'),(650,'relic_first_aid_kit_etching_e01','急救包')]:
   fitpaste(im,aid,(x,400,256,256));txt(im,x+128,710,name,30,anchor='mm')
  ImageDraw.Draw(im).rounded_rectangle((240,380,540,755),radius=10,outline='#648891',width=4)
  txt(im,1140,430,'记忆水晶',36);lines(im,1140,505,['普通遗物','每场战斗开始时，','随机揭示桌面5张背面牌。'],28,54)
 save(im,'journey_relics_empty' if empty else 'journey_relics')

for is_card in [True,False]:
 im=base('古老日记' if is_card else '流浪商队的谢礼')
 fitpaste(im,'ill_event_diary_etching_g01' if is_card else 'ill_event_caravan_gift_etching_g01',(220,260,720,480))
 txt(im,1070,280,'仔细阅读' if is_card else '收下谢礼',34)
 if is_card:
  c=Image.open(R/'ImageReview/batches/shop-k02/card_1_review.png').convert('RGBA');im.alpha_composite(c.resize((240,320),Image.Resampling.LANCZOS),(1070,340))
  lines(im,1360,410,['获得火球术 ×1','牌库 10 → 11张','生命 52 → 49'],26,55)
 else:
  fitpaste(im,'relic_memory_crystal_etching_e01',(1070,360,256,256));lines(im,1360,410,['获得记忆水晶','普通遗物','生命不变'],26,55)
 txt(im,230,800,'事件已结算，奖励已加入本次旅途。',27)
 btn(im,1240,870,380,'继续旅途');save(im,'event_card_result' if is_card else 'event_relic_result')
(B/'assets.json').write_text(json.dumps({'status':'pending-review','productionEligible':False,'role':'v1-static-flow-reference-batch','outputs':outputs,'dependencies':deps,'note':'All numeric values are illustrative; static reference only.'},ensure_ascii=False,indent=2),encoding='utf-8')

