# Base image
FROM python:3.14.0a2-alpine3.19

# Create a non-root user and group with a numeric UID and GID
RUN addgroup -g 1001 -S appuser && adduser -u 1001 -G appuser -S appuser

# Set working directory
WORKDIR /home/httpCatcherAPI

# Copy the Python requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Remove the requirements file
RUN rm requirements.txt

# Copy the application source code
COPY httpCatcherAPI.py .

# Adjust file permissions for the non-root user
RUN chown -R 1001:1001 /home/httpCatcherAPI

# Switch to the non-root user
USER 1001

# Start the Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "httpCatcherAPI:app"]

# Expose port 8000
EXPOSE 8000

# No health check routine added as container is intended to be used in Kubernetes environment
