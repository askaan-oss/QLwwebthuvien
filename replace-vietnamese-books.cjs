const fs=require('fs');
const groups={
'Tài chính':[
['Nhà đầu tư thông minh','Benjamin Graham','Đầu tư giá trị, phân tích doanh nghiệp và kiểm soát rủi ro tài chính.'],['Tâm lý học về tiền','Morgan Housel','Tài chính cá nhân, tiết kiệm và cách cảm xúc ảnh hưởng tới quyết định về tiền bạc.'],['Người giàu có nhất thành Babylon','George S. Clason','Những câu chuyện về tiết kiệm, quản lý tiền và xây dựng tài sản.'],['Bí mật tư duy triệu phú','T. Harv Eker','Tư duy tài chính cá nhân và thói quen quản lý tiền bạc.'],['Bước đi ngẫu nhiên trên phố Wall','Burton G. Malkiel','Thị trường chứng khoán, đầu tư dài hạn và phân bổ danh mục.']],
'Kinh doanh':[
['Khởi nghiệp tinh gọn','Eric Ries','Khởi nghiệp, thử nghiệm sản phẩm và học hỏi từ khách hàng.'],['Không đến một','Peter Thiel, Blake Masters','Khởi nghiệp công nghệ và xây dựng doanh nghiệp tạo ra giá trị mới.'],['Từ tốt đến vĩ đại','Jim Collins','Nghiên cứu về lãnh đạo và phát triển doanh nghiệp bền vững.'],['Để xây dựng doanh nghiệp hiệu quả','Michael E. Gerber','Xây dựng quy trình và hệ thống vận hành cho doanh nghiệp nhỏ.'],['Bắt đầu với câu hỏi tại sao','Simon Sinek','Lãnh đạo và truyền cảm hứng từ mục đích của tổ chức.']],
'Văn học':[
['Kiêu hãnh và định kiến','Jane Austen','Tình yêu, gia đình và định kiến xã hội trong văn học Anh.'],['Jane Eyre','Charlotte Brontë','Hành trình trưởng thành và khát vọng tự chủ của một người phụ nữ.'],['Đại gia Gatsby','F. Scott Fitzgerald','Giấc mơ, tình yêu và sự giàu có trong xã hội Mỹ.'],['Những người phụ nữ bé nhỏ','Louisa May Alcott','Câu chuyện trưởng thành, gia đình và ước mơ của bốn chị em.'],['Ông già và biển cả','Ernest Hemingway','Cuộc vật lộn của một ngư dân với biển cả và giới hạn bản thân.']],
'Tâm lý':[
['Tư duy nhanh và chậm','Daniel Kahneman','Tâm lý học nhận thức và những sai lệch trong quyết định.'],['Những đòn tâm lý trong thuyết phục','Robert B. Cialdini','Tâm lý học hành vi và các nguyên tắc thuyết phục.'],['Trí tuệ xúc cảm','Daniel Goleman','Nhận biết cảm xúc và vai trò của cảm xúc trong cuộc sống.'],['Dòng chảy','Mihaly Csikszentmihalyi','Trạng thái tập trung sâu và trải nghiệm tối ưu trong tâm lý học.'],['Giả thuyết hạnh phúc','Jonathan Haidt','Tìm hiểu hạnh phúc qua tâm lý học và các tư tưởng cổ điển.']],
'Kỹ năng sống':[
['Làm ra làm chơi ra chơi','Cal Newport','Làm việc sâu, tăng khả năng tập trung và giảm xao nhãng.'],['Nghệ thuật theo đuổi sự tối giản','Greg McKeown','Lựa chọn điều quan trọng và quản lý ưu tiên trong cuộc sống.'],['Hoàn thành mọi việc không hề khó','David Allen','Sắp xếp công việc và quản lý thời gian cá nhân.'],['Tâm lý học thành công','Carol S. Dweck','Tư duy phát triển và thái độ học hỏi trước thử thách.'],['Sức mạnh của thói quen','Charles Duhigg','Cách hình thành thói quen và thay đổi hành vi.']],
'Công nghệ':[
['Lập trình và cuộc sống','Jeff Atwood','Góc nhìn về lập trình, phát triển phần mềm và công việc của lập trình viên.'],['Cuộc cách mạng một cọng rơm','Masanobu Fukuoka','Nông nghiệp tự nhiên, sinh thái và cách con người tương tác với đất đai.'],['AI 2041','Kai-Fu Lee, Chen Qiufan','Trí tuệ nhân tạo và các kịch bản công nghệ trong tương lai.'],['Các thế giới song song','Michio Kaku','Vật lý, vũ trụ học và những giả thuyết về không gian.'],['Cuộc cách mạng công nghiệp lần thứ tư','Klaus Schwab','Công nghệ mới và tác động tới kinh tế, xã hội và lao động.']],
'Khoa học':[
['Lược sử thời gian','Stephen Hawking','Vũ trụ học, thời gian, hố đen và các câu hỏi vật lý.'],['Vũ trụ','Carl Sagan','Hành trình khám phá thiên văn và vị trí của con người trong vũ trụ.'],['Gen vị kỷ','Richard Dawkins','Tiến hóa, di truyền học và cách nhìn từ góc độ gen.'],['Lược sử vạn vật','Bill Bryson','Khám phá các câu chuyện khoa học về Trái Đất và sự sống.'],['Đời sống bí ẩn của cây','Peter Wohlleben','Sinh thái rừng và những tương tác trong thế giới thực vật.']],
'Lịch sử':[
['Súng, vi trùng và thép','Jared Diamond','Lịch sử các nền văn minh qua môi trường và địa lý.'],['Những con đường tơ lụa','Peter Frankopan','Lịch sử giao thương và giao thoa giữa các nền văn minh.'],['Việt Nam sử lược','Trần Trọng Kim','Khái quát lịch sử Việt Nam qua các thời kỳ.'],['Nhật ký Anne Frank','Anne Frank','Nhật ký về cuộc sống ẩn náu trong Thế chiến thứ hai.'],['Đại Việt sử ký toàn thư','Ngô Sĩ Liên và các sử thần triều Lê','Bộ sử ghi chép lịch sử Việt Nam thời kỳ cổ và trung đại.']],
'Văn hóa Việt Nam':[
['Việt Nam phong tục','Phan Kế Bính','Tìm hiểu phong tục, tập quán và đời sống văn hóa Việt Nam.'],['Thương nhớ mười hai','Vũ Bằng','Ký ức về phong vị, mùa và đời sống văn hóa miền Bắc.'],['Hà Nội băm sáu phố phường','Thạch Lam','Những trang viết về phố phường, con người và ẩm thực Hà Nội.'],['Miếng ngon Hà Nội','Vũ Bằng','Tản văn về ẩm thực và nếp sống Hà Nội.'],['Đất lề quê thói','Nhất Thanh','Khảo cứu phong tục và tập quán trong đời sống người Việt.']],
'Thiếu nhi':[
['Charlotte và Wilbur','E. B. White','Câu chuyện thiếu nhi về tình bạn giữa một chú lợn và một cô nhện.'],['Matilda','Roald Dahl','Một cô bé ham đọc sách với trí thông minh và khả năng đặc biệt.'],['Charlie và nhà máy sô cô la','Roald Dahl','Chuyến phiêu lưu kỳ thú trong một nhà máy sô cô la.'],['Khu vườn bí mật','Frances Hodgson Burnett','Tình bạn và sự trưởng thành qua việc chăm sóc một khu vườn.'],['Phù thủy xứ Oz','L. Frank Baum','Hành trình phiêu lưu của Dorothy và những người bạn.']]
};
const old=JSON.parse(fs.readFileSync('books-50-catalog.json','utf8').replace(/^\uFEFF/,''));
const rows=Object.entries(groups).flatMap(([category,books])=>books.map(([title,author,description])=>({title,author,category,description:description+' Danh mục bản tiếng Việt; giá và tồn kho phục vụ demo.',imageUrl:null})));
rows[26].category='Nông nghiệp';rows[28].category='Khoa học';
fs.writeFileSync('books-50-vietnamese.json',JSON.stringify(rows,null,2));
(async()=>{const base='http://localhost:5160/api';let token='';async function api(path,method='GET',body){const r=await fetch(base+path,{method,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},body:body?JSON.stringify(body):undefined});const j=await r.json();if(!r.ok)throw Error(j.message||r.status);return j.data;}
const list=(await api('/Products?pageSize=100')).items;
const plan=rows.map((row,i)=>{const b=list.find(b=>b.title===old[i].title)||list.find(b=>b.title===row.title&&b.author===row.author);if(!b)throw Error('Missing '+old[i].title);return {id:b.productId,before:b,after:{...b,...row,publisher:null,isbn:null}}});
if(new Set(plan.map(p=>p.id)).size!==50)throw Error('Duplicate IDs');
fs.writeFileSync('books-50-vietnamese-backup.json',JSON.stringify(plan,null,2));
token=(await api('/Auth/login','POST',{email:process.env.LIBRA_SEED_EMAIL,password:process.env.LIBRA_SEED_PASSWORD})).token;
for(const p of plan)await api('/Products/'+p.id,'PUT',p.after);
const final=(await api('/Products?pageSize=100')).items;console.log(JSON.stringify({updated:plan.length,total:final.length,verified:plan.every(p=>final.some(b=>b.productId===p.id&&b.title===p.after.title))}));
})().catch(e=>{console.error(e.message);process.exitCode=1});
