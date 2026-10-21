import pathlib,json,re,html,random,collections,math,hashlib,shutil
BASE=pathlib.Path(__file__).resolve().parent.parent
ROOT=BASE if pathlib.Path(__file__).resolve().parent.name=='build' else BASE/'outputs/Vikkypaedia_Pediatric_Infectious_Diseases'
chs=json.loads((ROOT/'build/extraction.json').read_text(encoding='utf-8'))
random.seed(20261021)
GROUPS={
 'Bacterial infections':{1,5,7,12,13,14,16,21,22,23,24,26,28,29,30,31,32,33,34,45,46,47,50,52,54,55,56,58,76,77,79,80,81,82,87,91,94,95,104,109,112,117,118,120,123,124,125,128,131,134,135,136,137,138,139,140,142,145,157,158,159,160,161,162,164,165,167},
 'Viral infections':{2,6,10,20,27,36,37,43,44,48,49,57,59,60,61,62,63,64,65,66,67,70,71,72,73,74,84,86,88,90,92,93,96,100,102,103,114,115,119,121,122,126,127,132,163,166,168},
 'Fungal infections':{9,19,25,35,38,51,68,89,98,111,113,133,146,147,148,149},
 'Protozoal infections':{3,4,11,15,18,39,41,42,53,78,85,151,153,155,156},
 'Helminths and ectoparasites':{8,17,40,69,83,97,99,105,106,107,110,129,130,141,143,144,150,152,154},
 'Syndromes and cross-cutting topics':{75,101,108,116}
}
FEATURES=[
 ('Fever',r'\bfever|febrile'),('Vesicles',r'vesicl|vesicul'),('Petechiae / purpura',r'petechi|purpur'),('Maculopapular rash',r'maculopapul|morbilliform'),('Ulcers / eschar',r'ulcer|eschar'),('Pruritus',r'pruritu|itching'),('Lymphadenopathy',r'lymphadenopathy|lymphadenitis'),('Conjunctivitis',r'conjunctiv|keratitis'),
 ('Pharyngitis',r'pharyng|tonsillit'),('Cough',r'\bcough'),('Pneumonia',r'pneumonia|pneumonitis'),('Wheeze / bronchiolitis',r'wheez|bronchiolitis'),('Diarrhea',r'diarrhe|gastroenteritis'),('Dysentery',r'bloody\s+diarrhea|dysenter'),('Vomiting',r'vomit|emesis'),('Hepatitis / jaundice',r'hepatitis|jaundice'),
 ('Hepatosplenomegaly',r'hepatosplenomegaly|splenomegaly|hepatomegaly'),('Meningitis',r'meningitis|meningeal'),('Encephalitis / seizures',r'encephalitis|encephalopathy|seizure'),('Weakness / paralysis',r'paralysis|paralytic|flaccid|\bweakness'),('Arthritis / bone pain',r'arthritis|arthralgia|osteomyelitis'),('Abscess / soft tissue',r'abscess|cellulitis|fasciitis'),('Sepsis / shock',r'sepsis|septicemia|\bshock'),('Anemia / hemolysis',r'\banemia|hemolysis|hemolytic'),
 ('Cytopenia',r'thrombocytopenia|leukopenia|pancytopenia'),('Eosinophilia',r'eosinophil'),('Congenital / neonatal',r'congenital|neonat|newborn|perinatal'),('Immunocompromised host',r'immunocompromis|immunosuppress|transplant'),('Tick / arthropod exposure',r'\btick|mosquito|arthropod|\bflea'),('Animal exposure',r'zoonot|\bcat\b|\bdog\b|rodent|livestock|animal bite'),('Water exposure',r'freshwater|swimming|contaminated water|waterborne'),('Travel / endemic setting',r'\btravel|endemic|tropical')]
PILLARS=[('Etiology and transmission',r'ETIOLOG|EPIDEMIOLOGY'),('Clinical recognition',r'CLINICAL MANIFESTATIONS|OVERVIEW'),('Diagnostic workup',r'DIAGNOSTIC|DIAGNOSIS'),('Treatment in the atlas',r'TREATMENT'),('Prevention and infection control',r'CONTROL MEASURES|PREVENTION')]
def safe(t):return html.escape(str(t))
def studyclean(t):
 t=re.sub(r'\([^)]*\b(?:Image|Table|Chapter)\s+\d[^)]*\)','',t,flags=re.I)
 t=re.sub(r'\b(?:this chapter|see chapter|see table|see fig(?:ure)?)\b[^.;]*[.;]?','',t,flags=re.I)
 return re.sub(r'\s+',' ',t).strip()
def sentences(t):
 # Decimal points and abbreviated names without punctuation stay intact.
 return [x.strip() for x in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9“])',t) if len(x.strip())>35 and x.strip()[-1:] in '.!?']
def excerpt(paras,n=2):
 for p in paras:
  if p['text'].strip() in ['None.','None','No specific therapy.']:
   return {k:p[k] for k in ['text','pdf_page','printed_page']}
  ss=sentences(studyclean(p['text']))
  if ss:
   t=' '.join(ss[:n])
   if len(t)>1100:t=ss[0]
   return {'text':t,'pdf_page':p['pdf_page'],'printed_page':p['printed_page']}
 return None
