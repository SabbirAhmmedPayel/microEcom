# Use Node.js LTS version
FROM node:20-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the backend code
COPY . .

# Expose the port your Express app runs on
EXPOSE 3000

# Start the application
CMD ["node", "index.js"]