FROM nginx:alpine

# Add metadata labels
LABEL maintainer="HN Summary Team"
LABEL description="HN Summary Frontend Service"
LABEL version="1.0"

# Copy static files directly
COPY index.html script.js styles.css health.html /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add healthcheck using dedicated health endpoint - using 127.0.0.1 instead of localhost
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:80/health.html || exit 1

# Create directories and adjust permissions for Nginx to work with non-root user
RUN adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /usr/share/nginx/html && \
    mkdir -p /var/cache/nginx/ \
             /var/cache/nginx/client_temp \
             /var/cache/nginx/proxy_temp \
             /var/cache/nginx/fastcgi_temp \
             /var/cache/nginx/uwsgi_temp \
             /var/cache/nginx/scgi_temp && \
    chmod -R 777 /var/cache/nginx/ && \
    touch /var/run/nginx.pid && \
    chmod 777 /var/run/nginx.pid && \
    # Explicitly set Nginx to run as appuser instead of removing the line
    sed -i 's/user  nginx;/user  appuser;/' /etc/nginx/nginx.conf && \
    # Ensure log directory is writable
    mkdir -p /var/log/nginx && \
    chmod -R 777 /var/log/nginx && \
    # Make nginx config directories writable for startup scripts
    chmod -R 777 /etc/nginx/conf.d

USER appuser

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
