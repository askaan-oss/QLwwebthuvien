from pathlib import Path
p=Path('work/report-final/build_report.py');s=p.read_text(encoding='utf-8')
s=s.replace("import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nfrom matplotlib.patches import FancyBboxPatch",'from PIL import ImageDraw, ImageFont\nimport math')
a=s.index("plt.rcParams");b=s.index('\ndef chapter3',a)
s=s[:a]+'''def network(path,ds,ps,vals):
 pos={0:(120,260),1:(390,260),2:(660,260),3:(660,450),4:(660,70),5:(930,260),6:(1200,450),7:(1200,70),8:(1470,260),9:(1740,260)}
 im=Image.new('RGB',(1880,530),'white');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
 for j,pre in enumerate(ps):
  for i in pre:
   x,y=pos[i];xx,yy=pos[j];start=(x+105,y);end=(xx-105,yy);dr.line([start,end],fill='#77808A',width=3)
   ang=math.atan2(end[1]-start[1],end[0]-start[0]);dr.polygon([end,(end[0]-14*math.cos(ang-.4),end[1]-14*math.sin(ang-.4)),(end[0]-14*math.cos(ang+.4),end[1]-14*math.sin(ang+.4))],fill='#77808A')
 for i,(x,y) in pos.items():
  critical=vals[2][i]==vals[0][i];dr.rounded_rectangle((x-105,y-50,x+105,y+50),12,fill='#FFF0DA' if critical else '#F0F3F6',outline='#B66B13' if critical else '#8693A0',width=2)
  dr.text((x,y-24),f'N{i+1} | {ds[i]} ngày',font=font,fill='black',anchor='mm');dr.text((x,y+20),f'ES {vals[0][i]}  EF {vals[1][i]}',font=font,fill='black',anchor='mm')
 im.save(path)
network(W/'cpm-base.png',dur,pred,base);network(W/'cpm-opt.png',optDur,optPred,opt)
im=Image.new('RGB',(1800,1000),'white');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27)
for day in range(0,65,4):
 x=450+day*20;dr.line((x,70,x,875),fill='#DDDDDD',width=2);dr.text((x,905),str(day),font=font,fill='black',anchor='mm')
for i in range(10):
 y=100+i*76;dr.text((20,y+15),f'N{i+1} {names[i]}',font=font,fill='black');dr.rectangle((450+base[0][i]*20,y,450+base[1][i]*20,y+24),fill='#919CB0');dr.rectangle((450+opt[0][i]*20,y+29,450+opt[1][i]*20,y+53),fill='#EBA74E')
dr.text((450,15),'Xám: mạng gốc 64 ngày     Cam: phương án 48 ngày',font=font,fill='black');dr.text((700,950),'Ngày làm việc tính từ thời điểm bắt đầu',font=font,fill='black');im.save(W/'gantt-corrected.png')
''' +s[b:]
s=s.replace(" tbl([['Nội dung','Mạng gốc','Phương án đề xuất']], [6,5,5])\n",'')
p.write_text(s,encoding='utf-8')
