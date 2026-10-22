const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'../../..'),out=path.join(root,'ImageReview/map'),batch=path.join(root,'ImageReview/batches/map-i04');
fs.mkdirSync(out,{recursive:true});
const ink='#252F32',blue='#648891';
const shapes={
 battle:'<path d="M23 20l21 22-6 6-22-21 1-10Zm18 32 9-9m-5 5 7 7M44 19 23 42l6 6 22-22-1-10ZM21 51l-8-8m4 4-6 7"/>',
 elite:'<path d="M20 24 32 17l12 7v24l-12 8-12-8Zm12-7v39M24 31l5 4m11-4-5 4M20 27 12 15l2 18 6 5m24-11 8-12-2 18-6 5"/><path d="m48 6 2 5 5 1-4 4 1 5-4-3-5 3 1-5-4-4 6-1Z" fill="#8D3D35" stroke="none"/>',
 event:'<path d="M22 22c0-14 23-14 23 0 0 9-13 9-13 20"/><circle cx="32" cy="51" r="2" fill="'+ink+'"/>',
 shop:'<path d="m24 10 8 3 9-3-5 13c18 13 18 31-4 32-23 0-21-20-4-32Zm2 14h14M29 12l3 10 5-10"/><path d="M22 39c-2 6 0 9 4 10m16-13 2 5"/>',
 campfire:'<path d="M31 9c5 12-8 14-7 24 0 9 13 11 17 2 4-9-5-14-2-20 0 0-4 3-5 7Z" fill="#A45443"/><path d="m17 46 31 10m-2-12-30 12m12-23c-1 7 6 9 8 3"/>',
 start:'<path d="M18 55V26a14 14 0 0 1 28 0v29M24 55V27a8 8 0 0 1 16 0v28M13 55h38M18 32h6m16 0h6M18 43h6m16 0h6M29 13v6m10-4-3 5"/>'};
function svg(body,w=192,h=192){return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`}
async function main(){let assets=[];
 async function save(id,s,w,h){fs.writeFileSync(path.join(out,id+'.svg'),s);await sharp(Buffer.from(s)).png().toFile(path.join(out,id+'.png'));assets.push({id,png:'map/'+id+'.png',svg:'map/'+id+'.svg',width:w,height:h,status:'pending-review',productionEligible:false});}
 for(const [name,body]of Object.entries(shapes))await save('node_'+name+'_i04',svg(`<g transform="scale(3)" fill="none" stroke="${ink}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${body}</g>`),192,192);
 for(const [state,color,width,dash]of [['future','#939A94',2,'6 7'],['available',blue,3,''],['selected',blue,5,''],['current',ink,6,''],['completed',ink,3,'']]){
 let body=`<circle cx="96" cy="96" r="82" fill="#E7E5D8" stroke="${color}" stroke-width="${width}" ${dash?`stroke-dasharray="${dash}"`:''}/><circle cx="96" cy="96" r="74" fill="none" stroke="${color}" stroke-width="1"/>`;
 if(state==='completed')body+='<path d="m136 143 9 9 18-22" fill="none" stroke="'+ink+'" stroke-width="5"/>';
 if(state==='selected')body+='<path d="m96 2 7 8-7 8-7-8Z" fill="'+blue+'"/>';
 await save('node_ring_'+state+'_i04',svg(body),192,192);}
 await save('marker_current_i04',svg('<path d="M3 3h230l12 10v47H12L3 50Z" fill="#E7E5D8" stroke="#252F32" stroke-width="2"/><path d="M12 10h222v42H12Z" fill="none" stroke="#939A94"/>',248,64),248,64);
 await save('panel_node_tip_i04',svg('<path d="M9 12h622v164H16L8 168Z" fill="#252F32" opacity=".18"/><path d="M3 3h620l10 10v153H13L3 156Z" fill="#E7E5D8" stroke="#252F32" stroke-width="2"/><path d="M15 14h604v140H15Z" fill="none" stroke="#939A94"/>',640,180),640,180);
 fs.writeFileSync(path.join(batch,'components.json'),JSON.stringify({batch:'map-i04',assets},null,2));
 let cells=assets.map((a,i)=>`<g transform="translate(${(i%4)*270},${Math.floor(i/4)*240})"><image href="data:image/png;base64,${fs.readFileSync(path.join(out,a.id+'.png')).toString('base64')}" x="35" y="10" width="190" height="180" preserveAspectRatio="xMidYMid meet"/><text x="135" y="220" text-anchor="middle" font-family="sans-serif" font-size="14" fill="${ink}">${a.id.replace('_i04','')}</text></g>`).join('');
 await sharp(Buffer.from(svg('<rect width="1080" height="960" fill="#DCDDD3"/>'+cells,1080,960))).png().toFile(path.join(batch,'components-review.png'));
 console.log(assets.length+' SVG+PNG components generated.');}
main().catch(e=>{console.error(e);process.exit(1)});
