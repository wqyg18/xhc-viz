run: curl main view
	clear
debug: main view
	clear

test_batch:
	uv run python batch_test.py --input test_input --output test_output

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