run: curl main view
	clear

# datafile变量
datafile = data/big_negetive_demands.json

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