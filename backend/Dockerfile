# The backend API as a container, for Render, Railway or any Docker host.
# NOT YET TESTED on a real host: build it once and try /health and /pdf before going live.
#
# Python 3.11 is required: Swiss Ephemeris (pyswisseph) ships ready-made builds for it.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV=production \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /srv

COPY requirements.txt .
# build-essential is needed only if pyswisseph has to be compiled; Chromium and its
# system libraries are installed by Playwright for the PDF generator.
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && pip install --no-cache-dir -r requirements.txt \
 && python -m playwright install --with-deps chromium \
 && apt-get purge -y build-essential && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

COPY app ./app

# Run as an ordinary user, not root
RUN useradd --create-home runner && mkdir -p /var/data && chown -R runner /srv /ms-playwright /var/data
USER runner

EXPOSE 8000
# One worker: each PDF starts a headless browser, and a small server has memory for one at a time
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --proxy-headers --forwarded-allow-ips='*'"]
