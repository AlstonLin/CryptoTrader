venv:
	virtualenv -p python3 venv
	./venv/bin/pip install -r requirements.txt

clean:
	rm -rf venv
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

update_requirements:
	./venv/bin/pip freeze > requirements.txt

start: venv
	./venv/bin/python run_bot.py
