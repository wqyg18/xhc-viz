run: curl main view
	clear

main:
	uv run python main.py
curl:
	curl -X POST http://localhost:8000/api/v1/dispatch \
		-H "Content-Type: application/json" \
		-d @data/req.json \
		-o data/response.json
view:
	# wslview input_map.html
	wslview output_map.html