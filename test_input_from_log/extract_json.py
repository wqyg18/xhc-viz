import json
import os
import glob

def extract_json_from_logs():
    # 1. 获取当前目录下所有的 .txt 文件
    txt_files = glob.glob('*.txt')
    
    if not txt_files:
        print("当前目录下没有找到 .txt 文件。")
        return

    keyword = "请求调度参数:"
    decoder = json.JSONDecoder()

    for txt_file in txt_files:
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 2. 查找关键字的位置
            key_index = content.find(keyword)
            
            if key_index != -1:
                # 从关键字之后寻找第一个 '{'
                start_index = content.find('{', key_index)
                
                if start_index != -1:
                    # 截取从 '{' 开始到文件末尾的所有内容
                    potential_json = content[start_index:]
                    
                    # 3. 核心步骤：利用 raw_decode 解析 JSON
                    # 它会解析出一个合法的 JSON 对象，并忽略后面的剩余字符
                    try:
                        json_obj, end_index = decoder.raw_decode(potential_json)
                        
                        # 4. 构造输出文件名 (同名，但后缀改为 .json)
                        json_filename = os.path.splitext(txt_file)[0] + '.json'
                        
                        # 5. 保存为 JSON 文件
                        with open(json_filename, 'w', encoding='utf-8') as f_out:
                            # ensure_ascii=False 保证中文正常显示，indent=4 用于美化格式
                            json.dump(json_obj, f_out, ensure_ascii=False, indent=4)
                            
                        print(f"[成功] 已提取: {txt_file} -> {json_filename}")
                        
                    except json.JSONDecodeError as e:
                        print(f"[失败] {txt_file} 包含关键字，但在解析 JSON 时出错: {e}")
                else:
                    print(f"[跳过] {txt_file} 包含关键字，但未找到 JSON 起始括号 '{{'")
            else:
                print(f"[跳过] {txt_file} 未包含关键字 '{keyword}'")

        except Exception as e:
            print(f"[错误] 处理文件 {txt_file} 时发生未知错误: {e}")

if __name__ == "__main__":
    extract_json_from_logs()
    input("\n处理完成，按回车键退出...")