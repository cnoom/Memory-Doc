"""Campfire preview: generated art plate plus approved B03 and independent text."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageOps,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]; B=R/'ImageReview/batches/campfire-l01';B.mkdir(parents=True,exist_ok=True)
src=Image.open(B/'source.png');im=ImageOps.fit(src.convert('RGBA'),(1920,1080),method=Image.Resampling.LANCZOS)
im.save(R/'ImageReview/backgrounds/bg_campfire_l01.png')
reg={a['id']:a for a in json.loads((R/'docs/design/art-inventory/developer-asset-registry.json').read_text(encoding='utf-8'))['items']}
def txt(x,y,s,size=28,color='#252F32',anchor='lm'):
 ImageDraw.Draw(im).text((x,y),s,font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size),fill=color,anchor=anchor)
def btn(x,y,w,s):
 a=reg['btn_primary_normal_b03'];p=R/a['paths']['png'];assert a['productionEligible'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'];h=round(w*112/640);im.alpha_composite(Image.open(p).convert('RGBA').resize((w,h),Image.Resampling.LANCZOS),(x,y));txt(x+w/2,y+h/2,s,26,'#F1EEE2','mm')
txt(160,36,'生命 34 / 60',30,'#F1EEE2');txt(960,36,'篝火',42,'#F1EEE2','mm');btn(1570,12,260,'旅途详情')
txt(1150,266,'休息',42);txt(1150,326,'回复最大生命的30%',29);txt(1150,376,'本次回复18点生命：34 / 60 → 52 / 60',26);btn(1320,426,350,'休息')
txt(1150,632,'升级卡牌',42);txt(1150,695,'选择牌库中的一张卡牌进行强化',28);txt(1150,746,'每张卡牌最多升级一次',25,'#48575A');btn(1320,796,350,'选择卡牌')
txt(960,1014,'休息与升级，选择一项完成本次篝火。',28,anchor='mm')
im.convert('RGB').save(B/'mockup_campfire_l01_1920x1080.png')
out=R/'ImageReview/backgrounds/bg_campfire_l01.png'
(B/'assets.json').write_text(json.dumps({'batch':'campfire-l01','assets':[{'id':'bg_campfire_l01','png':'backgrounds/bg_campfire_l01.png','width':1920,'height':1080,'sourceResolution':list(src.size),'native1080p':False,'status':'pending-review','productionEligible':False,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}],'reference':'mockup_campfire_l01_1920x1080.png','button':'Assets/UI/buttons/btn_primary_normal_b03.png'},ensure_ascii=False,indent=2),encoding='utf-8')
