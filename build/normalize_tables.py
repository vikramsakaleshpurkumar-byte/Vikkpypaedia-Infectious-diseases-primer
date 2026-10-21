import sys,pathlib,json,re
BASE=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE/'work/pymupdf_legacy'))
import pymupdf as fitz
ROOT=BASE if pathlib.Path(__file__).resolve().parent.name=='build' else BASE/'outputs/Vikkypaedia_Pediatric_Infectious_Diseases'
chs=json.loads((ROOT/'build/extraction.json').read_text(encoding='utf-8'))
doc=fitz.open(r'C:\Users\India\Downloads\Red_Book_Atlas_of_Pediatric_Infectious_Diseases_American_Academy.pdf')
patched=set();mapping={'002C':'003C','0031':'002B','0023':'2264','0024':'2265','002E':'003E'}
for pn in range(14,1120):
 for font in doc[pn].get_fonts():
  if 'MathematicalPi' not in font[3]:continue
  typ,value=doc.xref_get_key(font[0],'ToUnicode')
  if typ!='xref':continue
  x=int(value.split()[0])
  if x in patched:continue
  raw=doc.xref_stream(x).decode('latin1')
  raw=re.sub(r'(<[0-9A-Fa-f]+>\s*)<(002C|0031|0023|0024|002E)>',lambda m:m[1]+'<'+mapping[m[2]]+'>',raw)
  doc.update_stream(x,raw.encode('latin1'));patched.add(x)
rotated=[]
for c in chs:
 for pn in sorted(set(t['pdf_page'] for t in c['tables'])|set(range(c['pdf_start'],c['pdf_end']+1) if c['num'] in [51,101] else [])):
  src=doc[pn-1]
  lines=[l for b in src.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] if b['type']==0 for l in b['lines']]
  vertical=sum(abs(l['dir'][1])>.8 for l in lines)>len(lines)*.5
  tmp=fitz.open();tmp.insert_pdf(doc,from_page=pn-1,to_page=pn-1);page=tmp[0]
  if vertical:
   page.set_rotation(90);page.remove_rotation();rotated.append(pn)
  if c['num'] in [51,101]:page.get_pixmap(dpi=130,alpha=False).save(ROOT/f"tables/ch{c['num']:03d}_page{pn:04d}.jpg",jpg_quality=88)
  if c['tables']:
   old=[t for t in c['tables'] if t['pdf_page']==pn]
   found=page.find_tables(strategy='lines_strict').tables
   for i,t in enumerate(old):
    if i>=len(found):continue
    table=found[i];md=table.to_markdown()
    c['raw_md']=c['raw_md'].replace(t['markdown'],md)
    t['markdown']=md;t['orientation_normalized']=vertical
    page.get_pixmap(clip=fitz.Rect(table.bbox),dpi=150,alpha=False).save(ROOT/t['path'],jpg_quality=88)
  tmp.close()
 (ROOT/f"raw/chapters/{c['num']:03d}.md").write_text(c['raw_md'],encoding='utf-8')
 (ROOT/f"build/ch{c['num']:03d}.json").write_text(json.dumps(c,ensure_ascii=False),encoding='utf-8')
(ROOT/'build/extraction.json').write_text(json.dumps(chs,ensure_ascii=False),encoding='utf-8')
(ROOT/'build/table_orientation.json').write_text(json.dumps({'normalized_pdf_pages':rotated},indent=2),encoding='utf-8')
print('Normalized',len(rotated),'landscape table pages',flush=True)
