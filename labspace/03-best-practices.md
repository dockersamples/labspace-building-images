# Dockerfile Best Practices ⚡

Now that you understand layers, it's time to apply that knowledge. Three simple changes to your Dockerfile will make your builds faster, your images leaner, and your containers safer.

## The Caching Problem

Open :fileLink[Dockerfile]{path="Dockerfile"} and look at the instruction order. Right now it reads:

```dockerfile no-run-button
COPY . .
RUN pip install -r requirements.txt
```

**The problem:** Docker caches a layer only when nothing *above* it in the Dockerfile has changed. Because your source code is copied before `pip install` runs, any change to *any file* in the project — even a one-character edit — invalidates the pip install cache. Every rebuild reinstalls all your dependencies from scratch.

Try it: make a small change to the app and rebuild:

```bash
echo "# touched" >> src/app.py && docker build -t quote-app:v1 .
```

Notice that `pip install` runs again even though `requirements.txt` didn't change.

## Fix 1: Copy Dependencies Before Source Code 📦

1. Restructure the Dockerfile so that `requirements.txt` is copied and packages are installed *before* the source code is copied:

    ```dockerfile save-as=Dockerfile highlight=5-8
    FROM python:3.12

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY src/ ./src/

    EXPOSE 5050
    CMD ["python", "src/app.py"]
    ```

2. Build using the updated Dockerfile:

    ```bash
    docker build -t quote-app:v2 .
    ```

3. Now make another code change and rebuild:

    ```bash
    echo "# touched again" >> src/app.py && docker build -t quote-app:v2 .
    ```

    This time, `pip install` is **cached** — Docker sees that `requirements.txt` hasn't changed and skips straight to the `COPY src/` step. Only the layers that actually changed are rebuilt. ⚡

    ```console no-run-button no-copy-button highlight=2
    ...
     => CACHED [4/5] RUN pip install --no-cache-dir -r requirements.txt 
    ...
    ```

> [!TIP]
> The general pattern: copy files that change *infrequently* (dependency manifests, config files) as early as possible. Copy files that change *frequently* (source code) as late as possible.

## Fix 2: Add a .dockerignore File 🙈

Even with `COPY src/ ./src/`, Docker still sends your entire project directory to the build daemon as the "build context". This includes `.git`, test files, local caches, and anything else in your project folder. That slows things down and can accidentally leak files into your image.

A `.dockerignore` file tells Docker what to exclude from the build context — similar to `.gitignore`.

1. Create a `.dockerignore` file with the following contents::

    ```plaintext save-as=.dockerignore
    # Version control
    .git
    .gitignore

    # Python cache
    __pycache__
    *.pyc
    *.pyo
    *.pyd
    .Python

    # Virtual environments
    .venv
    venv/
    env/

    # Dev tools
    pytest.ini
    .pytest_cache/

    # Editor and OS files
    .DS_Store
    *.swp
    .env
    ```

> [!NOTE]
> `tests/` and `requirements-dev.txt` are intentionally *not* excluded here — the multi-stage build in a later section needs both in the build context for the test stage. The multi-stage build itself keeps them out of the production image, so there's no need to block them from the context too.

2. Rebuild and watch the "build context" line at the top of the output:

    ```bash
    docker build -t quote-app:v2 .
    ```

    The context size should be smaller now. You will see more significant changes in larger projects.

## Fix 3: Run as a Non-Root User 🛡️

By default, the process inside your container runs as `root`. While containers are isolated from the host, running as root inside a container is still unnecessary risk — it violates the principle of least privilege, and if a vulnerability allows a container escape, root access makes the situation much worse.

1. Add a `USER` instruction to switch to a non-privileged user before starting the app:

    ```dockerfile save-as=Dockerfile highlight=10
    FROM python:3.12

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY src/ ./src/

    USER nobody

    EXPOSE 5050
    CMD ["python", "src/app.py"]
    ```

    > [!NOTE]
    > `nobody` (UID 65534) is a built-in system user with no home directory and minimal permissions, available in most Linux-based images. For production, consider creating a dedicated app user with `RUN addgroup --system app && adduser --system --group app` for better control.

2. Rebuild the image:

    ```bash
    docker build -t quote-app:v2 .
    ```

3. Verify the `nobody` user is the default user by starting a new container and overriding the default command to run `whoami`:

    ```bash
    docker run --rm quote-app:v2 whoami
    ```

    The process now runs as `nobody`. 
    
4. Restart the app container with the improved image:

    ```bash
    docker stop quote-app && docker rm quote-app
    docker run -d -p 5050:5050 --name quote-app quote-app:v2
    ```

5. Confirm it still works:

    ```bash
    curl http://localhost:5050
    ```

With three changes — instruction reordering, `.dockerignore`, and a non-root user — your Dockerfile is already significantly better. Next up: eliminating the biggest source of bloat with multi-stage builds.
