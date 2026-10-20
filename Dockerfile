# CiteCheck web app as a Docker image: Hugging Face Spaces (Docker SDK, free "CPU basic") or any Docker host.
# Owner: Engineering.  Steps: deploy/DEPLOY.md.
FROM python:3.11-slim

# Hugging Face Spaces runs the container as user 1000.
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/home/user/.cache/huggingface \
    CITECHECK_LOG=/home/user/app/logs/usage.jsonl
WORKDIR /home/user/app

# CPU-only PyTorch first (much smaller than the default CUDA build), then everything else.
COPY --chown=user requirements.txt .
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1 \
 && pip install -r requirements.txt

COPY --chown=user . .
USER user
# Bake the data and the verifier model into the image, so the app starts fast and never downloads at request time.
RUN python -m data.fetch_scifact \
 && python -c "from src.nli import build_verifier; build_verifier('nli')._load()"

EXPOSE 8501
# XSRF protection off: Streamlit's file uploader is refused (HTTP 403) behind the Spaces proxy otherwise.
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.headless=true", "--server.enableXsrfProtection=false", "--browser.gatherUsageStats=false"]
