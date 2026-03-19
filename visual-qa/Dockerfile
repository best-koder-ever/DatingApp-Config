FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    android-tools-adb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/src

COPY requirements.txt /app/src/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/src/

ENTRYPOINT ["python", "run_visual_qa.py"]
CMD ["--use-case", "all"]
