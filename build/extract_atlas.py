import sys, pathlib, json, re, unicodedata, time, collections, html
BASE=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE/'work/pymupdf_legacy'))
import pymupdf as fitz
sys.stdout.reconfigure(encoding='utf-8')
SOURCE=pathlib.Path(r'C:\Users\India\Downloads\Red_Book_Atlas_of_Pediatric_Infectious_Diseases_American_Academy.pdf')
ROOT=BASE if pathlib.Path(__file__).resolve().parent.name=='build' else BASE/'outputs/Vikkypaedia_Pediatric_Infectious_Diseases'
for d in ['raw/chapters','wiki/chapters','wiki/flashcards','wiki/mcqs','wiki/parts','figures','tables','data/chapters','build']:
 (ROOT/d).mkdir(parents=True,exist_ok=True)
doc=fitz.open(SOURCE)
toc=doc.get_toc()
entries=[(int(m[1]),re.sub(r'^\d+\.\s*','',t),p) for _,t,p in toc if (m:=re.match(r'^(\d+)\.\s',t))]
index_page=next(p for _,t,p in toc if t=='Index')
def clean(t):
 t=unicodedata.normalize('NFKC',t).replace('\u00ad','')
 t=re.sub(r'(\w)-\s*\n\s*([a-z])',r'\1\2',t)
 return re.sub(r'\s+',' ',t).strip()
def get_blocks(page):
 blocks=[]
 # Inner margins alternate on recto/verso pages (gutter is not the page midpoint).
 mid=page.rect.width/2+(-15 if page.number%2 else 15)
 for b in page.get_text('dict')['blocks']:
  if b['type']!=0 or b['bbox'][1]<53 or b['bbox'][1]>page.rect.height-24: continue
  lines=[]
  for ln in b['lines']:
   spans=ln['spans']; t=''.join(s['text'] for s in spans)
   if not t.strip():continue
   lines.append({'text':t,'size':max(s['size'] for s in spans),'black':any('Black' in s['font'] for s in spans),'bbox':ln['bbox']})
  # PDF blocks occasionally span both columns: partition their individual lines first.
  for side in [0,1]:
   ls=[l for l in lines if (0 if l['bbox'][0]<mid else 1)==side]
   if ls:
    bb=(min(l['bbox'][0] for l in ls),min(l['bbox'][1] for l in ls),max(l['bbox'][2] for l in ls),max(l['bbox'][3] for l in ls))
    blocks.append({'bbox':bb,'lines':ls})
 # Text blocks are separate by column in this edition. Wide objects retain their text and page images.
 return sorted(blocks,key=lambda b:(0 if b['bbox'][0]<mid else 1,b['bbox'][1]))
def isheading(l):
 t=clean(l['text'])
 return l['black'] and 8<=l['size']<=10 and t.upper()==t and len(t)>3 and not t.startswith(('CHAPTER','TABLE','IMAGE'))
