import os
import random
from flask import Flask, jsonify

app = Flask(__name__)

QUOTES = [
    "Build once, run anywhere.",
    "Small images, big impact.",
    "Every layer tells a story.",
    "Containers are the building blocks of modern software delivery.",
    "Immutable infrastructure starts with immutable images.",
    "Don't ship what you don't need.",
]


@app.route("/")
def get_quote():
    return jsonify(quote=random.choice(QUOTES))


@app.route("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    app.run(host="0.0.0.0", port=port)
