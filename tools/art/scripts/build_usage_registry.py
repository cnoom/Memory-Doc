"""Normalize art paths and record measured metadata; never publishes assets."""
import json, hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/design/art-inventory/developer-asset-registry.json'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
items=[]
approved_b01_cards={'card_attack_daji_etching_b01','card_skill_gedang_etching_b01','card_attack_biji_etching_b01'}
approved_controls={f'btn_{kind}_{state}_a01' for kind in ['menu','danger'] for state in ['normal','hover','pressed','disabled']} | {f'{s}_a01' for s in ['toggle_off','toggle_on','check_off','check_on','slider_track','slider_fill','slider_thumb']} | {f'focus_{s}_a02' for s in ['button','toggle','check','slider']}
approved_b01_actors={'portrait_scholar_etching_b01','enemy_chaos_slime_etching_b01','enemy_training_dummy_etching_b01','enemy_goblin_etching_b01'}
approved_journal={f'journal_{s}_a01' for s in ['cover','page_edges','page_left','page_right','spine','binding','ribbon','fold']} | {f'decor_{s}_a02' for s in ['chapter_tab','loose_leaf','portrait_mount','paper_tape','stamp_frame','page_flourish','pressed_ring','margin_ticks','foreedge']}
approved_b01_icons={f'icon_{group}_{name}_etching_b01' for group,names in {'type':['attack','skill','ability','curse'],'status':['burn','freeze','poison','armor','vulnerable','weak'],'intent':['attack','charge','defend','special','berserk']}.items() for name in names}
def entry(a,base,status,batch,role):
    paths={k:f'{base}/{Path(a[k]).name}' if batch=='B03' else f'{base}/{a[k]}' for k in ['png','svg'] if k in a}
    for p in paths.values():assert (ROOT/p).is_file(),p
    im=Image.open(ROOT/paths['png']);alpha=im.getchannel('A').getextrema() if 'A' in im.getbands() else None
    items.append(dict(id=a['id'],batch=batch,status=status,role=role,productionEligible=status=='approved',paths=paths,width=im.width,height=im.height,hasAlpha=alpha is not None,alphaRange=alpha,sha256=hashlib.sha256((ROOT/paths['png']).read_bytes()).hexdigest(),spec={k:a[k] for k in ['slice','sliceOrder','display','window','textSafe','scaling','anchor','z','state','type','textColor'] if k in a},requiresEngineValidation=True))
for a in read('Assets/UI/ui-b03-manifest.json')['assets']:
    entry(a,'Assets/UI/'+a['publishedCategory'],'approved','B03','component')
for id,folder,role in [('bg_battle_etching_textless_v02','backgrounds','composite-background-with-actors'),('card_attack_dushubiji_illustration_v02','cards','card-illustration')]:entry({'id':id,'png':id+'.png'},'Assets/UI/'+folder,'approved','V02',role)
for batch,source in [('B01','ImageReview/batches/etching-b01/assets.json'),('B02','ImageReview/batches/ui-b02/assets.json'),('A01','ImageReview/batches/foundation-a01/assets.json'),('A02','ImageReview/batches/core-a02/assets.json')]:
    for a in read(source)['assets']:
        if batch=='B01' and a['id'] in approved_b01_actors:
            entry(a,'Assets/UI','approved',batch,'static-character-portrait' if a['id'].startswith('portrait_') else 'static-enemy-illustration')
            items[-1]['approvalNote']='2026-10-07: user approved the displayed scholar, chaos slime, training dummy and goblin static illustrations with 可以; animation assets are outside this approval.'
        elif batch=='B01' and a['id'] in approved_b01_icons:
            entry(a,'Assets/UI','approved',batch,'battle-icon')
            items[-1]['approvalNote']='2026-10-07: user approved the displayed 15 type/status/intent icons with 可以; PNG and SVG published with unchanged content.'
        elif batch=='B01' and a['id'] in approved_b01_cards:
            entry(a,'Assets/UI','approved',batch,'card-illustration')
            items[-1]['approvalNote']='2026-10-07: user approved the three standalone illustrations with 可以; opaque bone-white background intended for card illustration window, not transparent object use.'
        elif batch=='A01' and a['id']=='bg_battle_empty_a01':
            entry(a,'Assets/UI','approved',batch,'empty-battle-background')
            items[-1]['approvalNote']='2026-10-07: user approved current 1920x1080 empty background after disclosure of smaller resampled source; other A01/A02 assets remain pending.'
            items[-1]['provenance']={'generatedResolution':[1672,941],'deliveredResolution':[1920,1080],'method':'Lanczos3 cover resampling','native1080p':False}
        elif batch in {'A01','A02'} and a['id'] in approved_journal:
            entry(a,'Assets/UI','approved',batch,'journal-structure' if batch=='A01' else 'journal-ornament')
            items[-1]['approvalNote']='2026-10-07: user approved journal structure and ornaments; minor wording issues explicitly deferred. Buttons, controls and HUD are not covered.'
        elif batch in {'A01','A02'} and a['id'] in approved_controls:
            entry(a,'Assets/UI','approved',batch,'focus-overlay' if batch=='A02' else 'button' if a['id'].startswith('btn_') else 'settings-control')
            items[-1]['approvalNote']='2026-10-07: user approved all 19 displayed button/control/focus assets with 可以. Runtime interaction still needs engine implementation.'
        else:
            entry(a,'ImageReview','pending-review',batch,'legacy-style-candidate' if batch=='B02' else 'candidate')