chapters=[]; page_inventory=[]; started=time.time()
for idx,(num,title,start) in enumerate(entries):
 end=entries[idx+1][2]-1 if idx+1<len(entries) else index_page-1
 ch={'num':num,'title':title,'pdf_start':start,'pdf_end':end,'printed_start':start-14,'printed_end':end-14,'sections':[],'figures':[],'tables':[],'pages':[]}
 current=None; raw=[f'# {num}. {title}',f'> Red Book Atlas of Pediatric Infectious Diseases, 6th edition (2026). PDF pages {start}-{end}; printed pages {start-14}-{end-14}.','']
 for pn in range(start,end+1):
  page=doc[pn-1]; bs=get_blocks(page)
  raw += [f'\n## PDF page {pn} | printed page {pn-14}\n']
  page_text=[]; paras=[]
  for b in bs:
   buf=[]; body=True
   def flush():
    global current
    if buf:
     t=clean('\n'.join(buf));raw.append(t+'\n');page_text.append(t)
     if current is not None and body and len(t)>25 and not re.match(r'^(?:Image|Table|Courtesy|Reproduced|Adapted|From |Source:|©)',t):
      current['paragraphs'].append({'text':t,'pdf_page':pn,'printed_page':pn-14})
     buf.clear()
   for l in b['lines']:
    t=clean(l['text'])
    if re.match(r'^CHAPTER\s+\d+',t) or l['size']>12:continue
    if isheading(l):
     flush()
     # Wrapped section headings are separate lines in one block.
     if current and not current['paragraphs'] and current['pdf_page']==pn:
      current['heading']+=' '+t
      raw[-1]=f"### {current['heading']}\n"
     else:
      current={'heading':t,'pdf_page':pn,'paragraphs':[]};ch['sections'].append(current);raw.append(f'### {t}\n')
    else:
     if buf and ((l['size']>=8.7)!=body):flush()
     body=l['size']>=8.7
     buf.append(l['text'])
   flush()
  # Keep each original clinical image placement, including labels baked into its pixels.
  infos=page.get_image_info(xrefs=True)
  capblocks=[]
  for b in bs:
   t=clean('\n'.join(l['text'] for l in b['lines']))
   if re.match(r'^Image\s+\d+\.\d+',t):capblocks.append((b['bbox'],t))
  for j,im in enumerate(infos):
   r=fitz.Rect(im['bbox'])
   if r.width<45 or r.height<40 or r.get_area()<3000:continue
   if not r.intersects(page.rect):continue
   candidates=[(bb,t) for bb,t in capblocks if bb[1]>=r.y1-15 and abs(bb[0]-r.x0)<max(80,r.width*.6)]
   cap=min(candidates,key=lambda x:abs(x[0][1]-r.y1))[1] if candidates else ''
   # Some caption labels and prose are split into adjacent PDF blocks.
   if cap and len(cap)<35:
    cb=min(candidates,key=lambda x:abs(x[0][1]-r.y1))[0]
    follow=[b for b in bs if b['bbox'][1]>=cb[3]-2 and b['bbox'][1]-cb[3]<18 and abs(b['bbox'][0]-cb[0])<15]
    if follow:cap+=' '+clean('\n'.join(l['text'] for l in follow[0]['lines']))
   name=f'figures/ch{num:03d}_p{pn:04d}_{j+1:02d}.jpg'
   if not (ROOT/name).exists():
    pix=page.get_pixmap(clip=r & page.rect,dpi=150,alpha=False)
    pix.save(ROOT/name,jpg_quality=86)
   fig={'path':name,'caption':cap or f'Clinical image, printed page {pn-14}. Consult the source page for its complete caption.','caption_matched':bool(cap),'pdf_page':pn,'printed_page':pn-14,'chapter':num}
   ch['figures'].append(fig)
   raw.append(f"![{fig['caption'].replace('[','(').replace(']',')')}](../../{name})\n")
  # Convert only tables with detected cell geometry; preserve a rendered original alongside it.
  if re.search(r'\bTable\s+\d+\.', '\n'.join(page_text)):
   try:
    found=page.find_tables(strategy='lines_strict')
    for ti,table in enumerate(found.tables):
     cells=table.extract()
     if len(cells)<2 or max(map(len,cells),default=0)<2:continue
     md=table.to_markdown();name=f'tables/ch{num:03d}_p{pn:04d}_{ti+1}.jpg'
     page.get_pixmap(clip=fitz.Rect(table.bbox),dpi=150,alpha=False).save(ROOT/name,jpg_quality=88)
     ch['tables'].append({'pdf_page':pn,'printed_page':pn-14,'markdown':md,'path':name})
     raw += ['\n### Geometry-detected table\n',md,f'\n[View original table](../../{name})\n']
   except Exception as e:print('TABLE NOTICE',pn,str(e)[:120],flush=True)
  ch['pages'].append({'pdf_page':pn,'printed_page':pn-14,'characters':sum(len(t) for t in page_text)})
  page_inventory.append({'pdf_page':pn,'chapter':num,'characters':sum(len(t) for t in page_text),'images':len(infos)})
 ch['raw_md']='\n'.join(raw)
 (ROOT/f'raw/chapters/{num:03d}.md').write_text(ch['raw_md'],encoding='utf-8')
 (ROOT/f'build/ch{num:03d}.json').write_text(json.dumps(ch,ensure_ascii=False),encoding='utf-8')
 chapters.append(ch)
 print(f"{num:03d}/168 {title[:48]} | pages {start}-{end} | sections {len(ch['sections'])} | images {len(ch['figures'])} | elapsed {time.time()-started:.0f}s",flush=True)
(ROOT/'build/extraction.json').write_text(json.dumps(chapters,ensure_ascii=False),encoding='utf-8')
(ROOT/'build/page_inventory.json').write_text(json.dumps(page_inventory,indent=2),encoding='utf-8')
(ROOT/'build/source_metadata.json').write_text(json.dumps({'source':str(SOURCE),'title':'Red Book Atlas of Pediatric Infectious Diseases','edition':6,'year':2026,'editor':'Tina Q. Tan','publisher':'American Academy of Pediatrics','pdf_pages':len(doc),'chapters':len(chapters),'front_matter_pdf':[1,14],'content_pdf':[15,index_page-1],'index_pdf':[index_page,len(doc)],'toc':toc},ensure_ascii=False,indent=2),encoding='utf-8')
print('EXTRACTION COMPLETE',len(chapters),sum(len(c['figures']) for c in chapters),'images',sum(len(c['tables']) for c in chapters),'tables',flush=True)