def section_paras(c,pat):return [p for s in c['sections'] if re.search(pat,s['heading']) for p in s['paragraphs']]
def mdsrc(p):return f"Printed p. {p['printed_page']} / PDF p. {p['pdf_page']}"
catalog=[];atlas=[];therapies=[];cards=[];quizzes=[];allfigs=[]
def group(c):return next(k for k,v in GROUPS.items() if c['num'] in v)
for c in chs:
 # Rejoin paragraphs continued across columns/pages while retaining their page provenance.
 for s in c['sections']:
  merged=[]
  for p in s['paragraphs']:
   p={**p,'source_pages':[p['pdf_page']]}
   if merged and merged[-1]['text'][-1:] not in '.!?:;':
    merged[-1]['text']+=' '+p['text'];merged[-1]['source_pages']=sorted(set(merged[-1]['source_pages']+p['source_pages']))
   else:merged.append(p)
  s['paragraphs']=merged
 if not c['sections']:
  pagebody=c['raw_md'].split('## PDF page ')[1].split('\n',1)[1].split('## PDF page ')[0]
  paragraphs=[{'text':p.strip(),'pdf_page':c['pdf_start'],'printed_page':c['printed_start']} for p in pagebody.split('\n\n') if len(p.strip())>70]
  c['sections']=[{'heading':'OVERVIEW','paragraphs':paragraphs,'pdf_page':c['pdf_start']}]
 c['group']=group(c)
 clinical=section_paras(c,'CLINICAL MANIFESTATIONS|OVERVIEW')
 if not clinical:clinical=section_paras(c,'ETIOLOGIES, DIAGNOSIS, AND TREATMENT')
 ep=section_paras(c,'EPIDEMIOLOGY')
 feattext=' '.join(p['text'] for p in clinical+ep)
 c['features']=[label for label,pat in FEATURES if re.search(pat,feattext,re.I)]
 c['pillars']=[]
 for name,pat in PILLARS:
  p=excerpt(section_paras(c,pat))
  if p:c['pillars'].append({'label':name,**p})
 # Seven section-based recall cards, plus additional clinical / diagnostic paragraphs where useful.
 selected=[]
 for s in c['sections']:
  p=excerpt(s['paragraphs'],3)
  if p:selected.append((s['heading'].title(),p))
 for s in c['sections']:
  if len(selected)>=8:break
  if re.search('CLINICAL|DIAGNOSTIC|TREATMENT',s['heading']) and len(s['paragraphs'])>1:
   p=excerpt(s['paragraphs'][1:],2)
   if p and p['text'] not in [x[1]['text'] for x in selected]:selected.append((s['heading'].title()+' — additional detail',p))
 if len(selected)<6:
  for s in c['sections']:
   for p0 in s['paragraphs'][1:]:
    if len(selected)>=6:break
    p=excerpt([p0],2)
    if p and p['text'] not in [x[1]['text'] for x in selected]:selected.append((s['heading'].title()+' — focused detail',p))
 for cat,p in selected[:10]:
  cat=re.sub(r'[\d,]+$','',re.sub(r'\([^)]*\)','',cat)).strip()
  cards.append({'id':f"fc-{c['num']:03d}-{len([x for x in cards if x['ch']==c['num']])+1}",'ch':c['num'],'category':cat,'q':f"{c['title']}: recall the key points for {cat.lower()}.",'a':p['text'],'pdf_page':p['pdf_page'],'printed_page':p['printed_page'],'group':c['group']})
 if c['num'] in [51,101]:
  custom={51:[('Host risk','Which underlying host settings predispose children to uncommon invasive fungal infections?','Immunosuppression and other underlying host conditions predispose children to these infections. Reversing severe neutropenia and reducing immunosuppression, where feasible, are important management considerations.',263),('Acquisition','How can children acquire uncommon invasive fungal infections?','Acquisition can follow inhalation through the respiratory tract or direct inoculation after disruption of the skin barrier.',263),('Examples','Which uncommon invasive molds are introduced in the atlas overview?','The overview lists mucormycosis, fusariosis, scedosporiosis, and phaeohyphomycoses (black molds).',263),('Management context','Why should uncommon invasive fungal treatment not be reduced to a single universal drug rule?','Susceptibility data are limited, optimal treatments are not well established, and antifungal choice can depend on the particular species.',263),('Source control','What nonpharmacologic management measures are emphasized for invasive fungal infection?','Consider source control, reduction of immunosuppression, and surgical excision or debridement when feasible, together with specialist consultation.',263)],101:[('Returned traveler','Which parasitic diagnosis should be considered in a febrile traveler returning from a malaria transmission region?','Malaria should be considered when evaluating fever in a returned traveler from an area with ongoing malaria transmission.',629),('Long latency','Which infections in the overview can become apparent after long latency?','The overview highlights Chagas disease, neurocysticercosis, schistosomiasis, and strongyloidiasis.',629),('Exposure pattern','What exposure route is listed for neurotropic Angiostrongylus cantonensis infection?','Eating raw or improperly cooked infected mollusks, including inadvertent ingestion on raw produce, is listed as a route; other modes may occur.',630),('Clinical pattern','What presentation is listed for neurotropic Angiostrongylus cantonensis infection?','Eosinophilic meningitis with severe headache, neck stiffness, nausea, vomiting, sensory symptoms, and peripheral eosinophilia is listed.',630),('Diagnostic specimen','What diagnostic specimen distinction is made for gastrointestinal Angiostrongylus costaricensis infection?','Larvae and eggs may be identified in tissue, rather than stool. The table states that commercial NAAT and serologic testing are not available.',630)]}[c['num']]
  for j,(cat,q,a,pp) in enumerate(custom):cards.append({'id':f"fc-{c['num']:03d}-custom{j}",'ch':c['num'],'category':cat,'q':q,'a':a,'pdf_page':pp+14,'printed_page':pp,'group':c['group']})
 for s in c['sections']:
  if not re.search('TREATMENT|CONTROL MEASURES',s['heading']):continue
  # Keep full paragraph context for ages, route, intervals, maxima, and exceptions.
  for p in s['paragraphs']:
   t=studyclean(p['text'])
   if len(t)<60:continue
   drugs=re.findall(r'\b(?:amoxicillin(?:/clavulanate)?|ampicillin|penicillin(?: G)?|ceftriaxone|cefotaxime|cefepime|cefixime|vancomycin|clindamycin|doxycycline|azithromycin|erythromycin|clarithromycin|metronidazole|trimethoprim(?:-sulfamethoxazole)?|sulfamethoxazole|rifampin|rifampicin|isoniazid|pyrazinamide|ethambutol|acyclovir|valacyclovir|ganciclovir|valganciclovir|oseltamivir|remdesivir|nirmatrelvir|amphotericin|fluconazole|voriconazole|itraconazole|albendazole|mebendazole|ivermectin|praziquantel|chloroquine|artesunate|artemether|atovaquone|quinine|primaquine|tafenoquine|permethrin|vaccine|immunoglobulin|antitoxin)\b',t,re.I)
   dose=bool(re.search(r'\b\d+(?:\.\d+)?\s*(?:mg|mcg|μg|g|units|U|mL)\s*/',t,re.I))
   if drugs or dose:
    therapies.append({'ch':c['num'],'title':c['title'],'group':c['group'],'section':s['heading'],'drugs':list(dict.fromkeys(x.lower() for x in drugs)),'text':t,'has_dose':dose,'pdf_page':p['pdf_page'],'printed_page':p['printed_page']})
 entry={'num':c['num'],'title':c['title'],'group':c['group'],'features':c['features'],'pdf_start':c['pdf_start'],'pdf_end':c['pdf_end'],'printed_start':c['printed_start'],'printed_end':c['printed_end'],'figures':len(c['figures']),'tables':len(c['tables']),'cards':sum(x['ch']==c['num'] for x in cards),'summary':(excerpt(clinical) or {'text':''})['text']}
 catalog.append(entry)
 atlas.append({**entry,'etiology':excerpt(section_paras(c,'ETIOLOG|OVERVIEW'),3),'epidemiology':excerpt(ep,3),'diagnostics':excerpt(section_paras(c,'DIAGNOSTIC|DIAGNOSIS'),3)})
 allfigs+=c['figures']
 # Reader content is escaped source text, with source provenance on every paragraph.
 sections_html=''
 for s in c['sections']:
  sections_html+=f"<section><h2>{safe(s['heading'].title())}</h2>"
  for p in s['paragraphs']:
   sections_html+=f"<p>{safe(p['text'])}</p><small class='source'>Printed p. {p['printed_page']} · PDF p. {p['pdf_page']}</small>"
  sections_html+='</section>'
 figures_html=''
 for f in c['figures']:
  figures_html+=f"<figure><a href='{f['path']}' target='_blank'><img loading='lazy' src='{f['path']}' alt='{safe(f['caption'])}'></a><figcaption>{safe(f['caption'])}<br><small>Printed p. {f['printed_page']} · PDF p. {f['pdf_page']}</small></figcaption></figure>"
 tables_html=''.join(f"<figure><img loading='lazy' src='{t['path']}' alt='Original table on printed page {t['printed_page']}'><figcaption>Original table · printed p. {t['printed_page']}</figcaption></figure>" for t in c['tables'])
 pageviews=''
 if c['num'] in [51,101]:
  pageviews='<h2>Complete source page views</h2><p>These chapters use multi-page tables. The page views preserve their original row and column relationships. Click to enlarge.</p>'+''.join(f"<figure style='width:100%;margin:15px 0'><a href='tables/ch{c['num']:03d}_page{pn:04d}.jpg' target='_blank'><img loading='lazy' style='max-height:none' src='tables/ch{c['num']:03d}_page{pn:04d}.jpg' alt='Source page {pn-14}'></a><figcaption>Printed p. {pn-14} · PDF p. {pn}</figcaption></figure>" for pn in range(c['pdf_start'],c['pdf_end']+1))
 c['reader_html']=sections_html+pageviews+'<h2>Original tables</h2>'+tables_html+'<h2>Visual atlas</h2>'+figures_html
 payload={k:c[k] for k in ['num','title','group','pdf_start','pdf_end','printed_start','printed_end','features','pillars','figures','tables','reader_html']}
 (ROOT/f'data/chapters/ch_{c["num"]:03d}.js').write_text('window.registerChapter('+json.dumps(payload,ensure_ascii=False)+');\n',encoding='utf-8')
 wiki=[f"# {c['num']}. {c['title']}",f"> Source: Red Book Atlas of Pediatric Infectious Diseases, 6th edition (2026). Printed pp. {c['printed_start']}-{c['printed_end']}; PDF pp. {c['pdf_start']}-{c['pdf_end']}.",f"> Editorial study pathway: {c['group']} (not a part division in the source).",f"[Flashcards](../flashcards/{c['num']:03d}_flashcards.md) · [Quiz](../mcqs/{c['num']:03d}_mcqs.md) · [Full extraction](../../raw/chapters/{c['num']:03d}.md)",'\n## Five study pillars\n']
 for p in c['pillars']:wiki += [f"### {p['label']}",p['text'],f"*{mdsrc(p)}*\n"]
 wiki += ['## Clinical search tags',', '.join(c['features']),'\n## Full text, original tables, and images\n',c['raw_md']]
 (ROOT/f'wiki/chapters/{c["num"]:03d}.md').write_text('\n'.join(wiki),encoding='utf-8')
 deck=[f"# {c['title']} — active recall",'> Source-extracted study prompts; open the source page to verify context.\n']
 for f in [x for x in cards if x['ch']==c['num']]:deck += [f"<details><summary>{safe(f['q'])}</summary>\n",f['a'],f"\n*{mdsrc(f)}*\n</details>\n"]
 (ROOT/f'wiki/flashcards/{c["num"]:03d}_flashcards.md').write_text('\n'.join(deck),encoding='utf-8')

