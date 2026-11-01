/* Live workflows. No mock account, price calculation or order persistence. */
let liveQuote=null,quoteError='',quotePending=false,quoteVersion=0,liveAddresses=[],liveBusy=false;
function mergeBooks(incoming){for(const b of incoming){const index=books.findIndex(x=>x.id===b.id);if(index<0)books.push(b);else books[index]=b;}}
function liveSelected(){return cart.filter(i=>i.selected!==false).map(i=>({productId:i.bookId,quantity:i.quantity}));}
function selectionKey(){return 'libra.selection.'+(user?.id||'guest');}
function saveSelection(){sessionStorage.setItem(selectionKey(),JSON.stringify(cart.filter(i=>i.selected===false).map(i=>i.bookId)));}
async function syncLiveCart(){
 if(!user){cart=[];return;}
 const data=await LibraAPI.cart();let excluded=[];try{excluded=JSON.parse(sessionStorage.getItem(selectionKey())||'[]');}catch{}
 cart=data.items.map(i=>({bookId:i.productId,cartItemId:i.cartItemId,quantity:i.quantity,selected:!excluded.includes(i.productId)}));
 for(const item of data.items){let b=books.find(b=>b.id===item.productId);if(!b){b=await LibraAPI.product(item.productId);mergeBooks([b]);}b.price=item.productPrice;}
 header();
}
async function syncLiveFavorites(){if(!user){favorites=[];return;}const rows=await LibraAPI.favorites();favorites=rows.map(b=>b.productId);for(const r of rows)if(!books.some(b=>b.id===r.productId))mergeBooks([await LibraAPI.product(r.productId)]);}
function liveSummary(checkout=false){
 const q=liveQuote;return `<aside class="order-summary"><h2>Tóm tắt đơn hàng</h2>${quotePending?'<p role="status">Đang tính tiền từ nhà sách…</p>':quoteError?`<p class="form-error" role="alert">${esc(quoteError)}</p><button type="button" class="text-button" data-quote-retry>Thử tính lại</button>`:q?`<div><span>Tiền sách</span><b>${money(q.subtotal)}</b></div><div><span>Vận chuyển</span><b>${money(q.shippingFee)}</b></div><div><span>Giảm giá</span><b>−${money(q.discountAmount)}</b></div><div class="total"><span>Tổng cộng</span><b>${money(q.totalAmount)}</b></div>${q.discountMessage?`<p class="hint">${esc(q.discountMessage)}</p>`:''}`:'<p>Chọn sách để xem tổng tiền.</p>'}${!checkout?`<form id="coupon-form"><label for="coupon">Mã ưu đãi</label><div class="coupon-row"><input id="coupon" value="${esc(coupon)}" placeholder="GIAM10"><button ${quotePending?'disabled':''}>Áp dụng</button></div></form>${q&&!quoteError&&!quotePending&&liveSelected().length?'<a class="button full" href="#/thanh-toan">Thanh toán sách đã chọn →</a>':'<button class="button full" disabled>Chọn sách và kiểm tra tổng tiền</button>'}`:''}</aside>`;
}
function drawLiveQuote(){
 const y=window.scrollY,x=window.scrollX;const node=main.querySelector('.order-summary');const draft=main.querySelector('#coupon')?.value;if(node)node.outerHTML=liveSummary(location.hash.startsWith('#/thanh-toan'));if(draft!==undefined&&main.querySelector('#coupon'))main.querySelector('#coupon').value=draft;
 const submit=main.querySelector('#live-checkout button[type=submit]');if(submit){submit.disabled=quotePending||!!quoteError||!liveQuote||liveBusy;submit.textContent='Xác nhận đặt hàng'+(liveQuote?' · '+money(liveQuote.totalAmount):'');}
 window.scrollTo({left:x,top:y,behavior:'instant'});
}
async function refreshLiveQuote(){
 const version=++quoteVersion;liveQuote=null;quoteError='';quotePending=liveSelected().length>0;
 if(!quotePending){drawLiveQuote();return;}
 drawLiveQuote();try{const quote=await LibraAPI.preview({items:liveSelected(),discountCode:coupon||null});if(version===quoteVersion)liveQuote=quote;}catch(error){if(version===quoteVersion)quoteError=error.message;}finally{if(version===quoteVersion){quotePending=false;drawLiveQuote();}}
}
function updateLiveCartView(){refreshCartTotals();saveSelection();refreshLiveQuote();}
function addressFields(a={}){return `<div class="form-grid">${[['recipientName','Họ tên người nhận'],['recipientPhone','Số điện thoại'],['province','Tỉnh / Thành phố'],['district','Quận / Huyện'],['ward','Phường / Xã'],['detailedAddress','Số nhà, tên đường']].map(([key,label])=>`<label class="field">${label}<input name="${key}" value="${esc(a[key]||'')}" ${key==='detailedAddress'?'':'required'} maxlength="${key==='recipientPhone'?20:key==='detailedAddress'?500:100}" ${key==='recipientPhone'?'type="tel"':'type="text"'}></label>`).join('')}</div><label class="check"><input type="checkbox" name="isDefault" ${a.isDefault?'checked':''}> Địa chỉ mặc định</label>`;}
function addressPayload(form){const d=Object.fromEntries(new FormData(form));return {recipientName:d.recipientName.trim(),recipientPhone:d.recipientPhone.trim(),province:d.province.trim(),district:d.district.trim(),ward:d.ward.trim(),detailedAddress:d.detailedAddress.trim(),isDefault:!!d.isDefault};}
function liveCheckout(){
 return `<section class="wrap section">${heading('Thông tin giao hàng','Kiểm tra địa chỉ và số tiền trước khi xác nhận.')}<div class="checkout-layout"><form id="live-checkout" class="panel"><h2>Địa chỉ nhận hàng</h2><label class="field">Chọn địa chỉ<select id="address-choice" name="addressId"><option value="new">Nhập địa chỉ mới</option>${liveAddresses.map(a=>`<option value="${a.addressId}" ${a.isDefault?'selected':''}>${esc(a.recipientName+' — '+a.fullAddressString)}</option>`).join('')}</select></label><fieldset id="new-address" ${liveAddresses.some(a=>a.isDefault)?'hidden disabled':''}>${addressFields()}</fieldset><h2>Phương thức thanh toán</h2><label class="payment"><input type="radio" name="paymentMethod" value="COD" checked> Thanh toán khi nhận hàng (COD)</label>${LIBRA_CONFIG.onlinePaymentsEnabled?'<label class="payment"><input type="radio" name="paymentMethod" value="QR_TRANSFER"> Chuyển khoản QR</label><label class="payment"><input type="radio" name="paymentMethod" value="VNPAY"> VNPay</label>':''}<p class="hint">Đặt đơn COD chưa có nghĩa là đã thanh toán tiền.</p><label class="check"><input type="checkbox" required> Tôi đã kiểm tra thông tin nhận hàng.</label><p class="form-error" role="alert"></p><button class="button full" type="submit" disabled>Xác nhận đặt hàng</button></form><div>${liveSummary(true)}<div class="panel"><h3>Sách được chọn</h3>${selectedItems().map(i=>`<p>${esc(i.book.title)} × ${i.quantity}</p>`).join('')}</div></div></div></section>`;
}
async function liveOrders(version){
 const all=await LibraAPI.orders();if(version!==routeVersion)return;const mine=all.filter(o=>o.userId===user.id);
 main.innerHTML=`<section class="wrap section">${heading('Đơn hàng của tôi','Trạng thái được cập nhật từ nhà sách.')} ${mine.length?mine.map(o=>`<article class="panel order"><div class="order-heading"><h3>Đơn #${o.id}</h3><span class="status">${esc(o.status)}</span></div><p>${new Date(o.createdAt).toLocaleString('vi-VN')} · ${esc(o.paymentMethod)}</p>${o.items.map(i=>`<div class="order-line"><span>${esc(i.title)} × ${i.quantity}</span><b>${money(i.price*i.quantity)}</b></div>`).join('')}<div class="order-total"><span>Ship ${money(o.shipping)} · Giảm ${money(o.discount)}</span><b>${money(o.total)}</b></div><p>${esc(o.recipientName)} · ${esc(o.shippingAddress)}</p>${['PENDING_PAYMENT','PENDING_CONFIRMATION'].includes(o.statusCode)?`<button class="text-button" data-cancel-order="${o.id}">Hủy đơn hàng</button>`:''}${o.statusCode==='PENDING_PAYMENT'&&LIBRA_CONFIG.onlinePaymentsEnabled?` <a class="button" href="#/thanh-toan-don/${o.id}">Tiếp tục thanh toán</a>`:''}</article>`).join(''):empty('Chưa có đơn hàng','Đơn của bạn sẽ xuất hiện tại đây.')}</section>`;
}
async function paymentPage(id,version){
 const order=await LibraAPI.order(id);const payment=await LibraAPI.paymentStatus(id);if(version!==routeVersion)return;
 const pending=order.statusCode==='PENDING_PAYMENT';const p=typeof payment==='object'&&payment?payment:{};const url=safeLiveUrl(p.paymentUrl),qr=safeLiveUrl(p.qrCodeUrl);
 main.innerHTML=`<section class="wrap section">${heading('Thanh toán đơn #'+id,esc(order.status))}<div class="panel"><h2>${money(order.total)}</h2><p>Trạng thái giao dịch: ${esc(p.paymentStatus||'Chưa khởi tạo')}</p><p>${esc(p.note||'Chỉ coi là đã thanh toán khi nhà sách xác nhận.')}</p>${pending&&p.paymentMethod==='QR_TRANSFER'&&qr?`<img class="payment-qr" src="${esc(qr)}" alt="Mã QR thanh toán"><p>${esc(p.bankInfo)}</p>`:''}${pending&&url&&p.paymentMethod!=='QR_TRANSFER'?`<a class="button" href="${esc(url)}" target="_blank" rel="noopener noreferrer">Mở cổng thanh toán ↗</a>`:''}${pending&&LIBRA_CONFIG.onlinePaymentsEnabled?`<button class="button secondary" data-init-payment="${id}" data-method="${['QR_TRANSFER','VNPAY','ONLINE'].includes(order.paymentMethod)?order.paymentMethod:'VNPAY'}">${p.paymentId?'Tạo lại liên kết thanh toán':'Khởi tạo thanh toán'}</button>`:''}<button class="button secondary" data-payment-refresh="${id}">Cập nhật trạng thái</button><p class="form-error" id="payment-error" role="alert"></p><p><a href="#/don-hang">← Về đơn hàng của tôi</a></p></div></section>`;
}
function safeLiveUrl(value){try{const url=new URL(value,LIBRA_CONFIG.apiBaseUrl);return ['http:','https:'].includes(url.protocol)?url.href:'';}catch{return '';}}
const baseRender=render;
render=async function(){
 if(LIBRA_CONFIG.useMock)return baseRender();
 const version=++routeVersion;const [path,query='']=(location.hash.slice(1)||'/').split('?');const params=new URLSearchParams(query);header();
 try{
 if(['/gio-hang','/thanh-toan','/yeu-thich','/don-hang','/dia-chi','/quan-tri','/quan-ly','/nhan-vien'].includes(path)||path.startsWith('/thanh-toan-don/')){if(!user){main.innerHTML=empty('Vui lòng đăng nhập','Đăng nhập để sử dụng tính năng này.','#/dang-nhap','Đăng nhập');return;}}
 if(['/quan-tri','/quan-ly','/nhan-vien'].includes(path)){user=await LibraAPI.me();header();return renderAdmin(version,path);}
 if(path==='/sach'){
  main.innerHTML='<div class="empty" role="status">Đang tìm sách…</div>';const data=await LibraAPI.catalog(params);if(version!==routeVersion)return;mergeBooks(data.items);
  main.innerHTML=catalog(params);const content=main.querySelector('.catalog-layout > div');content.innerHTML=`<div class="results-bar"><span>${data.totalItems} cuốn sách · Trang ${data.page}/${Math.max(1,data.totalPages)}</span><span>Mới nhất</span></div>${data.items.length?`<div class="book-grid catalog-grid">${data.items.map(card).join('')}</div>`:empty('Không có sách phù hợp','Thử tìm kiếm hoặc danh mục khác.')}<div class="pagination">${data.page>1?`<button data-page="${data.page-1}">←</button>`:''}<button aria-current="page">${data.page}</button>${data.page<data.totalPages?`<button data-page="${data.page+1}">→</button>`:''}</div>`;
  main.querySelectorAll('#filter-form .check').forEach(el=>el.remove());document.querySelector('#search').value=params.get('q')||'';
 }else if(path==='/gio-hang'){
  await syncLiveCart();if(version!==routeVersion)return;main.innerHTML=cartPage();await refreshLiveQuote();
 }else if(path==='/thanh-toan'){
  await syncLiveCart();liveAddresses=await LibraAPI.addresses();if(version!==routeVersion)return;if(!liveSelected().length){main.innerHTML=empty('Chưa chọn sách','Chọn sách trong giỏ để tiếp tục.','#/gio-hang','Về giỏ');return;}main.innerHTML=liveCheckout();await refreshLiveQuote();
 }else if(path==='/dia-chi'){
  liveAddresses=await LibraAPI.addresses();if(version!==routeVersion)return;main.innerHTML=`<section class="wrap section">${heading('Sổ địa chỉ')}<div class="admin-books">${liveAddresses.map(a=>`<form class="panel" data-live-address="${a.addressId}"><h3>${esc(a.recipientName)}</h3>${addressFields(a)}<button class="button" type="submit">Lưu địa chỉ</button> <button type="button" class="text-button" data-delete-address="${a.addressId}">Xóa</button><p class="form-error" role="alert"></p></form>`).join('')}<form class="panel" data-live-address="new"><h3>Thêm địa chỉ mới</h3>${addressFields()}<button class="button" type="submit">Thêm địa chỉ</button><p class="form-error" role="alert"></p></form></div></section>`;
 }else if(path==='/don-hang'){await liveOrders(version);
 }else if(/^\/thanh-toan-don\/\d+$/.test(path)){await paymentPage(Number(path.split('/')[2]),version);
 }else{
  if(/^\/sach\/\d+$/.test(path)){mergeBooks([await LibraAPI.product(Number(path.split('/')[2]))]);if(version!==routeVersion)return;}
  if(path==='/yeu-thich'){await syncLiveFavorites();if(version!==routeVersion)return;}
  await baseRender();
  if(path==='/tai-khoan'&&user){const link=document.createElement('a');link.href='#/dia-chi';link.className='button secondary';link.textContent='Sổ địa chỉ';main.querySelector('.account-panel')?.append(link);}
  main.querySelectorAll('.rating').forEach(el=>el.remove());
  if(path==='/'){main.querySelectorAll('a[href*="sort=popular"]').forEach(a=>{a.href='#/sach';a.textContent='Khám phá sách →';});main.querySelectorAll('a[href*="sale=1"]').forEach(a=>a.href='#/sach');}
  if(path==='/chinh-sach')main.innerHTML=`<section class="wrap section prose">${heading('Giao hàng & thanh toán')}<h2>Phí giao hàng</h2><p>Phí vận chuyển 30.000₫, miễn phí cho tiền sách từ 300.000₫. Tổng tiền chính xác và điều kiện khuyến mãi được nhà sách xác nhận ở bước thanh toán.</p><h2>Ưu đãi</h2><p>Nhập mã GIAM10, SALE10 hoặc VIP50K tại giỏ hàng để kiểm tra điều kiện áp dụng.</p><h2>Thanh toán</h2><p>Với COD, bạn thanh toán khi nhận sách. Đơn hàng được ghi nhận trước khi giao, không đồng nghĩa đã thu tiền.</p><h2>Đổi trả</h2><p>Liên hệ nhà sách để xác nhận điều kiện đổi trả trước khi mua.</p></section>`;
 
 }

 document.title=(main.querySelector('h1')?.textContent||'Nhà sách')+' | Libra';
 window.scrollTo(0,0);
 }catch(error){if(version!==routeVersion)return;main.innerHTML=`<section class="wrap section">${heading('Chưa thể tải nội dung')}<p role="alert">${esc(error.message)}</p><button class="button" data-live-retry>Thử lại</button> <a href="#/dang-nhap">Đăng nhập</a></section>`;}
};
async function liveInit(){
 cart=[];favorites=[];user=null;loaded=true;header();document.querySelectorAll('header a[href*="sort=popular"]').forEach(a=>{a.href='#/sach';a.textContent='Khám phá sách';});document.querySelectorAll('header a[href*="sale=1"]').forEach(a=>{a.href='#/sach';a.textContent='Chọn sách';});main.innerHTML='<div class="empty" role="status">Đang kết nối nhà sách…</div>';
 try{user=await LibraAPI.me();books=await LibraAPI.books();const availableCategories=[...new Set(books.map(b=>b.category))];if(availableCategories.length)categories.splice(0,categories.length,...availableCategories);if(user)await Promise.all([syncLiveCart(),syncLiveFavorites()]);await render();}catch(error){main.innerHTML=`<div class="empty"><h1>Chưa kết nối được nhà sách</h1><p>${esc(error.message)}</p><button class="button" data-live-init>Thử kết nối lại</button><p><a href="#/dang-nhap">Đi đến đăng nhập</a></p></div>`;}
}
function intercept(event){event.preventDefault();event.stopImmediatePropagation();}
async function liveAction(button,action){if(liveBusy)return;liveBusy=true;if(button)button.disabled=true;try{await action();}catch(error){toast(error.message);}finally{liveBusy=false;if(button)button.disabled=false;}}
window.addEventListener('libra:unauthorized',()=>{if(LIBRA_CONFIG.useMock)return;user=null;cart=[];favorites=[];liveQuote=null;header();});
document.addEventListener('click',event=>{
 if(LIBRA_CONFIG.useMock)return;const b=event.target.closest('button');if(!b)return;
 const id=Number(b.dataset.add||b.dataset.favorite||b.dataset.remove);
 if(b.dataset.add||b.dataset.favorite||b.dataset.remove){intercept(event);if(!user){location.hash='/dang-nhap';toast('Đăng nhập để lưu giỏ hàng và yêu thích.');return;}liveAction(b,async()=>{
  if(b.dataset.add){await LibraAPI.addCart(id,b.dataset.detail?Number(document.querySelector('#quantity').value):1);await syncLiveCart();toast('Đã thêm sách vào giỏ.');}
  if(b.dataset.favorite){const on=!favorites.includes(id);await LibraAPI.favorite(id,on);await syncLiveFavorites();b.textContent=on?'♥':'♡';b.setAttribute('aria-pressed',String(on));b.classList.toggle('liked',on);if(location.hash.startsWith('#/yeu-thich'))await render();}
  if(b.dataset.remove){const item=cart.find(i=>i.bookId===id);await LibraAPI.removeCart(item.cartItemId);const y=window.scrollY;await render();window.scrollTo({top:y,behavior:'instant'});toast('Đã xóa sách khỏi giỏ.');}
 });return;}
 if(b.id==='logout'){intercept(event);liveAction(b,async()=>{try{await LibraAPI.logout();}finally{user=null;cart=[];favorites=[];coupon='';header();location.hash='/dang-nhap';}});return;}
 if(b.hasAttribute('data-quote-retry')){intercept(event);refreshLiveQuote();return;}
 if(b.hasAttribute('data-live-init')){intercept(event);liveInit();return;}
 if(b.hasAttribute('data-live-retry')){intercept(event);render();return;}
 if(b.dataset.cancelOrder||b.dataset.deleteAddress||b.dataset.initPayment||b.dataset.paymentRefresh){intercept(event);liveAction(b,async()=>{
  if(b.dataset.cancelOrder){await LibraAPI.cancelOrder(b.dataset.cancelOrder);await render();}
  if(b.dataset.deleteAddress){await LibraAPI.removeAddress(b.dataset.deleteAddress);await render();}
  if(b.dataset.initPayment){await LibraAPI.initiate(Number(b.dataset.initPayment),b.dataset.method);await render();}
  if(b.dataset.paymentRefresh)await render();
 });}
},true);
document.addEventListener('change',event=>{
 if(LIBRA_CONFIG.useMock)return;const el=event.target;
 if(el.id==='address-choice'){const box=main.querySelector('#new-address');box.hidden=box.disabled=el.value!=='new';return;}
 if(el.dataset.select||el.id==='select-all'){intercept(event);if(el.id==='select-all')cart.forEach(i=>i.selected=el.checked);else{const item=cart.find(i=>i.bookId===Number(el.dataset.select));if(item)item.selected=el.checked;}updateLiveCartView();return;}
 if(el.dataset.quantity){intercept(event);const item=cart.find(i=>i.bookId===Number(el.dataset.quantity)),n=Number(el.value);if(liveBusy){el.value=item.quantity;return;}if(!Number.isInteger(n)||n<1){el.value=item.quantity;toast('Số lượng phải là số nguyên từ 1.');return;}
 liveAction(el,async()=>{try{await LibraAPI.changeCart(item.cartItemId,n);await syncLiveCart();updateLiveCartView();}catch(error){el.value=item.quantity;throw error;}});}
},true);
document.addEventListener('submit',async event=>{
 if(LIBRA_CONFIG.useMock)return;const form=event.target;
 if(!['auth-form','coupon-form','live-checkout'].includes(form.id)&&!form.dataset.liveAddress)return;intercept(event);
 const button=form.querySelector('button[type=submit]')||form.querySelector('button');if(liveBusy)return;
 liveBusy=true;if(button)button.disabled=true;const errorBox=form.querySelector('.form-error');if(errorBox)errorBox.textContent='';
 try{
 const data=Object.fromEntries(new FormData(form));
 if(form.id==='auth-form'){
  if(form.dataset.register==='true'){if(data.password!==data.confirm)throw new Error('Mật khẩu xác nhận chưa khớp.');await LibraAPI.register({name:data.name.trim(),email:data.email.trim(),password:data.password});location.hash='/dang-nhap';toast('Đăng ký thành công. Bạn hãy đăng nhập.');}
  else{user=await LibraAPI.login({email:data.email.trim(),password:data.password});coupon='';await Promise.all([syncLiveCart(),syncLiveFavorites()]);location.hash=roleHome(user.role);header();}
 }else if(form.id==='coupon-form'){coupon=form.querySelector('#coupon').value.trim().toUpperCase();await refreshLiveQuote();
 }else if(form.dataset.liveAddress){await LibraAPI.saveAddress(addressPayload(form),form.dataset.liveAddress==='new'?null:form.dataset.liveAddress);await render();toast('Đã lưu địa chỉ.');
 }else{
  if(quotePending||!liveQuote||quoteError||!liveSelected().length)throw new Error('Vui lòng đợi nhà sách xác nhận tổng tiền.');
  const items=liveSelected();const quote=await LibraAPI.preview({items,discountCode:coupon||null});if(quote.totalAmount!==liveQuote.totalAmount){liveQuote=quote;drawLiveQuote();throw new Error('Tổng tiền vừa thay đổi. Vui lòng kiểm tra rồi xác nhận lại.');}
  let addressId=Number(data.addressId);if(data.addressId==='new'){const address=await LibraAPI.saveAddress(addressPayload(form));addressId=address.addressId;liveAddresses.push(address);const option=new Option(address.recipientName,addressId,true,true);form.querySelector('#address-choice').add(option);form.querySelector('#new-address').disabled=true;}
  const order=await LibraAPI.createOrder({addressId,items,discountCode:coupon||null,paymentMethod:data.paymentMethod});
  coupon='';liveQuote=null;cart=cart.filter(i=>!items.some(p=>p.productId===i.bookId));saveSelection();header();
  if(data.paymentMethod==='COD'){location.hash='/don-hang';toast('Đã tạo đơn COD. Bạn thanh toán khi nhận hàng.');}
  else{location.hash='/thanh-toan-don/'+order.id;try{await LibraAPI.initiate(order.id,data.paymentMethod);if(location.hash==='#/thanh-toan-don/'+order.id)await render();}catch(error){toast('Đơn đã được tạo, chưa khởi tạo được thanh toán: '+error.message);}}
 }
 }catch(error){if(errorBox)errorBox.textContent=error.message;else toast(error.message);}finally{liveBusy=false;if(button)button.disabled=false;drawLiveQuote();}
},true);
/* Additional live features. Contracts are documented in FEATURES-API.md. */
(function(){
 if(LIBRA_CONFIG.useMock)return;
 const req=(path,method='GET',data)=>LibraAPI.request(path,{method,...(data?{body:JSON.stringify(data)}:{})});
 const featureError=e=>e.status===404||e.status===501?'Tính năng đang chờ backend kết nối. Vui lòng thử lại sau.':e.message;
 let identity=undefined,epoch=0,unread=0,notices=[],noticeBusy=false,chatBusy=false,chatHistory=[];
 const oldHeader=header;
 header=function(){oldHeader();if(!document.querySelector('#libra-features'))return;
  const next=user?.id??null;if(next!==identity){identity=next;epoch++;unread=0;notices=[];chatHistory=[];noticeBusy=false;chatBusy=false;document.querySelector('#ai-messages').innerHTML='<p class="feature-hint">Bạn muốn tìm sách về chủ đề gì? Nhập tên sách, tác giả hoặc thể loại. Mỗi câu hỏi được xử lý riêng.</p>';document.querySelector('#ai-form button').disabled=false;document.querySelector('#notification-list').replaceChildren();document.querySelector('#notification-panel').hidden=true;}
  document.querySelector('#notification-toggle').hidden=!user;
  document.querySelector('#dashboard-link').hidden=!['manager','admin'].includes(user?.role);
  document.querySelector('#notification-count').textContent=unread?String(unread):'';
 };
 function mount(){if(document.querySelector('#libra-features'))return;
 const holder=document.createElement('div');holder.id='libra-features';holder.innerHTML=`<button id="ai-toggle" class="ai-launch" aria-controls="ai-panel" aria-expanded="false">✦ Tư vấn sách</button><section id="ai-panel" class="feature-panel ai-panel" aria-label="Tư vấn sách" hidden><div class="feature-heading"><div><b>✦ Trợ lý đọc sách</b><small>Tìm cuốn sách phù hợp với bạn</small></div><button type="button" data-close-feature="ai-panel" aria-label="Đóng tư vấn">×</button></div><div id="ai-messages" class="ai-messages" role="log" aria-live="polite"></div><form id="ai-form"><label for="ai-question">Bạn đang muốn đọc gì?</label><div><input id="ai-question" maxlength="1000" required placeholder="Ví dụ: văn học, James Clear"><button class="button" type="submit">Gửi</button></div><p id="ai-error" role="alert"></p></form></section><section id="notification-panel" class="feature-panel notification-panel" aria-label="Thông báo" hidden><div class="feature-heading"><b>Thông báo của bạn</b><button type="button" data-close-feature="notification-panel" aria-label="Đóng thông báo">×</button></div><div class="notification-actions"><button type="button" id="notification-refresh">Tải lại</button><button type="button" id="notification-read-all">Đọc tất cả</button></div><div id="notification-list" aria-live="polite"></div></section>`;document.body.append(holder);
 const actions=document.querySelector('.header-actions');const links=document.createElement('span');links.className='feature-header-links';links.innerHTML='<a id="dashboard-link" href="#/dashboard" hidden>Thống kê</a><button id="notification-toggle" type="button" aria-label="Mở thông báo" aria-controls="notification-panel" aria-expanded="false" hidden>🔔 <span id="notification-count"></span></button>';actions.append(links);header();pollNotices();
 }
 function toggle(id,open){const p=document.getElementById(id);p.hidden=!open;document.getElementById(id==='ai-panel'?'ai-toggle':'notification-toggle').setAttribute('aria-expanded',String(open));if(open&&id==='ai-panel')document.querySelector('#ai-question').focus();}
 function drawNotices(){document.querySelector('#notification-count').textContent=unread?String(unread):'';document.querySelector('#notification-read-all').disabled=!unread||noticeBusy;document.querySelector('#notification-list').innerHTML=notices.length?notices.map(n=>`<article class="notification-item ${n.isRead?'':'unread'}"><b>${esc(n.title)}</b><p>${esc(n.message)}</p><small>${n.createdAt?esc(new Date(n.createdAt).toLocaleString('vi-VN')):''}</small>${!n.isRead?`<button type="button" data-read-notice="${esc(n.notificationId)}">Đánh dấu đã đọc</button>`:''}${n.orderId||n.type==='order'||n.type==='payment'?`<a href="${['admin','manager','staff'].includes(user?.role)?'#/nhan-vien':'#/don-hang'}">Xem đơn hàng →</a>`:''}</article>`).join(''):'<p class="feature-hint">Bạn chưa có thông báo nào.</p>';}
 async function pollNotices(manual=false){if(!user||noticeBusy||document.hidden)return;const version=epoch;noticeBusy=true;try{const d=await req('/notifications');if(version!==epoch)return;if(!Array.isArray(d))throw Error('Dữ liệu thông báo chưa đúng định dạng.');notices=d;unread=d.filter(n=>!n.isRead).length;drawNotices();}catch(e){if(version===epoch&&manual)document.querySelector('#notification-list').innerHTML=`<p class="feature-hint" role="alert">${esc(featureError(e))}</p>`;}finally{if(version===epoch){noticeBusy=false;document.querySelector('#notification-read-all').disabled=!unread;}}}
 document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b)return;
 if(b.id==='ai-toggle')toggle('ai-panel',document.querySelector('#ai-panel').hidden);
 if(b.id==='notification-toggle'){const open=document.querySelector('#notification-panel').hidden;toggle('notification-panel',open);if(open)pollNotices(true);}
 if(b.dataset.closeFeature){toggle(b.dataset.closeFeature,false);document.getElementById(b.dataset.closeFeature==='ai-panel'?'ai-toggle':'notification-toggle').focus();}
 if(b.id==='notification-refresh')pollNotices(true);
 if(b.dataset.readNotice||b.id==='notification-read-all'){if(noticeBusy||!user)return;const version=epoch;noticeBusy=true;b.disabled=true;try{await req(b.dataset.readNotice?'/notifications/'+encodeURIComponent(b.dataset.readNotice)+'/read':'/notifications/mark-all-read','PUT');}catch(error){if(version===epoch)toast(featureError(error));}finally{if(version===epoch){noticeBusy=false;await pollNotices(true);}b.disabled=false;}}
 });
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){for(const id of ['ai-panel','notification-panel'])if(!document.getElementById(id)?.hidden){toggle(id,false);document.getElementById(id==='ai-panel'?'ai-toggle':'notification-toggle').focus();}}});
 document.addEventListener('submit',async e=>{if(e.target.id!=='ai-form')return;e.preventDefault();if(chatBusy)return;const input=document.querySelector('#ai-question'),message=input.value.trim();if(!message)return;const version=epoch;chatBusy=true;const button=e.target.querySelector('button'),log=document.querySelector('#ai-messages'),error=document.querySelector('#ai-error');button.disabled=true;error.textContent='';const bubble=document.createElement('p');bubble.className='chat-user';bubble.textContent=message;log.append(bubble);const waiting=document.createElement('p');waiting.className='feature-hint';waiting.textContent='Đang tìm sách phù hợp…';log.append(waiting);log.scrollTop=log.scrollHeight;
 try{const d=await req('/ai/chat','POST',{message});if(version!==epoch)return;if(typeof d?.response!=='string'||(d.relatedProducts!=null&&!Array.isArray(d.relatedProducts)))throw Error('Phản hồi tư vấn chưa đúng định dạng.');const ids=[...new Set((d.relatedProducts||[]).map(b=>b.productId))].filter(Number.isSafeInteger).slice(0,4);const results=await Promise.allSettled(ids.map(id=>LibraAPI.product(id)));if(version!==epoch)return;const recommendations=results.filter(r=>r.status==='fulfilled').map(r=>r.value);mergeBooks(recommendations);const reply=document.createElement('div');reply.className='chat-answer';reply.innerHTML=`<p>${esc(d.response)}</p>${recommendations.map(b=>`<a class="chat-book" href="#/sach/${b.id}"><b>${esc(b.title)}</b><span>${esc(b.author)} · ${money(b.price)} · ${b.stock>0?'Còn hàng':'Hết hàng'}</span></a>`).join('')}`;log.append(reply);chatHistory.push({role:'user',content:message},{role:'assistant',content:d.response});chatHistory=chatHistory.slice(-10);input.value='';}catch(err){if(version===epoch)error.textContent=featureError(err);}finally{waiting.remove();if(version===epoch){chatBusy=false;button.disabled=false;log.scrollTop=log.scrollHeight;}}});
 const oldRender=render;render=async function(){if((location.hash.slice(1).split('?')[0])!=='/dashboard')return oldRender();const version=++routeVersion;header();if(!user||!['admin','manager'].includes(user.role)){main.innerHTML=empty('Bạn không có quyền xem thống kê','Khu vực dành cho quản lý và quản trị.','#/tai-khoan','Về tài khoản');return;}
 const p=new URLSearchParams(location.hash.split('?')[1]||'');const today=new Date(),localDate=d=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;const from=p.get('from')||localDate(new Date(today.getFullYear(),today.getMonth(),1)),to=p.get('to')||localDate(today);
 main.innerHTML=`<section class="wrap section">${heading('Thống kê kinh doanh','Số liệu được tổng hợp từ các giao dịch của nhà sách.')}<a href="${roleHome(user.role)}">← Khu vực làm việc</a><form id="dashboard-filter" class="work-filter"><label>Từ ngày<input type="date" name="from" required value="${esc(from)}"></label><label>Đến ngày<input type="date" name="to" required value="${esc(to)}"></label><button class="button">Xem thống kê</button></form><div id="dashboard-content" role="status">Đang tải số liệu…</div></section>`;document.title='Thống kê | Libra';window.scrollTo(0,0);
 try{const raw=await req('/dashboard?'+new URLSearchParams({fromDate:from+'T00:00:00',toDate:to+'T23:59:59.999',topProducts:'5',lowStockThreshold:'5'}));const d=raw&&{revenue:raw.totalRevenue,orderCount:raw.totalOrders,customerCount:raw.totalCustomers,bestSellers:raw.bestSellingProducts,lowStock:raw.lowStockProducts,daily:raw.dailyRevenue};if(version!==routeVersion)return;if(!d||!['revenue','orderCount','customerCount'].every(k=>Number.isFinite(d[k]))||!['bestSellers','lowStock'].every(k=>Array.isArray(d[k])))throw Error('Dữ liệu thống kê chưa đúng định dạng.');const table=(rows,stock)=>rows.length?`<div class="dashboard-table"><table><thead><tr><th>Sách</th><th>${stock?'Tồn kho':'Đã bán'}</th></tr></thead><tbody>${rows.map(b=>`<tr><td><a href="#/sach/${Number(b.productId)}">${esc(b.title)}</a></td><td>${esc(stock?b.stockQuantity:b.quantitySold)}</td></tr>`).join('')}</tbody></table></div>`:'<p>Chưa có dữ liệu.</p>';document.querySelector('#dashboard-content').innerHTML=metrics([['Doanh thu',money(d.revenue)],['Đơn hàng',d.orderCount],['Tổng tài khoản hệ thống',d.customerCount],['Sách sắp hết',d.lowStock.length]])+`<div class="panel"><h2>Doanh thu ngày cuối kỳ</h2>${d.daily?`<p>${esc(String(d.daily.date).slice(0,10))}</p><h3>${money(d.daily.revenue)}</h3><p>${esc(d.daily.orderCount)} đơn hàng</p>`:'<p>Chưa ghi nhận doanh thu cho ngày cuối kỳ.</p>'}</div><div class="dashboard-columns"><section class="panel"><h2>Sách bán chạy</h2>${table(d.bestSellers,false)}</section><section class="panel"><h2>Sách sắp hết</h2>${table(d.lowStock,true)}</section></div>`;}catch(e){if(version===routeVersion)document.querySelector('#dashboard-content').innerHTML=`<div class="panel"><p role="alert">${esc(featureError(e))}</p><button class="button" data-live-retry>Thử lại</button></div>`;}};
 document.addEventListener('submit',e=>{if(e.target.id!=='dashboard-filter')return;e.preventDefault();const d=new FormData(e.target);if(d.get('from')>d.get('to')){toast('Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.');return;}const hash='#/dashboard?'+new URLSearchParams(d);if(location.hash===hash)render();else location.hash=hash;});
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();setInterval(()=>pollNotices(),60000);
})();

