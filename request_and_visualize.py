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
DEFAULT_API_URL = "http://localhost:8000/api/your-endpoint"  # 需要根据实际情况修改
DEFAULT_MAX_COUNT = 5

# 创建输出目录
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 发送请求到本地接口
def send_request(input_data, api_url):
    try:
        response = requests.post(api_url, json=input_data, timeout=None)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"请求失败: {e}")
        return None

# 处理单个请求
def process_one_request(rid, input_dir, output_dir, api_url):
    # 读取输入文件
    req_file = os.path.join(input_dir, f"{rid}_req.json")
    if not os.path.exists(req_file):
        print(f"输入文件不存在: {req_file}")
        return False
    
    with open(req_file, "r", encoding="utf-8") as f:
        req_data = json.load(f)
    
    # 发送请求
    print(f"处理请求: {rid}")
    new_rsp = send_request(req_data, api_url)
    
    if new_rsp:
        # 保存新的响应
        new_rsp_file = os.path.join(output_dir, f"{rid}_new_rsp.json")
        with open(new_rsp_file, "w", encoding="utf-8") as f:
            json.dump(new_rsp, f, indent=4, ensure_ascii=False)
        print(f"保存新响应: {new_rsp_file}")
        return True
    return False

# 获取所有的rid
def get_all_rids(input_dir):
    rids = set()
    for filename in os.listdir(input_dir):
        if filename.endswith("_req.json"):
            rid = filename[:-9]  # 移除 "_req.json"（长度为9）
            rids.add(rid)
    return sorted(rids)

# 请求所有输入
def request_all(input_dir, output_dir, api_url, max_count):
    ensure_dir(output_dir)
    
    # 获取所有rid
    all_rids = get_all_rids(input_dir)
    
    # 限制数量
    rids_to_process = all_rids[:max_count]
    print(f"将处理 {len(rids_to_process)} 个请求 (总共 {len(all_rids)} 个)")
    
    # 并行处理
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_one_request, rid, input_dir, output_dir, api_url)
            for rid in rids_to_process
        ]
    
    # 等待所有任务完成
    results = [future.result() for future in futures]
    success_count = sum(results)
    print(f"完成! 成功: {success_count}, 失败: {len(results) - success_count}")
    
    return rids_to_process

# 可视化单个对比
def visualize_one(rid, input_dir, new_output_dir, viz_dir):
    ensure_dir(viz_dir)
    
    # 读取原始输出和新输出
    req_file = os.path.join(input_dir, f"{rid}_req.json")
    orig_rsp_file = os.path.join(input_dir, f"{rid}_rsp.json")
    new_rsp_file = os.path.join(new_output_dir, f"{rid}_new_rsp.json")
    
    if not os.path.exists(req_file) or not os.path.exists(orig_rsp_file) or not os.path.exists(new_rsp_file):
        print(f"缺少文件，无法可视化: {rid}")
        return False
    
    # 处理原始响应，转换为create_output_visualization函数预期的格式
    with open(orig_rsp_file, "r", encoding="utf-8") as f:
        orig_rsp_data = json.load(f)
    
    # 处理原始输出
    orig_output = os.path.join(viz_dir, f"{rid}_original_output.html")
    if "data" not in orig_rsp_data:
        # 创建临时文件，添加data字段
        temp_orig_rsp_file = os.path.join(viz_dir, f"{rid}_temp_orig_rsp.json")
        with open(temp_orig_rsp_file, "w", encoding="utf-8") as f:
            json.dump({"data": orig_rsp_data}, f, indent=4, ensure_ascii=False)
        create_output_visualization(req_file, temp_orig_rsp_file, orig_output)
        os.remove(temp_orig_rsp_file)
    else:
        create_output_visualization(req_file, orig_rsp_file, orig_output)
    
    # 处理新响应，转换为create_output_visualization函数预期的格式
    with open(new_rsp_file, "r", encoding="utf-8") as f:
        new_rsp_data = json.load(f)
    
    # 处理新输出
    new_output = os.path.join(viz_dir, f"{rid}_new_output.html")
    if "data" not in new_rsp_data:
        # 创建临时文件，添加data字段
        temp_new_rsp_file = os.path.join(viz_dir, f"{rid}_temp_new_rsp.json")
        with open(temp_new_rsp_file, "w", encoding="utf-8") as f:
            json.dump({"data": new_rsp_data}, f, indent=4, ensure_ascii=False)
        create_output_visualization(req_file, temp_new_rsp_file, new_output)
        os.remove(temp_new_rsp_file)
    else:
        create_output_visualization(req_file, new_rsp_file, new_output)
    
    print(f"生成可视化对比: {orig_output} 和 {new_output}")
    return True