# One automated passage-recognition exercise per chapter. This is not represented as an authored board vignette.
stop={'the','and','with','from','that','this','have','infection','infections','disease','diseases','patients','children','people','which','most','more','other','also','often','been','than','including','caused','associated','clinical','in','of','to','a','or','is','are','can','may','for','be','as','an'}
def tokens(t):return set(w.lower() for w in re.findall(r'[A-Za-z]{4,}',t) if w.lower() not in stop)
for c in chs:
 p=excerpt(section_paras(c,'CLINICAL MANIFESTATIONS|OVERVIEW|ETIOLOGIES, DIAGNOSIS, AND TREATMENT'),3)
 if not p:continue
 if len(p['text'])<90:
  ps=section_paras(c,'CLINICAL MANIFESTATIONS|OVERVIEW|ETIOLOGIES, DIAGNOSIS, AND TREATMENT')
  p={**p,'text':studyclean(' '.join(x['text'] for x in ps[:3]))}
 stem=p['text']
 # Remove explicit topic words while preserving other clinical information.
 short=re.sub(r'\s*\(.*','',c['title']).strip()
 keys=[short]+[w for w in re.findall(r'[A-Za-z-]{5,}',short) if w.lower() not in {'infections','infection','diseases','disease','including','other','serious','neonatal','bacterial','group','human','with','caused','species','formerly','related'}]
 for k in sorted(set(keys),key=len,reverse=True):stem=re.sub(r'\b'+re.escape(k)+r'\b','[topic]',stem,flags=re.I)
 stem=re.sub(re.escape(short),'[topic]',stem,flags=re.I)
 if len(stem)<40:continue
 choices=[x for x in catalog if x['num']!=c['num'] and x['group']==c['group']]
 if len(choices)<3:choices=[x for x in catalog if x['num']!=c['num']]
 tv=tokens(p['text'])
 choices.sort(key=lambda x:len(tv & tokens(x['summary']))/max(1,len(tv|tokens(x['summary']))),reverse=True)
 picked=random.sample(choices[:min(12,len(choices))],3)
 opts=[{'text':c['title'],'ch':c['num']}]+[{'text':x['title'],'ch':x['num']} for x in picked];random.shuffle(opts)
 quizzes.append({'id':f"recall-{c['num']:03d}",'ch':c['num'],'kind':'Automated source recognition','q':'Which source topic matches this passage? Topic names have been masked.\n\n'+stem,'options':[o['text'] for o in opts],'answer':next(i for i,o in enumerate(opts) if o['ch']==c['num']),'explanation':'The passage was extracted from '+c['title']+'. Original wording: '+p['text'],'pdf_page':p['pdf_page'],'printed_page':p['printed_page'],'option_chapters':[o['ch'] for o in opts]})

