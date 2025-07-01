FROM node:18

WORKDIR /app

COPY /app .

RUN npm install -g expo-cli

RUN npm install

EXPOSE 19000 19001 19002 19006

CMD ["npx", "expo", "start", "--tunnel"]
