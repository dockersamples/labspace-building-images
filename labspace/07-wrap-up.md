# Wrap-up 🎉

You've taken a naive, oversized Dockerfile and transformed it into a production-grade image — step by step, each section building on the last.

## What You Built

Here's the final Dockerfile from this lab:

```dockerfile no-run-button
# ---- Stage 1: Test ----
FROM python:3.12 AS test

WORKDIR /app

COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY . .

RUN python -m pytest tests/ -v


# ---- Stage 2: Production ----
FROM python:3.12-slim AS production

WORKDIR /app

COPY --from=test /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

USER nobody

EXPOSE 5050
CMD ["python", "src/app.py"]
```

Compare that to where you started — `COPY . .` before `pip install`, running as root, no multi-stage, no `.dockerignore`. The final image is roughly **5–8× smaller** and significantly more secure.

## See the Improvement 📊

Do a final side-by-side comparison of everything you built throughout the lab:

```bash
docker images quote-app
```

You should see `v1` (naive, ~1 GB), `v2` (optimized but single-stage), and `v3` (multi-stage, slim base). The progression tells the story.

Verify the final image is still fully functional:

```bash
docker run --rm -p 5050:5050 quote-app:v3 &
sleep 2 && curl http://localhost:5050 && curl http://localhost:5050/health
```

```bash
docker stop $(docker ps -q --filter ancestor=quote-app:v3)
```

Want to check your image for known vulnerabilities? Docker Scout can scan it:

```bash
docker scout cves quote-app:v3
```

## Best Practices Checklist ✅

Use this as a reference for every Dockerfile you write:

**Layer management**
- [ ] Combine `apt-get install` and `rm -rf /var/lib/apt/lists/*` in a single `RUN`
- [ ] Combine install and cleanup of any temporary files in the same `RUN` step

**Build cache efficiency**
- [ ] Copy dependency manifests (`requirements.txt`, `package.json`) before source code
- [ ] Use `--no-cache-dir` (pip) or equivalent to avoid writing unnecessary cache to layers
- [ ] Keep a `.dockerignore` that excludes `.git`, caches, test files, and local config

**Security**
- [ ] Never use `ARG` or `ENV` to pass secrets — use `--mount=type=secret` instead
- [ ] Run the app process as a non-root user (`USER nobody` or a dedicated app user)
- [ ] Use `python:*-slim` or `python:*-alpine` instead of the full image for production

**Multi-stage builds**
- [ ] Run tests in a build stage — fail fast if tests break
- [ ] Use a minimal base image in the production stage
- [ ] Only copy what the runtime needs into the final stage (source code, installed packages)

## What to Explore Next

- **BuildKit cache mounts** — `--mount=type=cache` for persistent pip/apt caches across builds, making incremental builds even faster
- **Distroless base images** — `gcr.io/distroless/python3` for production services where you want the minimal possible attack surface
- **Docker Scout** — scan your images for known vulnerabilities: `docker scout cves quote-app:v3`
- **OCI image labels** — use `LABEL` to annotate images with version, maintainer, and source info for traceability

🎉 Well done — your containers are now leaner, faster to build, and safer to ship.
