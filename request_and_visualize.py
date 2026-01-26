import json
import os
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor

# 导入main.py中的可视化函数
from main import create_visualization, create_output_visualization

# 默认配置
DEFAULT_INPUT_DIR = "./mylog_input/app_2026-01-21"
DEFAULT_OUTPUT_DIR = "./new_responses"
DEFAULT_API_URL = "http://localhost:8000/api/your-endpoint"
DEFAULT_MAX_COUNT = 1000

# 创建输出目录
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

# 发送请求到本地接口
def send_request(input_data, api_url):
    try:
        response = requests.post(api_url, json=input_data, timeout=None)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"请求失败: {e}")
        return None

# 获取所有的rid
def get_all_rids(input_dir):
    rids = []
    # 递归遍历目录结构，处理按 车辆ID/状态 分类的文件
    # 结构: input_dir / {vehicle_id} / {status} / {rid}_req.json
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith("_req.json"):
                rid = filename[:-9]  # 移除 "_req.json"
                # 从路径中提取 status 和 vehicle_id
                # root 可能是 .../mylog_input/log_name/vehicle_id/status
                parts = os.path.normpath(root).split(os.sep)
                if len(parts) >= 2:
                    status = parts[-1]
                    vehicle_id = parts[-2]
                    rids.append({
                        "rid": rid,
                        "sub_dir": root,
                        "status": status,
                        "vehicle_id": vehicle_id
                    })
    return sorted(rids, key=lambda x: x["rid"])

# 处理单个请求
def process_one_request(item, log_new_rsp_dir, api_url):
    rid = item["rid"]
    sub_dir = item["sub_dir"]
    req_file = os.path.join(sub_dir, f"{rid}_req.json")
    if not os.path.exists(req_file):
        return False
    
    with open(req_file, "r", encoding="utf-8") as f:
        req_data = json.load(f)
    
    print(f"正在请求 API [RID: {rid}]...")
    new_rsp = send_request(req_data, api_url)
    
    if new_rsp:
        # 保持 vehicle_id 和 status 层级
        target_dir = os.path.join(log_new_rsp_dir, item["vehicle_id"], item["status"])
        ensure_dir(target_dir)
        
        new_rsp_file = os.path.join(target_dir, f"{rid}_new_rsp.json")
        with open(new_rsp_file, "w", encoding="utf-8") as f:
            json.dump(new_rsp, f, indent=4, ensure_ascii=False)
        return True
    return False

# 1. 请求所有输入
def request_all(input_dir, output_dir, api_url, max_count):
    log_name = os.path.basename(os.path.normpath(input_dir))
    log_new_rsp_dir = os.path.join(output_dir, log_name)
    ensure_dir(log_new_rsp_dir)
    
    all_items = get_all_rids(input_dir)
    items_to_process = all_items[:max_count]
    
    print(f"开始请求 API，日志: {log_name}, 数量: {len(items_to_process)}")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_one_request, item, log_new_rsp_dir, api_url)
            for item in items_to_process
        ]
    
    results = [future.result() for future in futures]
    print(f"完成! 成功: {sum(results)}, 失败: {len(results) - sum(results)}")

# 2. 可视化原始输入输出
def visualize_original(input_dir, viz_dir, max_count):
    log_name = os.path.basename(os.path.normpath(input_dir))
    log_viz_dir = os.path.join(viz_dir, log_name)
    ensure_dir(log_viz_dir)
    
    all_items = get_all_rids(input_dir)
    items_to_visualize = all_items[:max_count]
    
    print(f"正在生成原始可视化，日志: {log_name}")
    
    for item in items_to_visualize:
        rid = item["rid"]
        sub_dir = item["sub_dir"]
        status = item["status"]
        vehicle_id = item["vehicle_id"]
        
        # 保持目录层级: viz_dir/log_name/vehicle_id/status/
        vehicle_status_viz_dir = os.path.join(log_viz_dir, vehicle_id, status)
        ensure_dir(vehicle_status_viz_dir)
        
        req_file = os.path.join(sub_dir, f"{rid}_req.json")
        rsp_file = os.path.join(sub_dir, f"{rid}_rsp.json")
        
        if not os.path.exists(req_file):
            continue

        # 可视化输入 (所有状态都有输入)
        create_visualization(req_file, os.path.join(vehicle_status_viz_dir, f"{rid}_input.html"))
        
        # 只有 normal, empty, error 状态可能存在原始响应
        if status in ["normal", "empty", "error"] and os.path.exists(rsp_file):
            # 处理输出响应格式
            with open(rsp_file, "r", encoding="utf-8") as f:
                try:
                    rsp_data = json.load(f)
                except:
                    continue
            
            output_html = os.path.join(vehicle_status_viz_dir, f"{rid}_output.html")
            if "data" not in rsp_data:
                temp_rsp = os.path.join(vehicle_status_viz_dir, f"temp_{rid}.json")
                with open(temp_rsp, "w", encoding="utf-8") as f:
                    json.dump({"data": rsp_data}, f)
                create_output_visualization(req_file, temp_rsp, output_html)
                os.remove(temp_rsp)
            else:
                create_output_visualization(req_file, rsp_file, output_html)

