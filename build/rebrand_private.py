from pathlib import Path
import re,json
BASE=Path(__file__).resolve().parent.parent
ROOT=BASE/'outputs/Vikkypaedia_Pediatric_Infectious_Diseases'
TITLE='Vikkypaedia · Pediatric Infectious Diseases'
oldfolder='Vikkypaedia_Red_Book_Atlas_6e';newfolder=ROOT.name
oldanki='anki_red_book_atlas_6e.tsv';newanki='anki_pediatric_infectious_diseases.tsv'
# Retain provenance separately; cosmetic rebranding does not remove source credits.
(ROOT/'SOURCE_CREDITS.md').write_text('''# Source credits and permissions

This private study course contains material extracted from *Red Book Atlas of Pediatric Infectious Diseases*, 6th edition (2026), edited by Tina Q. Tan and published by the American Academy of Pediatrics (AAP).

Source PDF: `Red_Book_Atlas_of_Pediatric_Infectious_Diseases_American_Academy.pdf`, supplied by the user. Chapter numbers, printed-page references, original clinical wording, image captions, third-party credits, and source metadata are retained for traceability. Copyright © 2026 American Academy of Pediatrics; original rights remain with their respective holders. Private interface branding does not imply authorship or endorsement of the underlying material.

- [Publisher book record](https://publications.aap.org/aapbooks/monograph/797/Red-Book-Atlas-of-Pediatric-Infectious-Diseases)
- [Publisher permissions](https://publications.aap.org/pages/licensing-permissions)
- [Source updates and errata](https://publications.aap.org/redbook/resources/15805)

Original figure credits, copyright notices, and clinical attributions within extracted reference content have not been removed. Detailed provenance is in `build/source_metadata.json` and the verification files.
''',encoding='utf-8')
changed=[]
for p in ROOT.rglob('*'):
 if not p.is_file() or p.suffix.lower() not in {'.html','.js','.md','.json','.py','.cjs','.tsv'}:continue
 if p.name=='SOURCE_CREDITS.md':continue
 s=p.read_text(encoding='utf-8-sig');before=s
 s=s.replace(oldfolder,newfolder).replace(oldanki,newanki)
 if p.name in ['index.html','template.html']:
  s=s.replace('Vikkypaedia · Red Book Atlas 6e',TITLE)
  s=s.replace('RED BOOK ATLAS · PEDIATRIC INFECTIOUS DISEASES','PEDIATRIC INFECTIOUS DISEASES · PRIVATE STUDY')
  s=s.replace('6th edition · 2026 · Local study course','Private study course')
  s=s.replace('Source edition: AAP, 2026.<br>','Personal learning library.<br>')
 if p.name=='app.js':
  s=s.replace("JSON.parse(localStorage.getItem('vikkypaedia_redbook6e')||'{}')","JSON.parse(localStorage.getItem('vikkypaedia_pediatric_infections')||localStorage.getItem('vikkypaedia_redbook6e')||'{}')")
  s=s.replace("localStorage.setItem('vikkypaedia_redbook6e'","localStorage.setItem('vikkypaedia_pediatric_infections'")
  s=re.sub(r"function footer\(\)\{return .*?\}\n", "function footer(){return '<div class=\"footer\">Vikkypaedia · Pediatric Infectious Diseases · Private study course. <a href=\"README.md\" target=\"_blank\">Course guide</a> · <a href=\"SOURCE_CREDITS.md\" target=\"_blank\">Source credits</a></div>'}\n",s,count=1)
 if p.suffix=='.tsv':s=s.replace('RedBookAtlas6e','PediatricInfectiousDiseases')
 if p.name=='README.md':
  s=s.replace('# Vikkypaedia · Red Book Atlas 6e','# '+TITLE)
  s=re.sub(r'^Source: \*Red Book Atlas.*$', 'Source attribution and permissions are documented in [Source credits](SOURCE_CREDITS.md). The reference has 1,178 PDF pages; all 168 content chapters are included.',s,flags=re.M)
  s=re.sub(r'^This is an edition-based study course.*$', 'This is a private, edition-based learning course. Source details, permissions, and update references are kept in [Source credits](SOURCE_CREDITS.md).',s,flags=re.M)
 if p.name=='index.md':s=s.replace('# Vikkypaedia · Red Book Atlas 6e','# '+TITLE)
 if p.parent.name=='chapters' and p.suffix=='.md':
  s=s.replace('> Red Book Atlas of Pediatric Infectious Diseases, 6th edition (2026).', '> Private study reference ([source credits](../../SOURCE_CREDITS.md)).')
  s=s.replace('> Source: Red Book Atlas of Pediatric Infectious Diseases, 6th edition (2026).', '> Reference: [source credits](../../SOURCE_CREDITS.md).')
 if p.name=='log.md':s=s.replace('Nelson Textbook of Pediatrics','reference textbook')
 if s!=before:p.write_text(s,encoding='utf-8');changed.append(str(p.relative_to(ROOT)))
anki=ROOT/oldanki
if anki.exists():anki.rename(ROOT/newanki)
# Match retained data/extraction copies to neutral course-generated chapter headers.
for p in [ROOT/'build/extraction.json']+list((ROOT/'build').glob('ch[0-9][0-9][0-9].json')):
 if p.exists():
  s=p.read_text(encoding='utf-8').replace('> Red Book Atlas of Pediatric Infectious Diseases, 6th edition (2026).','> Private study reference (source credits: ../../SOURCE_CREDITS.md).')
  p.write_text(s,encoding='utf-8')
# Keep the source record intact in BUILD_REPORT, with a neutral artifact heading.
p=ROOT/'BUILD_REPORT.md';s=p.read_text(encoding='utf-8');s+='\n## Private interface branding\n\nThe interface, course folder, package name, and Anki tags use Pediatric Infectious Diseases branding. Original source credits, clinical attributions, and permissions notices remain in source reference material.\n';p.write_text(s,encoding='utf-8')
(ROOT/'build/private_rebrand.json').write_text(json.dumps({'title':TITLE,'changed_files':len(changed),'source_credits_retained':True,'source_clinical_text_unchanged':True,'legacy_progress_read_supported':True},indent=2),encoding='utf-8')
print(json.dumps({'folder':str(ROOT),'files_updated':len(changed),'anki':newanki},indent=2))
