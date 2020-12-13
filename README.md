# Simple Messenger

A simple messaging API written for Guild Education coding submission.

## Local development

For local development work, the flask app can be run directly on the host OS.
Note that all instructions assume the host OS is Mac OSX Catalina (10.15.7).

First time setup is as follows:

1. Create a virtual environment: `python3 -m venv .venv`
2. Activate the virtual environments: `source .venv/bin/activate`
3. Install application and development requirements: `pip install -r requirements_dev --upgrade`

Subsequent setup only requires the running of step #2 and optionally step #3 (if requirements have changed).

The `Makefile` contains entry points for common development tasks:
- `make lint`: Runs linting on the python app + test code
- `make test`: Runs the unit tests
- `make run`: Starts up the development server (with hot reloading)


## Docker

A Dockerfile is maintained to facilitate a more controlled execution environment.
- The image can be built with the following command: `docker build -t simple-messenger:latest .`
- The image instantiated with the following command: `docker run -d -p 5000:5000 simple-messenger:latest`
- The above commands are available via the `Makefile` as `dbuild` and `drun`


## Data Layer

This application uses postgresql as a data store. When running, it is expected
that a connection string is available under the environment variable: `SQLALCHEMY_DATABASE_URL`.

Commands in the make file set this value to be: `postgresql://simple_messenger_user:password123@localhost/simple_messenger` (or `.../simple_messenger_test`)

### DB Setup

The reccomended approach for a locally running version of Postgres (on OSX) is to use Postgres.app. It can be downloaded here:
https://postgresapp.com/downloads.html

Instructions for setup can be found here:
https://postgresapp.com/

Once installed, ensure that the application is started/running in the background. Then run: `make init_db_local`, which will teardown (if present) and recreate the
nessecary databases and user. This command creates:
- A database called `simple_messenger`, which is used when running the application directly
- A database called `simple_messenger_test`, which is used when running the unit tests
- A user called `simple_messenger` which owns both DBs. Note that this user has a trivial password and should not be used in production.

### Database Migrations

This project uses Flask-Migrate to manage its data models and data migrations. The following command is run to initalize the project:
```bash
env SQLALCHEMY_DATABASE_URL=postgresql://simple_messenger_user:password123@localhost/simple_messenger \
    FLASK_DEBUG=True \
    FLASK_APP=simple_messenger/app.py \
    flask db init
```

Note that this should never need to be re-run, and it will error if ran again (the `migrations/` directory already exists).
The following command should be run when brining up a new development environment: `make db_upgrade`

Changes to the schema should be captured using `make db_migrate` and a subsequently applied to the DB using `make db_upgrade`.
Note that migrations only apply to the default database. The tests create/destroy tables on `simple_messenger_test` during test execution.


## API

This service provides a minimal API for working with the data models (Users and Messages).

For users you can:
- create a new user (essentially just get the UUID)
- list all users
- see a single user

For messages you can:
- post a new message between 2 users
- list messages

The messaging listing endpoint supports a number of query parameters, and operates in 2 modes:
1. Global mode, all messages are returned. The results can be filtered using the `since` and `limit` params
2. Conversation mode. In this mode `sender_id` and `receiver_id` must both be provided. The results will only include messages sender from / sent to these users. `since` and `limit` can also be applied here.

### SWAGGER docs

There are swagger docs located in the `simple_messenger/static/swagger.yml` file. These can be viewed at the `/docs/` route. Note that they are manually maintained at this time, and since they are loaded at app creation, changes to the file will not be picked up by the dev server hot reload.
