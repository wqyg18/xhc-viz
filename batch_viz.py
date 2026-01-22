from main import create_output_visualization, create_visualization
import os
import re

json_dir = "./4c1396ccc039445ea171519d811d85cc"
html_dir = os.path.join(json_dir, "html")
os.makedirs(html_dir, exist_ok=True)

# 用于匹配： 1-req.json / 1-rsp.json 这种格式
req_pattern = re.compile(r"(\d+)-req\.json$")
rsp_pattern = re.compile(r"(\d+)-rsp\.json$")

# 收集所有 req / rsp
req_files = {}
rsp_files = {}

for fname in os.listdir(json_dir):
    full_path = os.path.join(json_dir, fname)

    if match := req_pattern.match(fname):
        idx = match.group(1)
        req_files[idx] = full_path

    elif match := rsp_pattern.match(fname):
        idx = match.group(1)
        rsp_files[idx] = full_path

# ---------- 处理 req，可单独生成 ----------
for idx, req_path in req_files.items():
    req_html = os.path.join(html_dir, f"{idx}-req.html")

    print(f"[REQ] {req_path} -> {req_html}")

    create_visualization(
        data_file=req_path,
        output_file=req_html
    )

# ---------- 处理 req + rsp 对 ----------
for idx in req_files:
    if idx in rsp_files:
        req_path = req_files[idx]
        rsp_path = rsp_files[idx]
        rsp_html = os.path.join(html_dir, f"{idx}-rsp.html")

        print(f"[RSP] {req_path} + {rsp_path} -> {rsp_html}")

        create_output_visualization(
            req_file=req_path,
            response_file=rsp_path,
            output_file=rsp_html,
        )
