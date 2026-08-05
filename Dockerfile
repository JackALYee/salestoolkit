# Streamax Sales Toolkit (Streamlit) — container image for hosts that support
# custom domains + WebSockets (Cloud Run, Render, Railway, Fly.io, any VM).
# Streamlit Community Cloud does NOT need this file; it's for the custom-domain
# deployment at streamax-salestoolkit.com.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# curl is only needed for the container healthcheck.
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Install deps first so code edits don't bust the layer cache.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run / Render inject $PORT; default to 8080 for local `docker run`.
ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -fsS "http://localhost:${PORT}/_stcore/health" || exit 1

# Shell form so ${PORT} expands at runtime.
CMD streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0