# Authored diagnostic vignettes: no dosing recommendations or manufactured patient data claims.
CASES=[
(1,'A child has a slowly enlarging, firm cervicofacial mass after dental disease. Draining sinus tracts cross tissue planes, and yellow sulfur granules are found in purulent material. Which diagnosis best fits?', ['Actinomycosis','Nocardiosis','Bartonella henselae infection','Tuberculosis'],'The combination of a disrupted oral mucosal barrier, invasive sinus tracts, and sulfur granules supports actinomycosis.'),
(5,'A painless papule after handling animal hides progresses to a vesicle and then a black eschar with marked surrounding edema. Which diagnosis best fits?', ['Anthrax','Plague','Tularemia','Scabies'],'A painless eschar with pronounced edema after exposure to infected animal material is characteristic of cutaneous anthrax.'),
(8,'A child from a setting with poor sanitation passes a large intestinal roundworm. Heavy infection is associated with intestinal obstruction and migration into the biliary tree. Which organism is most likely?', ['Ascaris lumbricoides','Enterobius vermicularis','Strongyloides stercoralis','Trichuris trichiura'],'The large intestinal roundworm and obstruction pattern support ascariasis.'),
(16,'A child develops a papule at a kitten scratch, followed by subacute regional lymphadenopathy. Which infection most closely matches this sequence?', ['Bartonella henselae infection','Toxoplasmosis','Infectious mononucleosis','Rubella'],'An inoculation papule followed by regional lymphadenopathy after kitten exposure is the classic cat-scratch disease pattern.'),
(31,'A young infant develops constipation, poor feeding, a weak cry, and progressive hypotonia with descending weakness. Which diagnosis best fits?', ['Infant botulism','Tetanus','Poliomyelitis','Rabies'],'Constipation, bulbar weakness, and descending flaccid weakness support infant botulism; the other choices have different defining patterns.'),
(40,'After walking barefoot on a tropical beach, a child develops an intensely itchy, slowly migrating serpiginous track on a foot. Which diagnosis best fits?', ['Cutaneous larva migrans','Scabies','Tinea corporis','Cutaneous leishmaniasis'],'A pruritic serpiginous track following contact with contaminated sand is typical of cutaneous larva migrans.'),
(45,'A child with incomplete immunization develops pharyngitis with an adherent gray pseudomembrane and cervical swelling. Which disease best fits?', ['Diphtheria','Pertussis','Influenza','Mumps'],'An adherent pharyngeal pseudomembrane with cervical swelling is a key recognition pattern for respiratory diphtheria.'),
(49,'An adolescent develops fever, exudative pharyngitis, posterior cervical lymphadenopathy, and splenomegaly. Which diagnosis best fits?', ['Epstein-Barr virus infectious mononucleosis','Pertussis','Norovirus infection','Scabies'],'The combination of exudative pharyngitis, posterior cervical nodes, and splenomegaly supports infectious mononucleosis.'),
(52,'An adolescent develops fever and unilateral neck pain after pharyngitis. Imaging shows internal jugular vein thrombosis and septic pulmonary emboli. Which syndrome best fits?', ['Lemierre syndrome','Kawasaki disease','Hemolytic-uremic syndrome','Congenital rubella syndrome'],'Postpharyngeal sepsis with internal jugular thrombophlebitis and septic emboli supports Lemierre syndrome, associated with Fusobacterium.'),
(53,'A child has prolonged foul-smelling, greasy diarrhea, bloating, and weight loss after drinking untreated stream water. Which infection best fits?', ['Giardiasis','Pinworm infection','Influenza','Tetanus'],'A malabsorptive diarrheal syndrome after contaminated water exposure supports giardiasis.'),
(67,'A neonate has grouped skin vesicles and seizures. Which viral infection is an especially important diagnostic consideration?', ['Herpes simplex virus infection','Parvovirus B19 infection','Molluscum contagiosum','Human papillomavirus infection'],'Neonatal vesicular lesions with central nervous system involvement are a key herpes simplex presentation.'),
(70,'An infant has several days of high fever. As the fever resolves, a pink maculopapular rash appears, most prominently on the trunk. Which illness best fits?', ['Roseola','Measles','Varicella','Mumps'],'A rash appearing with defervescence after several days of high fever is the classic roseola sequence.'),
(75,'A child has persistent fever with bilateral nonpurulent conjunctivitis, oral mucosal changes, a polymorphous rash, swollen hands and feet, and cervical lymphadenopathy. Which diagnosis best fits?', ['Kawasaki disease','Infant botulism','Tinea corporis','Giardiasis'],'This constellation of fever, mucocutaneous findings, extremity changes, and lymphadenopathy supports Kawasaki disease.'),
(82,'After a tick exposure, a child develops an expanding erythematous skin lesion. Later manifestations can include facial palsy and arthritis. Which infection best fits?', ['Lyme disease','Scabies','Candidiasis','Mumps'],'An expanding erythema migrans lesion with possible later neurologic or joint manifestations supports Lyme disease.'),
(86,'A child develops fever, cough, coryza, and conjunctivitis. Small whitish lesions are seen on the buccal mucosa before a generalized rash spreads from the face downward. Which disease best fits?', ['Measles','Rubella','Roseola','Varicella'],'The respiratory prodrome, conjunctivitis, buccal Koplik spots, and descending rash support measles.'),
(90,'A child has multiple small, smooth, pearly papules with central umbilication. Which diagnosis best fits?', ['Molluscum contagiosum','Impetigo','Scabies','Tinea corporis'],'Smooth, centrally umbilicated papules are characteristic of molluscum contagiosum.'),
(93,'An adolescent develops tender parotid swelling and pain with chewing. Orchitis is a recognized complication in postpubertal males. Which infection best fits?', ['Mumps','Rubella','Rotavirus infection','Tinea capitis'],'Parotitis with the recognized complication of orchitis supports mumps.'),
(103,'A well child develops bright red cheeks followed by a lacy rash on the trunk and limbs. Which infection best fits?', ['Parvovirus B19 infection','Measles','Varicella','Mumps'],'The slapped-cheek appearance followed by a lacy exanthem is typical of erythema infectiosum.'),
(109,'A child has repeated coughing paroxysms with posttussive vomiting. An inspiratory whoop may follow the paroxysms, although infants can present with apnea. Which disease best fits?', ['Pertussis','Diphtheria','Mumps','Tetanus'],'Paroxysmal cough, posttussive vomiting, and possible whoop or infant apnea support pertussis.'),
(110,'A school-aged child has intense perianal itching at night. Which infestation is most likely?', ['Enterobius vermicularis','Ascaris lumbricoides','Schistosoma species','Taenia solium'],'Nocturnal perianal pruritus is the characteristic presentation of pinworm infection.'),
(119,'After a mammalian bite, a patient develops encephalitis with hydrophobia and aerophobia. Which infection best fits?', ['Rabies','Poliomyelitis','Tetanus','Botulism'],'Hydrophobia and aerophobia with encephalitis after a mammalian exposure support furious rabies.'),
(129,'Several household members have intense nocturnal itching. A child has papules and burrows in the finger webs and flexural wrists. Which infestation best fits?', ['Scabies','Head lice','Cutaneous larva migrans','Tinea corporis'],'Household spread, nocturnal pruritus, and characteristic burrows in finger webs support scabies.'),
(133,'After a thorn injury, a child develops a skin nodule followed by a chain of nodules along regional lymphatic channels. Which infection best fits?', ['Sporotrichosis','Tinea corporis','Molluscum contagiosum','Varicella'],'Nodular lymphangitic spread after plant-related inoculation is a classic sporotrichosis pattern.'),
(145,'A child develops trismus, generalized rigidity, and painful stimulus-induced muscle spasms after a contaminated wound. Which diagnosis best fits?', ['Tetanus','Infant botulism','Poliomyelitis','Lyme disease'],'Trismus, rigidity, and stimulus-induced spasms reflect the characteristic tetanus syndrome.'),
(146,'A child has scalp scaling, patchy alopecia, and broken hairs. An inflammatory boggy lesion may develop. Which diagnosis best fits?', ['Tinea capitis','Tinea corporis','Scabies','Molluscum contagiosum'],'Scalp dermatophyte infection causes scaling and hair loss; an inflammatory kerion may occur.'),
(151,'An infant has hydrocephalus, intracranial calcifications, and chorioretinitis. Which congenital infection classically produces this combination?', ['Toxoplasmosis','Rubella','Parvovirus B19 infection','Varicella'],'Hydrocephalus, intracranial calcifications, and chorioretinitis form the classic congenital toxoplasmosis triad.'),
(163,'A child develops a pruritic eruption in successive crops. Macules, papules, vesicles, and crusts are present at the same time. Which infection best fits?', ['Varicella','Smallpox','Rubella','Roseola'],'Successive crops with lesions at different developmental stages support varicella.'),
(164,'A child develops profuse watery diarrhea with rapid dehydration after exposure to contaminated drinking water. The stool is described as rice-water. Which infection best fits?', ['Cholera','Shigellosis','Pinworm infection','Hepatitis A'],'Profuse rice-water diarrhea with rapid fluid loss is the classic cholera presentation.')
]
for j,(n,q,opts,why) in enumerate(CASES):
 c=chs[n-1];p=excerpt(section_paras(c,'CLINICAL MANIFESTATIONS'))
 answer=opts[0];random.shuffle(opts)
 quizzes.append({'id':f'vignette-{j+1:03d}','ch':n,'kind':'Authored clinical vignette','q':q,'options':opts,'answer':opts.index(answer),'explanation':why,'pdf_page':p['pdf_page'] if p else c['pdf_start'],'printed_page':p['printed_page'] if p else c['printed_start'],'option_chapters':[]})

