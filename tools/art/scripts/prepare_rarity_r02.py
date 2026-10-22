"""Reuse verified frame export/alpha pipeline for four R02 variants."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
s=(ROOT/'tools/art/scripts/prepare_rarity_r01.cjs').read_text(encoding='utf-8')
s=s.replace('card-rarity-r01','card-rarity-r02')
s=s.replace("for(const [i,rarity,name]of [[0,'common','普通 · 骨白'],[1,'uncommon','罕见 · 钢蓝'],[2,'rare','稀有 · 古金']]){", "for(const [i,type,rarity,name]of [[0,'skill','uncommon','技能 · 罕见'],[1,'skill','rare','技能 · 稀有'],[2,'ability','uncommon','能力 · 罕见'],[3,'ability','rare','能力 · 稀有']]){")
s=s.replace('border_card_attack_${rarity}_r01','border_card_${type}_${rarity}_r02')
s=s.replace("rarity+'.png'","type+'-'+rarity+'.png'")
s=s.replace("rarity+'-window-mask.png'","type+'-'+rarity+'-window-mask.png'")
s=s.replace("rarity+'-framed.png'","type+'-'+rarity+'-framed.png'")
s=s.replace('rarity,width:W','rarity,type,width:W')
s=s.replace("'Assets/UI/cards/card_attack_kaoju_etching_d01.png'","type==='skill'?'Assets/UI/cards/card_skill_sudu_etching_d01.png':'Assets/UI/cards/card_ability_quanshenguanzhu_etching_d01.png'")
s=s.replace('30+i*420','25+i*330').replace('1290','1340')
s=s.replace('R01 · 稀有度卡框对照','R02 · 技能与能力稀有度卡框')
s=s.replace('红色带仍代表攻击类型 · 同一插画仅作对比，不改变考据的普通稀有度 · 下排144 / 96像素','类型色带与稀有度边框分开 · 插画仅作对比，不改变实际稀有度 · 下排144 / 96像素')
s=s.replace("reused:['border_card_attack_ornate_c04']","reused:[]")
(ROOT/'tools/art/scripts/prepare_rarity_r02.cjs').write_text(s,encoding='utf-8')
