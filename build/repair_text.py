import pathlib,sys,json,re,unicodedata,collections,time
BASE=pathlib.Path(__file__).resolve().parent.parent;ROOT=BASE if pathlib.Path(__file__).resolve().parent.name=='build' else BASE/'outputs/Vikkypaedia_Pediatric_Infectious_Diseases'
sys.path.insert(0,str(BASE/'work/pymupdf_legacy'));import pymupdf as fitz
doc=fitz.open(r'C:\Users\India\Downloads\Red_Book_Atlas_of_Pediatric_Infectious_Diseases_American_Academy.pdf')
chs=json.loads((ROOT/'build/extraction.json').read_text(encoding='utf-8'))
# The source's MathematicalPi ToUnicode maps mathematical symbols to ASCII punctuation.
# Repair only that font, in memory; never replace punctuation in ordinary prose.
mapping={'002C':'003C','0031':'002B','0023':'2264','0024':'2265','002E':'003E'}
patched=set()
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
def clean(t):
 t=unicodedata.normalize('NFKC',t).replace('\u00ad','').replace('\x07',' ')
 t=re.sub(r'(\w)-\s*\n\s*([a-z])',r'\1\2',t)
 t=re.sub(r'\s+',' ',t).strip()
 for a,b in [('grampositive','gram-positive'),('gramnegative','gram-negative'),('Personto-person','Person-to-person'),('personto-person','person-to-person')]:t=t.replace(a,b)
 return t
counts=collections.Counter();started=time.time()
for c in chs:
 c['sections']=[];current=None;raw=[f"# {c['num']}. {c['title']}",f"> Red Book Atlas of Pediatric Infectious Diseases, 6th edition (2026). PDF pages {c['pdf_start']}-{c['pdf_end']}; printed pages {c['printed_start']}-{c['printed_end']}.", '']
 for pn in range(c['pdf_start'],c['pdf_end']+1):
  page=doc[pn-1];mid=page.rect.width/2+(-15 if page.number%2 else 15);blocks=[]
  for b in page.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks']:
   if b['type']!=0:continue
   ls=[]
   for l in b['lines']:
    ss=l['spans'];t=''.join(s['text'] for s in ss)
    if not t.strip() or l['bbox'][1]<53 or l['bbox'][1]>page.rect.height-24:continue
    ls.append({'text':t,'size':max(s['size'] for s in ss),'black':any('Black' in s['font'] for s in ss),'bbox':l['bbox']})
   for side in [0,1]:
    lines=[l for l in ls if (0 if l['bbox'][0]<mid else 1)==side]
    if lines:blocks.append({'lines':lines,'side':side,'y':min(l['bbox'][1] for l in lines)})
  blocks.sort(key=lambda b:(b['side'],b['y']))
  raw.append(f'\n## PDF page {pn} | printed page {pn-14}\n')
  for bi,b in enumerate(blocks):
   buf=[];body=True;lastheading=False
   def flush():
    global current
    if not buf:return
    t=clean('\n'.join(buf));raw.append(t+'\n')
    if body and len(t)>0 and not re.match(r'^(?:Image\s+\d|Table\s+\d|Courtesy|Reproduced|Adapted|From |Source:|©)',t):
     if current is None:
      current={'heading':'OVERVIEW','pdf_page':pn,'paragraphs':[]};c['sections'].append(current)
     current['paragraphs'].append({'text':t,'pdf_page':pn,'printed_page':pn-14})
    buf.clear()
   for l in b['lines']:
    t=clean(l['text'])
    if re.match(r'^CHAPTER\s+\d+',t) or l['size']>12:continue
    heading=l['black'] and 8<=l['size']<=10 and t.upper()==t and len(t)>3 and not t.startswith(('CHAPTER','TABLE','IMAGE'))
    if heading:
     flush()
     if current and lastheading:
      current['heading']+=' '+t;raw[-1]=f"### {current['heading']}\n"
     else:
      current={'heading':t,'pdf_page':pn,'paragraphs':[]};c['sections'].append(current);raw.append(f'### {t}\n')
     lastheading=True
    else:
     lastheading=False
     if buf and ((l['size']>=8.7)!=body):flush()
     body=l['size']>=8.7;buf.append(l['text'])
   flush()
  for f in [x for x in c['figures'] if x['pdf_page']==pn]:raw.append(f"![{f['caption'].replace('[','(').replace(']',')')}](../../{f['path']})\n")
  for t in [x for x in c['tables'] if x['pdf_page']==pn]:raw+=['\n### Geometry-detected table\n',t['markdown'],f"\n[View original table](../../{t['path']})\n"]
 c['raw_md']='\n'.join(raw)
 (ROOT/f"raw/chapters/{c['num']:03d}.md").write_text(c['raw_md'],encoding='utf-8')
 (ROOT/f"build/ch{c['num']:03d}.json").write_text(json.dumps(c,ensure_ascii=False),encoding='utf-8')
 counts[len(c['sections'])]+=1
(ROOT/'build/extraction.json').write_text(json.dumps(chs,ensure_ascii=False),encoding='utf-8')
(ROOT/'build/text_repairs.json').write_text(json.dumps({'symbol_cmaps_repaired':len(patched),'font':'MathematicalPi-One','mapping':{'comma':'less than','1':'plus','hash':'less than or equal','dollar':'greater than or equal','period':'greater than'},'applies_only_to_symbol_font':True,'short_clinical_statements_retained':True,'section_count_distribution':dict(counts)},indent=2),encoding='utf-8')
print('Text repaired:',len(chs),'chapters;',len(patched),'symbol maps;',round(time.time()-started,1),'seconds',flush=True)