ALIASES={'Nocardiosis':95,'Bartonella henselae infection':16,'Tuberculosis':157,'Plague':112,'Tularemia':159,'Scabies':129,'Ascaris lumbricoides':8,'Enterobius vermicularis':110,'Strongyloides stercoralis':141,'Trichuris trichiura':154,'Toxoplasmosis':151,'Infectious mononucleosis':49,'Rubella':127,'Infant botulism':31,'Tetanus':145,'Poliomyelitis':114,'Rabies':119,'Tinea corporis':147,'Cutaneous leishmaniasis':78,'Pertussis':109,'Influenza':74,'Mumps':93,'Norovirus infection':96,'Lemierre syndrome':52,'Kawasaki disease':75,'Hemolytic-uremic syndrome':50,'Congenital rubella syndrome':127,'Giardiasis':53,'Pinworm infection':110,'Herpes simplex virus infection':67,'Parvovirus B19 infection':103,'Molluscum contagiosum':90,'Human papillomavirus infection':73,'Roseola':70,'Measles':86,'Varicella':163,'Lyme disease':82,'Candidiasis':25,'Impetigo':137,'Rotavirus infection':126,'Tinea capitis':146,'Diphtheria':45,'Schistosoma species':130,'Botulism':31,'Head lice':105,'Cutaneous larva migrans':40,'Sporotrichosis':133,'Smallpox':132,'Cholera':164,'Shigellosis':131,'Hepatitis A':62,'Actinomycosis':1}
for q in quizzes:
 q['option_notes']=[]
 for i,o in enumerate(q['options']):
  n=q['option_chapters'][i] if q['option_chapters'] else ALIASES.get(o)
  if n:
   p=excerpt(section_paras(chs[n-1],'CLINICAL MANIFESTATIONS|OVERVIEW'),2)
   if p:q['option_notes'].append({'option':o,'ch':n,**p})

