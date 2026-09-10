FROM node:24-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY index.html vite.config.js .env.example ./
COPY src ./src

ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

EXPOSE 5173

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"]