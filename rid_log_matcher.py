import json
import os
import re
from collections import defaultdict

# 配置信息
log_file_path = "./mylog_input/app_2026-01-21.log"

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

    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 1. 匹配请求行
            req_match = re.search(req_pattern, line)
            if req_match:
                rid, req_json = req_match.groups()
                pending_requests[rid] = req_json.strip()
                stats["total_req_found"] += 1
                continue

            # 2. 匹配响应行
            rsp_match = re.search(rsp_pattern, line)
            if rsp_match:
                rid, rsp_json_str = rsp_match.groups()

                if rid in pending_requests:
                    req_json_str = pending_requests[rid]
                    try:
                        # 解析 JSON
                        req_data = json.loads(req_json_str)
                        rsp_data = json.loads(rsp_json_str.strip())
                        
                        # 使用递归函数提取字段，解决层级问题
                        d_type = find_key_recursive(req_data, "decision_type")
                        p_type = find_key_recursive(req_data, "plan_type")
                        
                        # 记录组合 (处理 None 的情况)
                        key_tuple = (d_type, p_type)
                        combination_counts[key_tuple] += 1
                        
                        # 过滤逻辑
                        if d_type == 1 and p_type == 0:
                            save_to_file(rid, req_data, "req")
                            save_to_file(rid, rsp_data, "rsp")
                            stats["success_pairs"] += 1
                        else:
                            stats["ignored_by_filter"] += 1
                            
                    except json.JSONDecodeError:
                        stats["failed_json"] += 1
                    
                    del pending_requests[rid]

    print_report(stats, combination_counts, len(pending_requests))

def save_to_file(rid, data, suffix):
    filename = f"{rid}_{suffix}.json"
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=4, ensure_ascii=False)

def print_report(stats, combination_counts, unmatched):
    total = stats["total_req_found"]
    print("\n" + "="*55)
    print(f"        调度业务分析报告 ({os.path.basename(log_file_path)})")
    print("="*55)
    print(f"1. 流量统计:")
    print(f"   - 日志扫描到的总请求数: {total}")
    print(f"   - 成功配对并保存 (1, 0) 组合: {stats['success_pairs']}")
    print(f"   - 因类型不符被过滤 (非1,0): {stats['ignored_by_filter']}")
    print(f"   - 只有请求没有响应 (丢包): {unmatched}")
    
    print(f"\n2. 字段组合占比 (Decision_Type, Plan_Type):")
    paired_total = sum(combination_counts.values())
    if paired_total > 0:
        for (d, p), count in sorted(combination_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / paired_total) * 100
            # 这里的 d 和 p 如果没搜到会显示 None
            label = f"({d}, {p})"
            mark = " [Target]" if d == 1 and p == 0 else ""
            print(f"   - {label:<15}: {count:>4} 次 ({percentage:>6.2f}%){mark}")
    
    success_rate = (stats["success_pairs"] / total * 100) if total > 0 else 0
    print("-" * 55)
    print(f"最终目标数据 (1,0) 提取率: {success_rate:.2f}%")
    print("="*55)

if __name__ == "__main__":
    extract_logs()