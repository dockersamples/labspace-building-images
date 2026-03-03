# Choosing a Base Image 🎯

The base image is the foundation of everything you build on top of. Picking the right one has a direct impact on image size, security surface area, and compatibility.

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

## Distroless: Going Even Further

For maximum security, Google's **distroless** images strip out everything except the language runtime — no shell, no package manager, no utilities. If an attacker gains code execution inside your container, there's almost nothing for them to work with.

```dockerfile no-run-button
FROM gcr.io/distroless/python3
```

The tradeoff: debugging is harder (no shell, no `exec` into the container for interactive troubleshooting). Distroless is worth it for production services once you're confident in your image.

For this lab, `python:3.12-slim` is the right call — and you're already using it in your production stage from the previous section. ✅

## A Note on Tags

Using `python:3.12` pins you to a major.minor version, but the underlying Debian/Alpine packages still update over time. For fully reproducible builds, pin to a specific digest:

```bash
docker inspect python:3.12-slim --format '{{index .RepoDigests 0}}'
```

```dockerfile no-run-button
FROM python:3.12-slim@sha256:<digest>
```

For most teams, pinning to the tag (`python:3.12-slim`) is a reasonable tradeoff between reproducibility and staying current with security patches.

In the next section, you'll tackle the most dangerous Dockerfile mistake: baking secrets into your images.
