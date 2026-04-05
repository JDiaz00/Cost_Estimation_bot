FROM python:3.11-slim

LABEL maintainer="Julio Diaz"
LABEL description="Construction Cost Estimation Chatbot"
LABEL version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home appuser
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 7860

CMD ["python", "run_gradio_app.py"]
