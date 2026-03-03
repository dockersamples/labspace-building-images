# Build Secrets 🔐

Secrets — API keys, tokens, passwords — are often needed at build time. For example, to authenticate to a private package registry, download a licensed dependency, or call an internal API.

## The Wrong Way: Build Arguments 🚨

A tempting but **dangerous** approach is to pass secrets as build arguments.

1. Create a file named `Dockerfile.bad-secret` with the following contents:

    ```dockerfile save-as=Dockerfile.bad-secret highlight=5-7
    FROM python:3.12-slim

    WORKDIR /app

    # 🚨 NEVER do this — secrets passed as ARG are visible in image history
    ARG API_KEY
    RUN echo "Configuring with key: ${API_KEY}"

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY src/ ./src/

    USER nobody
    EXPOSE 5050
    CMD ["python", "src/app.py"]
    ```

2. Build it with a secret value being passed with the `--build-arg` flag:

    ```bash
    docker build -f Dockerfile.bad-secret --build-arg API_KEY=super-secret-token-123 -t quote-app:bad-secret .
    ```

    You'll probably notice a warning in the build output similar to the following:

    ```console no-copy-button no-run-button
     1 warning found (use docker --debug to expand):
     - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ARG "API_KEY") (line 6)
    ```

3. Now check the image history:

    ```bash
    docker history quote-app:bad-secret
    ```

    Look carefully at the output. You can see your secret value right there in the layer history. 
    
    ```console no-copy-button no-run-button
    ... ARG API_KEY=super-secret-token-123 ...
    ```
    
    **Anyone who can pull this image can read your secrets**, regardless of where it's stored or who you share it with.

    > [!CAUTION]
    > `ARG` values are stored in the image metadata. Even if you use `RUN unset API_KEY` afterwards, the value is permanently embedded in the layer that used it.

## The Right Way: Build Secrets 🔒

Docker BuildKit provides `--mount=type=secret`, which makes a secret available during a single `RUN` step **without writing it to any layer**. The secret exists only in memory during that instruction and is never committed to the image.

The following steps are going to use a file that provides the secret, but there are other ways to present secrets to a build. Check out the [Build secrets documentation](https://docs.docker.com/build/building/secrets/) for additional guidance.

1. Create a file containing a secret value (this simulates a token file you'd have locally):

    ```bash
    printf "super-secret-token-123" > .mysecret
    ```

2. Create a `Dockerfile.good-secret` with the following contents:

    ```dockerfile save-as=Dockerfile.good-secret highlight=7-11
    FROM python:3.12-slim

    WORKDIR /app

    COPY requirements.txt .

    # The secret is available at /run/secrets/api_key during this RUN step only.
    # It is never written to any layer.
    RUN --mount=type=secret,id=api_key \
        echo "Configuring with key: $(cat /run/secrets/api_key | cut -c1-4)****" && \
        pip install --no-cache-dir -r requirements.txt

    COPY src/ ./src/

    USER nobody
    EXPOSE 5050
    CMD ["python", "src/app.py"]
    ```

3. Build the image now, specifying the secret with the `--secret` flag:

    ```bash
    docker build -f Dockerfile.good-secret --secret id=api_key,src=.mysecret -t quote-app:good-secret .
    ```

4. Inspect the history:

    ```bash
    docker history quote-app:good-secret
    ```

    The secret is nowhere in the output. 
    
5. Now verify that the secret isn't accessible inside the final image either:

    ```bash
    docker run --rm quote-app:good-secret cat /run/secrets/api_key
    ```

The file doesn't exist — the secret was available only during the build step, and nothing was persisted to the image. 🔒

## Clean Up

```bash
docker rmi quote-app:bad-secret quote-app:good-secret
rm .mysecret
```

> [!TIP]
> Add `.mysecret` (and any other local secret files) to your `.gitignore` and `.dockerignore` to ensure they're never accidentally committed to version control or included in the build context.

Head to the final section for a summary of everything you've learned.
