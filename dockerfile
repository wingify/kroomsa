FROM python:3.6.5-slim
COPY inference_requirements.txt /app/inference_requirements.txt
WORKDIR /app
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r inference_requirements.txt
RUN apt-get update -y && apt-get install libomp-dev libopenblas-dev -y
COPY . /app
EXPOSE 5000
CMD gunicorn -c /app/gunicorn_config.py server:app