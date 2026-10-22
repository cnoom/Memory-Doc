// Review unchanged illustrations without rejected card frames or sample card effects.
const fs=require('node:fs'),path=require('node:path'),sharp=require(process.argv[2]);
const root=path.resolve(__dirname,'../../..'),dir=path.join(root,'ImageReview');
let body='<rect width="1380" height="570" fill="#E8E2D3"/><g fill="#29382F" font-family="Microsoft YaHei,sans-serif"><text x="35" y="49" font-size="29">B01 · 三张初始卡插画</text><text x="35" y="83" font-size="17">仅审插画主体；卡框、文字与数值独立，后续卡框按 C02 方向制作</text>';
[['card_attack_daji_etching_b01','打击'],['card_skill_gedang_etching_b01','格挡'],['card_attack_biji_etching_b01','笔记']].forEach(([id,name],i)=>{let x=32+i*450;body+=`<rect x="${x}" y="112" width="416" height="414" rx="4" fill="#EFEADD" stroke="#BBC1AC"/><image href="data:image/png;base64,${fs.readFileSync(path.join(dir,'cards',id+'.png')).toString('base64')}" x="${x+16}" y="133" width="384" height="322"/><text x="${x+208}" y="497" text-anchor="middle" font-size="25">${name}</text>`;});
body+='</g>';
sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1380" height="570">${body}</svg>`)).png().toFile(path.join(dir,'batches/etching-b01/review_card_art_2026-10-07.png')).then(()=>console.log('3 unchanged illustrations rendered')).catch(e=>{console.error(e);process.exitCode=1});
