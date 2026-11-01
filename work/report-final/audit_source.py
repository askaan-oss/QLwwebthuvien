from docx import Document
from docx.oxml.ns import qn
from pathlib import Path
d=Document('work/report-final/source.docx')
out=Path('work/report-final')
(out/'tables.txt').write_text('\n\n'.join('TABLE '+str(i)+'\n'+'\n'.join(' | '.join(c.text for c in r.cells) for r in t.rows) for i,t in enumerate(d.tables)),encoding='utf-8')
for i,p in enumerate(d.paragraphs):
 ids=[x.get(qn('r:id')) for x in p._p.xpath('.//*[local-name()="imagedata"]')]
 if ids: print(i,ids)
for k,r in d.part.rels.items():
 if 'image' in r.reltype:
  (out/(k+'-'+Path(r.target_ref).name)).write_bytes(r.target_part.blob)
