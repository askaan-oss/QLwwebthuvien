import fs from 'node:fs/promises';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const dir='D:/QL dự án nhóm/work', output='D:/QL dự án nhóm/output';
const src=JSON.parse(await fs.readFile(`${dir}/source_tables.json`,'utf8'));
const acts=src[5].slice(1).map(([id,name,pre,t])=>({id,name,pre:pre==='-'?[]:pre.split(','),te:Number(t.replace(',','.'))}));
const wb=Workbook.create();
const cp=wb.worksheets.add('CPM'), ga=wb.worksheets.add('Gantt'), pe=wb.worksheets.add('PERT'), em=wb.worksheets.add('EMV');
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
function val(sh,a,v){sh.getRange(a).values=[[v]];}
function form(sh,a,v){sh.getRange(a).formulas=[[v]];}
function setup(sh,range,title){sh.showGridLines=false;sh.getRange(range).format.font={name:'Arial',size:10,color:'#202D38'};sh.getRange(range).format.rowHeight=25;sh.getRange(range).format.verticalAlignment='center';val(sh,'A2',title);sh.getRange('A2').format.font={name:'Arial',size:15,bold:true};}
function head(sh,range,values){sh.getRange(range).values=[values];sh.getRange(range).format={fill:'#294B63',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeight:36};}
function band(sh,first,last,end){for(let r=first;r<=last;r++)if(r%2===0)sh.getRange(`A${r}:${end}${r}`).format.fill='#F1F5F8';}
function widths(sh,arr,last){arr.forEach((w,i)=>sh.getRange(`${col(i+1)}1:${col(i+1)}${last}`).format.columnWidth=w);}
setup(pe,'A1:L32','PERT và dữ liệu đầu vào');widths(pe,[8,30,14,12,10,10,10,12,13,13,14,14],32);
val(pe,'A4','Nguồn: bao_cao_tuan_1_4.docx, Activity List tuần 4; TE nguồn đã làm tròn hai chữ số.');
val(pe,'A5','Ô vàng O–M–P là ước lượng AI đề xuất, chưa được nhóm xác nhận. Đơn vị: ngày làm việc.');
val(pe,'A6','TE = (O + 4M + P) / 6; phương sai = ((P − O) / 6)^2. Không làm tròn khi tính.');
val(pe,'A7','Mục tiêu tối ưu lấy từ bảng nguồn cho G, J, N, O; ô trống nghĩa là giữ thời lượng đang dùng.');
head(pe,'A9:L9',['Mã','Hoạt động','Tiền nhiệm','TE nguồn','O đề xuất','M đề xuất','P đề xuất','TE PERT','Phương sai','Lệch nguồn','TE tối ưu','TE đang dùng']);
const proposals=[];
for(let i=0;i<acts.length;i++){
 const a=acts[i],r=10+i;let trip;
 if(a.te===3.17)trip=[2,3,5];else if(a.te===4.17)trip=[3,4,6];else if(a.te===1.17)trip=[0.5,1,2.5];else if(a.te===6)trip=[4,6,8];else trip=[a.te-1,a.te,a.te+1];
 proposals.push({id:a.id,name:a.name,o:trip[0],m:trip[1],p:trip[2],te:(trip[0]+4*trip[1]+trip[2])/6,variance:((trip[2]-trip[0])/6)**2});
 pe.getRange(`A${r}:G${r}`).values=[[a.id,a.name,a.pre.join(',')||'—',a.te,...trip]];
 form(pe,`H${r}`,`=IF(COUNT(E${r}:G${r})<>3,"Thiếu OMP",IF(AND(E${r}>0,E${r}<=F${r},F${r}<=G${r}),(E${r}+4*F${r}+G${r})/6,"Sai OMP"))`);
 form(pe,`I${r}`,`=IF(ISNUMBER(H${r}),((G${r}-E${r})/6)^2,"n.a.")`);
 form(pe,`J${r}`,`=IF(ISNUMBER(H${r}),H${r}-D${r},"n.a.")`);
 if(['G','J','N'].includes(a.id))val(pe,`K${r}`,3);if(a.id==='O')val(pe,`K${r}`,2);
 form(pe,`L${r}`,`=IF('CPM'!$B$4=1,D${r},IF('CPM'!$B$4=2,H${r},"Chọn 1 hoặc 2"))`);
}
band(pe,10,26,'L');pe.getRange('E10:G26').format.fill='#FFF2CC';pe.getRange('K10:K26').format.fill='#FFF2CC';pe.getRange('D10:L26').setNumberFormat('0.00');pe.getRange('J10:J26').setNumberFormat('0.0000');
val(pe,'A29','Bộ O–M–P này là phương án bổ sung; nhiều bộ ba khác nhau có thể cho cùng TE.');
val(pe,'A32','Nhóm 11 có 5 thành viên, thời gian 9 tuần theo xác nhận của người học.');
val(pe,'A30','Tiền nhiệm là mạng cố định của báo cáo. Nếu đổi mạng, cần cập nhật công thức ES/LF ở CPM.');
pe.freezePanes.freezeRows(9);
setup(cp,'A1:K55','Nhóm 11  Lịch dự án website thư viện');widths(cp,[9,34,16,12,12,12,12,12,12,15,11],55);
val(cp,'A4','Chế độ');val(cp,'B4',1);cp.getRange('B4').format.fill='#FFF2CC';cp.getRange('B4').dataValidation={rule:{type:'list',values:['1','2']}};
val(cp,'C4','1 = TE nguồn; 2 = PERT đề xuất');val(cp,'A5','Quỹ ngày');val(cp,'B5',45);cp.getRange('B5').format.fill='#FFF2CC';val(cp,'C5','9 tuần × 5 ngày theo cập nhật của nhóm; chưa trừ ngày nghỉ.');
val(cp,'G4','Cơ sở');form(cp,'H4','=IF(COUNT(D10:D26)=17,MAX(F10:F26),"Thiếu dữ liệu")');
val(cp,'G5','Tối ưu');form(cp,'H5','=IF(COUNT(D34:D50)=17,MAX(F34:F50),"Thiếu dữ liệu")');
val(cp,'I4','Rút ngắn');form(cp,'J4','=IF(AND(ISNUMBER(H4),ISNUMBER(H5)),H4-H5,"n.a.")');
val(cp,'I5','Dự phòng');form(cp,'J5','=IF(AND(ISNUMBER(H4),ISNUMBER(B5)),B5-H4,"n.a.")');cp.getRange('H4:J5').setNumberFormat('0.00');
val(cp,'A7','CƠ SỞ  Các ô Găng = Có xác định đường găng; ES bắt đầu từ 0.');
const headers=['Mã','Hoạt động','Tiền nhiệm','TE','ES','EF','LS','LF','Slack','Găng','Cờ găng'];
head(cp,'A9:K9',headers);head(cp,'A33:K33',headers);val(cp,'A31','TỐI ƯU  Áp dụng thời lượng mục tiêu G, J, N và O rồi tính lại toàn mạng.');
for(const start of [10,34]){
 const end=start+16;const rowof=id=>start+acts.findIndex(a=>a.id===id);
 for(let i=0;i<acts.length;i++){
  const a=acts[i],r=start+i,pr=10+i;
  cp.getRange(`A${r}:C${r}`).values=[[a.id,a.name,a.pre.join(',')||'—']];
  form(cp,`D${r}`,start===10?`='PERT'!L${pr}`:`=IF('PERT'!K${pr}="",'PERT'!L${pr},'PERT'!K${pr})`);
  const valid=`COUNT($D$${start}:$D$${end})=17`;
  const es=a.pre.length?`MAX(${a.pre.map(id=>`F${rowof(id)}`).join(',')})`:'0';
  const succ=acts.filter(x=>x.pre.includes(a.id));const lf=succ.length?`MIN(${succ.map(x=>`G${rowof(x.id)}`).join(',')})`:`MAX($F$${start}:$F$${end})`;
  form(cp,`E${r}`,`=IF(${valid},${es},"n.a.")`);form(cp,`F${r}`,`=IF(${valid},E${r}+D${r},"n.a.")`);
  form(cp,`H${r}`,`=IF(${valid},${lf},"n.a.")`);form(cp,`G${r}`,`=IF(${valid},H${r}-D${r},"n.a.")`);
  form(cp,`I${r}`,`=IF(${valid},G${r}-E${r},"n.a.")`);form(cp,`J${r}`,`=IF(${valid},IF(ABS(I${r})<0.000001,"Có","Không"),"n.a.")`);form(cp,`K${r}`,`=IF(${valid},IF(ABS(I${r})<0.000001,1,0),"n.a.")`);
 }
 band(cp,start,end,'K');cp.getRange(`D${start}:I${end}`).setNumberFormat('0.00');cp.getRange(`A${start}:K${end}`).conditionalFormats.addCustom(`=$J${start}="Có"`,{fill:'#E0EAF1'});
}
val(cp,'A28','Đường găng nguồn: A–C–D–G–I–J–K–M–N–O–P–Q. Khi sửa thời lượng, xem lại cột Găng.');
val(cp,'A52','Lịch CPM chưa san bằng nguồn lực. Chia việc song song chỉ có hiệu lực khi đủ người hỗ trợ.');
val(cp,'A53','Với PERT đề xuất, cơ sở = 37,00 ngày và tối ưu = 32,50 ngày; lệch nguồn do làm tròn TE.');
val(cp,'A54','Độ lệch chuẩn chỉ tính cho đường găng ban đầu của PERT đề xuất; giả định các thời lượng độc lập.');
val(cp,'A55','Sigma');const path=['A','C','D','G','I','J','K','M','N','O','P','Q'];
form(cp,'B55',`=IF(COUNT('PERT'!I10:I26)=17,SQRT(SUM(${path.map(id=>`'PERT'!I${10+acts.findIndex(a=>a.id===id)}`).join(',')})),"n.a.")`);cp.getRange('B55').setNumberFormat('0.00');cp.freezePanes.freezeRows(9);
setup(ga,'A1:AZ49','Gantt  Ngày làm việc từ lúc khởi động');widths(ga,[8,30,11,11,11,3,...Array(45).fill(3.3)],49);
val(ga,'A4','Chế độ');form(ga,'B4',`=IF('CPM'!B4=1,"TE nguồn","PERT đề xuất")`);val(ga,'D4','Đậm: găng; nhạt: có dự trữ. Mỗi cột là một ngày, kể cả phần ngày có công việc.');
val(ga,'A6','CƠ SỞ');val(ga,'A28','TỐI ƯU');
for(const [hrow,start,cpstart] of [[7,8,10],[29,30,34]]){
 head(ga,`A${hrow}:E${hrow}`,['Mã','Hoạt động','ES','EF','Slack']);
 for(let day=1;day<=45;day++)val(ga,`${col(day+6)}${hrow}`,day);
 ga.getRange(`G${hrow}:AY${hrow}`).format={fill:'#294B63',font:{name:'Arial',size:10,color:'#FFFFFF'},horizontalAlignment:'center'};
 for(let i=0;i<17;i++){
  const r=start+i,cr=cpstart+i;
  ga.getRange(`A${r}:E${r}`).formulas=[[`='CPM'!A${cr}`,`='CPM'!B${cr}`,`='CPM'!E${cr}`,`='CPM'!F${cr}`,`='CPM'!I${cr}`]];
  ga.getRange(`G${r}:AY${r}`).formulas=[Array.from({length:45},(_,j)=>`=IF(AND(ISNUMBER($C${r}),ISNUMBER($D${r})),IF(AND(${col(j+7)}$${hrow}-1<$D${r},${col(j+7)}$${hrow}>$C${r}),IF(ABS($E${r})<0.000001,2,1),0),0)`)];
 }
 band(ga,start,start+16,'E');ga.getRange(`C${start}:E${start+16}`).setNumberFormat('0.00');const grid=ga.getRange(`G${start}:AY${start+16}`);grid.setNumberFormat(';;;');grid.conditionalFormats.add('cellIs',{operator:'equal',formula:2,format:{fill:'#294B63'}});grid.conditionalFormats.add('cellIs',{operator:'equal',formula:1,format:{fill:'#A8BECF'}});
}
val(ga,'A48','Nếu EF vượt 45, kéo dài lưới Gantt; thời lượng chính xác xem CPM.');ga.freezePanes.freezeRows(7);ga.freezePanes.freezeColumns(2);
setup(em,'A1:E16','Chi phí rủi ro kỳ vọng');widths(em,[31,15,24,24,25],16);
val(em,'A4','Nguồn: bao_cao_tuan_1_4.docx, bảng EMV tuần 4. Đây là số liệu minh họa.');
head(em,'A6:D6',['Rủi ro','Xác suất','Tác động VND','EMV VND']);
src[7].slice(1).forEach((r,i)=>{const row=7+i;em.getRange(`A${row}:C${row}`).values=[[r[0],Number(r[1].replace('%',''))/100,Number(r[2].replaceAll('.','').replace('đ',''))]];form(em,`D${row}`,`=B${row}*C${row}`);});
band(em,7,12,'D');em.getRange('B7:B12').setNumberFormat('0%');em.getRange('C7:D13').setNumberFormat('#,##0');val(em,'A13','Tổng EMV');form(em,'D13','=SUM(D7:D12)');em.getRange('A13:D13').format.font.bold=true;val(em,'A15','EMV không phải ngân sách dự án hoặc chi phí đã phát sinh.');
wb.recalculate();
function read(sh,a){return sh.getRange(a).values[0][0];}
function near(x,y,label){if(Math.abs(x-y)>1e-7)throw Error(`${label}: ${x} != ${y}`);}
near(read(cp,'H4'),37.02,'source baseline');near(read(cp,'H5'),32.51,'source optimized');near(read(em,'D13'),2825000,'EMV');
val(cp,'B4',2);wb.recalculate();near(read(cp,'H4'),37,'PERT baseline');near(read(cp,'H5'),32.5,'PERT optimized');
const old=read(pe,'E10');val(pe,'E10',null);wb.recalculate();if(typeof read(cp,'H4')==='number')throw Error('Missing O input was masked');
val(pe,'E10',old);val(pe,'G10',5);wb.recalculate();near(read(cp,'H4'),37+1/6,'input sensitivity');val(pe,'G10',4);val(cp,'B4',1);wb.recalculate();
const err=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:30},summary:'formula errors'});console.log(err.ndjson);
console.log(JSON.stringify({baseline:read(cp,'H4'),optimized:read(cp,'H5'),sigma:read(cp,'B55'),emv:read(em,'D13')}));
await fs.writeFile(`${dir}/pert_proposals.json`,JSON.stringify(proposals,null,2));
await fs.writeFile(`${dir}/schedule_verification.json`,JSON.stringify({baseline:read(cp,'H4'),optimized:read(cp,'H5'),sigma:read(cp,'B55'),emv:read(em,'D13'),checks:['source CPM','proposed PERT CPM','blank O guard','P sensitivity','EMV']}));
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(`${output}/QLDA_Nhom11_LichDuAn.xlsx`);
for(const [name,range] of [['CPM','A2:K28'],['CPM','A31:K55'],['PERT','A2:L30'],['Gantt','A2:AY25'],['Gantt','A28:AY48'],['EMV','A2:D15']]){
 try{const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(`${dir}/${name}_${range.startsWith('A31')||range.startsWith('A28')?'2':'1'}.png`,new Uint8Array(await blob.arrayBuffer()));}catch(e){console.log('RENDER '+name+': '+e.message);}
}
