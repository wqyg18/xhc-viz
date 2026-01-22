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
    pending_requests = {}
    stats = {
        "total_req_found": 0,
        "success_pairs": 0,        
        "ignored_by_filter": 0,    
        "failed_json": 0
    }
    combination_counts = defaultdict(int)
    vehicle_stats = defaultdict(lambda: {
        "total_req_found": 0,
        "success_pairs": 0,
        "ignored_by_filter": 0,
        "failed_json": 0
    })

    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 1. 匹配请求行
            req_match = re.search(req_pattern, line)
            if req_match:
                rid, req_json = req_match.groups()
                pending_requests[rid] = req_json.strip()
                # 从请求中提取vehicle_id用于统计
                try:
                    req_data = json.loads(req_json.strip())
                    req_vehicle_id = find_key_recursive(req_data, "vehicle_id")
                    if req_vehicle_id is None:
                        req_vehicle_id = "unknown"
                    vehicle_stats[req_vehicle_id]["total_req_found"] += 1
                except json.JSONDecodeError:
                    pass  # 如果请求JSON解析失败，不影响后续处理
                stats["total_req_found"] += 1
                continue

            # 2. 匹配响应行
            rsp_match = re.search(rsp_pattern, line)
            if rsp_match:
                rid, rsp_json_str = rsp_match.groups()

                if rid in pending_requests:
                    req_json_str = pending_requests[rid]
                    try:
                        # 解析请求 JSON 以获取 vehicle_id
                        req_data = json.loads(req_json_str)
                        vehicle_id = find_key_recursive(req_data, "vehicle_id")
                        
                        # 确保 vehicle_id 有值，否则使用默认值
                        if vehicle_id is None:
                            vehicle_id = "unknown"
                        
                        # 解析响应 JSON
                        rsp_data = json.loads(rsp_json_str.strip())
                        
                        # 使用递归函数提取字段，解决层级问题
                        d_type = find_key_recursive(req_data, "decision_type")
                        p_type = find_key_recursive(req_data, "plan_type")
                        
                        # 记录组合 (处理 None 的情况)
                        key_tuple = (d_type, p_type)
                        combination_counts[key_tuple] += 1
                        
                        # 过滤逻辑
                        if d_type == 1 and p_type == 0:
                            save_to_file(rid, req_data, "req", vehicle_id)
                            save_to_file(rid, rsp_data, "rsp", vehicle_id)
                            stats["success_pairs"] += 1
                            vehicle_stats[vehicle_id]["success_pairs"] += 1
                        else:
                            stats["ignored_by_filter"] += 1
                            vehicle_stats[vehicle_id]["ignored_by_filter"] += 1
                            
                    except json.JSONDecodeError:
                        stats["failed_json"] += 1
                        # 使用默认的 vehicle_id 记录失败情况
                        vehicle_id = "unknown"
                        vehicle_stats[vehicle_id]["failed_json"] += 1
                    
                    del pending_requests[rid]

    print_report(stats, combination_counts, len(pending_requests), vehicle_stats)

def save_to_file(rid, data, suffix, vehicle_id):
    # 为每个vehicle_id创建子文件夹
    vehicle_dir = os.path.join(output_dir, str(vehicle_id))
    if not os.path.exists(vehicle_dir):
        os.makedirs(vehicle_dir)
    
    filename = f"{rid}_{suffix}.json"
    path = os.path.join(vehicle_dir, filename)
    with open(path, "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=4, ensure_ascii=False)

def print_report(stats, combination_counts, unmatched, vehicle_stats):
    total = stats["total_req_found"]
    print("\n" + "="*55)
    print(f"        调度业务分析报告 ({os.path.basename(log_file_path)})")
    print("="*55)
    
    # 1. 全局流量统计
    print(f"1. 全局流量统计:")
    print(f"   - 日志扫描到的总请求数: {total}")
    print(f"   - 成功配对并保存 (1, 0) 组合: {stats['success_pairs']}")
    print(f"   - 因类型不符被过滤 (非1,0): {stats['ignored_by_filter']}")
    print(f"   - JSON解析失败: {stats['failed_json']}")
    print(f"   - 只有请求没有响应 (丢包): {unmatched}")
    
    # 2. 字段组合占比
    print(f"\n2. 字段组合占比 (Decision_Type, Plan_Type):")
    paired_total = sum(combination_counts.values())
    if paired_total > 0:
        for (d, p), count in sorted(combination_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / paired_total) * 100
            # 这里的 d 和 p 如果没搜到会显示 None
            label = f"({d}, {p})"
            mark = " [Target]" if d == 1 and p == 0 else ""
            print(f"   - {label:<15}: {count:>4} 次 ({percentage:>6.2f}%){mark}")
    
    # 3. 各车辆统计信息
    print(f"\n3. 各车辆统计信息:")
    print(f"   {'车辆ID':<15} {'总请求数':<10} {'成功配对':<10} {'被过滤':<10} {'解析失败':<10} {'成功率':<8}")
    print(f"   {'-'*15} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*8}")
    
    # 按车辆ID排序
    for vehicle_id in sorted(vehicle_stats.keys()):
        v_stats = vehicle_stats[vehicle_id]
        v_total = v_stats["total_req_found"]
        v_success = v_stats["success_pairs"]
        v_ignored = v_stats["ignored_by_filter"]
        v_failed = v_stats["failed_json"]
        
        v_success_rate = (v_success / v_total * 100) if v_total > 0 else 0
        print(f"   {vehicle_id:<15} {v_total:<10} {v_success:<10} {v_ignored:<10} {v_failed:<10} {v_success_rate:>7.2f}%")
    
    # 4. 最终目标数据提取率
    success_rate = (stats["success_pairs"] / total * 100) if total > 0 else 0
    print("\n" + "-" * 55)
    print(f"最终目标数据 (1,0) 提取率: {success_rate:.2f}%")
    print("="*55)

if __name__ == "__main__":
    extract_logs()