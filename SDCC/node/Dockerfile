# syntax=docker/dockerfile:1
# creo immagine
FROM node:12-alpine
RUN apk add --no-cache gcc musl-dev linux-headers python3 py3-pip python3-dev
# ^ scarico cose che mi servono
WORKDIR /node
# in /node copio tutto quello che sta in node
COPY node/ .
COPY ec2.json .
COPY requirements.txt .
# installo dipendenze e poi eseguo applicazione
RUN pip install -r requirements.txt
CMD ["python3", "run.py", "-v", "-a", "bully", "-c", "./ec2.json"]
