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

log_viz_origin_in_out:
	uv run python /home/wsl/viz/request_and_visualize.py visualize-original \
	--input-dir ./mylog_input/app_2026-01-21/ \
	--viz-dir ./mylog_output/visualization/original \
	--max-count 5

log_request_all:
	uv run python /home/wsl/viz/request_and_visualize.py request \
	--input-dir ./mylog_input/app_2026-01-21/ \
	--output-dir ./mylog_output/new_responses \
	--api-url http://localhost:8000/api/v1/dispatch \
	--max-count 5

log_viz_new_out:
	uv run python /home/wsl/viz/request_and_visualize.py visualize-new \
	--input-dir ./mylog_input/app_2026-01-21/ \
	--new-output-dir ./mylog_output/new_responses \
	--viz-dir ./mylog_output/visualization/new \
	--max-count 5