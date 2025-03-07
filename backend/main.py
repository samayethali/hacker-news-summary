import os
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs
import re
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import anthropic

# Load .env file
load_dotenv()

app = FastAPI(title="HN Summary API")

@app.get("/health")
async def health_check():
    """Health check endpoint for container monitoring."""
    return {"status": "healthy"}

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get environment variables
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

# Get model from environment, default to claude-3.7-sonnet if not specified
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3.7-sonnet")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

class HNRequest(BaseModel):
    url: str

class SummaryResponse(BaseModel):
    summary: str

def extract_hn_id(url: str) -> str:
    """Extract Hacker News item ID from a URL or return the ID if it's a number."""
    # Check if input is just a number (direct ID)
    if url.isdigit():
        return url
    
    # Try to parse as URL
    parsed_url = urlparse(url)
    
    # Check for news.ycombinator.com or hn.algolia.com URLs
    if 'news.ycombinator.com' in parsed_url.netloc:
        # Extract ID from URL path or query parameters
        if 'item' in parsed_url.path:
            match = re.search(r'item\?id=(\d+)', url)
            if match:
                return match.group(1)
        # Check query parameters
        query_params = parse_qs(parsed_url.query)
        if 'id' in query_params:
            return query_params['id'][0]
    
    elif 'hn.algolia.com' in parsed_url.netloc:
        # Extract ID from algolia URL
        match = re.search(r'/items/(\d+)', url)
        if match:
            return match.group(1)
    
    # If no ID found, raise an error
    raise ValueError("Could not extract Hacker News item ID from the provided URL")

async def fetch_hn_data(item_id: str) -> Dict[Any, Any]:
    """Fetch data from HN Algolia API."""
    url = f"https://hn.algolia.com/api/v1/items/{item_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from Hacker News API")
        return response.json()

def extract_comments(item: Dict[Any, Any]) -> List[str]:
    """Extract comments recursively, similar to the shell script's jq logic."""
    comments = []
    
    def process_comment(comment):
        if "author" in comment and "text" in comment and comment["text"]:
            comments.append(f"{comment['author']}: {comment['text']}")
        
        # Process child comments recursively
        if "children" in comment and comment["children"]:
            for child in comment["children"]:
                process_comment(child)
    
    # Process all top-level comments
    if "children" in item:
        for comment in item["children"]:
            process_comment(comment)
    
    return comments

async def generate_summary(comments: List[str]) -> str:
    """Generate a summary using the Anthropic Claude-3.7-Sonnet model."""
    if not comments:
        return "No comments found to summarize."
    
    # Join all comments into a single text
    all_comments = "\n\n".join(comments)
    
    # Updated prompt to focus on highly-rated comments and increase quote usage
    prompt = """Please summarize the key themes and notable opinions from this Hacker News discussion.

Key requirements:
- Focus on identifying and quoting the most insightful and well-received comments
- Use direct "quotations" extensively, always with author attribution
- Group related comments and perspectives under thematic markdown headers
- Fix any HTML entities in the comments
- Output in markdown format
- Prioritize depth over brevity - include interesting nuances and dissenting views
- For each major point, include 2-3 relevant quotes that showcase the discussion

Remember to:
- Use H2 (##) for main themes
- Use H3 (###) for subthemes or related perspectives
- Always wrap quotes in double quotation marks with author attribution
- Preserve the exact wording from comments when quoting
"""
    
    try:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": f"{all_comments}\n\n{prompt}"}
            ]
        )
        return response.content[0].text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Anthropic API: {str(e)}")

@app.post("/summarize", response_model=SummaryResponse)
async def summarize_hn_thread(request: HNRequest) -> JSONResponse:
    """
    Summarize a Hacker News thread from a URL.
    """
    try:
        # Extract the HN item ID from the URL
        item_id = extract_hn_id(request.url)
        
        # Fetch data from HN API
        data = await fetch_hn_data(item_id)
        
        # Extract comments from the response
        comments = extract_comments(data)
        
        # Generate summary with Anthropic
        summary = await generate_summary(comments)
        
        return JSONResponse(content={"summary": summary})
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
