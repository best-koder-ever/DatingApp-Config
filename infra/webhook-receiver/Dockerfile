FROM python:3.12-slim
RUN pip install flask
WORKDIR /app
COPY receiver.py .
CMD ["python", "receiver.py"]