for a in items:
    if a['batch'] in {'A01','A02'} and not a['productionEligible'] and any(p.startswith('ImageReview/'+category+'/') for p in a['paths'].values() for category in ['panels','bars']):
        a['status']='superseded'
        a['replacedBy']=a['id'].rsplit('_',1)[0]+'_a03'
        a['approvalNote']='2026-10-07: replaced by explicitly approved A03 assets; retained only as historical preview.'
    if a['batch']=='B01' and (a['id'].startswith('border_card_') or a['id'].startswith('cardback_')):
        a['status']='needs-revision'
        a['approvalNote']='2026-10-07: user found B01/C01 too plain and approved C02 ornament density as direction only; independent replacements await review.'
for a in read('ImageReview/batches/card-refinement-c01/assets.json')['assets']:
    entry(a,'ImageReview','needs-revision','C01','superseded-direction-candidate')
assert len({a['id'] for a in items})==len(items)
for a in read('ImageReview/batches/panel-refinement-a03/assets.json')['assets']:
    entry(a,'Assets/UI','approved','A03','panel-hud-bar')
    items[-1]['replaces']=a['replaces']
    items[-1]['approvalNote']='2026-10-07: user approved A03 refinement with 可以了. Use updated textSafe/slice metadata; target-engine layout validation remains required.'
assert len({a['id'] for a in items})==len(items)
data=dict(schemaVersion=1,asOf='2026-09-26',pathBase='repository-root',approvalPolicy='Snapshot only: current explicit user instructions supersede this registry; file presence is not approval.',items=items,references=[dict(id='V05-approved-design',path='Assets/UI/mockups/battle-journal-v05/index.html',role='approved-design-reference-not-runtime-code'),dict(id='A01-layered-preview',path='ImageReview/mockups/battle-foundation-a01/index.html',role='pending-layered-reference')],incompatibleSets=[dict(a='bg_battle_etching_textless_v02',b=['portrait_scholar_etching_b01','enemy_chaos_slime_etching_b01'],reason='Background already contains both actors; do not overlay independent actors on it.')])
for a in read('ImageReview/batches/card-production-c03/assets.json')['assets']:
    is_back=a['category']=='cardbacks'
    entry(a,'Assets/UI' if is_back else 'ImageReview','approved' if is_back else 'needs-revision','C03','universal-card-back' if is_back else 'card-frame')
    items[-1]['spec'].update({k:a[k] for k in ['windowMask','sourceResolution','exportMethod','universal'] if k in a})
    items[-1]['approvalNote']='2026-10-11: user explicitly approved universal C03 back with 卡背也没问题.'
    if a['category']=='cardframes':
        items[-1]['status']='needs-revision'
        items[-1]['approvalNote']='2026-10-11: user requested a larger description area and smaller bottom ornament; use approved C04 replacement.'
