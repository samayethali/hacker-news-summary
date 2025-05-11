import os
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs
import re
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl
from openai import OpenAI

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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set")

# Default to openai/gpt-4.1-mini if not specified
OPENROUTER_MODEL = "openai/gpt-4.1-mini"

# Initialize OpenAI client with OpenRouter base URL
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

PROMPT_TEMPLATE = """Please summarize the key themes and notable opinions from this Hacker News discussion.

Key requirements:
- Focus on identifying and quoting the most insightful and well-received comments
- Use direct "quotations" extensively, always with author attribution
- Group related comments and perspectives under thematic markdown headers
- Fix any HTML entities in the comments
- Output in markdown format
- Prioritize depth over brevity - include interesting nuances and dissenting views
- For each major point, include 2-3 relevant quotes that showcase the discussion

Remember to:
- Begin your response with a single title line "# Hacker News Discussion Summary", then immediately start the first ## theme. Do NOT include any other introductory text.
- Use H2 (##) for main themes
- Use H3 (###) for subthemes or related perspectives
- Always wrap quotes in double quotation marks with author attribution
- Preserve the exact wording from comments when quoting
"""

class HNRequest(BaseModel):
    url: str
    model: Optional[str] = None

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

async def generate_summary(comments: List[str], model: str = None) -> str:
    """Generate a summary using OpenRouter."""
    if not comments:
        return "No comments found to summarize."
    
    # Use provided model or default
    model_to_use = model or OPENROUTER_MODEL
    
    # Join all comments into a single text
    all_comments = "\n\n".join(comments)
    
    # Updated prompt to focus on highly-rated comments and increase quote usage
    prompt = PROMPT_TEMPLATE
    
    try:
        # Replace Anthropic API call with OpenRouter (via OpenAI SDK)
        response = client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "user", "content": f"{all_comments}\n\n{prompt}"}
            ],
            max_tokens=4000,
            extra_headers={
                "HTTP-Referer": "https://hn-summary-app.example.com",  # Replace with your actual site URL
                "X-Title": "HN Discussion Summarizer"  # Your app name
            }
            # Remove the reasoning parameter entirely
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")

async def stream_summary(comments: List[str], model: str = None):
    """Generate a summary using OpenRouter and stream the response."""
    if not comments:
        yield "No comments found to summarize."
        return

    model_to_use = model or OPENROUTER_MODEL
    all_comments = "\n\n".join(comments)
    prompt = PROMPT_TEMPLATE
    try:
        stream = client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "user", "content": f"{all_comments}\n\n{prompt}"}
            ],
            max_tokens=4000,
            stream=True,
            extra_headers={
                "HTTP-Referer": "https://hn-summary-app.example.com",
                "X-Title": "HN Discussion Summarizer"
            }
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        # Log the error for debugging
        print(f"Error during OpenRouter stream: {str(e)}")
        yield f"Error calling OpenRouter API: {str(e)}"

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
        
        # Use the model from the request if provided, otherwise use the default
        model_to_use = request.model or OPENROUTER_MODEL
        
        # Generate summary with OpenRouter
        summary = await generate_summary(comments, model_to_use)
        
        return JSONResponse(content={"summary": summary})
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/summarize_stream")
async def summarize_hn_thread_stream(request: HNRequest):
    """
    Summarize a Hacker News thread from a URL and stream the response.
    """
    try:
        item_id = extract_hn_id(request.url)
        data = await fetch_hn_data(item_id)
        comments = extract_comments(data)
        model_to_use = request.model or OPENROUTER_MODEL
        
        return StreamingResponse(stream_summary(comments, model_to_use), media_type="text/event-stream")
        
    except ValueError as e:
        # For streaming, we can't easily raise HTTPException for bad input after starting the stream.
        # Consider how to handle this. For now, let it propagate if it happens before streaming.
        # If streaming has started, this won't be caught here.
        # A simple way is to return a StreamingResponse that yields an error message.
        async def error_stream():
            yield f"Error: {str(e)}"
        return StreamingResponse(error_stream(), media_type="text/event-stream", status_code=400)
    except HTTPException as e:
        # If HTTPException is raised before streaming starts (e.g., from fetch_hn_data)
        async def error_stream_http():
            yield f"Error: {e.detail}"
        return StreamingResponse(error_stream_http(), media_type="text/event-stream", status_code=e.status_code)
    except Exception as e:
        # Generic error handling for streaming
        print(f"An unexpected error occurred during streaming setup: {str(e)}") # Log for server visibility
        async def error_stream_unexpected():
            yield f"An unexpected error occurred: {str(e)}"
        return StreamingResponse(error_stream_unexpected(), media_type="text/event-stream", status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
