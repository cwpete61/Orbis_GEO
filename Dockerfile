# Use official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install Node.js, curl, and dependencies needed by Playwright
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy package.json to the dashboard directory first for caching
COPY dashboard/package.json ./dashboard/

# Install Node dependencies
RUN cd dashboard && npm install

# Copy Python requirements first for caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and OS dependencies
RUN playwright install chromium --with-deps

# Copy the rest of the application code
COPY . .

# Ensure leads.json exists so Docker compose volume mapping doesn't create a directory
RUN touch leads.json && touch ORBIS-LOCAL-LIVE-REPORT.pdf

# Expose port 3000 to the outside world
EXPOSE 3000

# Set Node environment to production
ENV NODE_ENV=production

# Run the Node server when the container launches
CMD ["node", "dashboard/server.js"]
