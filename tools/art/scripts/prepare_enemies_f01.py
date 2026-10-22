import json, hashlib, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[3]
folder = ROOT/'ImageReview/batches/enemies-f01'
source = Path('C:/Users/Administrator/.codex/generated_images/01a11676-0a6c-7dd3-b7c7-20ab00b8e9c9')
ids = ['2ca83fc4-39e1-4cc2-b57d-0014a5394ae8','d12fee33-4756-495c-9e82-a7d5c11e50ac','13c4e64e-dcc2-4a23-bf7f-328bc89e5ea1','c1241006-52fa-4f4b-b5a4-f65f58fd7829','ea0e210a-5217-4f30-bc90-c159862545cc','b2bd2303-1858-489a-a9fa-f2c7507ed0dc']
prompts = json.loads((folder/'final-prompts.json').read_text(encoding='utf-8-sig'))
canvas = Image.new('RGB',(1200,1080),'#e7e0d0')
draw = ImageDraw.Draw(canvas)
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
draw.text((24,14),'F01 · 六种敌人静态立绘候选',fill='#252c2d',font=font)
assets=[]
for i,(p,uid) in enumerate(zip(prompts,ids)):
    aid='enemy_'+p['slug']+'_etching_f01'
    dest=ROOT/'ImageReview/enemies'/f'{aid}.png'
    dest.parent.mkdir(exist_ok=True)
    shutil.copy2(source/f'exec-{uid}.png',dest)
    im=Image.open(dest).convert('RGBA')
    alpha=im.getchannel('A'); lo,hi=alpha.getextrema()
    assert lo==0 and hi>=254
    x=(i%3)*400; y=55+(i//3)*505
    thumb=im.copy();thumb.thumbnail((310,390),Image.Resampling.LANCZOS)
    canvas.paste(thumb,(x+(400-thumb.width)//2,y),thumb)
    small=im.copy();small.thumbnail((70,90),Image.Resampling.LANCZOS)
    canvas.paste(small,(x+300,y+390),small)
    draw.text((x+20,y+410),p['name'],fill='#252c2d',font=font)
    assets.append(dict(id=aid,name=p['name'],category='enemies',png='enemies/'+dest.name,width=im.width,height=im.height,status='pending-review',productionEligible=False,sourceFile=f'exec-{uid}.png',alphaRange=[lo,hi],sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
canvas.save(folder/'review.png')
(folder/'assets.json').write_text(json.dumps(dict(batch='enemies-f01',assets=assets),ensure_ascii=False,indent=2),encoding='utf-8')
print('6 candidate PNGs copied; alpha and source hashes recorded.')
