from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image,ImageDraw
w=Path('work/report-final');out=w/'pages';out.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(w/'report-qa.pdf')
texts=[]
for i,page in enumerate(pdf):
 text=page.get_textpage().get_text_range();texts.append(f'PAGE {i+1}\n{text}')
 im=page.render(scale=1.25).to_pil();im.save(out/f'page-{i+1}.png')
for start in range(0,len(pdf),8):
 sheet=Image.new('RGB',(1600,2260),'#bbbbbb');dr=ImageDraw.Draw(sheet)
 for j in range(start,min(start+8,len(pdf))):
  im=Image.open(out/f'page-{j+1}.png');im.thumbnail((390,535));x=(j-start)%4*400;y=(j-start)//4*1130
  # two rows of four pages with space used for larger image height
  y=(j-start)//4*565;sheet.paste(im,(x,y+25));dr.text((x+5,y+5),str(j+1),fill='black')
 sheet.crop((0,0,1600,1130)).save(out/f'sheet-{start+1}.jpg')
(w/'pdf-text.txt').write_text('\n\n'.join(texts),encoding='utf-8')
print('pages',len(pdf))
