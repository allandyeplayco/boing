// Runs the level bot headless: node tools/check.mjs [levels.json]
import {createRequire} from 'module';const {chromium}=createRequire(import.meta.url)('playwright');
import {readFileSync} from 'fs';
import {fileURLToPath} from 'url';
import path from 'path';
const here=path.dirname(fileURLToPath(import.meta.url));
const file=process.argv[2];
const b=await chromium.launch();
const pg=await b.newPage({viewport:{width:390,height:844}});
pg.on('pageerror',e=>console.log('PAGE ERROR',e.message));
await pg.goto('file://'+path.join(here,'..','index.html'));
await pg.waitForFunction(()=>window.BOT_API);if(process.env.BUDGET)await pg.evaluate(b=>window.BUDGET=b,+process.env.BUDGET);
const levels=file?JSON.parse(readFileSync(file,'utf8')):null;
const res=await pg.evaluate(async(levels)=>{
  const L=levels||window.BOT_API.campaign();const out=[];
  for(let i=0;i<L.length;i++){const t=performance.now();const r=window.BOT_API.check(L[i],window.BUDGET);out.push({i:i+1,name:r.name,ok:r.ok,taps:r.taps,tight:r.tight,score:r.score,notap:r.noTap,short:r.shortcuts.join(' '),unsure:r.unsure.join(' '),nodes:r.nodes,ms:Math.round(performance.now()-t),plan:JSON.stringify(r.plan&&r.plan.map(s=>s.k)),windows:JSON.stringify(r.windows),level:L[i],trace:r.plan?window.BOT_API.trace(L[i],r.plan):{pts:[],taps:[]}})}
  return out},levels);
for(const r of res)console.log(`${String(r.i).padStart(2)} ${(r.name||'').padEnd(18)} ${r.ok?'WIN ':'FAIL'} taps ${r.taps} tight ${r.tight}ms score ${r.score} notap ${r.notap?"Y":"n"} shortcut[${r.short}] unsure[${r.unsure}] nodes ${r.nodes} ${r.ms}ms plan ${r.plan} win ${r.windows}`);
if(process.env.OUT){(await import('fs')).writeFileSync(process.env.OUT,JSON.stringify(res))}
await b.close();