for c in chs:
 qs=[q for q in quizzes if q['ch']==c['num']];lines=[f"# {c['title']} — quizzes",'> Automated source recognition and authored diagnostic vignettes are explicitly labeled. This bank has not undergone independent specialist review.\n']
 for i,q in enumerate(qs,1):
  lines += [f"## Question {i} · {q['kind']}",q['q'],'\n'+'\n'.join(f"{chr(65+k)}. {o}" for k,o in enumerate(q['options'])),f"\n<details><summary>Answer and rationale</summary>\n\n{chr(65+q['answer'])}. {q['options'][q['answer']]}\n\n{q['explanation']}\n\n{mdsrc(q)}\n</details>\n"]
 (ROOT/f'wiki/mcqs/{c["num"]:03d}_mcqs.md').write_text('\n'.join(lines),encoding='utf-8')

stats={'chapters':len(chs),'figures':len(allfigs),'matched_captions':sum(f['caption_matched'] for f in allfigs),'tables':sum(len(c['tables']) for c in chs),'flashcards':len(cards),'mcqs':len(quizzes),'vignettes':len(CASES),'source_recall':sum(q['kind'].startswith('Automated') for q in quizzes),'treatment_records':len(therapies),'dose_records':sum(x['has_dose'] for x in therapies),'words':sum(len(c['raw_md'].split()) for c in chs)}
source_info=json.loads((ROOT/'build/source_metadata.json').read_text(encoding='utf-8'))
data={'source_pdf':pathlib.Path(source_info['source']).as_uri(),'chapters':catalog,'atlas':atlas,'therapies':therapies,'cards':cards,'quizzes':quizzes,'figures':allfigs,'features':[x[0] for x in FEATURES],'groups':list(GROUPS),'stats':stats}
(ROOT/'data/course.js').write_text('window.COURSE='+json.dumps(data,ensure_ascii=False)+';\n',encoding='utf-8')
(ROOT/'build/course_data.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
(ROOT/'build/metrics.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
anki=['#separator:tab','#html:true','#tags column:3']
for f in cards:
 anki.append(safe(f['q'])+'\t'+safe(f['a'])+'<br><br>'+safe(mdsrc(f))+'\tRedBookAtlas6e Ch_'+f"{f['ch']:03d}"+' '+re.sub(r'\W+','_',f['category']))
(ROOT/'anki_pediatric_infectious_diseases.tsv').write_text('\n'.join(anki)+'\n',encoding='utf-8')
idx=['# Vikkypaedia · Red Book Atlas 6e',f"168 chapters · {len(allfigs):,} extracted images · {len(cards):,} cards · {len(quizzes):,} quizzes",'\n[Open the interactive course](index.html)\n','The book is alphabetical. The six study pathways below are editorial learning groupings.\n']
for k in GROUPS:
 gchs=[c for c in catalog if c['group']==k];part=['# '+k,'> Editorial study pathway; not a source-book part.\n']
 idx+=['\n## '+k]
 for c in gchs:
  line=f"- {c['num']}. [{c['title']}](wiki/chapters/{c['num']:03d}.md) · printed pp. {c['printed_start']}-{c['printed_end']}"
  idx.append(line);part.append(line.replace('(wiki/chapters/','(../chapters/'))
 (ROOT/f"wiki/parts/{re.sub(r'[^a-z]+','_',k.lower())}.md").write_text('\n'.join(part),encoding='utf-8')
(ROOT/'index.md').write_text('\n'.join(idx),encoding='utf-8')
(ROOT/'raw/chapters/00_INDEX.md').write_text('# Raw chapter index\n\n'+'\n'.join(f"- [{c['num']}. {c['title']}]({c['num']:03d}.md)" for c in catalog),encoding='utf-8')
at=['# Pathogen and disease atlas','> Text excerpts indexed by chapter; no inferred gene, inheritance, or OMIM records.\n']
for c in atlas:
 at+=['## '+str(c['num'])+'. '+c['title'],'Pathway: '+c['group']]
 for key in ['etiology','epidemiology','diagnostics']:
  if c[key]:at += ['### '+key.title(),c[key]['text'],mdsrc(c[key])]
(ROOT/'wiki/pathogen_atlas.md').write_text('\n\n'.join(at),encoding='utf-8')
rx=['# Treatment and dosing excerpts','> Source-edition learning reference, not an independently validated prescribing resource. Whole paragraph context is retained; verify the original page and current guidance before clinical use.\n']
for t in therapies:rx += [f"## {t['title']} · {t['section']}",t['text'],mdsrc(t)]
(ROOT/'wiki/therapies_matrix.md').write_text('\n\n'.join(rx),encoding='utf-8')
readme=f'''# Vikkypaedia · Red Book Atlas 6e

Open **index.html** in a desktop browser. No server, sign-in, network connection, or installation is required. Keep the folder structure intact. The ZIP contains the same portable course.

Source: *Red Book Atlas of Pediatric Infectious Diseases*, 6th edition (2026), edited by Tina Q. Tan, American Academy of Pediatrics. The source has 1,178 PDF pages: front matter 1–14, chapters 15–1120, and index 1121–1178. All 168 source chapters are included.

## Included

- Reader: all source chapters with five source-extracted study pillars, paragraph page references, images, and links to complete raw Markdown.
- Pathogen atlas: etiology, epidemiology, and diagnostic excerpts for every chapter.
- Clinical feature explorer: 32 searchable feature tags. Results reflect text matches, not a validated differential diagnosis or a probability estimate.
- Treatment matrix: {stats['treatment_records']:,} paragraph excerpts, including {stats['dose_records']} with detected dose units. Ages, dose limits, route, and duration must be checked in the original source context.
- {stats['flashcards']:,} section recall cards with progress saved in this browser, chapter / pathway scopes, and Anki TSV export.
- {stats['mcqs']} quizzes: {stats['source_recall']} automated passage-recognition questions and {stats['vignettes']} authored diagnostic vignettes. They are labeled separately and have source references. No independent specialist item review has been performed.
- {stats['figures']:,} extracted image placements, caption reveal self-test, chapter filters, and full-size viewing.
- {stats['tables']} geometry-detected tables rendered as images and converted to Markdown. Other source tables remain in the raw page text; they were not silently converted into invented structured data.

## How to study

1. Choose a pathway or a chapter. Read the five study pillars, then the source content.
2. Explain the clinical pattern aloud and work through its flashcards.
3. Use the visual spotter with captions hidden.
4. Complete authored vignettes and source-recognition quizzes; open source references after answering.
5. Revisit cards marked Needs review. Import `anki_pediatric_infectious_diseases.tsv` into Anki as Basic notes (field 1 Front, field 2 Back, field 3 Tags).

## Fidelity and limits

The reader is a structured extraction, not a facsimile. Raw Markdown retains small-font material and page markers; the clinical reader excludes captions from the clinical paragraphs and displays images separately. Some compound words may retain extraction artifacts. Multi-panel figures can share captions; {stats['figures']-stats['matched_captions']} image placements have no automatically matched caption and explicitly point to their source page. A rendered crop may include source labels. Clinical answers should be checked against the original PDF. Chapter numbering and page boundaries come from the embedded bookmarks, cross-checked against the printed contents and the 14-page offset.

The six pathways are course editorial groupings; the source book itself is alphabetical. No genetics / OMIM atlas is fabricated for this infectious disease text. Flashcards are source-extracted prompts; the automated quiz items are passage-recognition exercises rather than independently authored board questions. Progress storage depends on browser settings and stays on the device.

This is an edition-based study course, not a current treatment protocol. The current [AAP Red Book updates and errata](https://publications.aap.org/redbook/resources/15805) are separate from the source edition. The [AAP book page](https://publications.aap.org/aapbooks/monograph/797/Red-Book-Atlas-of-Pediatric-Infectious-Diseases) confirms the sixth edition. No live updates were merged into extracted textbook text.

## Build provenance

Built 21 October 2026 from the user-specified downloaded PDF. The two detailed supplied skill documents are byte-identical; the third is a shorter description of the same pipeline. The supplied Nelson examples, paths, counts, account names, publication steps, and force-push commands were treated as reference material. No remote repository or public website was created or modified.

See `BUILD_REPORT.md`, `build/verification.json`, and `build/source_metadata.json` for coverage and checks. Reproduction scripts are in `build/`; they require Python and PyMuPDF 1.26.7, and the source PDF path must be adapted for another machine.
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
(ROOT/'.nojekyll').touch()
(ROOT/'log.md').write_text('# Build log\n\n2026-10-21: Inspected supplied skill documents and exact downloaded PDF. Confirmed sixth edition 2026, 168 chapters. Extracted all content pages, original clinical image placements, and geometry-detected tables. Built source-linked study tools and local seven-mode app. No publication performed.\n',encoding='utf-8')
for script in ['extract_atlas.py','repair_text.py','normalize_tables.py','build_course.py']:
 if (BASE/'work'/script).exists():shutil.copyfile(BASE/'work'/script,ROOT/'build'/script)
print(json.dumps(stats,indent=2))
