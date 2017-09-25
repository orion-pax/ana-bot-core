FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u","./run.py"]
