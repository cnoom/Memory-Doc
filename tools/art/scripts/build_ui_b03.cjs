const fs=require('node:fs'),path=require('node:path'),sharp=require(process.argv[2]);
const root=path.resolve(__dirname,'../../..'),dir=path.join(root,'ImageReview/batches/ui-b03');fs.mkdirSync(path.join(dir,'assets'),{recursive:true});const list=[];
async function asset(id,w,h,body){const s=`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`;fs.writeFileSync(path.join(dir,'assets',id+'.svg'),s);await sharp(Buffer.from(s)).png().toFile(path.join(dir,'assets',id+'.png'));list.push({id,width:w,height:h,svg:'assets/'+id+'.svg',png:'assets/'+id+'.png'});}
const ring=`<g fill="none" stroke="currentColor" stroke-width="2"><path d="M35 9A24 24 0 0 1 55 28M55 36A24 24 0 0 1 35 55M27 55A24 24 0 0 1 8 36M8 28A24 24 0 0 1 27 9M31 1v17m0 28v17"/><path d="m21 43 8-15 15-9-9 16zM21 43l23-24"/></g>`;
(async()=>{
await asset('ornament_memory_ring_b03',64,64,`<g color="#B6C6C5">${ring}</g>`);
for(const type of ['primary','secondary'])for(const state of ['normal','hover','pressed','disabled']){
const dark=type==='primary',disabled=state==='disabled',hover=state==='hover',pressed=state==='pressed',fill=disabled?'#B7B7AC':dark?'#293A40':'#EEE9DD',line=disabled?'#858B81':hover?'#83B0C1':dark?'#92A7A5':'#737F77',offset=pressed?4:0;
await asset(`btn_${type}_${state}_b03`,640,112,`<path d="M8 14h617l8 6v82H16l-8-8Z" fill="#171E20" opacity=".35"/><g transform="translate(0 ${offset})"><path d="M4 4h618l10 10v82H14L4 86Z" fill="${fill}" stroke="${line}" stroke-width="2"/><path d="M18 16h592l10 8v60H26l-10-8V26" fill="none" stroke="${line}" stroke-width="1" opacity=".7"/><path d="M40 32 30 50l10 18m556-36 10 18-10 18M52 44l-5 6 5 6m532-12 5 6-5 6" fill="none" stroke="${line}" stroke-width="2"/><path d="M12 26v36m614-34v35" stroke="${line}" stroke-width="4"/></g>`);
}
await asset('badge_mark_paper_b03',240,100,'<path d="M8 12h222v74H12L2 76Z" fill="#171F22" opacity=".4"/><path d="M3 3h225v70l-9 12H3Z" fill="#A7C2CA" stroke="#354B53" stroke-width="2"/><path d="M16 13h195v59H16Z" fill="none" stroke="#597A83"/><path d="m42 24 7 15 16 6-16 6-7 16-6-16-16-6 16-6Z" fill="#293C42"/>');
await asset('seal_pairing_b03',128,128,'<g fill="none" stroke="#B2A1B4"><path d="m64 8 48 28v56l-48 28-48-28V36Z" stroke-width="4"/><path d="m64 18 39 23v46l-39 23-39-23V41Z" stroke-width="1.5"/><path d="M42 38v49m44-49v49M34 49h61M34 78h61m-40-24 18 18m0-18L55 72" stroke-width="4"/></g>');
fs.writeFileSync(path.join(dir,'assets.json'),JSON.stringify({batch:'ui-b03',status:'preview-not-approved',scope:'组合样张与按钮精修，非全套UI定稿',assets:list},null,2));console.log(list.length+' B03 assets');
})().catch(e=>{console.error(e);process.exitCode=1});
