# Log Classifier API

This project provides a web service that exposes a single endpoint to classify log text using a set of predefined classifiers. The service is built with [FastAPI](https://fastapi.tiangolo.com/) and can be easily deployed using Docker.

## Features

- **Single Endpoint**: `/classify` accepts a JSON payload with a `text` field.
- **Classification**: Returns a list of matching classifiers based on the input text.
- **Docker Support**: Easily containerize and deploy the application.

## Getting Started

### Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started) (optional, for containerized deployment)

[Read the Guide](DEPLOYMENT.md)

