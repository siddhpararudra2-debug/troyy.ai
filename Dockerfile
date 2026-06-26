FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY minimal_main.py .

ENV PYTHONPATH=/app
ENV PORT=8000
EXPOSE $PORT

CMD ["uvicorn", "minimal_main:app", "--host", "0.0.0.0", "--port", "8000"]
