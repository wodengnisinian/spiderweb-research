"""Compile checked literature into an offline reading pack; standard library only."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlsplit
import hashlib,html,json,re,time

ROOT=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def esc(s):return html.escape(str(s),quote=True)
def textval(s):return '；'.join(map(str,s)) if isinstance(s,list) else str(s or '')
def main():
    files=['ai_sources.json','human_sources.json','question_sources.json','root_sources.json','SYNTHESIS.json','AI_NOTES.md','HUMAN_NOTES.md','QUESTION_NOTES.md']
    hashes={f:sha(ROOT/f) for f in files};sources=[];index={};alias={};duplicates=[];errors=[]
    areas=['AI机制与意义','人类认知与语境','问句与交际','证据争议与正面案例']
    for name,area in zip(files[:4],areas):
        for s in load(ROOT/name)['sources']:
            for k in ['id','title','year','url','source_type','read_extent','claim_supported','limitations']:
                if not s.get(k):errors.append(f'{name}:{s.get("id")}:missing {k}')
            if urlsplit(s['url']).scheme not in ['https','http']:errors.append('invalid URL '+s['id'])
            key=re.sub('[^a-z0-9]','',s['title'].lower())
            urls=[]
            for field in ['url','primary_text_url','primary_copy_url','read_url','publisher_url']:
                u=s.get(field)
                if isinstance(u,str) and u.startswith(('http://','https://')) and u not in urls:urls.append(u)
            extended=s['id'] in ['H08','Q07'];kind=textval(s['source_type'])
            category='扩展阅读：核查有限' if extended else ('综述／Perspective' if re.search('综述|Perspective|perspective|synthesis',kind) else ('理论论证' if re.search('理论|哲学|theoretical',kind) and not re.search('实验|experiment',kind) else '实验／模型研究'))
            if key in index:
                old=index[key];old['aliases'].append(s['id']);old['areas'].append(area);old['urls']+= [u for u in urls if u not in old['urls']];old['origin_records'].append({'file':name,'id':s['id']});alias[s['id']]=old['id'];duplicates.append({'merged':s['id'],'into':old['id'],'reason':'same normalized paper title'});continue
            entry={**s,'authors':textval(s.get('authors')),'aliases':[s['id']],'areas':[area],'urls':urls,'category':category,'evidence_status':'扩展阅读' if extended else '主要参考','implication':textval(s.get('implication_for_our_question',s.get('implication'))),'origin_records':[{'file':name,'id':s['id']}]}
            sources.append(entry);index[key]=entry;alias[s['id']]=s['id']
    ids={x['id'] for x in sources};syn=load(ROOT/'SYNTHESIS.json')
    for sec in syn['sections']:
        for i in sec['refs']:
            if i not in alias:errors.append('unknown citation '+i)
            elif alias[i] in ['H08','Q07']:errors.append('limited reading used as primary evidence '+i)
    for x in syn['reading_order']:
        if x['id'] not in alias:errors.append('unknown reading target')
    for name in files:
        if '\ufffd' in (ROOT/name).read_text(encoding='utf-8'):errors.append('replacement character '+name)
    if errors:raise RuntimeError(errors)
    source_map={s['id']:s for s in sources};core=sum(s['evidence_status']=='主要参考' for s in sources)
    register={'date':'2026-11-05','scope':syn['scope'],'source_count':len(sources),'main_reference_count':core,'extended_reading_count':len(sources)-core,'deduplicated_records':duplicates,'selection':'Targeted primary scholarly sources; experiments, theory and reviews explicitly separated. Not exhaustive or a claim to cover all 2026 work.','sources':sources,'aliases':alias,'input_sha256':hashes}
    dump(ROOT/'SOURCE_REGISTER.json',register)
    def refs(rs):return ' '.join('<a href="#src-'+esc(alias[i])+'">['+esc(i)+']</a>' for i in rs)
    def table(headers,body):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in row)+'</tr>' for row in body)+'</tbody></table></div>'
    p=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>理解问题：定义、证据与验证资料</title><style>'+CSS+'</style></head><body><main>']
    p.append('<header><div class="meta">2026-11-05 · 定向原始文献调研</div><h1>什么算理解一个问题？</h1><p class="lead">先分清研究对象，再看证据支持到哪一步。'+str(len(sources))+'份去重资料：'+str(core)+'项主要参考、'+str(len(sources)-core)+'项核查有限的扩展阅读。各条保留实际读取范围与原始链接。</p><p>'+esc(syn['scope'])+'</p></header>')
    p.append('<nav><a href="#synthesis">研究综合</a> · <a href="#measurement">验证手段</a> · <a href="#reading">建议阅读顺序</a> · <a href="#library">资料库</a> · <a href="#limits">证据边界</a></nav>')
    p.append('<section id="synthesis"><h2>基于资料的工作定义与关键区分</h2><div class="callout">'+esc(syn['working_definition'])+'<p class="muted">'+esc(syn['definition_status'])+'</p></div>')
    for sec in syn['sections']:p.append('<article><h3>'+esc(sec['title'])+'</h3><p>'+esc(sec['text'])+' '+refs(sec['refs'])+'</p><p class="tag">'+esc(sec['status'])+'</p></article>')
    p.append('</section><section id="measurement"><h2>同义判断、复述、解释与求解，各能说明什么</h2>')
    p.append(table(['观察任务','可以支持的有限主张','尚不能单独确立'],[[esc(r['task']),esc(r['can_support']),esc(r['cannot_establish'])] for r in syn['measurement_relations']]))
    p.append('<p>这张对应表是整理者的综合，不是某篇论文已经证明的统一理解充要条件。</p></section>')
    p.append('<section id="reading"><h2>建议先读的十篇</h2><ol>')
    for r in syn['reading_order']:
        s=source_map[alias[r['id']]];p.append('<li><a href="'+esc(s['url'])+'">'+esc(s['title'])+'</a>（'+str(s['year'])+'）——'+esc(r['reason'])+' '+refs([r['id']])+'</li>')
    p.append('</ol></section><section id="library"><h2>可检索资料库</h2><div class="filters"><label>检索 <input id="search" type="search" placeholder="作者、标题、主题或年份"></label><label>类型 <select id="category"><option value="">全部</option>'+''.join('<option>'+esc(c)+'</option>' for c in sorted({s['category'] for s in sources}))+'</select></label><span id="shown"></span></div><div id="cards">')
    for s in sources:
        p.append('<article class="source" id="src-'+esc(s['id'])+'" data-category="'+esc(s['category'])+'"><div class="tag">'+esc(' / '.join(s['aliases']))+' · '+esc(s['evidence_status'])+' · '+esc(s['category'])+' · '+str(s['year'])+'</div><h3><a href="'+esc(s['url'])+'">'+esc(s['title'])+'</a></h3><p class="muted">'+esc(s['authors'])+'<br>'+esc('、'.join(s['areas']))+'</p>')
        p.append('<p><b>资料类型：</b>'+esc(s['source_type'])+'</p><p><b>支持的主张：</b>'+esc(textval(s['claim_supported']))+'</p><p><b>局限：</b>'+esc(textval(s['limitations']))+'</p><p><b>与当前问题的关系：</b>'+esc(s['implication'])+'</p><details><summary>实际读取范围与原始入口</summary><p>'+esc(s['read_extent'])+'</p><ul>'+''.join('<li><a href="'+esc(u)+'">'+esc(u)+'</a></li>' for u in s['urls'])+'</ul><p>登记来源：'+esc('；'.join(x['file']+' : '+x['id'] for x in s['origin_records']))+'</p></details></article>')
    p.append('</div></section><section id="limits"><h2>阅读范围和证据边界</h2><ul>'+''.join('<li>'+esc(x)+'</li>' for x in syn['limits'])+'</ul><p>H08 Kintsch与Q07 Karttunen已明确列为扩展阅读，不作为本页关键综合的主证据。Frank与Goodman在两个分支出现，合并为同一条，不重复计数。某些综述引用了原始实验，也不视作新的独立样本。</p>')
    p.append('<div class="scroll"><table><tr><th>本地资料</th><th>用途</th></tr>'+''.join('<tr><td><a href="'+esc(f)+'">'+esc(f)+'</a></td><td>'+esc(desc)+'</td></tr>' for f,desc in [('SOURCE_REGISTER.json','去重来源、链接、类型与读取范围'),('SYNTHESIS.json','工作定义与综合主张的来源映射'),('AI_NOTES.md','AI文献阅读笔记'),('HUMAN_NOTES.md','人类认知文献阅读笔记'),('QUESTION_NOTES.md','问句语义与语用阅读笔记'),('AUDIT.json','编译与范围核验')])+'</table></div></section><footer>只做资料收集和综合。理论、原始实验、模型分析和观点综述分别标注；本文没有运行新模型实验。</footer></main><script>'+JS+'</script></body></html>')
    page=''.join(p);(ROOT/'REPORT.html').write_text(page,encoding='utf-8')
    class Check(HTMLParser):
        def __init__(self):super().__init__();self.ids=[];self.hrefs=[];self.src=[]
        def handle_starttag(self,t,attrs):
            a=dict(attrs)
            if 'id' in a:self.ids.append(a['id'])
            if 'href' in a:self.hrefs.append(a['href'])
            if 'src' in a:self.src.append(a['src'])
    ck=Check();ck.feed(page)
    if len(ck.ids)!=len(set(ck.ids)):errors.append('duplicate HTML id')
    for h in ck.hrefs:
        if h.startswith('#') and h[1:] not in ck.ids:errors.append('missing anchor '+h)
        elif not h.startswith('#') and not urlsplit(h).scheme and h!='AUDIT.json' and not (ROOT/h).is_file():errors.append('missing local link '+h)
    if ck.src:errors.append('unexpected embedded network/file resources')
    for f,d in hashes.items():
        if sha(ROOT/f)!=d:errors.append('input changed during compile '+f)
    old=ROOT.parent/'question-understanding-only';receipt=load(old/'RUN_MANIFEST.json');unchanged=sha(old/'understanding.py')==receipt['source_sha256']
    for r in receipt['runs']:
        unchanged=unchanged and sha(Path(r['path'])/'best.pt')==r['frozen']['checkpoint_sha256']
    if not unchanged:errors.append('previous model snapshot changed')
    audit={'status':'passed' if not errors else 'failed','passed':not errors,'date':'2026-11-05','source_count':len(sources),'main_reference_count':core,'extended_reading_count':len(sources)-core,'duplicate_records_merged':duplicates,'categories':dict(Counter(s['category'] for s in sources)),'source_required_fields_checked':True,'citation_ids_resolved':True,'limited_sources_excluded_from_primary_synthesis':True,'input_hashes_unchanged':True,'html_internal_and_local_links_checked':True,'external_embedded_resources':0,'previous_understanding_model_source_and_two_weights_match_frozen_receipts':unchanged,'new_experiments_run':False,'models_imported_or_trained_by_this_builder':False,'browser_render_inspected':False,'errors':errors,'input_sha256':hashes,'output_sha256':{f:sha(ROOT/f) for f in ['SOURCE_REGISTER.json','SYNTHESIS.json','REPORT.html']},'builder_sha256':sha(Path(__file__))}
    dump(ROOT/'AUDIT.json',audit);print(json.dumps({k:audit[k] for k in ['status','source_count','main_reference_count','extended_reading_count','categories','errors']},ensure_ascii=False));assert not errors

CSS='''body{margin:0;background:#f2f5f7;color:#182b3d;font:16px/1.8 "Segoe UI","Microsoft YaHei",sans-serif}main{max-width:1120px;margin:auto;padding:36px 40px 60px;background:#fff}h1{font-size:36px;line-height:1.3}h2{font-size:25px;margin-top:0}h3{font-size:19px;margin:10px 0}.lead{font-size:19px}.meta,.tag,.muted{color:#596f80}.tag{font-size:13px}.callout{padding:18px 22px;border-left:4px solid #2d718b;background:#edf6f8}a{color:#176181;text-underline-offset:3px}nav{padding:16px 0;border-bottom:1px solid #d4e0e5;line-height:2}section{margin-top:36px;scroll-margin-top:20px}article{margin:20px 0}.source{border:1px solid #d9e4e8;border-radius:8px;padding:18px 22px}.source:target{border-color:#267b9d;background:#f3fafc}details{padding:10px 0}summary{cursor:pointer;color:#215b72}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:10px 12px;border:1px solid #dbe5e9;text-align:left;vertical-align:top}th{background:#eef5f7}.filters{display:flex;gap:18px;flex-wrap:wrap;align-items:center;padding:14px;background:#edf4f7;border-radius:6px}input,select{font:inherit;padding:6px 10px;border:1px solid #a8bfcb;border-radius:4px;max-width:100%}li{margin:8px 0}footer{margin-top:36px;border-top:1px solid #d4e0e5;padding-top:18px;font-size:13px;color:#596f80}@media(max-width:720px){main{padding:22px 15px}h1{font-size:28px}.source{padding:14px}.filters{display:block}.filters label{display:block;margin-bottom:8px}td,th{padding:8px}}@media print{body{background:white}main{max-width:none;padding:0}nav,.filters{display:none}.source{break-inside:avoid}}'''
JS='''const cards=[...document.querySelectorAll('.source')];function filter(){const q=document.querySelector('#search').value.toLowerCase();const cat=document.querySelector('#category').value;let n=0;for(const c of cards){const yes=(!cat||c.dataset.category===cat)&&c.textContent.toLowerCase().includes(q);c.hidden=!yes;if(yes)n++;}document.querySelector('#shown').textContent=n+' / '+cards.length+' 条';}document.querySelector('#search').addEventListener('input',filter);document.querySelector('#category').addEventListener('change',filter);filter();'''
if __name__=='__main__':main()
