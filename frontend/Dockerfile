FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json first to leverage Docker cache
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Build-time API base URL (CRA reads REACT_APP_* during build)
ARG REACT_APP_API_BASE_URL=http://localhost:8000
ENV REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL}

# Build the application
RUN npm run build

# Install a simple server to serve static content
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start the service
CMD ["serve", "-s", "build", "-l", "3000"] 