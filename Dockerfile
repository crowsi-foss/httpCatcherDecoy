# Base image
FROM python:3.14.0a1-alpine3.19

# Create a non-root user and group with a numeric UID and GID
RUN addgroup -g 1001 -S appuser && adduser -u 1001 -G appuser -S appuser

# Set working directory in container
WORKDIR /home/httpCatcherAPI

# Create a dedicated writable directory for temporary files
RUN mkdir -p /home/httpCatcherAPI/tmp && chmod 1777 /home/httpCatcherAPI/tmp

# Set TMPDIR environment variable to point to the writable directory
ENV TMPDIR=/home/httpCatcherAPI/tmp

# Copy the Python requirements file into the container
COPY requirements.txt .

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Delete the requirements file from the container
RUN rm requirements.txt

# Copy the httpCatcherAPI source code into the working directory
COPY httpCatcherAPI.py .

# Adjust file permissions so the non-root user owns all necessary files
RUN chown -R 1001:1001 /home/httpCatcherAPI

# Switch to the non-root user
USER 1001

# Start a Gunicorn web server in the container that listens on port 8000 and hosts the httpCatcherAPI
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "httpCatcherAPI:app"]

# Expose port 8000
EXPOSE 8000

# No health check routine added as the container is intended to be used in a Kubernetes environment
