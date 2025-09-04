# 🗺️ Viz - 物流路径规划可视化工具

一个专业的物流路径规划可视化工具，基于Folium地图库，提供美观的物流配送路线可视化展示。

## ✨ 核心功能

- 🗺️ **交互式地图可视化** - 使用Folium创建美观的交互式地图
- 🚚 **物流路径规划** - 支持车辆路径规划(VRP)问题的可视化
- 📍 **多类型标记** - 仓库、车辆、站点、未指派站点的区分显示
- 🛣️ **动态路线动画** - 使用AntPath插件展示动态行驶路线
- 📊 **详细信息弹窗** - 点击标记显示完整的物流信息
- 🎯 **坐标转换** - 支持BD-09到WGS84坐标系的精确转换

## 🏗️ 项目结构

```
viz/
├── main.py                 # 主应用程序 - 物流可视化核心逻辑
├── utils/
│   ├── __init__.py
│   └── coord_transform.py  # 坐标转换工具 (BD-09 → WGS84)
├── pyproject.toml          # 项目配置和依赖管理
├── Makefile               # 构建和运行脚本
├── data/                  # 数据文件目录
│   ├── req.json          # 请求数据示例
│   └── response.json     # 响应数据示例
└── README.md             # 项目文档
```

## 🚀 快速开始

### 安装依赖

```bash
# 使用 uv 包管理器（推荐）
uv sync

# 或者使用 pip
pip install -e .
```

### 运行应用

```bash
# 完整流程：发送请求 → 生成响应 → 可视化结果
make run

# 或者分步执行：
make curl    # 发送API请求获取路径规划结果
make main    # 生成输入地图可视化
make view    # 查看输出结果地图
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

## 📁 主要文件说明

### main.py
主应用程序，包含两个主要功能：
1. `create_visualization()` - 创建输入数据的基础可视化
2. `create_output_visualization()` - 创建美化后的输出结果可视化

### utils/coord_transform.py
坐标转换工具，提供：
- `bd09_to_wgs84()` - 百度坐标系到WGS84坐标系的转换
- 精确的坐标转换算法实现

### Makefile
自动化脚本：
- `make run` - 完整运行流程
- `make curl` - 发送API请求
- `make main` - 运行主程序
- `make view` - 查看结果

## 🎨 可视化特性

- **颜色编码**：绿色表示正需求(补货)，橙色表示负需求(取货)
- **动态路线**：蚂蚁路径动画显示行驶路线
- **顺序标记**：使用带数字的圆形标记显示配送顺序
- **图层控制**：可切换显示已指派路线和未指派站点
- **详细信息**：点击标记显示完整的物流信息

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