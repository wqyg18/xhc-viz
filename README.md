# 🗺️ Viz - 物流路径规划可视化工具

一个专业的物流路径规划可视化工具，基于Folium地图库，提供美观的物流配送路线可视化展示。

## ✨ 核心功能

- 🗺️ **交互式地图可视化** - 使用Folium创建美观的交互式地图
- 🚚 **物流路径规划** - 支持车辆路径规划(VRP)问题的可视化
- 📍 **多类型标记** - 仓库、车辆、站点、未指派站点的区分显示
- 🛣️ **动态路线动画** - 使用AntPath插件展示动态行驶路线
- 📊 **详细信息弹窗** - 点击标记显示完整的物流信息
- 🎯 **坐标转换** - 支持BD-09到WGS84坐标系的精确转换
- 📝 **日志解析** - 从算法日志自动提取数据并生成可视化
- 🔄 **批量处理** - 支持批量测试和批量可视化
- 🔍 **日志匹配** - 从算法日志中提取输入输出，匹配请求响应关系
- 📈 **对比可视化** - 支持原始响应与新响应的可视化对比
- 🔌 **本地接口集成** - 支持调用本地算法接口并可视化结果

## 🏗️ 项目结构

```
viz/
├── main.py                 # 主应用程序 - 物流可视化核心逻辑
├── batch_viz.py           # 批量可视化脚本
├── batch_test.py          # 批量测试脚本
├── viz_from_logs.py       # 从日志生成可视化
├── rid_log_matcher.py     # 日志请求响应匹配器
├── request_and_visualize.py # 请求与可视化对比工具
├── utils/
│   ├── __init__.py
│   └── coord_transform.py  # 坐标转换工具 (BD-09 → WGS84)
├── pyproject.toml          # 项目配置和依赖管理
├── Makefile               # 构建和运行脚本
├── data/                  # 主要数据文件目录
│   ├── req.json          # 请求数据
│   └── response.json     # API响应数据
├── test_input/           # 批量测试输入数据
├── test_output/          # 批量测试输出结果
├── test_input_from_log/  # 从日志提取的测试输入
├── test_output_from_log/ # 从日志提取的测试输出
├── from_logs/            # 原始日志文件和解析数据
├── mylog_input/          # 算法日志输入目录
├── mylog_output/         # 算法日志输出目录
└── README.md             # 项目文档
```

## 📁 文件夹详解

### 📊 数据文件夹

