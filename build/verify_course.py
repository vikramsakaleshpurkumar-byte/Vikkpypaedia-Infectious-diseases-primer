import pathlib,json,re,subprocess,hashlib,collections,sys,urllib.parse
from PIL import Image
BASE=pathlib.Path(__file__).resolve().parent.parent;ROOT=BASE if pathlib.Path(__file__).resolve().parent.name=='build' else BASE/'outputs/Vikkypaedia_Pediatric_Infectious_Diseases'
data=json.loads((ROOT/'build/course_data.json').read_text(encoding='utf-8'));ext=json.loads((ROOT/'build/extraction.json').read_text(encoding='utf-8'))
checks=[];errors=[]
def check(name,yes,detail=None):
 checks.append({'name':name,'passed':bool(yes),'detail':detail})
 if not yes:errors.append(name)
nums=[c['num'] for c in data['chapters']]
check('Chapter numbering exactly 1–168',nums==list(range(1,169)))
pages=[p['pdf_page'] for c in ext for p in c['pages']]
check('All 1,106 content pages assigned once',pages==list(range(15,1121)),{'pages':len(pages),'duplicates':len(pages)-len(set(pages))})
for sub,pattern in [('raw/chapters','[0-9][0-9][0-9].md'),('wiki/chapters','[0-9][0-9][0-9].md'),('wiki/flashcards','*_flashcards.md'),('wiki/mcqs','*_mcqs.md'),('data/chapters','ch_*.js')]:check(sub+' count',len(list((ROOT/sub).glob(pattern)))==168)
check('Six study pathways',len(data['groups'])==6)
check('32 clinical search features',len(data['features'])==32)
check('At least six cards per chapter',all(c['cards']>=6 for c in data['chapters']),min(c['cards'] for c in data['chapters']))
check('Every chapter has a quiz',set(q['ch'] for q in data['quizzes'])==set(nums))
check('Every chapter indexed in pathogen atlas',len(data['atlas'])==168 and all(x['etiology'] for x in data['atlas']))
check('Quiz answer indices and unique options',all(0<=q['answer']<4 and len(q['options'])==4 and len(set(q['options']))==4 for q in data['quizzes']))
check('Unique card and quiz identifiers',len(set(c['id'] for c in data['cards']))==len(data['cards']) and len(set(q['id'] for q in data['quizzes']))==len(data['quizzes']))
check('Automated quiz source titles masked',all(data['chapters'][q['ch']-1]['title'].lower() not in q['q'].lower() for q in data['quizzes'] if q['kind'].startswith('Automated')))
tooltext=json.dumps(data['cards']+data['quizzes'],ensure_ascii=False)
check('Study tools have no chapter meta boilerplate',not re.search(r'\b(?:this chapter|see chapter|see table|see fig(?:ure)?)\b',tooltext,re.I))
missing=[];badimages=[]
for f in data['figures']:
 p=ROOT/f['path']
 if not p.exists():missing.append(str(p));continue
 try:
  with Image.open(p) as im:im.verify()
 except Exception:badimages.append(str(p))
check('All image placements exist and decode',not missing and not badimages,{'missing':len(missing),'invalid':len(badimages)})
badrefs=[]
for fn in list((ROOT/'wiki').rglob('*.md'))+list((ROOT/'raw').rglob('*.md'))+[ROOT/'index.md']:
 txt=fn.read_text(encoding='utf-8')
 for rel in re.findall(r'\]\(([^)]+)\)',txt):
  if re.match(r'^[A-Za-z]+:|^#',rel):continue
  p=(fn.parent/rel.split('#')[0]).resolve()
  if not p.exists():badrefs.append((str(fn),rel))
check('Markdown navigation and asset links resolve',not badrefs,badrefs[:10])
badpages=[]
for kind in ['cards','quizzes','therapies']:
 for row in data[kind]:
  c=data['chapters'][row['ch']-1]
  if not c['pdf_start']<=row['pdf_page']<=c['pdf_end'] or row['printed_page']!=row['pdf_page']-14:badpages.append(row.get('id',row['ch']))
check('Study tool page references within source chapter',not badpages,badpages[:10])
badjs=[]
for p in (ROOT/'data').rglob('*.js'):
 r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
 if r.returncode:badjs.append({'file':str(p),'error':r.stderr})
check('JavaScript syntax in every data/app bundle',not badjs,badjs[:2])
for i,s in enumerate(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',(ROOT/'index.html').read_text(encoding='utf-8'),re.S)):
 r=subprocess.run(['node','--check'],input=s,capture_output=True,text=True)
 check('Inline script syntax '+str(i),r.returncode==0)
raw127=(ROOT/'raw/chapters/127.md').read_text(encoding='utf-8')
check('Known mathematical glyph repairs preserved','≥12 months' in raw127 and 'CD4+' in raw127 and 'percentage <15%' in raw127)
check('Short treatment statements retained','Management is supportive.' in (ROOT/'raw/chapters/093.md').read_text(encoding='utf-8'))
orientation=json.loads((ROOT/'build/table_orientation.json').read_text(encoding='utf-8'))
check('Landscape table normalization recorded',len(orientation['normalized_pdf_pages'])==18)
check('Nonstandard chapters have complete source page images',all((ROOT/f'tables/ch{n:03d}_page{pn:04d}.jpg').exists() for n in [51,101] for pn in range(ext[n-1]['pdf_start'],ext[n-1]['pdf_end']+1)))
source=pathlib.Path(json.loads((ROOT/'build/source_metadata.json').read_text(encoding='utf-8'))['source'])
digest=hashlib.file_digest(source.open('rb'),'sha256').hexdigest()
report={'passed':not errors,'checks':checks,'errors':errors,'source_sha256':digest,'source_bytes':source.stat().st_size,'metrics':data['stats'],'unmatched_captions':[f['path'] for f in data['figures'] if not f['caption_matched']]}
(ROOT/'build/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'checks':len(checks),'errors':errors,'metrics':data['stats']},indent=2))
if errors:sys.exit(1)
