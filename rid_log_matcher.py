import json
import os
import re
import argparse
from collections import defaultdict

# 解析命令行参数
parser = argparse.ArgumentParser(description='匹配日志中的请求和响应，并按vehicle_id分类保存')
parser.add_argument('log_file', type=str, help='日志文件名，必须位于mylog_input目录下')
args = parser.parse_args()

# 构建完整的日志文件路径
log_file_name = args.log_file
log_file_path = os.path.join('./mylog_input', log_file_name)

# 验证日志文件是否存在且在mylog_input目录下
if not os.path.exists(log_file_path):
    print(f"错误: 日志文件 {log_file_path} 不存在")
    exit(1)

# 确保日志文件确实在mylog_input目录下
abs_log_path = os.path.abspath(log_file_path)
abs_mylog_dir = os.path.abspath('./mylog_input')
if not abs_log_path.startswith(abs_mylog_dir):
    print(f"错误: 日志文件必须位于mylog_input目录下")
    exit(1)

# 设置输出目录
base_dir = os.path.dirname(log_file_path)
log_name = os.path.splitext(os.path.basename(log_file_path))[0]
output_dir = os.path.join(base_dir, log_name)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 正则表达式
req_pattern = r"rid=([a-f0-9\-]+).*?接收到调度请求详情[\s:]+(\{.*)"
rsp_pattern = r"rid=([a-f0-9\-]+).*?调度算法输出详情[\s:]+(\{.*)"

