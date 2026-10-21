'use strict';
const D=window.COURSE;
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let saved={};try{saved=JSON.parse(localStorage.getItem('vikkypaedia_pediatric_infections')||localStorage.getItem('vikkypaedia_redbook6e')||'{}')}catch{}
const state={chapter:saved.chapter||1,mode:'reader',cardStatus:saved.cards||{},tags:new Set(),cardIndex:0,cardDeck:[],quizList:[],qi:0,answers:{},galleryCount:36,resultCount:40,flipped:false};
let chapterRequest=0;
function persist(){try{localStorage.setItem('vikkypaedia_pediatric_infections',JSON.stringify({chapter:state.chapter,cards:state.cardStatus}))}catch{}}
function matches(obj,q){const str=typeof obj==='string'?obj:JSON.stringify(obj);return q.toLowerCase().split(/\s+/).filter(Boolean).every(t=>str.toLowerCase().includes(t))}
function meta(n=state.chapter){return D.chapters.find(c=>c.num===n)||D.chapters[0]}
function source(p,n){return `<div class="source-link">Printed p. ${p.printed_page} · PDF p. ${p.pdf_page} &nbsp; <button class="small-btn" onclick="openSource(${n},${p.pdf_page})">Read source</button> &nbsp; <a href="${esc(D.source_pdf)}#page=${p.pdf_page}" target="_blank">Original PDF page</a></div>`}
function footer(){return '<div class="footer">Vikkypaedia · Pediatric Infectious Diseases · Private study course. <a href="README.md" target="_blank">Course guide</a> · <a href="SOURCE_CREDITS.md" target="_blank">Source credits</a></div>'}
function toggleSidebar(){document.body.classList.toggle('sidebar-open')}
function closeSidebar(){document.body.classList.remove('sidebar-open')}
function renderChapters(){
 const q=$('chapter-search').value,g=$('pathway').value;
 const cs=D.chapters.filter(c=>(!g||c.group===g)&&matches([c.title,c.summary,c.features],q));
 $('chapter-count').textContent=`${cs.length} of 168 chapters`;
 $('chapters').innerHTML=cs.map(c=>`<button class="chapter-item ${c.num===state.chapter?'selected':''}" ${c.num===state.chapter?'aria-current="true"':''} onclick="selectChapter(${c.num})"><span class="num">${String(c.num).padStart(3,'0')}</span><span>${esc(c.title)}<small>pp. ${c.printed_start}–${c.printed_end} · ${c.figures} images</small></span></button>`).join('');
}
function selectChapter(n){state.chapter=n;state.cardIndex=0;persist();closeSidebar();renderChapters();$('chapter-badge').textContent=`☰ Ch ${n}`;setMode(state.mode)}
function moveChapter(d){selectChapter(Math.max(1,Math.min(168,state.chapter+d)))}
function openSource(n,p){state.chapter=n;state.sourcePage=p;persist();renderChapters();$('chapter-badge').textContent=`☰ Ch ${n}`;setMode('reader')}
function setMode(mode){
 state.mode=mode;state.resultCount=40;state.galleryCount=36;state.flipped=false;closeSidebar();
 document.body.classList.toggle('blind',mode==='quiz');
 document.querySelectorAll('.nav-tabs button').forEach(b=>{b.classList.toggle('active',b.dataset.mode===mode);b.setAttribute('aria-current',b.dataset.mode===mode?'page':'false')});
 $('main').scrollTop=0;
 ({reader:renderReader,atlas:renderAtlas,features:renderFeatures,therapy:renderTherapy,cards:renderCards,quiz:renderQuiz,spotter:renderSpotter}[mode])();
}
function header(kicker,title,desc){return `<div class="eyebrow">${kicker}</div><h2 class="heading">${title}</h2><p class="subtitle">${desc}</p>`}
function renderReader(){
 const c=meta();const token=++chapterRequest;
 $('view').innerHTML=header(`Chapter ${String(c.num).padStart(3,'0')} · ${esc(c.group)}`,esc(c.title),`Printed pp. ${c.printed_start}–${c.printed_end} · PDF pp. ${c.pdf_start}–${c.pdf_end}`)+`<div class="metrics"><div class="metric"><b>168</b> chapters</div><div class="metric"><b>${D.stats.figures.toLocaleString()}</b> images</div><div class="metric"><b>${D.stats.flashcards.toLocaleString()}</b> cards</div><div class="metric"><b>${D.stats.mcqs}</b> quizzes</div></div><div class="chapter-navigation"><button onclick="moveChapter(-1)" ${c.num===1?'disabled':''}>← Previous</button><button onclick="moveChapter(1)" ${c.num===168?'disabled':''}>Next chapter →</button></div><div id="chapter-body"><p>Opening chapter…</p></div>`;
 const finish=()=>{if(token!==chapterRequest||state.mode!=='reader')return;const ch=window.CHAPTERS[c.num];if(!ch)return;
  $('chapter-body').innerHTML=`<div class="pillars">${ch.pillars.map(p=>`<div class="pillar"><h3>${esc(p.label)}</h3><p>${esc(p.text)}</p><small>Printed p. ${p.printed_page} · PDF p. ${p.pdf_page}</small></div>`).join('')}</div><div class="toolbar"><button class="primary" onclick="setMode('cards')">Study chapter cards</button><button onclick="setMode('spotter')">Open visual spotter</button><a class="small-btn" href="${esc(D.source_pdf)}#page=${c.pdf_start}" target="_blank">Open original PDF</a><a class="small-btn" href="raw/chapters/${String(c.num).padStart(3,'0')}.md" target="_blank">Full extracted Markdown</a></div><div>${ch.features.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div><div class="notice">Source-edition excerpts for study. Confirm treatment details in the original page and current guidance. Raw Markdown retains small-font text omitted from the clinical reader.</div><article class="reader">${ch.reader_html}</article>${footer()}`;
  if(state.sourcePage){const text=`PDF p. ${state.sourcePage}`;const target=[...document.querySelectorAll('.reader .source')].find(x=>x.textContent.trim().endsWith(text));if(target)target.scrollIntoView({block:'center'});delete state.sourcePage}
 };
 if(window.CHAPTERS[c.num])finish();else{const s=document.createElement('script');s.src=`data/chapters/ch_${String(c.num).padStart(3,'0')}.js`;s.onload=finish;s.onerror=()=>{if(token===chapterRequest)$('chapter-body').innerHTML='<p class="load-error">The chapter data could not load. Keep the data folder beside index.html.</p>'};document.head.appendChild(s)}
}
function groupOptions(){return '<option value="">All pathways</option>'+D.groups.map(g=>`<option>${esc(g)}</option>`).join('')}
function renderAtlas(){
 $('view').innerHTML=header('Reference library','Pathogen & disease atlas','Etiology, epidemiology, and diagnostic excerpts for all 168 chapters. Every excerpt points back to its source page.')+`<div class="toolbar"><input id="atlas-search" aria-label="Search pathogen atlas" placeholder="Organism, transmission, diagnostic test…" oninput="updateAtlas()"><select id="atlas-group" aria-label="Atlas pathway" onchange="updateAtlas()">${groupOptions()}</select></div><div id="atlas-results"></div>${footer()}`;updateAtlas();
}
function updateAtlas(){
 const q=$('atlas-search').value,g=$('atlas-group').value;
 const rows=D.atlas.filter(c=>(!g||c.group===g)&&matches(c,q));
 $('atlas-results').innerHTML=`<div class="result-head"><small>${rows.length} topics</small></div>`+rows.slice(0,state.resultCount).map(c=>`<div class="card"><div class="pathway-label">${esc(c.group)}</div><h3>${esc(c.title)}</h3>${['etiology','epidemiology','diagnostics'].map(k=>c[k]?`<details ${q?'open':''}><summary>${{etiology:'Etiology',epidemiology:'Epidemiology & transmission',diagnostics:'Diagnostic workup'}[k]}</summary><p>${esc(c[k].text)}</p>${source(c[k],c.num)}</details>`:'').join('')}<button class="small-btn" onclick="openSource(${c.num},${c.pdf_start})">Open chapter ${c.num}</button></div>`).join('')+(rows.length>state.resultCount?'<button class="more" onclick="state.resultCount+=40;updateAtlas()">Show more topics</button>':'')+(rows.length?'':'<p class="empty">No topics match this search.</p>');
}
function renderFeatures(){
 $('view').innerHTML=header('Explore connections','Clinical feature explorer','Select findings to explore matching source topics. Scores count text tags; they are not diagnostic probabilities and do not distinguish negated findings.')+`<div class="toolbar"><input id="feature-search" aria-label="Filter clinical topics" placeholder="Optional topic or clue…" oninput="updateFeatures()"><button onclick="state.tags.clear();renderFeatureChips();updateFeatures()">Clear findings</button></div><div class="chips" id="feature-chips"></div><div id="feature-results"></div>${footer()}`;renderFeatureChips();updateFeatures();
}
function renderFeatureChips(){$('feature-chips').innerHTML=D.features.map((t,i)=>`<button class="${state.tags.has(t)?'selected':''}" aria-pressed="${state.tags.has(t)}" onclick="toggleFeature(${i})">${esc(t)}</button>`).join('')}
function toggleFeature(i){const t=D.features[i];state.tags.has(t)?state.tags.delete(t):state.tags.add(t);renderFeatureChips();updateFeatures()}
function updateFeatures(){
 const q=$('feature-search').value;const tags=[...state.tags];
 let rows=D.chapters.map(c=>({...c,matched:tags.filter(t=>c.features.includes(t))})).filter(c=>matches([c.title,c.summary,c.features],q)&&(!tags.length||c.matched.length));rows.sort((a,b)=>b.matched.length-a.matched.length||a.num-b.num);
 $('feature-results').innerHTML=`<small>${rows.length} topics · ${tags.length} selected findings · ranked by overlap</small>`+rows.slice(0,40).map(c=>`<div class="card"><div class="result-head"><h3>${esc(c.title)}</h3>${tags.length?`<b class="badge">${c.matched.length}/${tags.length} tags</b>`:''}</div><p>${esc(c.summary)}</p><div>${c.matched.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div><button class="small-btn" onclick="openSource(${c.num},${c.pdf_start})">Read source</button></div>`).join('')+(rows.length?'':'<p class="empty">No source topics match.</p>');
}
function renderTherapy(){
 $('view').innerHTML=header('Source-edition reference','Treatment & dosing excerpts','Search complete extracted paragraphs by drug or disease. Dose detection marks text containing dose units; it does not validate a regimen.')+`<div class="notice">Verify the original source context and current clinical guidance before prescribing. Table-based schedules may require the full chapter. No dose calculations or inferred regimens are supplied.</div><div class="toolbar"><input id="rx-search" aria-label="Search treatments" placeholder="Drug, disease, or phrase…" oninput="state.resultCount=40;updateTherapy()"><select id="rx-group" aria-label="Treatment pathway" onchange="updateTherapy()">${groupOptions()}</select><label><input type="checkbox" id="rx-dose" onchange="updateTherapy()"> Dose units only</label></div><div id="rx-results"></div>${footer()}`;updateTherapy();
}
function updateTherapy(){
 const q=$('rx-search').value,g=$('rx-group').value,dose=$('rx-dose').checked;
 const rows=D.therapies.filter(r=>(!g||r.group===g)&&(!dose||r.has_dose)&&matches(r,q));
 $('rx-results').innerHTML=`<small>${rows.length} source paragraphs</small>`+rows.slice(0,state.resultCount).map(r=>`<div class="card"><div class="pathway-label">${esc(r.section)} ${r.has_dose?'· DOSE UNITS DETECTED':''}</div><h3>${esc(r.title)}</h3><div>${r.drugs.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div><p class="rx-quote">${esc(r.text)}</p>${source(r,r.ch)}</div>`).join('')+(rows.length>state.resultCount?'<button class="more" onclick="state.resultCount+=40;updateTherapy()">Show more excerpts</button>':'')+(rows.length?'':'<p class="empty">No excerpts match.</p>');
}
function inScope(x,scope){return scope==='all'||scope==='chapter'&&x.ch===state.chapter||scope==='pathway'&&meta(x.ch).group===meta().group}
function scopeOptions(){return '<option value="chapter">Current chapter</option><option value="pathway">Current pathway</option><option value="all">Whole course</option>'}
function renderCards(){
 $('view').innerHTML=header('Active recall','Recall before you reveal',`Source-extracted prompts from ${esc(meta().title)}. Answer aloud, reveal the source excerpt, then mark your confidence.`)+`<div class="toolbar"><select id="card-scope" aria-label="Flashcard scope" onchange="buildCardDeck()">${scopeOptions()}</select><select id="card-filter" aria-label="Flashcard status" onchange="buildCardDeck()"><option value="all">All cards</option><option value="review">Needs review</option><option value="mastered">Mastered</option><option value="new">Unseen</option></select><button onclick="shuffle(state.cardDeck);state.cardIndex=0;showCard()">Shuffle</button><a class="small-btn" href="anki_pediatric_infectious_diseases.tsv" download>Download Anki TSV</a></div><div id="card-area"></div><p class="keyboard">Space: reveal · ← / →: navigate · 1: needs review · 2: mastered</p>${footer()}`;buildCardDeck();
}
function buildCardDeck(){const scope=$('card-scope').value,filter=$('card-filter').value;state.cardDeck=D.cards.filter(c=>inScope(c,scope)&&(filter==='all'||filter==='new'&&!state.cardStatus[c.id]||state.cardStatus[c.id]===filter));state.cardIndex=0;showCard()}
function showCard(){state.flipped=false;const deck=state.cardDeck;const f=deck[state.cardIndex];if(!f){$('card-area').innerHTML='<p class="empty">No cards in this selection.</p>';return}
 const mastered=deck.filter(c=>state.cardStatus[c.id]==='mastered').length;
 $('card-area').innerHTML=`<div class="progress-line">${state.cardIndex+1} / ${deck.length} · ${mastered} mastered · ${esc(state.cardStatus[f.id]||'Unseen')}</div><div class="fc-stage"><div class="flip" id="flip-card"><div class="face front"><div class="eyebrow">${esc(f.category)}</div><p class="question">${esc(f.q)}</p><button class="primary" onclick="flipCard()">Reveal answer</button></div><div class="face back" aria-hidden="true"><div class="eyebrow">Source excerpt</div><p>${esc(f.a)}</p>${source(f,f.ch)}<button class="small-btn" onclick="flipCard()">Back to prompt</button></div></div></div><div class="card-actions"><button onclick="moveCard(-1)">← Previous</button><button onclick="markCard('review')">1 · Needs review</button><button class="primary" onclick="markCard('mastered')">2 · Mastered</button><button onclick="moveCard(1)">Next →</button></div>`;
 $('flip-card').querySelector('.back').inert=true;
}
function flipCard(){if(!$('flip-card'))return;state.flipped=!state.flipped;$('flip-card').classList.toggle('flipped',state.flipped);$('flip-card').querySelector('.front').inert=state.flipped;$('flip-card').querySelector('.back').inert=!state.flipped;$('flip-card').querySelector('.back').setAttribute('aria-hidden',!state.flipped);$('flip-card').querySelector('.front').setAttribute('aria-hidden',state.flipped)}
function moveCard(d){if(!state.cardDeck.length)return;state.cardIndex=(state.cardIndex+d+state.cardDeck.length)%state.cardDeck.length;showCard()}
function markCard(status){const f=state.cardDeck[state.cardIndex];if(!f)return;state.cardStatus[f.id]=status;persist();moveCard(1)}
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function renderQuiz(){
 $('view').innerHTML=header('Blind practice','Quiz studio','Choose authored diagnostic vignettes or automated passage recognition. Source chapter details appear after answering. This item bank has not undergone independent specialist review.')+`<div class="toolbar"><select id="quiz-kind" aria-label="Quiz kind" onchange="buildQuiz()"><option value="Authored clinical vignette">Authored clinical vignettes</option><option value="Automated source recognition">Automated source recognition</option><option value="all">Both kinds</option></select><select id="quiz-scope" aria-label="Quiz scope" onchange="buildQuiz()"><option value="all">Whole course</option><option value="chapter">Current chapter</option><option value="pathway">Current pathway</option></select><button class="primary" onclick="buildQuiz(25)">Random 25-question block</button><button onclick="buildQuiz()">Reset session</button></div><div id="quiz-area"></div>${footer()}`;buildQuiz();
}
function buildQuiz(limit){const kind=$('quiz-kind').value,scope=$('quiz-scope').value;state.quizList=D.quizzes.filter(q=>inScope(q,scope)&&(kind==='all'||q.kind===kind));if(limit)shuffle(state.quizList);if(limit)state.quizList=state.quizList.slice(0,limit);state.qi=0;state.answers={};showQuiz()}
function showQuiz(){
 const q=state.quizList[state.qi];if(!q){$('quiz-area').innerHTML='<p class="empty">No questions match this selection. Try the whole course or automated source recognition.</p>';return}
 const answered=Object.keys(state.answers).length,correct=state.quizList.filter(x=>state.answers[x.id]===x.answer).length;
 const selection=state.answers[q.id],done=selection!==undefined;
 $('quiz-area').innerHTML=`<div class="progress-line">Question ${state.qi+1} of ${state.quizList.length} · ${answered} answered · ${correct} correct${answered?' ('+Math.round(100*correct/answered)+'%)':''}</div><div class="card quiz"><div class="eyebrow">${esc(q.kind)}</div><p class="quiz-stem">${esc(q.q)}</p><div>${q.options.map((o,i)=>`<button class="option ${done?(i===q.answer?'correct':i===selection?'wrong':''):''}" ${done?'disabled':''} onclick="answerQuiz(${i})"><b>${String.fromCharCode(65+i)}.</b><span>${esc(o)}</span></button>`).join('')}</div>${done?`<div class="rationale"><b>${selection===q.answer?'Correct.':'Review this item.'}</b><p>${esc(q.explanation)}</p>${source(q,q.ch)}${q.option_notes?.length?'<details><summary>Option-by-option source comparison</summary>'+q.option_notes.map(o=>`<p><b>${esc(o.option)}</b><br>${esc(o.text)}</p>${source(o,o.ch)}`).join('')+'</details>':''}${q.option_chapters.length?'<details><summary>Compare source topics</summary>'+q.option_chapters.map(n=>`<p><button class="small-btn" onclick="openSource(${n},${meta(n).pdf_start})">${esc(meta(n).title)}</button></p>`).join('')+'</details>':''}</div>`:''}</div><div class="card-actions"><button onclick="moveQuiz(-1)" ${state.qi===0?'disabled':''}>← Previous</button><button class="primary" onclick="moveQuiz(1)" ${state.qi===state.quizList.length-1?'disabled':''}>Next question →</button></div>`;
}
function answerQuiz(i){const q=state.quizList[state.qi];if(q&&state.answers[q.id]===undefined){state.answers[q.id]=i;showQuiz()}}
function moveQuiz(d){state.qi=Math.max(0,Math.min(state.quizList.length-1,state.qi+d));showQuiz()}
function renderSpotter(){
 $('view').innerHTML=header('Look · describe · recall','The visual spotter',`${D.stats.figures.toLocaleString()} extracted image placements. Describe the findings before revealing the original caption. Click an image to enlarge it.`)+`<div class="toolbar"><select id="spotter-scope" aria-label="Image scope" onchange="state.galleryCount=36;updateSpotter()">${scopeOptions()}</select><input id="spotter-search" aria-label="Search image captions" placeholder="Search captions…" oninput="state.galleryCount=36;updateSpotter()"><label><input id="spotter-test" type="checkbox" checked onchange="updateSpotter()"> Hide captions</label></div><div id="spotter-results"></div>${footer()}`;updateSpotter();
}
function updateSpotter(){
 const scope=$('spotter-scope').value,q=$('spotter-search').value,test=$('spotter-test').checked;
 const fs=D.figures.filter(f=>inScope({ch:f.chapter},scope)&&matches(f.caption,q));
 $('spotter-results').innerHTML=`<p class="pathway-label">${fs.length} image placements${test?' · source topic hidden until reveal':''}</p><div class="gallery">`+fs.slice(0,state.galleryCount).map(f=>{const idx=D.figures.indexOf(f);return `<div class="card spotter"><img loading="lazy" src="${f.path}" alt="${test?'Clinical study image':esc(f.caption)}" onclick="zoomImage(${idx})"><div id="caption-${idx}">${test?`<button class="hidden-caption" onclick="revealCaption(${idx})">Describe the image, then reveal caption</button>`:captionHTML(f)}</div></div>`}).join('')+'</div>'+(fs.length>state.galleryCount?'<button class="more" onclick="state.galleryCount+=36;updateSpotter()">Load more images</button>':'')+(fs.length?'':'<p class="empty">No images match this selection.</p>');
}
function captionHTML(f){return `<div class="caption"><b>${esc(meta(f.chapter).title)}</b><p>${esc(f.caption)}</p>${source(f,f.chapter)}</div>`}
function revealCaption(i){$('caption-'+i).innerHTML=captionHTML(D.figures[i])}
function zoomImage(i){const f=D.figures[i];const div=document.createElement('div');div.className='overlay';div.id='lightbox';div.setAttribute('role','dialog');div.setAttribute('aria-modal','true');div.setAttribute('aria-label','Enlarged clinical image');div.innerHTML=`<button onclick="closeZoom()">Close ✕</button><img src="${f.path}" alt="Enlarged clinical image">`;div.addEventListener('click',e=>{if(e.target===div)closeZoom()});document.body.appendChild(div);div.querySelector('button').focus()}
function closeZoom(){$('lightbox')?.remove()}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeZoom();closeSidebar();return}if(['INPUT','SELECT','TEXTAREA','BUTTON'].includes(e.target.tagName))return;if(state.mode==='cards'){if(e.code==='Space'){e.preventDefault();flipCard()}if(e.key==='ArrowRight')moveCard(1);if(e.key==='ArrowLeft')moveCard(-1);if(e.key==='1')markCard('review');if(e.key==='2')markCard('mastered')}});
if(!D){$('view').innerHTML='<p class="load-error">Missing course data. Keep index.html and its data folder together.</p>'}else{$('pathway').innerHTML+=D.groups.map(g=>`<option>${esc(g)}</option>`).join('');state.chapter=Math.max(1,Math.min(168,state.chapter));$('chapter-badge').textContent=`☰ Ch ${state.chapter}`;renderChapters();setMode('reader')}

