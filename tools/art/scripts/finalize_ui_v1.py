"""Finalize UI documentation under user's explicit delegated approval; no art repaint."""
from pathlib import Path
import json,shutil,hashlib,re
R=Path(__file__).resolve().parents[3];U=R/'Assets/UI';E=R/'美术资源v1';A=R/'ImageReview/_archived/2026-10-21/ui-finalization'
def saveold(p):
 q=A/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True)
 if not q.exists():shutil.copy2(p,q)
def write(p,s):
 if p.exists():saveold(p)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def publish(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==src.read_bytes(),dst
 else:shutil.copy2(src,dst)
for folder,target,names in [('battle-u01','battle-u01',['normal.png','boss_phase3.png','assets.json','README.md']),('entry-h02','entry-h02',['mockup_loading_h02_1920x1080.png','mockup_main_menu_h02_1920x1080.png']),('campfire-l01','campfire-l01',['mockup_campfire_l01_1920x1080.png'])]:
 for n in names:publish(R/'ImageReview/batches'/folder/n,U/'mockups'/target/n)
header='> **视觉定稿，可按稿接入。** 2026-10-21统一状态。设计参考表示分层实现依据，不表示未批准；productionEligible=false仅禁止将组合图误作独立运行贴图。客户端实现与实机验收另行记录。\n\n'
folders=['map-i03','settings-j02','shop-k02','shop-k04','campfire-l03','event-m01','reward-n01','relic-reward-o01','v1-closure-p01','motion-r01','effects-t01','startup-v03','battle-u01']
replacements={
'状态：待用户审阅；':'状态：视觉定稿；','Q01候选字体':'Q01正式字体','状态：待审。':'状态：视觉定稿。','待审组合参考':'已定稿组合参考','T01 通用特效候选':'T01 通用特效定稿',
'后续K03拆分底图与状态仍待审。':'K03底图已正式收录，状态按shop-k03说明接入。',
'后续J03拆分面板仍待审，不能由本方向确认推定为已发布。':'J03独立面板已正式收录，按settings-j03说明接入。',
'后续拆分需使用正式Boss头像、独立节点和状态组件；旅途详情页尚未绘制。':'独立地图组件使用I04；旅途详情使用已定稿P01三页签。',
'事件M01仍待确认，本次制作不自动批准该批。':'事件M01已正式定稿。',
'2026-10-17，1920×1080，待审组合，不是客户端截图。':'2026-10-21，1920×1080，按用户授权定稿，不是客户端截图。',
'该新组合仍需用户确认，不能宣称已替代V05全部界面。':'该组合按本次授权定稿，替代V05战斗常态的旧贴图外观；暂停与详情继续采用V05结构。',
'2026-10-16，四张透明贴图，均待用户审阅，未发布至Assets/UI或美术资源v1。':'四张透明贴图均已批准并发布至Assets/UI及美术资源v1。',
'此次仍需审阅页面方向':'页面方向已定稿',
}
for folder in folders:
 p=U/'mockups'/folder/'README.md';s=p.read_text(encoding='utf-8')
 s=re.sub(r'^> .*下[文方].*覆盖。\s*','',s)
 for x,y in replacements.items():s=s.replace(x,y)
 if folder=='effects-t01':s=s.replace('Boss第三阶段仍未完成。','Boss三阶段静态图均已收录。')
 write(p,header+s)
 for name in ['assets.json','manifest.json']:
  p=U/'mockups'/folder/name
  if p.exists():
   d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(visualStatus='final',implementationStatus='not-verified',runtimeTexture=False)
   if folder=='battle-u01':d.update(status='approved-design-reference',productionEligible=False,approvalBasis='User delegated remaining UI finalization',finalizedOn='2026-10-21')
   write(p,json.dumps(d,ensure_ascii=False,indent=2))
for folder,spec in [('entry-h02','entry-h03/README.md'),('campfire-l01','campfire-l01/README.md')]:
 write(U/'mockups'/folder/'README.md',header+f'# 界面定稿\n\n本目录保存已确认布局稿，独立资源和接入说明见Assets/UI/{spec}。图中文字与数据由客户端独立渲染；旧字体形态以正式Q01字体替换后验收。\n')
rows=[('启动Logo','startup-v03','startup_cover_v03.png'),('主菜单','entry-h02','mockup_main_menu_h02_1920x1080.png'),('加载页','entry-h02','mockup_loading_h02_1920x1080.png'),('角色选择','v1-closure-p01','character_select.png'),('地图','map-i03','mockup_map_i03_1920x1080.png'),('战斗','battle-u01','normal.png'),('暂停手记/卡牌详情','battle-journal-v05','index.html'),('设置','settings-j02','mockup_settings_j02_1920x1080.png'),('商店','shop-k02','mockup_shop_k02_1920x1080.png'),('移除卡牌','shop-k04','selected.png'),('篝火','campfire-l01','mockup_campfire_l01_1920x1080.png'),('强化卡牌','campfire-l03','selected.png'),('事件选择与结果','event-m01','choices.png'),('战后卡牌奖励','reward-n01','selected.png'),('Boss遗物奖励','relic-reward-o01','selected.png'),('旅途详情','v1-closure-p01','journey_profile.png'),('胜利/失败结算','v1-closure-p01','victory.png')]
screens=[]
for title,folder,name in rows:
 p=U/'mockups'/folder/name;assert p.is_file(),p
 screens.append(dict(name=title,visualStatus='final',implementationStatus='not-verified',runtimeTexture=False,reference=p.relative_to(U).as_posix(),clientSpec=f'mockups/{folder}/README.md',finalizedOn='2026-10-21'))
write(U/'integration-v1/ui-finalization.json',json.dumps(dict(asOf='2026-10-21',pathBase='Assets/UI or art package root',authorization='用户：检查类似UI，帮我定了；继续未完成任务',screens=screens,additionalFinalBatches=['motion-r01','effects-t01'],pendingEngineering=['非16:9适配','长列表/排序菜单/悬浮说明','Boss实景pivot','启动失败分支','目标引擎字体与动效验证']),ensure_ascii=False,indent=2))
lines=['# v1 UI视觉定稿清单','', '2026-10-21。共17类界面全部标记视觉定稿，另有2批动效/特效表现规范已定稿。用户授权本次统一定稿，U01战斗常态采用正式资源组合，暂停与详情沿用V05结构。没有重绘或修改玩法。','', '**设计参考 ≠ 未定稿。** visualStatus=final表示可按稿实现；runtimeTexture=false/productionEligible=false表示组合图不能直接作为独立贴图导入；implementationStatus=not-verified表示尚无客户端实机验收证据。不要因后两项再次阻塞视觉接入。','', '|界面|正式来源（Assets/UI根目录）|状态|','|---|---|---|']
for a in screens:lines.append(f"|{a['name']}|{a['reference']}|视觉定稿，可接入|")
lines+=['','交付包来源路径请通过设计参考索引中的references与文件清单查找；组合参考副本位于设计参考/相应ID，不能直接把本表仓库路径拼到交付包中。','', '未绘制的长列表、排序展开、溢出、非16:9布局、启动失败分支仍须工程补充和截图验证；这不撤销已有页面定稿。不得删功能或声称未覆盖分支已像素验收。启动Logo仍为整图方向，独立拆分尚未提供。','', '历史草稿、被否决L02、旧启动V01/V02、旧卡框和I04占位详情不在本次批准范围。U01卡面小字与生命填充等工程约束以battle-replacement.md为准，不能照抄组装脚本作为游戏逻辑。']
write(U/'integration-v1/ui-finalization.md','\n'.join(lines)+'\n')
# Synchronize only tracked exports whose old hashes still match; retain backups.
registry=json.loads((R/'docs/design/art-inventory/developer-asset-registry.json').read_text(encoding='utf-8'))
oldhash={a['path']:a['sha256'] for a in json.loads((E/'设计参考索引.json').read_text(encoding='utf-8'))['files']}
for ref in registry['references']:
 if not ref.get('exportReference'):continue
 srcs=list((R/ref['bundleDirectory']).rglob('*')) if ref.get('bundleDirectory') else [R/p for p in [ref['path'],ref['clientSpec']]+ref.get('additionalPaths',[])]
 for src in srcs:
  if not src.is_file():continue
  rel=src.relative_to(R/ref['bundleDirectory']) if ref.get('bundleDirectory') else src.name
  dst=E/'设计参考'/ref['id']/rel
  if dst.exists() and dst.read_bytes()!=src.read_bytes():
   assert hashlib.sha256(dst.read_bytes()).hexdigest()==oldhash[dst.relative_to(E).as_posix()],dst
   saveold(dst);shutil.copy2(src,dst)
print(f'Finalized {len(screens)} screen families and 2 effect-reference batches; backed up changed documentation.')
