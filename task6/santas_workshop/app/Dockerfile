FROM node:22.12.0-alpine AS build

WORKDIR /app

COPY package.json ./

RUN npm install

COPY . .

EXPOSE 8000

ENTRYPOINT ["node", "app.js"]