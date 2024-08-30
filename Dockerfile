FROM python:3.10-bullseye

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y libsndfile1

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
pip install style-bert-vits2

RUN pip install -r requirements.txt

CMD uvicorn main:app --host 0.0.0.0 --port $PORT