for a in read('ImageReview/batches/card-production-c04/assets.json')['assets']:
    entry(a,'Assets/UI','approved','C04','card-frame')
    items[-1]['spec'].update({k:a[k] for k in ['windowMask','sourceResolution','exportMethod'] if k in a})
    items[-1]['spec']['windowMask']='Assets/UI/cardframes/border_card_attack_ornate_c04_window_mask.png'
    items[-1]['approvalNote']='2026-10-11: user approved enlarged description area with 可以了. C04 attack frame approved.'
assert len({a['id'] for a in items})==len(items)
data['asOf']='2026-10-13'
for a in read('ImageReview/batches/relics-e02/assets.json')['assets']:
    entry(a,'Assets/UI','approved','E02','relic-icon')
    items[-1]['approvalNote']='2026-10-13: user confirmed publication of the fifteen displayed E02 relic icons with 继续吧.'
    items[-1]['spec'].update({'rarity':a['rarity'],'sourceResolution':a['sourceResolution'],'displaySizes':[48,64]})
    if a['name']=='思维导图': items[-1]['spec']['gameplayAvailability']='suspended-per-design-07-v1.31; art completion does not restore availability'
for a in read('ImageReview/batches/relics-e01/assets.json')['assets']:
    entry(a,'Assets/UI','approved','E01','relic-icon')
    items[-1]['approvalNote']='2026-10-13: user approved first four relic icons with 继续吧，没什么问题.'
    items[-1]['spec'].update({'rarity':a['rarity'],'sourceResolution':a['sourceResolution'],'displaySizes':[48,64]})
for a in read('ImageReview/batches/card-illustrations-d08/assets.json')['assets']:
    entry(a,'Assets/UI','approved','D08','card-illustration')
    items[-1]['spec']['rarity']='common'
    items[-1]['approvalNote']='2026-10-11: published after agent review under standing authorization for small card illustrations; not individually user-reviewed. Scout is a card illustration, not a standalone character portrait.'
for a in read('ImageReview/batches/card-illustrations-d09/assets.json')['assets']:
    entry(a,'Assets/UI','approved','D09','card-illustration')
    items[-1]['spec']['rarity']='uncommon'
    items[-1]['approvalNote']='2026-10-11: published after agent review under standing batch authorization for small card illustrations; not individually user-reviewed.'
for a in read('ImageReview/batches/card-illustrations-d10/assets.json')['assets']:
    entry(a,'Assets/UI','approved','D10','card-illustration')
    if a['type']=='skill': items[-1]['spec']['rarity']='rare'
    items[-1]['approvalNote']='2026-10-13: published after agent review under standing batch authorization for small card illustrations; not individually user-reviewed.'
for a in read('ImageReview/batches/card-illustrations-d07/assets.json')['assets']:
    entry(a,'Assets/UI','approved','D07','card-illustration')
    items[-1]['spec']['rarity']='common'
    items[-1]['approvalNote']='2026-10-11: published after agent review under standing batch authorization for small card illustrations; not individually user-reviewed.'
for a in read('ImageReview/batches/card-illustrations-d06/assets.json')['assets']:
    entry(a,'Assets/UI','approved','D06','card-illustration')
    items[-1]['approvalNote']='2026-10-11: published after agent review under standing batch authorization for small card illustrations; not individually user-reviewed. Curse cards use C05 without rarity variants.'
for a in read('ImageReview/batches/card-illustrations-d05/assets.json')['assets']:
    entry(a,'Assets/UI','approved','D05','card-illustration')
    items[-1]['spec']['rarity']='rare'
    items[-1]['approvalNote']='2026-10-11: published after agent review under standing batch authorization for small card illustrations; not individually user-reviewed.'
for a in read('ImageReview/batches/card-illustrations-d04/assets.json')['assets']:
    entry(a,'Assets/UI','approved','D04','card-illustration')
    items[-1]['spec']['rarity']='uncommon'
    items[-1]['approvalNote']='2026-10-11: published after agent review under standing batch authorization for small card illustrations; not individually user-reviewed.'
for a in read('ImageReview/batches/card-rarity-r02/assets.json')['assets']:
    entry(a,'Assets/UI','approved','R02','card-frame')
    items[-1]['spec'].update({k:a[k] for k in ['rarity','windowMask'] if k in a})
    items[-1]['spec']['windowMask']='Assets/UI/cardframes/'+a['id']+'_window_mask.png'
    assert (ROOT/items[-1]['spec']['windowMask']).is_file()
    items[-1]['approvalNote']='2026-10-11: user approved all four R02 skill/ability uncommon and rare frames with 可以.'
