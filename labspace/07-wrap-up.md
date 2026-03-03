# Wrap-up 🎉

You've taken a naive, oversized Dockerfile and transformed it into a production-grade image — step by step, each section building on the last.

## What You Built

Here's the final Dockerfile from this lab:

```dockerfile no-run-button
# ---- Stage 1: Base ----
# Install only production dependencies into a virtual environment.
FROM dhi.io/python:3.13-dev AS base

WORKDIR /app

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ---- Stage 2: Test ----
# Extend the base stage with dev dependencies and run tests.
FROM base AS test

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN python -m pytest tests/ -v


# ---- Stage 3: Production ----
FROM dhi.io/python:3.13 AS production

WORKDIR /app

# Copy the production-only venv from the base stage — no dev dependencies included.
COPY --from=base /app/venv /app/venv

# Copy source from the test stage. This creates an explicit dependency on the test
# stage, so if tests fail the production image won't be built.
COPY --from=test /app/src ./src/

ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER nobody

EXPOSE 5050
CMD ["python", "src/app.py"]
```

Compare that to where you started — `COPY . .` before `pip install`, running as root, no multi-stage, no `.dockerignore`. The final image uses Docker Hardened Images with near-zero CVEs and is significantly more secure.

## See the Improvement 📊

Do a final side-by-side comparison of everything you built throughout the lab:

```bash
docker images quote-app
```

You should see `v1` (naive, ~1 GB), `v2` (optimized but single-stage), `v3` (multi-stage, slim base), and `dhi` (Docker Hardened Images). The progression tells the story.

Verify the final image is still fully functional:

```bash
docker run --rm -p 5050:5050 quote-app:dhi &
sleep 2 && curl http://localhost:5050 && curl http://localhost:5050/health
```

```bash
docker stop $(docker ps -q --filter ancestor=quote-app:dhi)
```

Want to check your image for known vulnerabilities? Docker Scout can scan it:

```bash
docker scout cves quote-app:dhi
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
- [ ] Use a minimal base image for production (`python:*-slim`, `python:*-alpine`, or Docker Hardened Images at `dhi.io`)

**Multi-stage builds**
- [ ] Run tests in a build stage — fail fast if tests break
- [ ] Use a minimal base image in the production stage
- [ ] Only copy what the runtime needs into the final stage (source code, installed packages)

## What to Explore Next

- **BuildKit cache mounts** — `--mount=type=cache` for persistent pip/apt caches across builds, making incremental builds even faster
- **Docker Scout** — scan your images for known vulnerabilities: `docker scout cves quote-app:dhi`
- **OCI image labels** — use `LABEL` to annotate images with version, maintainer, and source info for traceability

🎉 Well done — your containers are now leaner, faster to build, and safer to ship.
