FROM python:3.10-alpine

COPY birthday_calendar.py birthday_calendar.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "birthday_calendar.py"]