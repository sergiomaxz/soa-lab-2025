FROM python:3.9-slim
WORKDIR /app
# Встановлюємо бібліотеки для криптографії та вебу
RUN pip install flask flask-cors requests pika python-jose[cryptography]
COPY . .
CMD ["python", "app.py"]