# Troubleshooting Guide

## Common Issues

### "Failed to fetch" Error

**Symptoms:**
- When clicking "Summarize", you see "Error: Failed to fetch"
- No detailed error message is shown in the UI

**Root Cause:**
This can occur due to networking issues between the frontend and backend containers, or if the backend service is not responding correctly.

**Solution:**
1. Make sure both services are running correctly
2. Verify the environment variables are properly set
3. Use the provided rebuild script to ensure a clean setup:
   ```bash
   ./rebuild-and-run.sh
   ```
   
   For development mode (building images locally):
   ```bash
   ./rebuild-and-run.sh dev
   ```

**Verifying the Fix:**
1. Open `http://localhost:8081` in your browser
2. Submit a Hacker News URL
3. Check the browser's developer console (F12) to see the API URL being used
4. The response headers will include debugging information about which backend was targeted

## Additional Debugging Tips

### Checking Docker Network Communication

To check if your containers can communicate with each other:

```bash
# List running containers
docker ps

# Enter the frontend container
docker exec -it frontend /bin/sh

# Try to reach the backend from inside the container
wget -O- http://backend:8000/health
```

### Checking Nginx Configuration

To verify the Nginx configuration is correct:

```bash
# Enter the frontend container
docker exec -it FRONTEND_CONTAINER_ID /bin/sh

# Check Nginx configuration
nginx -t

# View Nginx logs
cat /var/log/nginx/error.log
```

### Browser Network Analysis

1. Open your browser's Developer Tools (F12)
2. Go to the Network tab
3. Click the "Summarize" button
4. Look for the request to `/api/summarize` and check:
   - Request URL
   - Response status
   - Response headers (especially the X-Debug-* headers)
