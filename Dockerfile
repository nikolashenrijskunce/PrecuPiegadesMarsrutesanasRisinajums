FROM python:3.12-slim

WORKDIR /flask-app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000 

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]