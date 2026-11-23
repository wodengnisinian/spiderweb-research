from pathlib import Path
from datetime import datetime
from hashlib import sha256
import json
import struct

root=Path(__file__).resolve().parent
digest=lambda p:sha256(p.read_bytes()).hexdigest()
audit=json.loads((root/"AUDIT.json").read_text(encoding="utf-8"))
for rec in audit["files"]:
    p=root/rec["path"]
    assert p.stat().st_size==rec["bytes"] and digest(p)==rec["sha256"],rec["path"]
register=json.loads((root/"MODEL_REGISTER.json").read_text(encoding="utf-8"))
sources=json.loads((root/"SOURCE_REGISTER.json").read_text(encoding="utf-8"))
assert len(register["models"])==31
assert len(sources["sources"])==80
assert (root/"打开资料.html").read_bytes()==(root/"REPORT.html").read_bytes()
png=(root/"架构分层图.png").read_bytes()
assert png[:8]==b"\x89PNG\r\n\x1a\n"
assert struct.unpack(">II",png[16:24])==(2240,1600)
working=root.parent.parent/"模型底层架构调查"
copied=[]
if working.is_dir() and working!=root:
    for p in working.iterdir():
        if p.is_file():
            assert digest(p)==digest(root/p.name),p.name
            copied.append(p.name)
files=[{"path":p.name,"bytes":p.stat().st_size,"sha256":digest(p)} for p in sorted(root.iterdir()) if p.is_file() and p.name not in ["AUDIT.json","FINAL_QA.json"]]
audit["files"]=files
audit["verification_boundary"]="字段、本地链接、SVG XML与文件hash；不是模型复现或能力验证。架构PNG已由助手实际打开查看。HTML浏览器布局未人工验收。"
(root/"AUDIT.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
qa={"date":datetime.now().astimezone().isoformat(timespec="seconds"),"status":"passed","cards":31,"unique_source_urls":80,"source_copy_hash_matches":len(copied),"hashes_verified":len(files),"html_entries_identical":True,"png_dimensions":[2240,1600],"visual_review":{"reviewed":"架构分层图.png","method":"助手使用view_image实际打开查看","result":"标题、四层标签和说明可读，未见遮挡或裁切","png_sha256":digest(root/"架构分层图.png")},"independent_content_review":"另一研究助手只读复核4组JSON及构建逻辑，未发现与来源卡冲突或夸大验证范围的实质问题。","browser_layout_reviewed":False,"model_training_or_inference_executed":False,"audit_sha256":digest(root/"AUDIT.json"),"self_hash_excluded":True}
(root/"FINAL_QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":"passed","cards":31,"sources":80,"source_copy_matches":len(copied),"hashed_files":len(files)},ensure_ascii=True))
