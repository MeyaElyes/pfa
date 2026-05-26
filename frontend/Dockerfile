# Stage 1: build the Angular app
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN NODE_OPTIONS=--max-old-space-size=4096 npx ng build --configuration=production

# Stage 2: serve with nginx
FROM nginx:alpine

COPY --from=builder /app/dist/pfa-frontend /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
