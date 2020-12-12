init_db_local:
	psql -c "DROP DATABASE IF EXISTS simple_messenger"
	psql -c "DROP DATABASE IF EXISTS simple_messenger_test"
	psql -c "DROP USER IF EXISTS simple_messenger_user"
	psql -c "CREATE USER simple_messenger_user WITH PASSWORD 'password123'"
	psql -c "CREATE DATABASE simple_messenger OWNER simple_messenger_user"
	psql -c "CREATE DATABASE simple_messenger_test OWNER simple_messenger_user"

db_migrate:
	env SQLALCHEMY_DATABASE_URL=postgresql://simple_messenger_user:password123@localhost/simple_messenger \
		FLASK_DEBUG=True \
		FLASK_APP=simple_messenger/app.py \
		flask db migrate

db_upgrade:
	env SQLALCHEMY_DATABASE_URL=postgresql://simple_messenger_user:password123@localhost/simple_messenger \
		FLASK_DEBUG=True \
		FLASK_APP=simple_messenger/app.py \
		flask db upgrade

lint:
	flake8 simple_messenger tests

test:
	env SQLALCHEMY_DATABASE_URL=postgresql://simple_messenger_user:password123@localhost/simple_messenger_test \
	py.test tests

run:
	env SQLALCHEMY_DATABASE_URL=postgresql://simple_messenger_user:password123@localhost/simple_messenger \
		FLASK_DEBUG=True \
		FLASK_APP=simple_messenger/app.py \
		flask run

shell:
	env SQLALCHEMY_DATABASE_URL=postgresql://simple_messenger_user:password123@localhost/simple_messenger \
		FLASK_DEBUG=True \
		FLASK_APP=simple_messenger/app.py \
		flask shell

dbuild:
	docker build -t simple-messenger:latest .

drun:
	docker run -d -p 5000:5000 simple-messenger:latest
