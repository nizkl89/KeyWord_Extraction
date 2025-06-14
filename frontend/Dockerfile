FROM node:20 AS builder

WORKDIR /app

COPY package.json package-lock.json ./ 

RUN npm install

COPY src/ ./src

RUN ls -la /./*

COPY public ./public

COPY .babelrc ./

RUN npm run build:js && npm run build:css

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/public /usr/share/nginx/html 

COPY etc/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]