FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
# This ensures it uses the script we just updated
CMD ["npm", "run", "dev"]