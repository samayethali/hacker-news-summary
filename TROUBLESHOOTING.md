# Troubleshooting Guide

## Common Issues

### "Failed to fetch" Error on ARM64 Deployments

**Symptoms:**
- The application works fine on x86/AMD64 systems
- When clicking "Summarize" on ARM64 systems, you see "Error: Failed to fetch"
- No detailed error message is shown in the UI

**Root Cause:**
The original frontend code attempted to directly access the backend container by hostname (`http://backend:8000`), which works differently across architectures due to how Docker networking and browser security policies interact in different environments.

**Solution Implemented:**
1. Modified frontend code to use a relative URL path (`/api/summarize`) instead of hardcoded container hostnames
2. Added Nginx reverse proxy configuration to correctly route API requests to the appropriate backend service
3. Added debugging information in the response headers and console logs

**How to Apply the Fix:**
1. Make sure you have the latest code with the fixes
2. Run the provided script to rebuild and restart your containers:
   ```bash
   ./rebuild-and-run.sh prod-arm64
   ```
   (Replace `prod-arm64` with your desired profile: `dev-x86`, `dev-arm64`, `prod-x86`, or `prod-arm64`)

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
docker exec -it FRONTEND_CONTAINER_ID /bin/sh

# Try to reach the backend from inside the container
wget -O- http://backend-dev-x86:8000/health  # For dev-x86 profile
wget -O- http://backend-dev-arm64:8000/health  # For dev-arm64 profile
wget -O- http://backend-x86:8000/health  # For x86 profile
wget -O- http://backend-arm64:8000/health  # For arm64 profile
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
