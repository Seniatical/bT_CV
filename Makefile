dependencies:
	pip install -r requirements.txt

setToken:
	@echo "Setting new bot token"
	@echo $(token) > "bot.token"
	@echo "Token set in 'bot.token', this will override any token set in .env!"

run:
	python3 src/check_dependencies.py
	python3 src/check_file_stores.py
	python3 src/check_database.py
	python3 src/make_logs.py

	clear

	python3 src/main.py

test:
	@echo "Testing command trees"
	python3 tests/trees.py