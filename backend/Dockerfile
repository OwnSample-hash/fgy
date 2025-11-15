FROM python:3.13-alpine

EXPOSE 8000

ENV ENV=PROD

RUN pip install --no-cache-dir pipenv && \
  mkdir -p /app/data && \
  adduser -D appuser

WORKDIR /app
VOLUME /app/data

COPY backend /app
RUN chown -R appuser:appuser /app
USER appuser

RUN pipenv install --deploy --ignore-pipfile

CMD ["pipenv", "run", "python", "main.py"]
# Vim: set expandtab tabstop=2 shiftwidth=2:
