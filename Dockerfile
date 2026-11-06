FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY app.py /app/app.py

RUN pip install --no-cache-dir .

EXPOSE 8501
EXPOSE 5678

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

