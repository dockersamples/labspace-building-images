# Welcome: Building Container Images! 🐳

You've already run Docker containers — now it's time to build them properly. In this lab, you'll take a simple Python web app and progressively improve how its container image is built, learning the practices used in real production environments along the way.

By the end, you'll know how to:

- 🔍 Read an image's layer history and understand what Docker actually built
- ⚡ Structure Dockerfiles so expensive steps are cached and fast rebuilds are the norm
- 🛡️ Run containers as non-root users and protect secrets at build time
- 📦 Drastically reduce image size using multi-stage builds
- 🎯 Choose the right base image for any situation

## Verify Your Environment ✅

Confirm Docker is available and running:

```bash
docker version
```

You should see both a **Client** and **Server** section. If so, you're good to go.

## Meet the Sample App 🎯

Throughout this lab, you'll be working with a small **Quote of the Day** API — a Python Flask app that returns random developer wisdom. It's simple enough to stay out of the way while you focus on the Docker side.

Take a look at the project files:

```bash
ls -la
```

Open these files in the IDE to explore them:

- :fileLink[src/app.py]{path="src/app.py"} — the Flask application
- :fileLink[requirements.txt]{path="requirements.txt"} — Python dependencies
- :fileLink[Dockerfile]{path="Dockerfile"} — the starting Dockerfile

> [!NOTE]
> This Dockerfile works, but it has several issues you'll identify and fix over the course of the lab. For now, the goal is just to get something running.

## Build and Run the Image 🚀

1. Build the image:

    ```bash
    docker build -t quote-app:v1 .
    ```

    > [!TIP]
    > The first build may take a moment — Docker needs to pull the base image and install dependencies. Subsequent builds will be much faster once the layer cache is warm.

2. Run a container using the image you just built:

    ```bash
    docker run -d -p 5050:5050 --name quote-app quote-app:v1
    ```

3. Test the app:

    ```bash
    curl http://localhost:5050
    ```

    You should see a JSON response with a random quote. Open it in the browser:

4. Open your browser to :tabLink[http://localhost:5050]{href="http://localhost:5050" title="Quote App" id="quote-app"} to view the site

5. Check the health endpoint too:

    ```bash
    curl http://localhost:5050/health
    ```

Your app is running in a container. In the next section, you'll look under the hood to understand what Docker actually built — and discover a common mistake that silently inflates image sizes.
