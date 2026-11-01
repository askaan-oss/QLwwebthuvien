const {chromium}=require('playwright');
(async()=>{
const base='http://localhost:5160/api';let token;let added=false;let b;
async function api(path,method='GET',data){let r=await fetch(base+path,{method,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},body:data?JSON.stringify(data):undefined});let j=await r.json();if(!r.ok)throw Error(j.message);return j.data;}
try{
token=(await api('/Auth/login','POST',{email:'khach.test@libra.vn',password:'Libra@123'})).token;
const cart=await api('/Cart');console.log('cart structure',JSON.stringify(cart));
await api('/Cart/add','POST',{productId:2,quantity:1});added=true;
b=await chromium.launch({channel:'msedge',headless:true});const p=await b.newPage({viewport:{width:1440,height:1050}});
await p.goto('http://127.0.0.1:4173/');await p.evaluate(t=>sessionStorage.setItem('libra.jwt',t),token);
for(const [route,name] of [['gio-hang','cart'],['thanh-toan','checkout'],['sach/2','preview']]){
await p.goto('http://127.0.0.1:4173/#/'+route);await p.reload();await p.waitForTimeout(4000);
if(name==='preview'){await p.locator('[data-preview-book] summary').click();await p.waitForTimeout(2500);await p.locator('.reading-preview').screenshot({path:'work/report-final/preview.png'});}else await p.screenshot({path:'work/report-final/'+name+'.png'});
console.log(name,(await p.locator('main').innerText()).slice(0,100));
}
await p.locator('#notification-toggle').click();await p.waitForTimeout(1500);await p.locator('#notification-panel').screenshot({path:'work/report-final/notifications.png'});
}finally{if(added)await api('/Cart/item/2','DELETE');if(token)await api('/Auth/logout','POST');if(b)await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
