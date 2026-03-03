# Quote of the Day API

A simple Python Flask app used as the sample application throughout the *Building Container Images: Best Practices* labspace.

## Endpoints

- `GET /` — returns a random quote as JSON
- `GET /health` — returns `{"status": "ok"}`

## Running with Docker

```bash
docker build -t quote-app .
docker run -p 5050:5050 quote-app
curl http://localhost:5050
```
