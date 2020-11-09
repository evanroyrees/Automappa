FROM python:3.7-slim-buster

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY . .
CMD [ "--help" ]
ENTRYPOINT [ "python", "index.py" ]