| 文件夹 | 📝 用途 | 🔗 对应文件/命令 |
|:------:|---------|------------------|
| **`data/`** | 存放主要的请求数据和API响应结果 | [main.py](file:///home/wsl/viz/main.py) 默认输入<br>`make run` / `make debug` |
| **`test_input/`** | 存放用于批量测试的输入JSON文件 | [batch_test.py](file:///home/wsl/viz/batch_test.py) 输入<br>`make test_batch` |
| **`test_output/`** | 存放批量测试的输出结果（HTML + JSON） | [batch_test.py](file:///home/wsl/viz/batch_test.py) 输出<br>`make test_batch` |
| **`test_input_from_log/`** | 存放从日志提取的测试数据（JSON + TXT） | [batch_test.py](file:///home/wsl/viz/batch_test.py) 输入<br>`make test_batch_from_log` |
| **`test_output_from_log/`** | 存放从日志提取数据的测试输出 | [batch_test.py](file:///home/wsl/viz/batch_test.py) 输出<br>`make test_batch_from_log` |
| **`from_logs/`** | 存放原始日志文件和解析后的数据 | [viz_from_logs.py](file:///home/wsl/viz/viz_from_logs.py) 输入/输出 |
| **`mylog_input/`** | 存放算法日志文件，用于提取输入输出数据 | [rid_log_matcher.py](file:///home/wsl/viz/rid_log_matcher.py) 输入 |
| **`mylog_output/`** | 存放从算法日志提取的请求响应数据 | [rid_log_matcher.py](file:///home/wsl/viz/rid_log_matcher.py) 输出 |
| **`4c1396ccc039445ea171519d811d85cc/`** | 特定数据集（哈希命名） | [batch_viz.py](file:///home/wsl/viz/batch_viz.py) 输入/输出 |

### 🛠️ 工具文件夹

| 文件夹 | 📝 用途 | 📄 说明 |
|:------:|---------|--------|
| **`utils/`** | 工具函数模块 | 包含坐标转换等功能 |

### ⚙️ 系统文件夹

| 文件夹 | 📝 用途 | 📄 说明 |
|:------:|---------|--------|
| **`.venv/`** | Python虚拟环境 | 项目依赖管理 |
| **`__pycache__/`** | Python缓存 | 编译后的字节码 |

## 🔗 文件与命令对应关系

### 1️⃣ [main.py](file:///home/wsl/viz/main.py) - 主可视化脚本

```bash
# 输入
data/req.json          # 请求数据
data/response.json     # API响应数据

# 输出
input_map.html         # 输入地图（站点分布）
output_map.html        # 输出地图（路径规划）

# 对应Make命令
make run    # 完整流程：发送请求 → 生成可视化
make debug  # 仅生成可视化（不发送请求）
```

### 2️⃣ [batch_viz.py](file:///home/wsl/viz/batch_viz.py) - 批量可视化脚本

```bash
# 输入
4c1396ccc039445ea171519d811d85cc/
├── 1-req.json
├── 1-rsp.json
├── 2-req.json
├── 2-rsp.json
└── ...

# 输出
4c1396ccc039445ea171519d811d85cc/html/
├── 1-req.html
├── 1-rsp.html
├── 2-req.html
├── 2-rsp.html
└── ...
```

### 3️⃣ [viz_from_logs.py](file:///home/wsl/viz/viz_from_logs.py) - 从日志生成可视化

```bash
# 输入
from_logs/
└── 428203a665124523ad6dab289aff247e.txt  # 原始日志文件

# 输出
from_logs/428203a665124523ad6dab289aff247e/
├── req.json          # 解析后的请求数据
├── response.json     # 解析后的响应数据
├── input_map.html    # 输入地图
└── output_map.html   # 输出地图
```

### 4️⃣ [batch_test.py](file:///home/wsl/viz/batch_test.py) - 批量测试脚本

```bash
# 使用 test_input 的批量测试
make test_batch
# 输入: test_input/*.json
# 输出: test_output/run_YYYYMMDD_HHMMSS/

# 使用 test_input_from_log 的批量测试
make test_batch_from_log
# 输入: test_input_from_log/*.json
# 输出: test_output_from_log/run_YYYYMMDD_HHMMSS/
```

### 5️⃣ [rid_log_matcher.py](file:///home/wsl/viz/rid_log_matcher.py) - 日志请求响应匹配器

```bash
# 输入
mylog_input/app_YYYY-MM-DD.log  # 算法日志文件

# 输出
mylog_input/app_YYYY-MM-DD/{rid}_req.json  # 提取的请求数据
mylog_input/app_YYYY-MM-DD/{rid}_rsp.json  # 提取的响应数据

# 功能
# - 从算法日志中提取请求和响应数据
# - 基于rid匹配请求响应对
# - 过滤特定类型的决策(decision_type=1, plan_type=0)
# - 生成调度业务分析报告
```

### 6️⃣ [request_and_visualize.py](file:///home/wsl/viz/request_and_visualize.py) - 请求与可视化对比工具

```bash
# 命令1: 发送请求到本地算法接口
python request_and_visualize.py request --input-dir mylog_input/app_YYYY-MM-DD --api-url http://localhost:8000/api/your-endpoint

# 命令2: 可视化原始输入输出
python request_and_visualize.py visualize-original --input-dir mylog_input/app_YYYY-MM-DD

# 命令3: 可视化新响应
python request_and_visualize.py visualize-new --input-dir mylog_input/app_YYYY-MM-DD --new-output-dir new_responses

# 命令4: 对比可视化新旧响应
python request_and_visualize.py visualize-compare --input-dir mylog_input/app_YYYY-MM-DD --new-output-dir new_responses

# 输出
# - 新响应数据: new_responses/{rid}_new_rsp.json
# - 可视化结果: visualization/original/ 或 visualization/compare/
```

## 🎯 工作流程总结

```mermaid
graph LR
    A[单次测试] --> B[data/]
    B --> C[main.py]
    C --> D[根目录HTML文件]

    E[批量测试] --> F[test_input/]
    F --> G[batch_test.py]
    G --> H[test_output/]

    I[日志可视化] --> J[from_logs/*.txt]
    J --> K[viz_from_logs.py]
    K --> L[from_logs/{hash}/]

    M[批量可视化] --> N[4c1396ccc039445ea171519d811d85cc/]
    N --> O[batch_viz.py]
    O --> P[4c1396ccc039445ea171519d811d85cc/html/]

    Q[算法日志处理] --> R[mylog_input/app_YYYY-MM-DD.log]
    R --> S[rid_log_matcher.py]
    S --> T[mylog_input/app_YYYY-MM-DD/]

    T --> U[request_and_visualize.py request]
    U --> V[new_responses/]
    T --> W[request_and_visualize.py visualize-original]
    T --> X[request_and_visualize.py visualize-compare]
    V --> X
    W --> Y[visualization/original/]
    X --> Z[visualization/compare/]
```

## 📋 Makefile命令说明

| 命令 | 🎯 功能 | 📂 涉及文件夹 |
|:-----|:--------|:-------------|
| `make run` | 发送请求到API并生成可视化 | `data/` → 根目录HTML |
| `make debug` | 仅生成可视化（不发送请求） | `data/` → 根目录HTML |
| `make test_batch` | 批量测试（使用test_input） | `test_input/` → `test_output/` |
| `make test_batch_from_log` | 批量测试（使用test_input_from_log） | `test_input_from_log/` → `test_output_from_log/` |

## 🚀 快速开始

### 安装依赖

```bash
# 使用 uv 包管理器（推荐）
uv sync

# 或者使用 pip
pip install -e .
```

### 运行应用

#### 单次测试

```bash
# 完整流程：发送请求 → 生成响应 → 可视化结果
make run

# 或者分步执行：
make curl    # 发送API请求获取路径规划结果
make main    # 生成输入地图可视化
make view    # 查看输出结果地图

# 仅生成可视化（不发送请求）
make debug
```

#### 从日志生成可视化

```bash
# 1. 将日志文件放入 from_logs/ 目录
# 2. 运行日志解析脚本
python viz_from_logs.py

# 脚本会自动：
# - 解析日志中的请求和响应数据
# - 生成 req.json 和 response.json
# - 创建 input_map.html 和 output_map.html
# - 自动在浏览器中打开可视化结果
```

#### 批量测试

```bash
# 使用 test_input 目录进行批量测试
make test_batch

# 使用 test_input_from_log 目录进行批量测试
make test_batch_from_log

# 输出结果会保存在 test_output/run_YYYYMMDD_HHMMSS/ 目录下
```

#### 批量可视化

```bash
# 对已有的一批 JSON 数据进行批量可视化
python batch_viz.py

# 输入: 4c1396ccc039445ea171519d811d85cc/ 目录下的 *-req.json 和 *-rsp.json
# 输出: 4c1396ccc039445ea171519d811d85cc/html/ 目录下的 HTML 文件
```

## 📋 数据格式

### 请求数据 (data/req.json)
包含仓库信息、车辆信息、站点需求等物流数据：
- `depot`: 仓库信息（位置、名称等）
- `vehicle`: 车辆信息（当前位置、容量、状态等）
- `stations`: 配送站点列表（需求、位置、服务时间等）

### 响应数据 (data/response.json)
包含路径规划结果：
- `routes`: 规划好的配送路线
- `unassigned_tasks`: 未指派的站点任务
- 各站点的到达时间、服务时间等信息

## 🛠️ 技术栈

- **Python 3.12+** - 主要编程语言
- **Folium** - 交互式地图可视化
- **坐标转换算法** - BD-09到WGS84精确转换
- **Makefile** - 自动化构建流程

## � 主要文件说明

### main.py
主应用程序，包含两个主要功能：
1. `create_visualization()` - 创建输入数据的基础可视化
2. `create_output_visualization()` - 创建美化后的输出结果可视化

### batch_viz.py
批量可视化脚本，用于处理多组请求-响应对：
- 自动匹配 `*-req.json` 和 `*-rsp.json` 文件
- 批量生成输入和输出地图
- 输出到 `html/` 子目录

### batch_test.py
批量测试脚本，用于自动化测试：
- 读取输入目录中的JSON文件
- 发送API请求获取响应
- 生成可视化结果
- 支持时间戳命名避免覆盖

### rid_log_matcher.py
日志请求响应匹配器，用于从算法日志中提取数据：
- 基于正则表达式提取日志中的请求和响应
- 用rid字段匹配请求响应对
- 递归搜索嵌套JSON结构中的关键字段
- 过滤特定决策类型的调度数据
- 生成详细的调度业务分析报告

### request_and_visualize.py
请求与可视化对比工具，集成本地接口调用和可视化功能：
- 发送请求到本地算法接口获取新响应
- 可视化原始输入输出数据
- 对比原始响应与新响应的可视化结果
- 支持并行处理多个请求
- 支持自定义输入输出目录和处理数量

### viz_from_logs.py
日志解析脚本，从日志文件提取数据：
- 解析日志中的请求调度参数和计划调度结果
- 支持Java对象格式的解析
- 自动生成JSON和HTML文件
- 自动在浏览器中打开可视化结果

### utils/coord_transform.py
坐标转换工具，提供：
- `bd09_to_wgs84()` - 百度坐标系到WGS84坐标系的转换
- 精确的坐标转换算法实现

### Makefile
自动化脚本：
- `make run` - 完整运行流程（发送请求 + 生成可视化）
- `make debug` - 仅生成可视化（不发送请求）
- `make curl` - 发送API请求
- `make main` - 运行主程序
- `make view` - 查看结果
- `make test_batch` - 批量测试
- `make test_batch_from_log` - 从日志批量测试

## 🎨 可视化特性

- **颜色编码**：绿色表示正需求(补货)，橙色表示负需求(取货)
- **动态路线**：蚂蚁路径动画显示行驶路线
- **顺序标记**：使用带数字的圆形标记显示配送顺序
- **图层控制**：可切换显示已指派路线和未指派站点
- **详细信息**：点击标记显示完整的物流信息

## 💡 使用场景

### 场景 1：快速测试单个案例
```bash
# 1. 准备请求数据到 data/req.json
# 2. 运行完整流程
make run

# 3. 查看生成的可视化
# - input_map.html: 显示站点分布
# - output_map.html: 显示规划路线
```

### 场景 2：从历史日志生成可视化
```bash
# 1. 将日志文件放入 from_logs/ 目录
cp your_log.txt from_logs/

# 2. 运行日志解析
python viz_from_logs.py

# 3. 自动生成并打开可视化结果
# 结果保存在 from_logs/{log_hash}/ 目录
```

### 场景 3：批量测试多个案例
```bash
# 1. 准备多个测试JSON文件到 test_input/ 目录
# 2. 运行批量测试
make test_batch

# 3. 查看批量测试结果
# 结果保存在 test_output/run_YYYYMMDD_HHMMSS/ 目录
```

### 场景 4：批量可视化已有数据
```bash
# 1. 准备成对的 req/rsp JSON文件
# 2. 运行批量可视化
python batch_viz.py

# 3. 查看生成的HTML文件
# 结果保存在对应目录的 html/ 子目录
```

### 场景 5：从算法日志提取数据并可视化
```bash
# 1. 将算法日志文件放入 mylog_input/ 目录
cp your_algorithm_log.log mylog_input/app_2026-01-21.log

# 2. 运行日志匹配器提取请求响应数据
python rid_log_matcher.py

# 3. 查看提取的结果和分析报告
# 结果保存在 mylog_input/app_2026-01-21/ 目录
# 控制台会显示调度业务分析报告

# 4. 可视化原始输入输出
python request_and_visualize.py visualize-original --input-dir mylog_input/app_2026-01-21

# 5. 查看原始可视化结果
# 结果保存在 visualization/original/ 目录
```

### 场景 6：调用本地接口并对比可视化
```bash
# 1. 确保本地算法接口正在运行
# 2. 发送请求到本地接口获取新响应
python request_and_visualize.py request --input-dir mylog_input/app_2026-01-21 --api-url http://localhost:8000/api/your-endpoint

# 3. 对比可视化原始响应与新响应
python request_and_visualize.py visualize-compare --input-dir mylog_input/app_2026-01-21 --new-output-dir new_responses

# 4. 查看对比可视化结果
# 结果保存在 visualization/compare/ 目录
```

## 🔧 开发

### 安装开发依赖

```bash
uv sync --dev
```

### 代码格式化

```bash
make format
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 📧 问题反馈: [GitHub Issues](https://github.com/your-username/viz/issues)
- 💬 讨论: 项目讨论区

---

⭐ 如果这个物流可视化工具对您有帮助，请给它一个星标！