# 可视化所有对比
def visualize_all(input_dir, new_output_dir, viz_dir, max_count):
    ensure_dir(viz_dir)
    
    # 获取所有已处理的rid
    all_rids = get_all_rids(input_dir)
    rids_to_visualize = all_rids[:max_count]
    
    print(f"将可视化 {len(rids_to_visualize)} 个对比")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(visualize_one, rid, input_dir, new_output_dir, viz_dir)
            for rid in rids_to_visualize
        ]
    
    results = [future.result() for future in futures]
    success_count = sum(results)
    print(f"可视化完成! 成功: {success_count}, 失败: {len(results) - success_count}")

# 可视化原始输入输出
def visualize_original(input_dir, viz_dir, max_count):
    ensure_dir(viz_dir)
    
    all_rids = get_all_rids(input_dir)
    rids_to_visualize = all_rids[:max_count]
    
    print(f"将可视化 {len(rids_to_visualize)} 个原始输入输出")
    
    for rid in rids_to_visualize:
        req_file = os.path.join(input_dir, f"{rid}_req.json")
        rsp_file = os.path.join(input_dir, f"{rid}_rsp.json")
        
        if not os.path.exists(req_file) or not os.path.exists(rsp_file):
            print(f"缺少原始文件: {rid}")
            continue
        
        # 可视化输入（基础分布图）
        input_html = os.path.join(viz_dir, f"{rid}_input.html")
        create_visualization(req_file, input_html)
        
        # 处理输出，转换为create_output_visualization函数预期的格式
        with open(rsp_file, "r", encoding="utf-8") as f:
            rsp_data = json.load(f)
        
        # 检查响应格式，如果没有外层的data字段，添加它
        if "data" not in rsp_data:
            # 创建临时文件，添加data字段
            temp_rsp_file = os.path.join(viz_dir, f"{rid}_temp_rsp.json")
            with open(temp_rsp_file, "w", encoding="utf-8") as f:
                json.dump({"data": rsp_data}, f, indent=4, ensure_ascii=False)
            
            # 可视化输出（路线图）
            output_html = os.path.join(viz_dir, f"{rid}_output.html")
            create_output_visualization(req_file, temp_rsp_file, output_html)
            
            # 删除临时文件
            os.remove(temp_rsp_file)
        else:
            # 直接使用原始文件
            output_html = os.path.join(viz_dir, f"{rid}_output.html")
            create_output_visualization(req_file, rsp_file, output_html)
        
        print(f"生成原始可视化: {input_html} 和 {output_html}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="请求本地接口并可视化对比结果")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # request 命令
    req_parser = subparsers.add_parser("request", help="请求所有输入")
    req_parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR, help="输入目录")
    req_parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="新响应输出目录")
    req_parser.add_argument("--api-url", default=DEFAULT_API_URL, help="本地接口URL")
    req_parser.add_argument("--max-count", type=int, default=DEFAULT_MAX_COUNT, help="最大处理数量")
    
    # visualize-original 命令
    viz_orig_parser = subparsers.add_parser("visualize-original", help="可视化原始输入输出")
    viz_orig_parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR, help="输入目录")
    viz_orig_parser.add_argument("--viz-dir", default="./visualization/original", help="可视化输出目录")
    viz_orig_parser.add_argument("--max-count", type=int, default=DEFAULT_MAX_COUNT, help="最大可视化数量")
    
    # visualize-new 命令
    viz_new_parser = subparsers.add_parser("visualize-new", help="可视化新的输出")
    viz_new_parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR, help="输入目录")
    viz_new_parser.add_argument("--new-output-dir", default=DEFAULT_OUTPUT_DIR, help="新响应目录")
    viz_new_parser.add_argument("--viz-dir", default="./visualization/new", help="可视化输出目录")
    viz_new_parser.add_argument("--max-count", type=int, default=DEFAULT_MAX_COUNT, help="最大可视化数量")
    
    # visualize-compare 命令
    viz_compare_parser = subparsers.add_parser("visualize-compare", help="对比新旧输出")
    viz_compare_parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR, help="输入目录")
    viz_compare_parser.add_argument("--new-output-dir", default=DEFAULT_OUTPUT_DIR, help="新响应目录")
    viz_compare_parser.add_argument("--viz-dir", default="./visualization/compare", help="可视化输出目录")
    viz_compare_parser.add_argument("--max-count", type=int, default=DEFAULT_MAX_COUNT, help="最大可视化数量")
    
    args = parser.parse_args()
    
    if args.command == "request":
        request_all(args.input_dir, args.output_dir, args.api_url, args.max_count)
    elif args.command == "visualize-original":
        visualize_original(args.input_dir, args.viz_dir, args.max_count)
    elif args.command == "visualize-new":
        visualize_all(args.input_dir, args.new_output_dir, args.viz_dir, args.max_count)
    elif args.command == "visualize-compare":
        visualize_all(args.input_dir, args.new_output_dir, args.viz_dir, args.max_count)
    else:
        parser.print_help()