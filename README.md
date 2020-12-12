# Simple Messenger

A simple messaging API written for Guild Education coding submission.

## Local development

For local development work, the flask app can be run directly on the host OS. First time setup is as follows:

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
