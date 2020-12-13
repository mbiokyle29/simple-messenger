FROM python:3.8

ENV PYTHONUNBUFFERED=1
WORKDIR /app/

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY simple_messenger /app/simple_messenger/
COPY migrations /app/migrations/

ENV FLASK_APP=simple_messenger/app.py
CMD flask run -h 0.0.0.0 -p 5000
