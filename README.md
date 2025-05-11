# Hacker News Discussion Summarizer

A web application that summarizes Hacker News discussions using the OpenRouter API.

![HN Discussion Summarizer Screenshot](img/screenshot.png)

## Features

- Simple, clean interface for entering Hacker News URLs
- Accepts full HN URLs or just item IDs
- Summarizes discussions with thematic organization
- Supports multiple LLMs via OpenRouter
- Renders results in formatted markdown
- Allows for downloading the summary as Markdown
- Dockerized deployment for easy setup
- Cross-architecture compatibility (works on x86 and ARM64)

## Setup

### Prerequisites

- Docker and Docker Compose
- OpenRouter API key

### Docker Deployment

#### Quick Start (Production Mode)

1. Clone this repository:
   ```
   git clone https://github.com/samayethali/hacker-news-summary.git
   cd hacker-news-summary
   ```

2. Configure your environment variables (required):
   - Rename `.env.example` to `.env` and set your OpenRouter API key

3. For most users, simply run:

```bash
docker compose up -d
```

This will automatically pull the pre-built multi-architecture images that match your system architecture (x86_64/AMD64 or ARM64).

Access the application by navigating to:
```
http://localhost:8081
```

To stop the services:
```bash
docker compose down
```

#### Development Mode

If you're developing or extending the application and want to build the images locally:

```bash
# Using the helper script:
./run.sh dev

# Or manually with environment variable:
BUILD_LOCALLY=true docker compose up -d --build
```

## API Endpoints

- `POST /summarize`: Accepts a JSON payload with a `url` field containing a Hacker News URL or item ID
- `POST /summarize_stream`: Streams the summary response for a Hacker News URL or item ID

## Project Structure

```
hacker-news-summary/
├── .env.example           # Example environment variables file
├── .gitignore             # Git ignore file
├── docker-compose.yml     # Docker Compose configuration
├── LICENSE                # License file
├── rebuild-and-run.sh     # Helper script to rebuild and run the application
├── run.sh                 # Helper script to run the application
├── backend/
│   ├── .dockerignore      # Docker ignore file for backend
│   ├── Dockerfile         # Backend Docker configuration
│   ├── entrypoint.sh      # Docker entrypoint script
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Dependencies
├── frontend/
│   ├── .dockerignore      # Docker ignore file for frontend
│   ├── Dockerfile         # Frontend Docker configuration
│   ├── health.html        # Health check page
│   ├── index.html         # HTML interface
│   ├── nginx.conf         # Nginx configuration
│   ├── script.js          # Frontend logic
│   └── styles.css         # Styling
├── README.md              # This file
```
