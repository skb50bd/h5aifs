FROM python:3.9
RUN apt-get update && apt-get install -y fuse
# RUN modprobe fuse
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir /app/dflix
CMD [ "python", "main.py", "http://cdn.dflix.live", "/app/dflix" ]
