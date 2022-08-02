dependencies:
	pip install -r requirements.txt

setToken:
	@echo "Setting new bot token"
	@echo $(token) > "bot.token"
	@echo "Token set in 'bot.token', this will override any token set in .env!"

run:
	python3 core/check_dependencies.py
	python3 core/check_file_stores.py
	python3 core/check_database.py
	python3 core/make_logs.py

	clear

	python3 core/main.py
