"""Annotated engineering figure from approved card art; no image repaint."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib
R=Path(__file__).resolve().parents[3];B=R/'ImageReview/batches/card-guide-w01';B.mkdir(parents=True,exist_ok=True)
reg={a['id']:a for a in json.loads((R/'docs/design/art-inventory/developer-asset-registry.json').read_text(encoding='utf-8'))['items']}
def asset(k):
 a=reg[k];assert a['productionEligible'];p=R/a['paths']['png'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'];return Image.open(p).convert('RGBA')
font=R/'Assets/UI/fonts/q01/SourceHanSansSC-Regular.otf';serif=R/'Assets/UI/fonts/q01/SourceHanSerifSC-Regular.otf'
def text(im,x,y,s,n=27,c='#252F32',title=False):ImageDraw.Draw(im).text((x,y),s,font=ImageFont.truetype(str(serif if title else font),n),fill=c)
def card(fid):
 f=asset(fid);a=reg[fid];w=a['spec']['window'];o=Image.new('RGBA',f.size)
 art=ImageOps.fit(asset('card_attack_daji_etching_b01'),(w['width'],w['height']),method=Image.Resampling.LANCZOS);o.alpha_composite(art,(w['x'],w['y']));o.putalpha(Image.open(R/a['spec']['windowMask']).convert('L'));o.alpha_composite(f)
 draw=ImageDraw.Draw(o);draw.text((507,206),'打击',font=ImageFont.truetype(str(serif),70),fill='#252F32',anchor='mm');draw.text((480,995),'造成6点伤害',font=ImageFont.truetype(str(font),48),fill='#252F32',anchor='mm');return o
im=Image.new('RGB',(2400,1800),'#E7E5D8');d=ImageDraw.Draw(im);d.rectangle((0,0,2400,145),fill='#252F32');text(im,65,25,'记忆勇者  /  卡牌美术接入指导',52,'#F1EEE2',True);text(im,68,96,'W01 · 基于正式C04/C05/R01/R02资产 · 源像素与屏幕像素分开计算',25,'#C2CECB')
text(im,65,175,'01  卡面结构与安全区',36,title=True);text(im,65,230,'示例：普通攻击「打击」；源画布960×1280',24)
c=card('border_card_attack_ornate_c04');c=c.resize((480,640),Image.Resampling.LANCZOS);im.paste(c,(85,300),c)
for box,col in [((235,153,545,107),'#8D3D35'),((156,300,649,496),'#355C67'),((180,858,600,280),'#8D3D35')]:
 x,y,w,h=box;d.rectangle((85+x/2,300+y/2,85+(x+w)/2,300+(y+h)/2),outline=col,width=3)
for yy,heading,lines in [(340,'标题安全区',['x235  y153  w545  h107','标题实时渲染，居中；禁止压住饰边']),(510,'插画窗口',['x156  y300  w649  h496','这是外接矩形，实际形状必须用专属mask']),(740,'描述安全区',['x180  y858  w600  h280','数值、词条来自数据；正文不能进入底饰'])]:
 d.line((570,yy+28,615,yy+28),fill='#648891',width=3);text(im,635,yy,heading,30)
 for j,s in enumerate(lines):text(im,635,yy+48+j*40,s,23)
text(im,85,967,'比例3:4；等比缩放；禁止九宫格',26)
d.line((1160,175,1160,1020),fill='#A7B0A8',width=2)
text(im,1220,175,'02  合成顺序与字体',36,title=True)
rules=[('Z0  插画 + 专属窗口遮罩','只裁插画；保留卡框自身透明外角。'),('Z1  正式卡框','按类型×稀有度选择，不能给普通框整体染色。'),('Z2  文字与数值','标题思源宋体Regular；正文思源黑体Regular。'),('Z3  状态 / 焦点','标记纸签、封锁与选中轮廓独立；不盖正文。')]
for i,(a,b) in enumerate(rules):text(im,1220,250+i*128,a,29);text(im,1220,299+i*128,b,25)
text(im,1220,790,'正文 #252F32    辅助 #48575A',28);text(im,1220,840,'焦点 #648891    损失 #8D3D35',28);text(im,1220,900,'s = 显示宽 / 960；坐标和安全区乘s',27);text(im,1220,947,'字体按屏幕字号渲染，不随大卡截图一起缩小。',25)
d.line((65,1040,2335,1040),fill='#A7B0A8',width=2);text(im,65,1070,'03  稀有度使用现成框',34,title=True)
for i,(fid,label) in enumerate([('border_card_attack_ornate_c04','普通 / 骨白'),('border_card_attack_uncommon_r01','罕见 / 钢蓝'),('border_card_attack_rare_r01','稀有 / 古金')]):
 a=card(fid).resize((180,240),Image.Resampling.LANCZOS);im.paste(a,(90+i*285,1140),a);text(im,90+i*285,1398,label,24)
text(im,65,1460,'攻击/技能/能力各3档，诅咒单独1框。',25);text(im,65,1505,'稀有度文字放详情/奖励标签，不只靠颜色识别。',23)
text(im,1000,1070,'04  小卡与详情采用不同文字密度',34,title=True)
for j,s in enumerate(['桌面144×192（1080p） / 96×128（720p），格心固定。','奖励示例380×507；详情按容器等比，完整卡文独立排版。','小卡标题/关键数值优先，完整词条放详情；不要强塞长文。','U01小卡13/11px仅为现有样例，尚非最低可读字号标准。','卡背统一：不能暴露类型、稀有度、病毒或隐藏词条。','已知标记背面只显示×N；封锁不能遮正文或禁用查看。','强化复用原插画，仅更新该实例文字；禁止虚构数值。']):text(im,1000,1145+j*55,s,25)
d.rectangle((65,1580,2335,1740),fill='#D5D9CD');text(im,90,1600,'验收：错框 / 错mask / 拉伸 / 裁主体 / 溢出 / 背面泄露 / 图集偏移 均不通过',29)
text(im,90,1650,'先核对ID与SHA256，再检查明暗底、144px实际尺寸、长卡名、多词条和强化态。',27)
text(im,90,1693,'本图为实现指导，不是运行时贴图；新排版建议需实机验证，未改变已确认资源。',24)
im.save(B/'card_art_guide_2400x1800.png')
frames=[]
for a in reg.values():
 if a['productionEligible'] and a['role']=='card-frame':
  spec=a['spec'];assert (R/spec['windowMask']).is_file();frames.append({'id':a['id'],'path':a['paths']['png'],'sourceSize':[a['width'],a['height']],'sha256':a['sha256'],'spec':spec})
(B/'frame-specs.json').write_text(json.dumps({'coordinateSpace':'source pixels; top-left origin','frames':frames,'runtimeTexture':False},ensure_ascii=False,indent=2),encoding='utf-8');print('Guide rendered; 10 frame specs verified.')
