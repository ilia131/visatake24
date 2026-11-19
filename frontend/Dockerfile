
FROM node:22-alpine AS builder

WORKDIR /app

COPY . .

ARG VITE_API_BASE_URL=/api/v1/

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm ci && npm run build


FROM nginx:alpine

COPY --chmod=755 --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
