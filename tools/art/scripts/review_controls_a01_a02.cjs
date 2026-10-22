// Contact sheet of existing control assets; sample labels are not baked into assets.
const fs=require('node:fs'),path=require('node:path'),sharp=require(process.argv[2]);
const root=path.resolve(__dirname,'../../..'),dir=path.join(root,'ImageReview');
const text=(s,x,y,n=20,c='#2A3B32')=>`<text x="${x}" y="${y}" font-family="Microsoft YaHei,sans-serif" font-size="${n}" fill="${c}">${s}</text>`;
const img=(f,x,y,w,h)=>`<image href="data:image/png;base64,${fs.readFileSync(path.join(dir,f)).toString('base64')}" x="${x}" y="${y}" width="${w}" height="${h}"/>`;
let s='<rect width="1400" height="970" fill="#E9E3D2"/>'+text('A01 / A02 · 按钮与设置控件',36,49,30)+text('19项候选：8个按钮状态、7个控件部件、4个焦点覆层；本图标签仅用于审阅',36,82,17);
['常态','悬停','按下','禁用'].forEach((v,i)=>s+=text(v,190+i*306,134,20));
for(const [row,kind,label]of [[0,'menu','页内菜单'],[1,'danger','危险操作']]){
 const y=160+row*91;s+=text(label,36,y+30,19);
 ['normal','hover','pressed','disabled'].forEach((state,i)=>{let x=166+i*306;s+=img(`buttons/btn_${kind}_${state}_a01.png`,x,y,280,49)+text(row?'返回主菜单':'继续探索',x+63,y+32,22,state==='disabled'?'#939885':row?'#985B48':'#354D3C');});
}
s+='<path d="M36 350h1328" stroke="#B1BAA0"/>'+text('设置控件 · 开关 / 复选框 / 滑条',36,390,25);
const controls=[['toggle_off','关闭',128,64],['toggle_on','开启',128,64],['check_off','未勾选',64,64],['check_on','已勾选',64,64]];
controls.forEach(([id,label,w,h],i)=>{const x=48+i*220;s+=`<rect x="${x}" y="417" width="196" height="126" fill="#F3ECDD" stroke="#BEC5AE"/>`+img(`controls/${id}_a01.png`,x+(196-w)/2,430,w,h)+text(label,x+64,524,18);});
s+=text('滑条：轨道＋填充＋滑块',954,440,18)+img('controls/slider_track_a01.png',954,468,360,22)+img('controls/slider_fill_a01.png',954,468,180,22)+img('controls/slider_thumb_a01.png',1115,458,42,42);
s+='<path d="M36 577h1328" stroke="#B1BAA0"/>'+text('键盘焦点 · 雾蓝轮廓叠加在当前控件上',36,619,25);
s+=img('buttons/btn_menu_normal_a01.png',48,660,350,61)+img('overlays/focus_button_a02.png',48,660,350,61)+text('继续探索',145,700,24)+text('按钮焦点',150,765,18);
s+=img('controls/toggle_on_a01.png',484,658,128,64)+img('overlays/focus_toggle_a02.png',484,658,128,64)+text('开关焦点',511,765,18);
s+=img('controls/check_on_a01.png',763,658,64,64)+img('overlays/focus_check_a02.png',763,658,64,64)+text('复选框焦点',744,765,18);
s+=img('controls/slider_track_a01.png',962,682,352,22)+img('controls/slider_fill_a01.png',962,682,176,22)+img('controls/slider_thumb_a01.png',1106,660,64,64)+img('overlays/focus_slider_a02.png',1106,660,64,64)+text('滑块焦点',1098,765,18);
s+=text('控件禁用组合示例（保持选中值，降低透明度）',36,830,21)+`<g opacity=".4">`+img('controls/toggle_on_a01.png',48,864,96,48)+img('controls/check_on_a01.png',204,864,48,48)+img('controls/slider_track_a01.png',320,883,256,16)+img('controls/slider_fill_a01.png',320,883,128,16)+img('controls/slider_thumb_a01.png',428,870,42,42)+'</g>'+text('交互时需同时阻断输入；图中仅展示外观',660,899,18);
sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="970">${s}</svg>`)).png().toFile(path.join(dir,'batches/core-a02/review_controls_2026-10-07.png')).then(()=>console.log('Control review board rendered')).catch(e=>{console.error(e);process.exitCode=1});
