FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-hin \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

RUN groupadd --system ugcrulebook \
    && useradd --system --gid ugcrulebook --create-home ugcrulebook \
    && install -d -o ugcrulebook -g ugcrulebook /app/feedback

COPY --chown=ugcrulebook:ugcrulebook . .

USER ugcrulebook

RUN python -c "from backend.vectorstore import collection, index_documents; index_documents(); assert collection.count() > 0, 'Document indexing produced no chunks'"

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]