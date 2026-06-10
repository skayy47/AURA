# AURA Backend — HF Spaces / Railway / Render compatible
# Bakes Playwright + Chromium at build time for the PDF report.
# Set PORT=7860 on HF Spaces; defaults to 8000 for local docker run.

FROM python:3.11-slim

# System deps for Chromium (Playwright renders the Data Intelligence Report).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libxkbcommon0 libpango-1.0-0 \
    libcairo2 libasound2 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python deps first (layer cache)
COPY AURA-BACKEND/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers into the image (bakes Chromium — no cold-start download)
RUN pip install --no-cache-dir playwright && \
    playwright install chromium --with-deps

# Copy backend source
COPY AURA-BACKEND/ ./

# Copy Jinja2 templates and static sample data
COPY AURA-BACKEND/templates/ ./templates/
COPY AURA-BACKEND/static/ ./static/

ENV PORT=8000
EXPOSE 8000

# $PORT is set by HF Spaces (7860) / Railway / Render — falls back to 8000 locally
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
