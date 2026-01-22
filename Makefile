run: curl main view
	clear
debug: main view
	clear

test_batch:
	uv run python batch_test.py --input test_input --output test_output

test_batch_from_log:
	uv run python batch_test.py --input test_input_from_log --output test_output_from_log

# datafile变量
datafile = data/req.json

main:
	uv run python main.py --data_file $(datafile)
curl:
	curl -X POST http://localhost:8000/api/v1/dispatch \
		-H "Content-Type: application/json" \
		-d @$(datafile) \
		-o data/response.json

view:
	wslview input_map.html
	wslview output_map.html

DIR ?= ./test_output
batch_view:
	@echo "正在搜索目录 $(DIR) 中的 HTML 文件..."
	@for file in $$(ls $(DIR)/*.html 2>/dev/null); do \
		echo "正在打开 $$file..."; \
		wslview $$file; \
	done

# 日志可视化命令，接受日志文件名作为参数
# 使用方法: make log_viz_origin_in_out LOG_FILE=<log_file_name>
log_viz_origin_in_out:
	@if [ -z "$(LOG_FILE)" ]; then \
		echo "错误: 请指定日志文件名"; \
		exit 1; \
	fi
	LOG_NAME=$(shell basename "$(LOG_FILE)" .log) && \
	uv run python ./request_and_visualize.py visualize-original \
	--input-dir ./mylog_input/$$LOG_NAME/ \
	--viz-dir ./mylog_output

# 启动Python HTTP服务器，方便直接访问生成的HTML文件
run_http_server:
	@echo "启动HTTP服务器，访问地址: http://localhost:8000"
	uv run python -m http.server 8000

# 运行日志匹配器，接受日志文件名作为参数
# 使用方法: make run_log_matcher LOG_FILE=<log_file_name>
run_log_matcher:
	@if [ -z "$(LOG_FILE)" ]; then \
		echo "错误: 请指定日志文件名，使用方法: make run_log_matcher LOG_FILE=<log_file_name>"; \
		exit 1; \
	fi
	uv run python ./rid_log_matcher.py $(LOG_FILE)

# 一键完成：匹配日志 -> 生成可视化 -> 提示启动 Server
# 使用方法: make log_viz_all LOG_FILE=app_2026-01-21.log
log_viz_all:
	@if [ -z "$(LOG_FILE)" ]; then \
		echo "错误: 请指定日志文件名，例如: make log_viz_all LOG_FILE=app_2026-01-21.log"; \
		exit 1; \
	fi
	@echo "--- 步骤 1: 正在匹配日志 rid ---"
	$(MAKE) run_log_matcher LOG_FILE=$(LOG_FILE)
	@echo "--- 步骤 2: 正在生成可视化 HTML ---"
	$(MAKE) log_viz_origin_in_out LOG_FILE=$(LOG_FILE)
	@echo "--- 步骤 3: 处理完成！---"
	@echo "请运行 'make run_http_server' 并访问浏览器查看结果。"