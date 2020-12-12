lint:
	flake8 simple_messenger tests

test:
	py.test tests

run:
	env FLASK_DEBUG=True FLASK_APP=simple_messenger/app.py flask run
