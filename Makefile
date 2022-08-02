dependencies:
	pip install -r requirements.txt

run:
	python3 core/check_dependencies.py
	python3 core/check_file_stores.py
	python3 core/check_database.py

	python3 core/make_logs.py
	python3 core/main.py
