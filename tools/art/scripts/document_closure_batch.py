"""Document and validate pending closure previews; does not publish."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]
B=R/'ImageReview/batches'
colors='正文 #252F32；深色按钮文字 #F1EEE2；辅助说明 #48575A；禁用文字 #485356；选中描边 #648891；强调 #355C67；失败/损失 #8D3D35。'
texts={
'v1-closure-p01':f'''# P01 首版静态界面补充

状态：待用户审阅；10张1920×1080组合参考，不是可直接铺满运行时的独立背景。复用已确认的卡图、卡框、角色、遗物、插画及B03/A03组件。字体采用Q01候选字体。

## 内容与布局

|文件|内容|
|---|---|
|victory / defeat|胜败结算：章节、击败敌人、累计获得金币、剩余生命四项|
|character_select|学者选择；初始60生命、10张卡，只有已定义角色|
|journey_profile|个人信息、被动；详情页内部展示金币和卡组数量|
|journey_cards / journey_cards_empty|当前卡组、分类筛选及空结果|
|journey_relics / journey_relics_empty|已持有遗物及空状态|
|event_card_result / event_relic_result|事件获得卡牌/遗物结果|

坐标基于1920×1080：主面板(140,90,1640,920)，页标题(220,160)，详情页签从(230,225)开始，每项宽300，间隔40；返回按钮(1450,135,250)。卡组列表从(230,465)开始，单卡220×293，横向步长245；右侧详情从(1310,485)开始。结算按钮位于y=880；事件继续按钮(1240,870,380)。文字由客户端独立渲染。

## 字体与颜色

标题使用思源宋体Regular，正文/按钮使用思源黑体Regular。页面标题42px，主要状态64px，正文25–29px，按钮24px，辅助文字22–23px；最终字号以实际窗口缩放验证。{colors}

## 规则

初始牌库：打击4、格挡4、笔记1、读书笔记1；数量为库内数量，不是战斗复制后的牌数。相同名称但强化/附加词条不同应分组。结算金币为旅途累计获得量。示例数值不作为新规则。事件卡牌结果示例未触发学者25%附加共鸣；实际必须由结算结果驱动。空遗物页是独立测试状态，不与两件遗物的个人信息样例绑定。

本批布局尚未提供排序展开、滚动长列表和所有悬浮提示状态；对应客户端需要复用现有控件完成。来源见assets.json；重建脚本tools/art/scripts/compose_v1_closure_p01.py。
''',
'fonts-q01':'''# Q01 字体候选交付

状态：待审；尚未发布到Assets/UI或美术资源v1。

思源黑体SC Regular用于正文、按钮与数字，思源宋体SC Regular用于标题。两个OTF来自Adobe官方GitHub仓库；精确下载URL、固定提交、文件大小和SHA256见manifest.json。对应LICENSE文件必须随字体保留。按SIL Open Font License使用；修改或子集化时需重新核对保留字体名和许可要求。

未安装到系统，预览脚本直接加载。已用Pillow检查中文、数字、箭头等样本文字可加载；未声称完整Unicode覆盖。客户端应按实际文案建立字库，验证中文标点、缺字回退和字体图集内存。此批仅Regular字重，不能假称包含Bold字体文件。
''',
'ui-icons-q02':f'''# Q02 补充图标

状态：待审。24个独立图标，每个含192×192透明PNG及SVG；完整ID、用途、哈希见assets.json。资源位于ImageReview/icons。overview.png是组合审阅图，不是运行时图集。

涵盖翻开/翻回/丢弃/离场/入场、消耗/移除/顽固/隐秘/迅速、共鸣/剑/盾、换位/污染/封锁，以及强化/排序/筛选/详情/牌库/金币/关闭/返回。

原色#252F32，线宽9/192，透明背景。建议32–48px显示；暗底改用#F1EEE2的独立着色，保持同一透明轮廓。首次出现的词条需要文字或悬浮说明，不能依赖形状独自传达规则。{colors}

属于原生SVG功能符号，配合现有木刻插画，不替换正式卡牌、遗物插画。已检查尺寸、透明通道和SVG/XML解析；最终小尺寸清晰度仍需客户端验证。
''',
'motion-r01':'''# R01 首版动效参考

状态：待审。index.html为可播放设计参考，不是游戏实现；以项目根目录为HTTP服务根目录打开，或直接用浏览器打开HTML。依赖相对路径下正式资源、K02卡面组合及Q01字体，不能单独拷走HTML。

|效果|建议时长|
|---|---|
|翻牌|300ms，90度切面|
|配对成功|400ms，原格心淡出|
|不匹配|220ms，保持正面|
|牌区流转|350ms，终点绑定真实锚点|
|换位|500ms，只移动不翻开|
|受击 / 飘字|280 / 1000ms|
|攻击 / 待机 / 死亡|380 / 1800 / 500ms|
|封锁盖印|280ms|
|行动条临界|300ms，末三格错峰100ms|
|Boss阶段提示|500ms|
|遗物触发|400ms，最大1.08倍|

每项手动播放，可重复触发；支持减少动态与系统prefers-reduced-motion。游戏规则、时序打断、暂停恢复、伤害与治疗实际数值由客户端负责。Boss只使用基础立绘加提示，不是阶段变体。没有角色逐帧动画、骨骼动画、篝火火焰序列或粒子贴图。

浏览器已检查全部图片加载并试播翻牌。其余效果参数可见CSS，仍需用户审阅及引擎内时序验证。字体颜色：正文#252F32、深底#F1EEE2、受击#8D3D35、治疗/焦点#648891。
'''}
for folder,txt in texts.items():(B/folder/'README.md').write_text(txt,encoding='utf-8')
p=B/'v1-closure-p01'; data=json.loads((p/'assets.json').read_text(encoding='utf-8'));font=ImageFont.truetype(str(B/'fonts-q01/SourceHanSansSC-Regular.otf'),22)
labels=['胜利结算','失败结算','学者选择','个人信息','当前卡组','卡组筛选空状态','遗物详情','遗物空状态','事件获得卡牌','事件获得遗物']
sheet=Image.new('RGB',(1280,2000),'#e5e3d5');d=ImageDraw.Draw(sheet)
for i,(name,label) in enumerate(zip(data['outputs'],labels)):
 im=Image.open(p/(name+'.png'));assert im.size==(1920,1080)
 x=(i%2)*640;y=(i//2)*400;sheet.paste(im.resize((640,360),Image.Resampling.LANCZOS),(x,y));d.text((x+16,y+365),label,font=font,fill='#252F32')
sheet.save(p/'overview.jpg',quality=92)
print('Documented four batches; checked ten 1920x1080 previews.')
