FROM node:22.12.0-alpine

WORKDIR /app

COPY package.json ./

RUN npm install

COPY server.js ./

EXPOSE 1337

ENTRYPOINT ["node", "server.js"]