def find_key_recursive(data, key):
    """
    深度优先搜索：在嵌套字典或列表中查找指定的 key
    """
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for v in data.values():
            result = find_key_recursive(v, key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_key_recursive(item, key)
            if result is not None:
                return result
    return None

def extract_logs():
    pending_requests = {} # rid -> {"content": str, "v_id": str, "d_type": int, "p_type": int}
    stats = {
        "total_req_found": 0,
        "success_pairs": 0,        
        "ignored_by_filter": 0,    
        "failed_json": 0,
        "empty_routes": 0,
        "algorithm_error": 0
    }
    combination_counts = defaultdict(int)
    vehicle_stats = defaultdict(lambda: {
        "total_req": 0,
        "target_req": 0,
        "normal": 0,
        "empty": 0,
        "error": 0,
        "unmatched": 0,
        "filtered": 0,
        "failed_json": 0
    })

    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 1. 匹配请求行
            req_match = re.search(req_pattern, line)
            if req_match:
                req_id_match = re.search(r"rid=([a-f0-9\-]+)", line)
                if req_id_match:
                    rid = req_id_match.group(1)
                    req_content = line.split("接收到调度请求详情", 1)[1].strip()
                    if req_content.startswith(":") or req_content.startswith("："):
                        req_content = req_content[1:].strip()
                    
                    v_id = "unknown"
                    d_type = None
                    p_type = None
                    try:
                        req_data = json.loads(req_content)
                        v_id = find_key_recursive(req_data, "vehicle_id") or "unknown"
                        d_type = find_key_recursive(req_data, "decision_type")
                        p_type = find_key_recursive(req_data, "plan_type")
                    except:
                        pass
                    
                    pending_requests[rid] = {
                        "content": req_content,
                        "v_id": v_id,
                        "d_type": d_type,
                        "p_type": p_type
                    }
                    vehicle_stats[v_id]["total_req"] += 1
                    stats["total_req_found"] += 1
                continue

            # 2. 匹配响应行
            rsp_match = re.search(rsp_pattern, line)
            if rsp_match:
                rid, rsp_json_str = rsp_match.groups()

                if rid in pending_requests:
                    req_info = pending_requests[rid]
                    v_id = req_info["v_id"]
                    d_type = req_info["d_type"]
                    p_type = req_info["p_type"]
                    
                    combination_counts[(d_type, p_type)] += 1
                    
                    try:
                        req_data = json.loads(req_info["content"])
                        rsp_data = json.loads(rsp_json_str.strip())
                        
                        # 过滤逻辑 (1,0)
                        if d_type == 1 and p_type == 0:
                            vehicle_stats[v_id]["target_req"] += 1
                            # 判断健康度
                            if rsp_data.get("status") != "Success":
                                status_label = "error"
                                stats["algorithm_error"] += 1
                                vehicle_stats[v_id]["error"] += 1
                            else:
                                routes = rsp_data.get("data", {}).get("routes", []) if "data" in rsp_data else rsp_data.get("routes", [])
                                if not routes:
                                    status_label = "empty"
                                    stats["empty_routes"] += 1
                                    vehicle_stats[v_id]["empty"] += 1
                                else:
                                    status_label = "normal"
                                    stats["success_pairs"] += 1
                                    vehicle_stats[v_id]["normal"] += 1
                            
                            save_to_file(rid, req_data, "req", v_id, status_label)
                            save_to_file(rid, rsp_data, "rsp", v_id, status_label)
                        else:
                            stats["ignored_by_filter"] += 1
                            vehicle_stats[v_id]["filtered"] += 1
                            
                    except json.JSONDecodeError:
                        stats["failed_json"] += 1
                        vehicle_stats[v_id]["failed_json"] += 1
                    
                    del pending_requests[rid]

    # 处理只有请求没有响应的情况 (unmatched)
    for rid, req_info in pending_requests.items():
        v_id = req_info["v_id"]
        d_type = req_info["d_type"]
        p_type = req_info["p_type"]
        
        if d_type == 1 and p_type == 0:
            vehicle_stats[v_id]["target_req"] += 1
            vehicle_stats[v_id]["unmatched"] += 1
            try:
                req_data = json.loads(req_info["content"])
                save_to_file(rid, req_data, "req", v_id, "unmatched")
            except:
                pass
        else:
            # 非目标请求的丢失，通常不关心，但也计入 filtered
            vehicle_stats[v_id]["filtered"] += 1

    print_report(stats, combination_counts, len(pending_requests), vehicle_stats)

def save_to_file(rid, data, suffix, vehicle_id, status_label):
    # 路径结构: output_dir/vehicle_id/status_label/rid_suffix.json
    target_dir = os.path.join(output_dir, str(vehicle_id), status_label)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    filename = f"{rid}_{suffix}.json"
    path = os.path.join(target_dir, filename)
    with open(path, "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=4, ensure_ascii=False)

def print_report(stats, combination_counts, unmatched_total, vehicle_stats):
    total = stats["total_req_found"]
    print("\n" + "="*85)
    print(f"          调度业务分析报告 ({os.path.basename(log_file_path)})")
    print("="*85)
    
    print(f"1. 全局流量统计:")
    print(f"   - 总扫描请求数: {total}")
    print(f"   - [Normal]    成功配对且有路径 (1,0): {stats['success_pairs']}")
    print(f"   - [Empty]     成功配对但路径为空 (1,0): {stats['empty_routes']}")
    print(f"   - [Error]     算法内部报错 (1,0): {stats['algorithm_error']}")
    print(f"   - [Unmatched] 有请求无响应 (丢失): {unmatched_total}")
    print(f"   - [Filtered]  非目标决策类型 (非1,0): {stats['ignored_by_filter']}")
    print(f"   - [Fail]      JSON解析失败: {stats['failed_json']}")
    
    print(f"\n2. (Decision, Plan) 组合分布:")
    paired_total = sum(combination_counts.values())
    if paired_total > 0:
        for (d, p), count in sorted(combination_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / paired_total) * 100
            label = f"({d}, {p})"
            mark = " [Target]" if d == 1 and p == 0 else ""
            print(f"   - {label:<15}: {count:>4} 次 ({percentage:>6.2f}%){mark}")
    
    print(f"\n3. 车辆明细统计:")
    # 表头增加 Target 和 Filtered 列
    header = f"{'车辆ID':<12} {'总请求':>6} | {'目标(1,0)':>9} {'Normal':>7} {'Empty':>6} {'Error':>6} {'丢失':>5} | {'过滤':>5}"
    print(f"   {header}")
    print(f"   {'-'*82}")
    
    for v_id in sorted(vehicle_stats.keys()):
        v = vehicle_stats[v_id]
        row = f"{v_id:<12} {v['total_req']:>6} | {v['target_req']:>9} {v['normal']:>7} {v['empty']:>6} {v['error']:>6} {v['unmatched']:>5} | {v['filtered']:>5}"
        print(f"   {row}")
    
    target_total = sum(v["target_req"] for v in vehicle_stats.values())
    success_rate = (stats["success_pairs"] / target_total * 100) if target_total > 0 else 0
    print("\n" + "-" * 85)
    print(f"目标业务 (1,0) 完结率 (Normal/Target): {success_rate:.2f}%")
    print("="*85)

if __name__ == "__main__":
    extract_logs()