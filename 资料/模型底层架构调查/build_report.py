from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import html
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent
INPUTS = ["foundation_models.json", "open_models.json", "alternative_models.json", "closed_multimodal_models.json"]

def save_json(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def esc(value):
    return html.escape(str(value), quote=True)

def items(values):
    return "<ul>" + "".join("<li>" + esc(v) + "</li>" for v in values) + "</ul>"

def draw_map():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    from matplotlib.patches import FancyBboxPatch
    font = FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc")
    plt.rcParams["svg.fonttype"] = "path"
    fig, ax = plt.subplots(figsize=(14, 10), dpi=160)
    fig.patch.set_facecolor("#f8fafc")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")
    def text(x,y,s,size=16,weight="normal",ha="left",color="#172b3a"):
        ax.text(x,y,s,fontproperties=font,fontsize=size,weight=weight,ha=ha,va="center",color=color,linespacing=1.6)
    text(.35,9.6,"模型架构：四个需要分别看的层面",23,"bold")
    text(.35,9.1,"同一个模型可以同时是：因果解码器 + 混合信息机制 + 稀疏 MoE。",12,color="#526373")
    rows = [
      (7.35,"1  序列骨架",["编码器\n例：BERT","因果解码器\n例：Llama 3.1","编码器—解码器\n例：原始 T5","递归或混合\n例：Mamba / Qwen3-Next"],"决定输入与输出如何组织、哪些位置允许互相读取。"),
      (5.45,"2  跨位置信息传递",["Softmax 注意力\nMHA / MQA / GQA / MLA","状态空间或递归\nMamba / RWKV","线性注意力变体\nGated DeltaNet","局部卷积\n例：ResNet 视觉骨干"],"注意力的缓存共享、状态压缩与局部感受野，是不同的设计维度。"),
      (3.55,"3  参数激活方式",["Dense\n逐位置计算使用稠密 FFN","Sparse MoE\n路由选择部分专家 FFN"],"MoE 通常描述前馈子层的条件计算；不表示多个独立大模型共同商议。"),
      (1.65,"4  训练与系统",["训练目标\n下一 token / MLM / 去噪等","后训练\nSFT / 偏好优化 / RL 等","系统能力\n检索 / 工具 / 代理调度"],"这一层影响最终行为，需要与网络结构分列；不能由名称推断隐藏拓扑。")
    ]
    for y,title,boxes,note in rows:
        text(.35,y+0.8,title,16,"bold")
        w=(13.3-(len(boxes)-1)*.18)/len(boxes)
        for i,label in enumerate(boxes):
            x=.35+i*(w+.18)
            ax.add_patch(FancyBboxPatch((x,y-.35),w,.9,boxstyle="round,pad=0.01,rounding_size=.06",edgecolor="#b8c6d0",facecolor="#ffffff",linewidth=.9))
            text(x+w/2,y+.1,label,12,ha="center")
        text(.35,y-.63,note,11,color="#526373")
    text(.35,.32,"示意图按公开版本归纳，不是互斥分类树，也不代表闭源模型的完整内部结构。",11,color="#526373")
    fig.subplots_adjust(left=.015,right=.995,bottom=.01,top=.995)
    fig.savefig(ROOT/"架构分层图.png",dpi=160)
    fig.savefig(ROOT/"架构分层图.svg")
    plt.close(fig)

models=[]
checks=[]
for name in INPUTS:
    raw=json.loads((ROOT/name).read_text(encoding="utf-8-sig"))
    if isinstance(raw,dict):
        raw=raw.get("models",raw.get("cards",raw))
    assert isinstance(raw,list),name
    for record in raw:
        required=["id","model","version","publication_date","architecture_summary","components","disclosed_details","unknowns","sources"]
        assert all(k in record for k in required),(name,record.get("id"))
        assert all(isinstance(record[k],list) and record[k] for k in ["components","disclosed_details","unknowns","sources"]),record["id"]
        for source in record["sources"]:
            assert all(source.get(k) for k in ["title","url","read_extent"]),(record["id"],source)
            assert urlsplit(source["url"]).scheme=="https",source
        record["input_file"]=name
        models.append(record)
    checks.append({"check":"input_schema","file":name,"passed":True,"cards":len(raw)})
assert len({m["id"] for m in models})==len(models)
date=datetime.now().astimezone().isoformat(timespec="seconds")
save_json("MODEL_REGISTER.json",{"generated_at":date,"scope":"主流语言/多模态模型与代表性基础架构抽样，精确版本，不声称穷尽或全部为最新版本。","models":models})
source_index={}
for m in models:
    for s in m["sources"]:
        v=source_index.setdefault(s["url"],{"title":s["title"],"url":s["url"],"used_by":[],"read_extents":[]})
        v["used_by"].append(m["id"])
        if s["read_extent"] not in v["read_extents"]:v["read_extents"].append(s["read_extent"])
for s in json.loads((ROOT/"supporting_sources.json").read_text(encoding="utf-8")):
    assert all(s.get(k) for k in ["title","url","read_extent"])
    source_index[s["url"]]={"title":s["title"],"url":s["url"],"used_by":["report_mechanisms_complexity"],"read_extents":[s["read_extent"]]}
save_json("SOURCE_REGISTER.json",{"generated_at":date,"sources":list(source_index.values()),"note":"阅读范围由研究记录逐项标注；不是所有链接可达性的自动复查，也不代表下载了全部论文或权重。"})
draw_map()

css="""
:root{color-scheme:light dark;--bg:#f5f6f8;--fg:#182735;--muted:#526373;--paper:white;--line:#d4dce3;--soft:#eef3f7;--link:#175e9c}
@media(prefers-color-scheme:dark){:root{--bg:#151c23;--fg:#e8eef4;--muted:#b6c2cd;--paper:#202a34;--line:#465563;--soft:#2a3845;--link:#9ac9ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font-family:system-ui,'Microsoft YaHei',sans-serif;line-height:1.8;font-size:16px}main{max-width:1180px;margin:auto;padding:32px 30px 70px}h1{font-size:31px;line-height:1.4}h2{margin-top:42px;padding-bottom:7px;border-bottom:1px solid var(--line)}h3{margin:0 0 8px}a{color:var(--link);overflow-wrap:anywhere}p{margin:12px 0}nav{display:flex;flex-wrap:wrap;gap:10px 22px}section{margin:20px 0}.note{background:var(--soft);padding:16px 20px;border-radius:8px}.muted{color:var(--muted)}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;background:var(--paper)}th,td{vertical-align:top;text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);overflow-wrap:anywhere}th{background:var(--soft)}td:first-child{min-width:170px}details{margin:14px 0;padding:16px 20px;background:var(--paper);border:1px solid var(--line);border-radius:8px}summary{font-size:18px;font-weight:600;cursor:pointer}ul{padding-left:24px;margin:8px 0 14px}li{margin:5px 0}.formula{padding:14px;background:var(--soft);white-space:pre-wrap;overflow-wrap:anywhere;font-family:Consolas,monospace}img{width:100%;height:auto;display:block}small{font-size:13px}.pill{display:inline-block;background:var(--soft);padding:1px 8px;border-radius:4px;font-size:13px}@media(max-width:600px){main{padding:18px 14px 40px}h1{font-size:25px}th,td{padding:9px}summary{font-size:17px}}@media print{details{break-inside:avoid}main{max-width:none}body{background:white;color:black}nav{display:none}}
"""
foundation_link='<a href="https://arxiv.org/html/1706.03762v7">原始 Transformer §3</a>'
gqa_link='<a href="https://aclanthology.org/2023.emnlp-main.298.pdf">GQA §2</a>'
taxonomy_rows=[
 ("编码器 Transformer","BERT（原始版本）","双向读取输入，在上下文中更新各位置表示；常接分类、标注或其他任务头。","原始BERT使用MLM和NSP训练；训练目标与编码器结构分别记录。"),
 ("因果解码器 Transformer","Llama 3.1、Qwen3、Mistral、DeepSeek-V3等具体版本","每个位置读取其允许的前文，多层更新表示后预测后续token。","自回归是输出组织；Dense/MoE、GQA/MLA可进一步细分。"),
 ("编码器—解码器","原始Transformer、原始T5","编码输入，再用因果解码器通过交叉注意力读取编码结果。","不是简单地把输入和输出都叫成‘理解层’。"),
 ("递归 / 选择性SSM","LSTM、GRU、Mamba-1/2、RWKV-7","按机制维护和更新状态；不同模型的状态形状与更新方程不同。","固定宽度下的状态成本较稳定，不等于无损保存任意长历史。"),
 ("Retention / 线性注意力及混合","RetNet、Gated DeltaNet、Qwen3-Next","以可递归的聚合/更新处理历史；混合模型再插入全注意力层。","不同线性机制并不相同，也不能直接等同softmax注意力。"),
 ("卷积与视觉Transformer","ResNet、CLIP视觉分支中的ResNet或ViT","卷积逐级聚合局部视觉特征；ViT将图像patch组织为token进行注意力交互。","CNN、ViT是骨干，CLIP的图文对比目标是另一层设计。"),
 ("潜空间扩散与DiT","LDM/Stable Diffusion v1、DiT论文模型","在去噪/生成过程中反复调用网络；LDM可用U-Net，DiT用Transformer骨干。","扩散描述生成建模/采样路线，不能与Transformer当作完全互斥类别。")
]
taxonomy="<div class='scroll'><table><thead><tr><th>架构路线</th><th>本次代表</th><th>信息怎样传递</th><th>需要分清</th></tr></thead><tbody>"+"".join("<tr>"+"".join("<td>"+esc(x)+"</td>" for x in row)+"</tr>" for row in taxonomy_rows)+"</tbody></table></div>"

matrix="<div class='scroll'><table><thead><tr><th>模型 / 组件</th><th>精确版本</th><th>公开结构摘要</th><th>核对出处</th></tr></thead><tbody>"
cards=""
for m in models:
    sid=esc(m["id"])
    matrix+=f"<tr><td><a href='#{sid}'>{esc(m['model'])}</a></td><td>{esc(m['version'])}</td><td>{esc(m['architecture_summary'])}</td><td>"+"<br>".join(f"<a href='{esc(s['url'])}'>{esc(s['title'])}</a>" for s in m["sources"])+"</td></tr>"
    extra="".join(f"<p><strong>{label}：</strong>{esc(m[key])}</p>" for key,label in [("architecture_family","结构家族"),("state_flow","状态传递"),("attention_replacement","与注意力的关系"),("training_objective","训练目标"),("complexity_scope","复杂度范围"),("disclosure_status","披露状态")] if m.get(key))
    cards+=f"<details id='{sid}'><summary>{esc(m['model'])} · {esc(m['version'])}</summary><p class='muted'>发表时间：{esc(m['publication_date'])}</p><p>{esc(m['architecture_summary'])}</p>"+extra+"<h4>组件</h4>"+items(m["components"])+"<h4>已核到的细节</h4>"+items(m["disclosed_details"])+"<h4>未知项与适用边界</h4>"+items(m["unknowns"])+"<h4>原始来源与实际阅读范围</h4><ol>"+"".join(f"<li><a href='{esc(s['url'])}'>{esc(s['title'])}</a><br><small>{esc(s['read_extent'])}</small></li>" for s in m["sources"])+"</ol></details>"
matrix+="</tbody></table></div>"
reading_links="".join(f"<li><a href='{f}'>{esc(f)}</a></li>" for f in ["MODEL_REGISTER.json","SOURCE_REGISTER.json","OPEN_MODELS_NOTES.md","ALTERNATIVE_NOTES.md","DISCLOSURE_NOTES.md","架构分层图.svg","架构分层图.mmd","AUDIT.json","build_report.py"])
prior_href="../打开资料.html" if ROOT.parent.name=="针对-理解-的调查资料" else "../针对-理解-的调查资料/打开资料.html"

body=f"""<h1>各类模型的底层架构调查</h1>
<p class='muted'>资料核对日期：2026-11-05｜以原论文、开发者模型卡、官方配置和参考实现为依据</p>
<nav><a href='#overview'>架构分层</a><a href='#families'>路线对比</a><a href='#matrix'>全部条目</a><a href='#mechanisms'>关键机制</a><a href='#understanding'>与理解问题的关系</a><a href='#cards'>逐项证据</a><a href='#process'>过程与限制</a><a href='#files'>资料文件</a></nav>
<section class='note'><strong>本次整理 {len(models)} 个模型、架构或组件条目，关联 {len(source_index)} 个不同来源链接。</strong><p>它们不是{len(models)}个都处于同一层级的完整大模型：包含指定模型版本、基础网络和注意力组件。范围以语言/多模态基础模型为主，并纳入代表性递归、视觉和扩散路线。这是一份有版本边界的架构抽样，不是全世界所有模型名录，也不声称每个条目都是2026年最新产品。</p></section>
<section id='overview'><h2>先把架构放在正确层面</h2><p>“Transformer”“MoE”“强化学习”“推理模型”“RAG”分别可能指网络骨干、参数激活、训练方式、行为定位和系统组织。比较底层架构，需要把这些层面展开。同一模型可同时具备多项特征。</p><img src='架构分层图.png' alt='四个架构观察层面：序列骨架、跨位置信息传递、参数激活，以及训练和系统。详见下表与各模型证据卡。'><p><a href='架构分层图.svg'>打开可缩放图</a></p></section>
<section id='families'><h2>主要架构路线</h2>{taxonomy}<p class='muted'>此表是对下列来源卡的综合归纳，不给各路线附加未经测量的“理解分数”。</p></section>
<section id='matrix'><h2>模型与组件总表</h2><p>点击名称查看版本、组件、未知项和实际阅读范围；来源链接打开原始资料。</p>{matrix}</section>
<section id='mechanisms'><h2>真正需要比较的关键机制</h2>
<h3>1. 注意力不是完整网络</h3><p>在标准Transformer中，跨位置的信息交互与逐位置前馈计算交替进行，旁边还有残差、归一化和位置信息。原始模型采用编码器—解码器；现代具体模型可采用不同堆叠和组件。{foundation_link}。</p>
<div class='formula'>Q = XWq,  K = XWk,  V = XWv\nAttention(Q,K,V) = softmax(QKᵀ / √d + M)V\n说明：M控制允许读取的位置；Q/K/V是可学习投影产生的表示。</div>
<h3>2. MHA / MQA / GQA / MLA 改变的内容不同</h3><p>MHA为各头使用各自K/V；MQA让查询头共享一组K/V；GQA按查询组共享K/V。它们都可以保留多个查询头。MLA在DeepSeek-V3等指定版本中采用低秩潜在表示压缩K/V相关信息，并处理位置项；不能把它说成简单的“更少KV头”。{gqa_link}；MLA细节见DeepSeek-V3证据卡。</p>
<h3>3. Dense 与 MoE</h3><p>稠密模型与稀疏MoE的差别之一，是每个token的前馈计算是否通过路由激活部分专家。专家是可训练的子网络，并不天然对应人类命名的语义领域。总参数、单token激活参数、专家数和top-k必须按版本分别核对；激活参数也不能直接当作端到端速度或内存占用。见Mixtral、DeepSeek-V3、Qwen3-Next和Llama4 Scout卡。</p>
<h3>4. 递归状态、SSM、线性注意力及混合</h3><p>LSTM/GRU维护门控状态；Mamba采用输入相关的选择性状态空间机制；RWKV-7、RetNet、Gated DeltaNet又有各自更新形式。它们不能仅因“可递归”就合并成同一算法。混合模型可交替使用线性状态更新和全注意力。若宽度、状态维与层数固定，部分机制在递归生成时可保持相对输入长度恒定的状态规模，但状态压缩并不保证无损记忆任意历史。</p>
<h3>5. 复杂度要带条件</h3><p>标准全局softmax注意力的跨token乘法随长度n含二次项；FFN和投影还有其他成本。MQA/GQA主要减少KV头缓存，并没有消除所有两两交互。<a href='https://arxiv.org/abs/2205.14135'>FlashAttention</a>等内核优化可减少实际内存流量，不能据此把全局注意力的算术成本自动写成线性。不同结构的真实速度还取决于长度、批量、硬件、精度、实现与并行方式。本次没有做性能实测。</p>
</section>
<section id='understanding'><h2>这些结构与“理解问题”有什么关系</h2>
<p><strong>架构提供信息处理的方式；是否形成了可用的问题含义，需要另外提供行为或表征证据。</strong>这里的判断是本次研究的分析原则，不是任何一篇架构论文已经证明的统一理解定理。</p>
<ul><li>编码器能让各输入位置在上下文中互相更新，因此适合研究单个问题的表征；能输出向量还不足以确认关系方向、否定范围、指代与询问目标都已掌握。</li><li>因果解码器也能在训练后处理整段已给问题并产生解释。因果掩码规定计算依赖，并不直接等于“只能看局部”或“不能理解”。</li><li>SSM/递归路线需要观察哪些语义信息被状态保留、何时被覆盖；MoE路线需要观察路由和专家计算实际贡献，不能把路由热图等同语义解释。</li><li>需要区分骨干、训练数据、优化、任务定义和评测。先前小型实验的失败不能由本次文献调查改写为成功，也不能单凭那个失败推断所有自注意力架构都不可能理解。</li></ul>
<p>对后续“单纯理解问题”的研究，本资料可用于选择和比较骨干，测试内容仍应围绕问题本身：问什么、涉及谁和什么关系、条件与否定如何约束含义、改写后哪些应保持或改变。本轮只搜集与整理资料，没有执行新的训练、推理或检索链实验。</p>
</section>
<section id='cards'><h2>逐项版本与证据卡</h2>{cards}</section>
<section id='process'><h2>搜集过程、已知限制和未完成范围</h2>
<ol><li>将任务拆为基础骨干与组件、开放权重语言模型、替代序列结构、闭源公开披露与多模态四组，并行查阅后合并。</li><li>优先打开原始论文全文、官方模型卡、配置或开发者实现。各卡记录实际阅读范围；只读到局部时，范围保留在来源字段，不冒充通读全部报告。</li><li>按精确版本核对。开放权重模型的名称相近，不表示版本架构相同；未核到的字段保留未知。</li><li>核对来源数据结构、唯一编号、出处字段、离线页面本地链接及交付文件SHA-256。AUDIT.json仅记录这些交付检查，不代表复现了模型或性能。</li></ol>
<p>主要限制：未下载模型权重；未复现实验；未做统一速度、内存、能力排名；未重新验证每一个外链在所有网络环境都可打开。架构披露不足的GPT-4o、Claude 3等条目列明未知，不能从“推理”或产品名称猜测层数、参数、专家和注意力类型。某些历史版本被纳入是为了比较机制，不意味着它仍是该系列最新版本。详见各组NOTES文件中的访问限制。</p>
<p>未系统覆盖语音专用、世界模型、图神经网络、推荐系统、机器人策略以及全部视频生成模型；这些应作为后续独立方向，不能由本报告推断其结构。</p>
</section>
<section id='files'><h2>资料文件</h2><ul>{reading_links}</ul><p><a href='{prior_href}'>上一份：针对“理解”的调查资料</a></p><p class='muted'>生成时间：{esc(date)}。本页面和图形可离线阅读，来源链接需联网。build_report.py读取同目录来源JSON重建报告与图形，需Python和matplotlib；Windows默认使用微软雅黑字体。</p></section>
"""
document="<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>模型底层架构调查</title><style>"+css+"</style></head><body><main>"+body+"</main></body></html>"
(ROOT/"打开资料.html").write_text(document,encoding="utf-8")
(ROOT/"REPORT.html").write_text(document,encoding="utf-8")

class LinkParser(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if "id" in d:self.ids.add(d["id"])
        for key in ["href","src"]:
            if key in d:self.links.append(d[key])
parsed=LinkParser();parsed.feed(document)
local=[]
for link in parsed.links:
    p=urlsplit(link)
    if p.scheme or p.netloc:continue
    if not p.path:
        assert not p.fragment or p.fragment in parsed.ids,link
        continue
    target=(ROOT/unquote(p.path)).resolve()
    if p.path=="AUDIT.json":continue
    assert target.is_file(),str(target)
    local.append(str(target))
ET.parse(ROOT/"架构分层图.svg")
checks.extend([{"check":"unique_model_ids","passed":True},{"check":"local_links","passed":True,"count":len(local)},{"check":"svg_xml","passed":True}])
files=[]
for path in sorted(ROOT.iterdir()):
    if path.is_file() and path.name!="AUDIT.json":
        files.append({"path":path.name,"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
save_json("AUDIT.json",{"generated_at":date,"status":"passed","model_architecture_or_component_cards":len(models),"unique_source_urls":len(source_index),"checks":checks,"files":files,"verification_boundary":"数据字段、本地链接、SVG XML和文件hash；不代表模型复现、能力或性能验证。图形人工查看另记VISUAL_QA.json。浏览器布局尚未人工核对。"})
print(json.dumps({"status":"passed","cards":len(models),"unique_sources":len(source_index),"files":len(files),"entry":str(ROOT/"打开资料.html")},ensure_ascii=False))
