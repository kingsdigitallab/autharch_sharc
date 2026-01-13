FROM node:16

WORKDIR /app/vue
COPY ./compose/dev/vue/start /start
RUN chmod +x /start

ENTRYPOINT ["/start"]