for a in read('ImageReview/batches/card-rarity-r01/assets.json')['assets']:
    entry(a,'Assets/UI','approved','R01','card-frame')
    items[-1]['spec'].update({k:a[k] for k in ['rarity','windowMask'] if k in a})
    items[-1]['spec']['windowMask']='Assets/UI/cardframes/'+a['id']+'_window_mask.png'
    items[-1]['approvalNote']='User approved R01 uncommon/rare attack frames with 可以 on 2026-10-11.'
for a in read('ImageReview/batches/card-illustrations-d03/assets.json')['assets']:
    entry(a,'Assets/UI','approved','D03','card-illustration')
    items[-1]['approvalNote']='2026-10-11: published after agent visual review under standing user authorization for batch small card illustrations, without per-batch confirmation.'
for a in read('ImageReview/batches/card-illustrations-d02/assets.json')['assets']:
    entry(a,'Assets/UI','approved','D02','card-illustration')
    items[-1]['approvalNote']='2026-10-11: published after agent review under explicit standing authorization: 这种icon可以批量生成无需向我确认.'
for a in read('ImageReview/batches/card-illustrations-d01/assets.json')['assets']:
    entry(a,'Assets/UI','approved','D01','card-illustration')
    items[-1]['approvalNote']='2026-10-11: user approved 考据、速读、全神贯注 standalone illustrations with 可以、. Opaque bone-white paper; framed previews are not runtime assets.'
for a in read('ImageReview/batches/card-production-c05/assets.json')['assets']:
    entry(a,'Assets/UI','approved','C05','card-frame')
    items[-1]['spec'].update({k:a[k] for k in ['windowMask','sourceResolution'] if k in a})
    items[-1]['spec']['windowMask']='Assets/UI/cardframes/'+a['id']+'_window_mask.png'
    assert (ROOT/items[-1]['spec']['windowMask']).is_file()
    items[-1]['approvalNote']='2026-10-11: user approved the displayed C05 skill, ability and curse frames with 可以.'
data['references'].append(dict(id='C02-approved-card-direction',path='Assets/UI/mockups/card_face_back_ornate_c02.png',role='approved-direction-reference-not-runtime-asset',approvalScope='Card face/back ornament density and visual direction only; standalone layers and other card types await production and review.',approvalQuote='足够了',approvedOn='2026-10-07'))
for a in read('ImageReview/batches/enemies-f01/assets.json')['assets']:
    entry(a,'Assets/UI','approved','F01','static-enemy-illustration')
    items[-1]['approvalNote']='2026-10-13: user approved all six displayed F01 enemy static illustrations with 可以; animation and boss phase variants excluded.'
    items[-1]['spec']['scope']='Static full-body only; animations excluded. Memory devourer is baseline form; phase variants excluded.'
for a in read('ImageReview/batches/events-g01/assets.json')['assets']:
    entry(a,'Assets/UI','approved','G01','event-illustration')
    items[-1]['approvalNote']='2026-10-13: user approved all ten displayed G01 event illustrations with 可以.'
    items[-1]['spec']['eventId']=a['eventId']
    items[-1]['spec']['scope']='Opaque narrative illustration; UI text and choices rendered separately.'
for a in read('ImageReview/batches/entry-h03/assets.json')['assets']:
    entry(a,'Assets/UI','approved','H03','entry-screen-background')
    items[-1]['approvalNote']='2026-10-14: user confirmed H03 backgrounds and client handoff with 确认.'
    items[-1]['spec'].update({'native1080p':False,'sourceResolution':a['sourceResolution'],'clientSpec':'Assets/UI/entry-h03/README.md','clientTokens':'Assets/UI/entry-h03/client-tokens.json'})
data['references'].append(dict(id='I03-approved-map-direction',path='Assets/UI/mockups/map-i03/mockup_map_i03_1920x1080.png',clientSpec='Assets/UI/mockups/map-i03/README.md',role='approved-direction-reference-not-runtime-asset',approvalQuote='可以了',approvedOn='2026-10-14',exportReference=True,productionEligible=False))
for a in read('ImageReview/batches/map-i04/assets.json')['assets']:
    entry(a,'Assets/UI','approved','I04','map-background' if a['id']=='bg_map_i04' else 'map-component')
    items[-1]['approvalNote']='2026-10-15: user explicitly approved publication of all fourteen I04 standalone map assets.'
    if a['id']=='bg_map_i04': items[-1]['spec'].update({'sourceResolution':a['sourceResolution'],'native1080p':False})
    items[-1]['spec']['clientSpec']='Assets/UI/map-i04/README.md'
