const {chromium}=require('playwright');
const fs=require('fs');
const base='http://localhost:5160/api';
async function login(email){const r=await fetch(base+'/Auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password:'Libra@123'})});const j=await r.json();if(!j.data?.token)throw Error(JSON.stringify(j));return j.data.token;}
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const ctx=await browser.newContext({viewport:{width:1440,height:1050},deviceScaleFactor:1});
 const p=await ctx.newPage();
 async function go(hash,name){await p.goto('http://127.0.0.1:4173/#/'+hash);await p.reload();await p.waitForFunction(()=>!document.querySelector('main')?.innerText.includes('Đang kết nối'));await p.waitForTimeout(2500);console.log(name,(await p.locator('main').innerText()).slice(0,160));await p.screenshot({path:'work/report-final/'+name+'.png'});}
 await go('','home');await go('sach','catalog');await go('sach/2','detail');await go('dang-nhap','login');
 const token=await login('khach.test@libra.vn');await p.evaluate(t=>sessionStorage.setItem('libra.jwt',t),token);
 await go('gio-hang','cart');await go('thanh-toan','checkout');await go('don-hang','orders');await go('sach/2','preview');
 console.log('buttons',await p.locator('main button').allTextContents());
 await p.locator('#ai-toggle').click();await p.locator('#ai-question').fill('Tư vấn sách về tài chính và quản lý tiền');await p.locator('#ai-form button').click();await p.waitForTimeout(18000);await p.screenshot({path:'work/report-final/ai.png'});
 const manager=await login('quanly.test@libra.vn');await p.evaluate(t=>sessionStorage.setItem('libra.jwt',t),manager);await go('quan-ly','manager');await go('dashboard','dashboard');
 const admin=await login('quantri.test@libra.vn');await p.evaluate(t=>sessionStorage.setItem('libra.jwt',t),admin);await go('quan-tri','admin');
 for(const t of [token,manager,admin])await fetch(base+'/Auth/logout',{method:'POST',headers:{Authorization:'Bearer '+t}});
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
