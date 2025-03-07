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

The application now supports automatic multi-architecture detection, which makes it much simpler to deploy on any system without manually selecting architecture-specific profiles.

#### 1. Quick Start (Production Mode)

For most users, simply run:

```bash
docker compose up -d
```

This will automatically pull the pre-built multi-architecture images that match your system architecture (x86_64/AMD64 or ARM64).

To stop the services:
```bash
docker compose down
```

#### 2. Development Mode

If you're developing or extending the application and want to build the images locally:

```bash
# Using the helper script:
./compose-up.sh dev

# Or manually with environment variable:
BUILD_LOCALLY=true docker compose up -d --build
```

#### 3. Using the Helper Script

A convenience script is provided to easily switch between modes:

```bash
# Production mode (using pre-built images)
./compose-up.sh

# Development mode (building locally)
./compose-up.sh dev
```

#### 4. Customizing Images

You can customize the image repository and tag in your `.env` file:

```
# In your .env file:
BUILD_LOCALLY=false
IMAGE_REPO=your-registry/hacker-news-summary
IMAGE_TAG=v1.0.0
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