data['asOf']='2026-10-14'
data['references'].append(dict(id='J02-approved-settings-direction',path='Assets/UI/mockups/settings-j02/mockup_settings_j02_1920x1080.png',clientSpec='Assets/UI/mockups/settings-j02/README.md',role='approved-direction-reference-not-runtime-asset',approvalQuote='继续吧',approvedOn='2026-10-14',exportReference=True,productionEligible=False))
for a in read('ImageReview/batches/settings-j03/assets.json')['assets']:
    entry(a,'Assets/UI','approved','J03','settings-panel')
    items[-1]['approvalNote']='2026-10-14: user approved J03 settings panel with 可以.'
    items[-1]['spec'].update({'clientSpec':'Assets/UI/settings-j03/README.md','clientLayout':'Assets/UI/settings-j03/client-layout.json','sourceResolution':a['sourceResolution'],'native1080p':False})
data['asOf']='2026-10-15'
data['references'].append(dict(id='K02-approved-shop-direction',path='Assets/UI/mockups/shop-k02/mockup_shop_k02_1920x1080.png',clientSpec='Assets/UI/mockups/shop-k02/README.md',role='approved-direction-reference-not-runtime-asset',approvalQuote='继续吧',approvedOn='2026-10-15',exportReference=True,productionEligible=False))
for a in read('ImageReview/batches/shop-k03/assets.json')['assets']:
    entry(a,'Assets/UI','approved','K03','shop-background')
    items[-1]['approvalNote']='2026-10-15: user approved K03 textless background and state direction with 继续吧.'
    items[-1]['spec'].update({'clientSpec':'Assets/UI/shop-k03/README.md','sourceResolution':a['sourceResolution'],'native1080p':False})
data['references'].append(dict(id='K04-approved-removal-direction',path='Assets/UI/mockups/shop-k04/selected.png',clientSpec='Assets/UI/mockups/shop-k04/README.md',role='approved-flow-reference-not-runtime-asset',approvalQuote='继续吧',approvedOn='2026-10-15',exportReference=True,productionEligible=False))
for a in read('ImageReview/batches/campfire-l01/assets.json')['assets']:
    entry(a,'Assets/UI','approved','L01','campfire-background')
    items[-1]['approvalNote']='2026-10-15: user approved L01 background and campfire layout with 没问题.'
    items[-1]['spec'].update({'clientSpec':'Assets/UI/campfire-l01/README.md','sourceResolution':a['sourceResolution'],'native1080p':False})
data['references'].append(dict(id='L03-approved-upgrade-direction',path='Assets/UI/mockups/campfire-l03/selected.png',clientSpec='Assets/UI/mockups/campfire-l03/README.md',role='approved-flow-reference-not-runtime-asset',approvalQuote='可以，继续吧',approvedOn='2026-10-15',exportReference=True,productionEligible=False))
data['references'].append(dict(id='N01-approved-card-reward',path='Assets/UI/mockups/reward-n01/selected.png',clientSpec='Assets/UI/mockups/reward-n01/README.md',additionalPaths=['Assets/UI/mockups/reward-n01/unselected.png','Assets/UI/mockups/reward-n01/claimed.png','Assets/UI/mockups/reward-n01/skipped.png'],role='approved-flow-reference-not-runtime-asset',approvalQuote='可以',approvedOn='2026-10-15',exportReference=True,productionEligible=False))
for a in read('ImageReview/batches/ui-icons-q02/assets.json')['assets']:
    entry(a,'Assets/UI','approved','Q02','functional-ui-icon')
    items[-1]['spec']['clientSpec']='Assets/UI/icons-q02/README.md'
    items[-1]['approvalNote']='2026-10-15: user approved P01/Q01/Q02/R01 with 可以.'
