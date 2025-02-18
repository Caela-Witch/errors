FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup --system appgroup && adduser --system --group appuser
USER appuser

COPY app.py ./
COPY templates ./templates
COPY ssl ./ssl

EXPOSE 8080 8443

CMD gunicorn -w 4 -b 0.0.0.0:8080 app:app & \
    gunicorn -w 4 --certfile ssl/server.cert --keyfile ssl/private.cert -b 0.0.0.0:8443 app:app

