// Native vector extensions to the existing monochrome UI icon vocabulary.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'../../..'),out=path.join(root,'ImageReview/icons'),batch=path.join(root,'ImageReview/batches/ui-icons-q02');fs.mkdirSync(out,{recursive:true});fs.mkdirSync(batch,{recursive:true});
const paper='<rect x="52" y="30" width="88" height="132" rx="7"/>';
const arrow='<path d="M36 96h120m-28-27 28 27-28 27"/>';
const eye='<path d="M24 96Q96 20 168 96Q96 172 24 96Z"/><circle cx="96" cy="96" r="22"/>';
const icons=[
 ['trigger_flip','翻开',paper+'<path d="M29 64Q18 112 54 131m-3-24 3 24-25-4M163 128q15-50-22-66m0 24V62l25 4"/>'],
 ['trigger_flipback','翻回',paper+'<path d="M40 90h110M63 67 40 90l23 23"/><path d="M77 134h38"/>'],
 ['trigger_discard','丢弃',paper+'<path d="M96 75v65m-23-23 23 23 23-23M32 155v20h128v-20"/>'],
 ['trigger_leave','离场',paper+arrow],
 ['trigger_enter','入场',paper+'<path d="M20 96h88M85 73l23 23-23 23"/>'],
 ['behavior_exhaust','消耗','<path d="M53 154V34h85v54l-21 4 12 24-31 8 8 29Z"/><path d="m140 119 13 12m-22 21 10 12m22-60 8 10"/>'],
 ['behavior_remove','移除',paper+'<path d="m64 60 64 72M128 60l-64 72"/>'],
 ['behavior_stubborn','顽固','<path d="M96 25 153 48v58q-8 38-57 61-49-23-57-61V48Z"/><path d="M96 52v84M73 96l23 40 23-40"/>'],
 ['behavior_hidden','隐秘',eye+'<path d="m30 164 132-136"/>'],
 ['behavior_swift','迅速','<path d="m109 22-66 86h48l-8 62 66-88h-49Z"/><path d="M20 50h36M18 143h36"/>'],
 ['match_resonance','共鸣','<circle cx="70" cy="96" r="42"/><circle cx="122" cy="96" r="42"/><path d="M96 31v18m0 94v18"/>'],
 ['match_sword','剑','<path d="m40 165 37-37m-18-18 30 30m-13-20 63-77 27-17-8 34-74 69Z"/>'],
 ['match_shield','盾','<path d="M96 24 156 47v55q-5 43-60 67-55-24-60-67V47Z"/><path d="M96 46v96M60 83h72"/>'],
 ['intent_swap','换位','<path d="M28 66h136m-27-23 27 23-27 23M164 126H28m27-23-27 23 27 23"/>'],
 ['intent_pollute','污染',paper+'<path d="M96 60q-42 47-26 64 26 25 52-1 15-17-26-63Z"/>'],
 ['intent_lock','封锁','<rect x="44" y="79" width="104" height="83" rx="9"/><path d="M62 79V57a34 34 0 0 1 68 0v22M96 108v27"/>'],
 ['action_upgrade','强化','<path d="M96 161V34M53 78l43-44 43 44M42 169h108"/>'],
 ['action_sort','排序','<path d="M45 35v122m-20-21 20 21 20-21M87 45h77M87 92h53M87 139h29"/>'],
 ['action_filter','筛选','<path d="M25 35h142l-56 64v49l-30 15V99Z"/>'],
 ['action_details','详情',eye],
 ['action_deck','牌库','<rect x="30" y="28" width="95" height="130" rx="6"/><path d="M142 45v127H47M157 60v125H63M54 63h47M54 87h47"/>'],
 ['action_gold','金币','<circle cx="96" cy="96" r="68"/><circle cx="96" cy="96" r="51"/><path d="m96 53 25 43-25 43-25-43Z"/>'],
 ['action_close','关闭','<path d="m48 48 96 96M144 48l-96 96"/>'],
 ['action_return','返回','<path d="M162 104H31m40-40-40 40 40 40"/>']
];
(async()=>{let assets=[];for(const [name,label,body] of icons){const id='icon_'+name+'_q02';const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192"><g fill="none" stroke="#252F32" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">${body}</g></svg>`;fs.writeFileSync(path.join(out,id+'.svg'),svg);await sharp(Buffer.from(svg)).png().toFile(path.join(out,id+'.png'));assets.push({id,label,png:'icons/'+id+'.png',svg:'icons/'+id+'.svg',width:192,height:192,status:'pending-review',productionEligible:false,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(out,id+'.png'))).digest('hex')});}fs.writeFileSync(path.join(batch,'assets.json'),JSON.stringify({batch:'ui-icons-q02',assets},null,2));console.log(assets.length+' SVG/PNG pairs rendered');})();
