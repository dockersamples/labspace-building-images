FROM python:3.14

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5050

CMD ["python", "src/app.py"]
