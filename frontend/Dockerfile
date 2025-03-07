FROM nginx:alpine

# Copy static files directly
COPY index.html script.js styles.css /usr/share/nginx/html/

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

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
    # Remove default nginx user directive since we're using a non-root user
    sed -i '/user nginx;/d' /etc/nginx/nginx.conf

USER appuser

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
