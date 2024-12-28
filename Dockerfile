FROM python:3.10-slim

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# TODO: use volume
COPY data/llm-vs-llm.db ./data/llm-vs-llm.db

COPY visualization.py .
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["python", "visualization.py"]