FROM python:3.11.0
RUN mkdir /backendforchina
WORKDIR /backendforchina
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
