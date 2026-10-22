"""Card reward preview assembled from approved assets; not game implementation."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3]; B=R/'ImageReview/batches/reward-n01'; B.mkdir(parents=True,exist_ok=True)
reg={a['id']:a for a in json.loads((R/'docs/design/art-inventory/developer-asset-registry.json').read_text(encoding='utf-8'))['items']}; deps={}
def asset(i):
 a=reg[i]; p=R/a['paths']['png']; assert a['productionEligible'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'];deps[i]=a['paths']['png'];return Image.open(p).convert('RGBA')
def panel(w,h):
 im=asset('panel_paper_a03'); o=Image.new('RGBA',(w,h)); xs=[0,32,224,256];ys=xs;dx=[0,32,w-32,w];dy=[0,32,h-32,h]
 for i in range(3):
  for j in range(3):o.alpha_composite(im.crop((xs[i],ys[j],xs[i+1],ys[j+1])).resize((dx[i+1]-dx[i],dy[j+1]-dy[j]),Image.Resampling.LANCZOS),(dx[i],dy[j]))
 return o
def txt(im,x,y,s,n=25,c='#252F32',anchor='lm'):
 ImageDraw.Draw(im).text((x,y),s,font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n),fill=c,anchor=anchor)
def btn(im,x,y,w,s,disabled=False,secondary=False):
 a=asset('btn_'+('secondary' if secondary else 'primary')+'_'+('disabled' if disabled else 'normal')+'_b03');h=round(w*112/640);im.alpha_composite(a.resize((w,h),Image.Resampling.LANCZOS),(x,y));txt(im,x+w/2,y+h/2,s,24,'#485356' if disabled or secondary else '#F1EEE2','mm')

cards=[('火球术','普通 · 攻击','border_card_attack_ornate_c04','card_attack_huoqiushu_etching_d07',['造成6点伤害']),('连锁雷','罕见 · 攻击','border_card_attack_uncommon_r01','card_attack_liansuolei_etching_d09',['造成3点伤害','随机翻开周围','1张背面牌']),('魔力共鸣','稀有 · 技能','border_card_skill_rare_r02','card_skill_moligongming_etching_d10',['造成4点伤害','抽1张牌到桌面','[共鸣] [消耗]'])]
composed=[]
for name,rarity,fid,aid,lines in cards:
 frame=asset(fid);spec=reg[fid]['spec'];w=spec['window'];o=Image.new('RGBA',frame.size)
 o.alpha_composite(ImageOps.fit(asset(aid),(w['width'],w['height']),method=Image.Resampling.LANCZOS),(w['x'],w['y']))
 o.putalpha(Image.open(R/spec['windowMask']).convert('L'));o.alpha_composite(frame)
 t=spec['textSafe']['title'];txt(o,t['x']+t['width']/2,t['y']+t['height']/2,name,76,anchor='mm')
 for j,line in enumerate(lines):txt(o,480,918+j*76,line,55,anchor='mm')
 composed.append(o)
for state in ['unselected','selected','claimed','skipped']:
 im=asset('bg_battle_empty_a01');im.alpha_composite(Image.new('RGBA',im.size,(0,0,0,150)));im.alpha_composite(panel(1640,940),(140,70))
 txt(im,960,138,'卡牌奖励',44,anchor='mm')
 txt(im,960,202,('选择一张加入牌库，也可以跳过本次卡牌奖励。' if state in ['unselected','selected'] else '本次卡牌奖励已结算。'),27,anchor='mm')
 if state in ['selected','unselected']:
  for i,card in enumerate(composed):
   x=300+i*470
   im.alpha_composite(card.resize((380,507),Image.Resampling.LANCZOS),(x,275))
   txt(im,x+190,823,cards[i][1],25,anchor='mm')
   if state=='selected' and i==1:
    ImageDraw.Draw(im).rounded_rectangle((x+10,268,x+370,786),radius=12,outline='#648891',width=5)
    txt(im,x+190,864,'已选中',24,'#355C67','mm')
  btn(im,360,922,320,'跳过奖励',secondary=True)
  btn(im,1240,922,320,'确认选择',disabled=state=='unselected')
 elif state=='claimed':
  im.alpha_composite(composed[1].resize((380,507),Image.Resampling.LANCZOS),(450,290))
  txt(im,1030,410,'已获得：连锁雷',36);txt(im,1030,480,'加入牌库 ×1',30,'#355C67');txt(im,1030,545,'牌库：10张 → 11张',27)
  txt(im,1030,612,'其余两张未获得',25,'#48575A');btn(im,1110,770,410,'继续旅途')
 else:
  txt(im,960,445,'已跳过卡牌奖励',40,anchor='mm');txt(im,960,525,'没有获得卡牌，牌库保持10张。',28,anchor='mm');btn(im,755,715,410,'继续旅途')
 im.convert('RGB').save(B/(state+'.png'))
(B/'assets.json').write_text(json.dumps({'status':'pending-review','productionEligible':False,'role':'card-reward-flow-reference','dependencies':deps,'states':['unselected','selected','claimed','skipped'],'note':'Rarity mix is illustrative, not one-per-rarity guarantee; no additional art generated.'},ensure_ascii=False,indent=2),encoding='utf-8')

