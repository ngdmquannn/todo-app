# VULN #9 — Insecure Dockerfile (CWE-250, CWE-1269)
#   - uses outdated Python image with known CVEs
#   - copies everything (.env, .git, creds) into the image
#   - runs pip as root, no --no-cache-dir
#   - final container runs as root
#   - Flask debug mode exposed on 0.0.0.0 (see run.py)
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python","run.py"]