for rid,folder,path in [('P01-static-closure','v1-closure-p01','overview.jpg'),('R01-motion','motion-r01','index.html')]:
    base=f'Assets/UI/mockups/{folder}'
    data['references'].append(dict(id=rid,path=f'{base}/{path}',clientSpec=f'{base}/README.md',bundleDirectory=base,role='approved-design-reference-not-runtime-asset',status='approved',approvalQuote='可以',approvedOn='2026-10-15',productionEligible=False,exportReference=True))
data['supplementalFiles']=[dict(path=p.relative_to(ROOT).as_posix(),status='approved',role='font-package',sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted((ROOT/'Assets/UI/fonts/q01').iterdir()) if p.is_file()]
for a in read('ImageReview/batches/v1-effects-s01/assets.json')['assets']:
    if a.get('status')=='approved':
        entry(a,'Assets/UI','approved','S01','static-boss-phase-illustration')
        items[-1]['approvalNote']='2026-10-16: user approved phase II with 我觉得可以; phase III and effects excluded.'
        items[-1]['spec'].update({'clientSpec':'Assets/UI/boss-phase2-s01/README.md','phase':2,'visibleBounds':a['visibleBounds'],'scope':'Static phase II only; tight edge padding, align visible feet in engine.'})
data['asOf']='2026-10-16'
for a in read('ImageReview/batches/effects-t01/assets.json')['assets']:
    entry(a,'Assets/UI','approved','T01','effect-texture')
    items[-1]['spec']['clientSpec']='Assets/UI/mockups/effects-t01/README.md'
    items[-1]['approvalNote']='2026-10-17: user approved the unified review page with 审阅通过.'
for rid,folder,path in [('M01-event','event-m01','choices.png'),('O01-relic-reward','relic-reward-o01','selected.png'),('T01-effects-reference','effects-t01','index.html')]:
    base=f'Assets/UI/mockups/{folder}'
    data['references'].append(dict(id=rid,path=f'{base}/{path}',clientSpec=f'{base}/README.md',bundleDirectory=base,role='approved-design-reference-not-runtime-asset',status='approved',approvalQuote='审阅通过',approvedOn='2026-10-17',productionEligible=False,exportReference=True))
for a in read('ImageReview/batches/boss-phase3-s02/assets.json')['assets']:
    entry(a,'Assets/UI','approved','S02','static-boss-phase-illustration')
    items[-1]['spec'].update({'phase':3,'clientSpec':'Assets/UI/boss-phase3-s02/README.md','visibleBounds':a['visibleBounds']})
    items[-1]['approvalNote']='2026-10-17: user approved phase III with 确认没有问题. Static art only.'
data['asOf']='2026-10-17'
data['references'].append(dict(id='V03-startup',path='Assets/UI/mockups/startup-v03/startup_cover_v03.png',clientSpec='Assets/UI/mockups/startup-v03/README.md',bundleDirectory='Assets/UI/mockups/startup-v03',role='approved-design-reference-not-runtime-asset',status='approved',approvalQuote='就这个吧',approvedOn='2026-10-17',productionEligible=False,exportReference=True))
for rid,folder,path in [('U01-battle-final','battle-u01','normal.png'),('H02-entry-final','entry-h02','mockup_main_menu_h02_1920x1080.png'),('L01-campfire-final','campfire-l01','mockup_campfire_l01_1920x1080.png')]:
    base=f'Assets/UI/mockups/{folder}'
    data['references'].append(dict(id=rid,path=f'{base}/{path}',clientSpec=f'{base}/README.md',bundleDirectory=base,role='final-ui-design-specification',status='approved',approvalBasis='User delegated UI finalization',approvedOn='2026-10-21',productionEligible=False,exportReference=True))
for ref in data['references']:
    if ref.get('exportReference') or ref['id']=='V05-approved-design':
        ref.update(visualStatus='final',implementationStatus='not-verified',runtimeTexture=False)
        if ref['id']=='V05-approved-design':
            ref.update(clientSpec='Assets/UI/mockups/battle-journal-v05/README.md',bundleDirectory='Assets/UI/mockups/battle-journal-v05',exportReference=True,productionEligible=False)
data['uiFinalization']='Assets/UI/integration-v1/ui-finalization.json'
data['asOf']='2026-10-21'
OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(items)} assets checked; {sum(a["productionEligible"] for a in items)} approved standalone entries')
