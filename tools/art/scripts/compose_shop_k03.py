"""Compose approved assets over the imagegen shop plate; no repainting of assets."""
from pathlib import Path
import json, hashlib, shutil
from PIL import Image, ImageOps, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'ImageReview/batches/shop-k03'; B.mkdir(parents=True,exist_ok=True)
REG={a['id']:a for a in json.loads((ROOT/'docs/design/art-inventory/developer-asset-registry.json').read_text(encoding='utf-8'))['items']}
import sys, re
STATE=sys.argv[1] if len(sys.argv)>1 else "normal"
used={}
def asset(id):
    a=REG[id]; assert a['productionEligible'] and a['status']=='approved'
    p=ROOT/a['paths']['png']; assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
    used[id]={'path':a['paths']['png'],'sha256':a['sha256']}
    return Image.open(p).convert('RGBA')
def font(s): return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',s)
def text(im,xy,s,size=26,fill='#252F32',anchor='mm'):
    ImageDraw.Draw(im).text(xy,s,font=font(size),fill=fill,anchor=anchor)
src=B/'plate_source.png'
canvas=ImageOps.fit(Image.open(src).convert('RGBA'),(1920,1080),method=Image.Resampling.LANCZOS)
def button(x,y,w,label):
    price_match=re.search(r'(\d+) 金币',label)
    balance=30 if STATE=='poor' else 105 if STATE=='sold' else 150
    disabled=bool(price_match and int(price_match.group(1))>balance) or (STATE=='sold' and '45 金币' in label)
    if STATE=='sold' and '45 金币' in label: label='已售罄'
    elif disabled: label=label.replace('购买 · ','').replace('选择卡牌 · ','')+' · 不足'
    im=asset('btn_primary_disabled_b03' if disabled else 'btn_primary_normal_b03'); h=round(w*im.height/im.width)
    canvas.alpha_composite(im.resize((w,h),Image.Resampling.LANCZOS),(x,y))
    text(canvas,(x+w/2,y+h/2),label,20 if w<250 else 24,'#485356' if disabled else '#F1EEE2')
cards=[
 ('火球术','普通 · 攻击','border_card_attack_ornate_c04','card_attack_huoqiushu_etching_d07',['造成6点伤害'],45),
 ('连锁雷','罕见 · 攻击','border_card_attack_uncommon_r01','card_attack_liansuolei_etching_d09',['造成3点伤害','随机翻开周围','1张背面牌'],60),
 ('魔力共鸣','稀有 · 技能','border_card_skill_rare_r02','card_skill_moligongming_etching_d10',['造成4点伤害','抽1张牌到桌面','[共鸣] [消耗]'],75)]
for i,(name,rarity,fid,aid,lines,price) in enumerate(cards):
    frame=asset(fid); spec=REG[fid]['spec']; win=spec['window']
    art=ImageOps.fit(asset(aid),(win['width'],win['height']),method=Image.Resampling.LANCZOS)
    layer=Image.new('RGBA',frame.size); layer.alpha_composite(art,(win['x'],win['y']))
    maskpath=ROOT/spec['windowMask']; layer.putalpha(Image.open(maskpath).convert('L'))
    used[fid+'_mask']={'path':spec['windowMask'],'sha256':hashlib.sha256(maskpath.read_bytes()).hexdigest()}
    layer.alpha_composite(frame)
    title=spec['textSafe']['title']; text(layer,(title['x']+title['width']/2,title['y']+title['height']/2),name,76)
    for j,line in enumerate(lines): text(layer,(480,918+j*76),line,55)
    layer.save(B/f'card_{i+1}_review.png')
    x=188+330*i
    canvas.alpha_composite(layer.resize((350,467),Image.Resampling.LANCZOS),(x,275))
    text(canvas,(x+175,796),rarity,25)
    button(x+25,844,300,f'购买 · {price} 金币')
for y,aid,name,rarity,lines,price in [
 (234,'relic_memory_crystal_etching_e01','记忆水晶','普通',['战斗开始时，随机','揭示5张背面牌'],95),
 (455,'relic_chain_core_etching_e02','连锁核心','罕见',['配对成功时，随机','揭示1张背面牌'],130)]:
    canvas.alpha_composite(asset(aid).resize((160,160),Image.Resampling.LANCZOS),(1245,y+12))
    text(canvas,(1420,y+26),name,30,anchor='lm'); text(canvas,(1420,y+65),rarity,22,anchor='lm')
    for j,line in enumerate(lines): text(canvas,(1420,y+104+j*31),line,23,anchor='lm')
    button(1625,y+126,210,f'购买 · {price} 金币')
text(canvas,(1420,791),'选择并移除牌库中的一张卡牌',24,anchor='lm')
button(1500,847,320,'选择卡牌 · 75 金币')
text(canvas,(185,38),'生命 52 / 60',30,'#F1EEE2',anchor='lm')
text(canvas,(960,38),'商店',42,'#F1EEE2')
text(canvas,(1400,38),'金币 '+('30' if STATE=='poor' else '105' if STATE=='sold' else '150'),30,'#F1EEE2')
button(1610,14,250,'旅途详情')
text(canvas,(330,145),'卡牌',42)
text(canvas,(1345,145),'遗物',42)
text(canvas,(1380,680),'移除卡牌',38)
text(canvas,(340,1025),'离开后无法返回此商店',23,anchor='lm')
button(1530,992,300,'离开商店')
out=B/f'mockup_shop_k03_{STATE}.png'; canvas.convert('RGB').save(out)
(B/f'dependencies_{STATE}.json').write_text(json.dumps({'id':'mockup_shop_k03_'+STATE,'status':'pending-review','productionEligible':False,'role':'composite-reference-with-approved-assets','width':1920,'height':1080,'plateSourceResolution':list(Image.open(src).size),'dependencies':used,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Composed and verified {len(used)} approved dependencies.')
