import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path


def open_html(file_path):
    """
    跨平台打开 HTML 文件：支持 Windows, macOS, WSL, 和普通 Linux
    """
    path_str = str(file_path)
    system = platform.system().lower()

    try:
        # 1. 优先检测是否在 WSL 环境中
        # 检查内核信息中是否包含 microsoft 关键字
        if "microsoft" in platform.uname().release.lower():
            if shutil.which("wslview"):
                subprocess.run(["wslview", path_str])
                return
            else:
                print(
                    "提示：WSL 环境下建议安装 wslu (sudo apt install wslu) 以便使用 wslview 打开浏览器"
                )

        # 2. Windows 环境
        if system == "windows":
            os.startfile(path_str)

        # 3. macOS 环境
        elif system == "darwin":
            subprocess.run(["open", path_str])

        # 4. 普通 Linux 环境
        else:
            # xdg-open 是 Linux 下通用的打开文件命令
            if shutil.which("xdg-open"):
                subprocess.run(["xdg-open", path_str])
            else:
                # 最后尝试使用 Python 自带的 webbrowser
                import webbrowser

                webbrowser.open(f"file://{os.path.abspath(path_str)}")

    except Exception as e:
        print(f"尝试打开文件失败: {e}")


def parse_java_object_to_dict(s, key_context=None):
    """
    内部辅助函数：将 Java toString 格式转换为 Python 字典
    key_context: 传入当前的键名，用于决定是否强制转换类型
    """
    s = s.strip()

    # 1. 处理列表 [...]
    if s.startswith("[") and s.endswith("]"):
        content = s[1:-1]
        parts = []
        depth = 0
        start = 0
        for i, char in enumerate(content):
            if char in "([":
                depth += 1
            elif char in ")]":
                depth -= 1
            elif char == "," and depth == 0:
                parts.append(content[start:i].strip())
                start = i + 1
        parts.append(content[start:].strip())
        # 列表中的元素递归解析
        return [parse_java_object_to_dict(p) for p in parts if p]

    # 2. 处理对象 ClassName(key=value)
    obj_match = re.match(r"^[a-zA-Z0-9.]+\((.*)\)$", s)
    if obj_match:
        content = obj_match.group(1)
        kv_pairs = {}
        depth = 0
        start = 0
        current_key = None
        for i, char in enumerate(content):
            if char in "([":
                depth += 1
            elif char in ")]":
                depth -= 1
            elif char == "=" and depth == 0:
                current_key = content[start:i].strip()
                start = i + 1
            elif char == "," and depth == 0:
                if current_key:
                    val_str = content[start:i].strip()
                    parsed_val = parse_java_object_to_dict(val_str, current_key)
                    # 只有当值不是 None 时才加入字典（模拟你期望的 JSON 行为）
                    if parsed_val is not None:
                        kv_pairs[current_key] = parsed_val
                start = i + 1

        # 处理最后一对 KV
        if current_key:
            val_str = content[start:].strip()
            parsed_val = parse_java_object_to_dict(val_str, current_key)
            if parsed_val is not None:
                kv_pairs[current_key] = parsed_val
        return kv_pairs

    # 3. 基础类型转换逻辑
    if s.lower() == "null":
        return None
    if s.lower() == "true":
        return True
    if s.lower() == "false":
        return False

    # 强制将这些键对应的值视为字符串，不转为数字
    force_str_keys = {
        "location_id",
        "trace_id",
        "request_id",
        "vehicle_id",
        "node_index",
    }

    if key_context in force_str_keys:
        return s

    try:
        if "." in s:
            return float(s)
        # 如果不是强制字符串的 Key，尝试转 int
        return int(s)
    except ValueError:
        return s


def extract_logs_as_json(file_path):
    """
    提取 '请求调度参数' 和 '计划调度结果'
    """
    final_data_list = []

    # 匹配 JSON 格式的请求
    re_params = re.compile(r"请求调度参数:\s*(\{.*\})")
    # 匹配 Java toString 格式的结果
    re_result = re.compile(r"计划调度结果:\s*(DispatchResponse\(.*\))")

    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 处理请求参数
            param_match = re_params.search(line)
            if param_match:
                try:
                    final_data_list.append(json.loads(param_match.group(1)))
                except:
                    pass

            # 处理调度结果
            result_match = re_result.search(line)
            if result_match:
                try:
                    dict_data = parse_java_object_to_dict(result_match.group(1))
                    final_data_list.append(dict_data)
                except Exception as e:
                    print(f"解析 Java 对象失败: {e}")

    return final_data_list


def process_log_file(input_file):
    """
    针对单个日志文件进行解析、目录创建和可视化生成
    """
    # 1. 获取不带后缀的文件名并创建对应目录
    log_path = Path(input_file)
    if not log_path.exists():
        print(f"错误：找不到文件 {input_file}")
        return

    base_name = log_path.stem
    target_dir = Path("from_logs") / base_name
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- 正在处理: {base_name} ---")

    # 2. 提取数据
    results = extract_logs_as_json(str(log_path))

    if len(results) < 2:
        print(f"警告：{base_name} 提取到的数据不足（共 {len(results)} 条）。")

    # 3. 定义并保存文件路径
    req_json = target_dir / "req.json"
    res_json = target_dir / "response.json"
    input_map = target_dir / "input_map.html"
    output_map = target_dir / "output_map.html"

    # 保存 JSON 数据
    files_to_save = [req_json, res_json]
    for i, data in enumerate(results[:2]):
        with open(files_to_save[i], "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"已生成: {files_to_save[i]}")

    # 4. 调用可视化函数
    if len(results) >= 2:
        from main import create_output_visualization, create_visualization

        try:
            # 站点地图
            create_visualization(data_file=str(req_json), output_file=str(input_map))
            # 路线地图
            create_output_visualization(
                req_file=str(req_json),
                response_file=str(res_json),
                output_file=str(output_map),
            )
            print(f"成功保存 HTML 映射至: {target_dir}")

            # --- 新增：使用 wslview 自动打开 HTML 文件 ---
            for html_file in [input_map, output_map]:
                if html_file.exists():
                    print(f"正在打开可视化页面: {html_file}")
                    open_html(html_file)
            # ------------------------------------------

        except Exception as e:
            print(f"生成可视化地图或打开时出错: {e}")


if __name__ == "__main__":
    target_log = ""

    if os.path.exists(target_log):
        process_log_file(target_log)
    else:
        # 备选：如果目录下有多个txt，可以批量处理
        for txt_file in Path("./from_logs").glob("*.txt"):
            process_log_file(txt_file)
        print(f"未找到文件: {target_log}")