# 3. 可视化新旧对比
def visualize_compare_one(item, log_new_rsp_base, log_viz_base):
    rid = item["rid"]
    sub_dir = item["sub_dir"]
    status = item["status"]
    vehicle_id = item["vehicle_id"]
    
    vehicle_status_viz_dir = os.path.join(log_viz_base, vehicle_id, status)
    ensure_dir(vehicle_status_viz_dir)
    
    req_file = os.path.join(sub_dir, f"{rid}_req.json")
    orig_rsp_file = os.path.join(sub_dir, f"{rid}_rsp.json")
    # 这里的 new_rsp_file 路径也要对应上新的 vehicle_id/status 层级
    new_rsp_file = os.path.join(log_new_rsp_base, vehicle_id, status, f"{rid}_new_rsp.json")
    
    if not all(os.path.exists(f) for f in [req_file, orig_rsp_file, new_rsp_file]):
        return False

    # 生成 Original 和 New 的 HTML
    for suffix, rsp_f in [("original", orig_rsp_file), ("new", new_rsp_file)]:
        out_html = os.path.join(vehicle_status_viz_dir, f"{rid}_{suffix}_output.html")
        with open(rsp_f, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if "data" not in data:
            temp = os.path.join(vehicle_status_viz_dir, f"temp_{rid}_{suffix}.json")
            with open(temp, "w", encoding="utf-8") as f:
                json.dump({"data": data}, f)
            create_output_visualization(req_file, temp, out_html)
            os.remove(temp)
        else:
            create_output_visualization(req_file, rsp_f, out_html)
    return True

def visualize_compare_all(input_dir, new_output_dir, viz_dir, max_count):
    log_name = os.path.basename(os.path.normpath(input_dir))
    log_viz_base = os.path.join(viz_dir, log_name)
    log_new_rsp_base = os.path.join(new_output_dir, log_name)
    
    all_items = get_all_rids(input_dir)
    items_to_viz = all_items[:max_count]
    
    print(f"正在生成对比可视化，日志: {log_name}")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(visualize_compare_one, item, log_new_rsp_base, log_viz_base)
            for item in items_to_viz
        ]
    
    success = sum([f.result() for f in futures])
    print(f"对比可视化完成: 成功 {success}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="请求本地接口并可视化对比结果")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 基础参数模版
    def add_common_args(p):
        p.add_argument("--input-dir", default=DEFAULT_INPUT_DIR)
        p.add_argument("--max-count", type=int, default=DEFAULT_MAX_COUNT)

    # request
    req_p = subparsers.add_parser("request")
    add_common_args(req_p)
    req_p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    req_p.add_argument("--api-url", default=DEFAULT_API_URL)

    # visualize-original
    viz_orig_p = subparsers.add_parser("visualize-original")
    add_common_args(viz_orig_p)
    viz_orig_p.add_argument("--viz-dir", default="./mylog_output")

    # visualize-compare
    viz_comp_p = subparsers.add_parser("visualize-compare")
    add_common_args(viz_comp_p)
    viz_comp_p.add_argument("--new-output-dir", default=DEFAULT_OUTPUT_DIR)
    viz_comp_p.add_argument("--viz-dir", default="./mylog_output/visualization/compare")

    args = parser.parse_args()
    
    if args.command == "request":
        request_all(args.input_dir, args.output_dir, args.api_url, args.max_count)
    elif args.command == "visualize-original":
        visualize_original(args.input_dir, args.viz_dir, args.max_count)
    elif args.command == "visualize-compare":
        visualize_compare_all(args.input_dir, args.new_output_dir, args.viz_dir, args.max_count)
    else:
        parser.print_help()