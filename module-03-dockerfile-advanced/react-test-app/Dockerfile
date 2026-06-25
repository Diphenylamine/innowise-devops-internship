#Этап 1 - сборка

FROM node:18 AS build
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build

#Этап 2 - запуск
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html