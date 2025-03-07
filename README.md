# Hacker News Discussion Summarizer

A web application that summarizes Hacker News discussions using the Anthropic API.

![HN Discussion Summarizer Screenshot](img/screenshot.png)

## Features

- Simple, clean interface for entering Hacker News URLs
- Accepts full HN URLs or just item IDs
- Fetches and parses HN discussion threads
- Summarizes discussions with thematic organization
- Renders results in formatted markdown
- Dockerized deployment for easy setup
- Allows for downloading the result as Markdown
- Cross-architecture compatibility (works on x86 and ARM64)

## Setup

### Prerequisites

- Docker and Docker Compose
- Anthropic API key

### Configuration

1. Clone this repository:
   ```
   git clone https://github.com/samayethali/hacker-news-summary.git
   cd hacker-news-summary
   ```

2. Configure your environment variables:
   - Rename `.env.example` to `.env`
   - Edit the `.env` file in the root directory
   - Set your Anthropic API key: `ANTHROPIC_API_KEY=your_api_key_here`
   - Optionally set the model: `ANTHROPIC_MODEL=claude-3-7-sonnet-20250219` (defaults to `claude-3-5-haiku-20241022` if not specified)

### Docker Deployment

> **Note**: If you're upgrading from a previous version, run the `./rebuild-and-run.sh` script to apply the latest fixes for cross-architecture compatibility.

The application provides three distinct deployment profiles to suit different environments:

#### 1. Development Mode

Use these profiles when developing or extending the application. They build the images locally from source:

**For x86_64/AMD64 Systems (Intel/AMD):**
```bash
docker compose --profile dev-x86 up -d
```

To stop the services:
```bash
docker compose --profile dev-x86 down
```

**For ARM64 Systems (e.g., Apple Silicon, Raspberry Pi 4):**
```bash
docker compose --profile dev-arm64 up -d
```

To stop the services:
```bash
docker compose --profile dev-arm64 down
```

#### 2. Production Mode - x86_64/AMD64 Systems

For deployment on Intel/AMD based systems:

```bash
docker compose --profile prod-x86 up -d
```

To stop the services:
```bash
docker compose --profile prod-x86 down
```

#### 3. Production Mode - ARM64 Systems

For deployment on ARM-based systems (e.g., Apple Silicon, Raspberry Pi 4):

```bash
docker compose --profile prod-arm64 up -d
```

To stop the services:
```bash
docker compose --profile prod-arm64 down
```

After starting any of these profiles, access the application by navigating to:
```
http://localhost:8081
```

## API Endpoints

- `POST /summarize`: Accepts a JSON payload with a `url` field containing a Hacker News URL or item ID

## Project Structure

```
hacker-news-summary/
├── .env                   # Environment variables
├── docker-compose.yml     # Docker Compose configuration
├── backend/
│   ├── main.py            # FastAPI application
│   ├── requirements.txt   # Dependencies
│   └── Dockerfile         # Backend Docker configuration
├── frontend/
│   ├── index.html         # HTML interface
│   ├── styles.css         # Styling
│   ├── script.js          # Frontend logic
│   └── Dockerfile         # Frontend Docker configuration
└── README.md              # This file
```
