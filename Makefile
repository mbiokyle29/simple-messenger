lint:
	flake8 simple_messenger tests

test:
	py.test tests

run:
	env FLASK_DEBUG=True FLASK_APP=simple_messenger/app.py flask run

dbuild:
	docker build -t simple-messenger:latest .

drun:
	docker run -d -p 5000:5000 simple-messenger:latest
