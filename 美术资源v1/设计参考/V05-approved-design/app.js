const $=s=>document.querySelector(s);
const emblem=`<svg class="back-mark" viewBox="0 0 100 120" fill="none" aria-hidden="true"><path d="M42 20A35 35 0 0 0 16 50M15 64A35 35 0 0 0 42 89M58 90A35 35 0 0 0 85 65M85 50A35 35 0 0 0 58 20" stroke="currentColor" stroke-width="2.4"/><path d="M50 5v23M50 84v23" stroke="currentColor" stroke-width="1.2"/><path d="m34 74 14-23 18-14-13 24z" stroke="currentColor" stroke-width="1.4"/><path d="m34 74 32-37M42 67l8-7M48 51l10-7" stroke="currentColor" stroke-width=".9"/></svg>`;
const sword=`<svg viewBox="0 0 40 44" fill="none" aria-hidden="true"><path d="m13 30 17-23 8-3-2 9-20 21M7 28l12 10M12 33l-7 8M5 39l3 3" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/></svg>`;
const shield=`<svg viewBox="0 0 28 30" fill="none" aria-hidden="true"><path d="M14 2c4 4 8 4 11 4v10c-1 6-6 10-11 13C9 26 4 22 3 16V6c4 0 7 0 11-4Z" stroke="currentColor" stroke-width="1.8"/><path d="M14 7v17" stroke="currentColor"/></svg>`;
const grid=$('#grid');
for(let i=0;i<16;i++){
 const card=document.createElement('button');card.className='card'+(i===6?' face':'');card.dataset.slot=i;card.setAttribute('aria-label',i===6?'读书笔记，查看详情':`第${Math.floor(i/4)+1}行第${i%4+1}列，背面牌${i===7?'，标记一层':''}`);
 card.innerHTML=i===6?`<span class="type-mark"></span><h3 class="card-name">读书笔记</h3><div class="card-art"><img src="references/card_attack_dushubiji_illustration_v02.png" alt=""></div><div class="card-effect"><span class="trigger">配对</span><strong>8</strong><span>伤害</span></div><div class="card-flip">翻开 · 标记邻牌</div><div class="card-tail"><span class="resonance">共鸣</span><span class="detail-cue">详情 ›</span></div>`:emblem+(i===7?'<span class="marked">✦×1</span>':'');
 card.onclick=()=>i===6?toggleDetail():toast('此页仅预览 UI，不翻开隐藏牌。点击「读书笔记」可查看详情。');grid.append(card);
}
$('#sword-icon').innerHTML=sword;$('#shield-icon').innerHTML=shield;
for(let i=0;i<10;i++){const segment=document.createElement('span');segment.className='segment';segment.setAttribute('aria-hidden','true');$('#meter').append(segment)}
let mode='normal',timer;
function setMode(next){mode=next;const danger=next==='danger';$('#stage').classList.toggle('danger',danger);const value=danger?9:1;$('#meter').setAttribute('aria-valuenow',value);document.querySelectorAll('.segment').forEach((el,i)=>el.classList.toggle('lit',i<value));$('#action-value').innerHTML=`${value} <small>/ 10</small>`;$('#remaining').innerHTML=`距行动 <b>${10-value}</b> 点`;$('#intent-note').textContent=danger?'仅差 1 点 · 即将行动':'行动条满时执行';$('#detail-action').textContent=`行动 ${value}/10`;$('#normal').classList.toggle('active',!danger);$('#danger').classList.toggle('active',danger);$('#toast').hidden=true;}
function toggleDetail(force){const open=force??$('#detail').hidden;$('#detail').hidden=!open;$('#stage').classList.toggle('detail-open',open);$('#show-detail').classList.toggle('active',open);if(open){$('#toast').hidden=true;$('#close-detail').focus({preventScroll:true})}}
function toast(text){clearTimeout(timer);$('#toast').textContent=text;$('#toast').hidden=false;timer=setTimeout(()=>$('#toast').hidden=true,5000)}
$('#normal').onclick=()=>setMode('normal');$('#danger').onclick=()=>setMode('danger');$('#show-detail').onclick=()=>toggleDetail();$('#close-detail').onclick=()=>toggleDetail(false);
document.addEventListener('keydown',e=>{if(e.key==='Escape'){toggleDetail(false);$('#toast').hidden=true;$('.card.face').focus({preventScroll:true})}});
$('#refill').onclick=()=>toast(mode==='danger'?'重新铺满的行动条代价为 +2；当前距敌人行动仅差 1 点。此预览不执行清桌。':'重新铺满会清理桌面并使行动条 +2。此预览不执行清桌。');
const piles={draw:'抽牌堆剩余 4 张。此预览不展示抽取顺序或隐藏牌位置。',discard:'弃牌堆 0 张。',exhaust:'消耗堆 0 张；本场战斗不参与洗回。',memory:'记忆记录 1：读书笔记 · 翻开 → 标记相邻 1 张背面牌。记录不显示目标牌的隐藏身份。'};
document.querySelectorAll('[data-pile]').forEach(b=>b.onclick=()=>toast(piles[b.dataset.pile]));document.querySelectorAll('[data-info]').forEach(b=>b.onclick=()=>toast(b.dataset.info));
$('#help').onclick=()=>toast('这是美术与交互预览。可切换常态、临界状态，点击正面牌看详情；没有战斗模拟。');
function resize(){const compact=innerWidth<1500||innerHeight<960;$('#stage').classList.toggle('compact',compact);const w=compact?1280:1920,h=compact?720:1080;const scale=Math.min(innerWidth/w,Math.max(320,innerHeight-76)/h);document.documentElement.style.setProperty('--scale',scale);$('#viewport').style.width=w*scale+'px';$('#viewport').style.height=h*scale+'px';}
addEventListener('resize',resize);resize();setMode(new URLSearchParams(location.search).get('mode')==='danger'?'danger':'normal');if(new URLSearchParams(location.search).has('detail'))toggleDetail(true);
window.preview={setMode,toggleDetail};
