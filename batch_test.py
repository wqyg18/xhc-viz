import os
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime

# 从 main.py 导入可视化函数
# 注意：如果 main.py 依赖相对路径的 utils，请确保运行此脚本时在根目录下
from main import create_visualization, create_output_visualization

def run_batch(input_dir, output_base_dir, api_url):
    # 1. 创建带有时间戳的输出目录，避免覆盖
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_base_dir, f"run_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🚀 开始批量测试")
    print(f"📂 输入目录: {input_dir}")
    print(f"📂 输出目录: {output_dir}")
    print(f"🔗 API 地址: {api_url}")
    print("-" * 50)

    # 获取所有 json 文件
    files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    files.sort() # 排序，保证顺序一致

    success_count = 0
    fail_count = 0

    for filename in files:
        file_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        
        # 为当前文件创建一个子文件夹，或者直接以前缀命名
        # 这里选择直接以前缀命名放在 output_dir 下，文件少时比较直观
        current_req_file = file_path
        current_res_file = os.path.join(output_dir, f"{base_name}_response.json")
        current_input_map = os.path.join(output_dir, f"{base_name}_input.html")
        current_output_map = os.path.join(output_dir, f"{base_name}_output.html")

        print(f"正在处理: {filename} ...", end=" ", flush=True)

        try:
            # 2. 读取请求数据
            with open(current_req_file, 'r', encoding='utf-8') as f:
                req_data = json.load(f)

            # 3. 发送请求 (替代 curl)
            try:
                response = requests.post(
                    api_url,
                    json=req_data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status() # 检查 HTTP 错误
                res_json = response.json()
                
                # 保存响应数据
                with open(current_res_file, 'w', encoding='utf-8') as f:
                    json.dump(res_json, f, indent=2, ensure_ascii=False)

            except requests.exceptions.RequestException as e:
                print(f"[API 错误] {e}")
                fail_count += 1
                continue

            # 4. 生成可视化
            # 生成输入地图
            create_visualization(
                data_file=current_req_file, 
                output_file=current_input_map
            )

            # 生成结果地图
            create_output_visualization(
                req_file=current_req_file,
                response_file=current_res_file,
                output_file=current_output_map
            )
            
            print("✅ 完成")
            success_count += 1

        except Exception as e:
            print(f"❌ 失败: {str(e)}")
            fail_count += 1

    print("-" * 50)
    print(f"🎉 批量测试结束. 成功: {success_count}, 失败: {fail_count}")
    print(f"查看结果请访问: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量运行物流规划测试")
    parser.add_argument("--input", default="data", help="包含请求JSON的文件夹")
    parser.add_argument("--output", default="results", help="结果保存的基础文件夹")
    parser.add_argument("--url", default="http://localhost:8000/api/v1/dispatch", help="API 地址")
    
    args = parser.parse_args()
    
    run_batch(args.input, args.output, args.url)