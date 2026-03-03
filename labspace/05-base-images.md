# Choosing a Base Image 🎯

The base image is the foundation of everything you base on top of. Picking the right one has a direct impact on image size, security surface area, and compatibility.

Python alone comes in several variants with very different sizes and tradeoffs:

| Image | Approximate size | Use case |
|-------|-----------------|----------|
| `python:3.12` | ~1 GB | Full Debian — most compatible, largest |
| `python:3.12-slim` | ~130 MB | Debian without optional packages — good default |
| `python:3.12-alpine` | ~50 MB | Alpine Linux — smallest, uses musl libc |

Pull them and compare:

```bash
docker pull python:3.12-slim && docker pull python:3.12-alpine
```

```bash
docker images python
```

> [!WARNING]
> Alpine uses **musl libc** instead of **glibc**. Most pure-Python packages work fine, but packages with C extensions (numpy, Pillow, cryptography) may fail to install or behave differently. `python:3.12-slim` is usually the safer default for Python apps.

## Docker Hardened Images 🔒

Community images like `python:3.12-slim` are well-maintained, but they still ship with packages your app doesn't need — and those packages carry CVEs. **Docker Hardened Images (DHI)** take a different approach: they are built from scratch to include only what is strictly necessary to run the application, resulting in up to 95% fewer vulnerabilities than their community equivalents.

DHI are **free to use** and available at `dhi.io`, but do require authentication. 

1. Login using your Docker Hub credentials:

    ```bash
    docker login dhi.io
    ```

    Note that if you're running this lab in Docker Desktop and you're authenticated in Docker Desktop, this login will automatically finish.

2. Once authenticated, you can pull any DHI image:

    ```bash
    docker pull dhi.io/python:3.13
    ```

    ```bash
    docker images dhi.io/python
    ```

### Dev vs Runtime Variants

DHI images come in two variants:

| Variant | Example | Contains |
|---------|---------|----------|
| Runtime | `dhi.io/python:3.13` | Python runtime only — no shell, no package manager |
| Dev | `dhi.io/python:3.13-dev` | Adds shell and package manager for base-time use |

This maps naturally onto the multi-stage pattern from the previous section, with one extra wrinkle: the runtime image has **no pip**, so you can't `RUN pip install` in the production stage. The solution is to install packages into a **virtual environment** in the dev stage and copy the whole venv across.

There's also a subtlety around test dependencies. If you install both production and dev deps into the same venv before copying it, pytest ends up in your production image. The clean solution is **three stages**:

1. **`base`** — install only production deps into a venv
2. **`test`** — extend `base` with dev deps and run tests
3. **`production`** — copy the clean venv from `base` and source from `test`

Copying source from `test` (rather than the base context) preserves the dependency that blocks the production base if tests fail.

1. Update your Dockerfile to use DHI base images:

    ```dockerfile save-as=Dockerfile
    # ---- Stage 1: Build ----
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

2. Build the new image and give it a tag of `dhi`:

    ```bash
    docker build -t quote-app:dhi .
    ```

3. Compare the size against your previous image:

    ```bash
    docker images quote-app
    ```

> [!NOTE]
> DHI runtime images have no shell, so `docker run --rm quote-app:dhi sh` will fail — which is the point. There's nothing for an attacker to work with. Use the `-dev` variant or a sidecar debugging container if you need to inspect a running container.

### Why DHI Over Distroless?

Both DHI and Google's distroless images follow the same principle of shipping the minimum possible runtime. DHI adds:

- **Continuous CVE monitoring and patching** by Docker, with critical issues addressed within 7 days
- **SLSA Build Level 3 provenance** — cryptographic proof of how and where the image was built
- **SBOMs included** — a full software bill of materials for every image
- **Familiar Docker Hub authentication** — no new tooling required

## A Note on Tags

Using a version tag like `python:3.12-slim` is convenient, but the underlying packages update over time. For fully reproducible builds, pin to a specific digest:

```bash
docker inspect python:3.12-slim --format '{{index .RepoDigests 0}}'
```

```dockerfile no-run-button
FROM python:3.12-slim@sha256:<digest>
```

For most teams, pinning to the tag is a reasonable tradeoff between reproducibility and staying current with security patches. DHI makes this easier — each image is continuously updated and the vulnerability data is publicly transparent, so you can trust that the latest tag is in good shape.

In the next section, you'll tackle the most dangerous Dockerfile mistake: baking secrets into your images.
