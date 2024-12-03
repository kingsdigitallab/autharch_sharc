FROM nginx:stable
RUN mkdir /app
COPY vue/html /app
COPY ./compose/production/vue/nginx.conf /etc/nginx/nginx.conf

#FROM node:lts-alpine
#
##from https://v2.vuejs.org/v2/cookbook/dockerize-vuejs-app.html
#
## install simple http server for serving static content
#RUN npm install -g http-server
#
## make the 'app' folder the current working directory
#WORKDIR /app
#
## copy both 'package.json' and 'package-lock.json' (if available)
#COPY vue/package*.json ./
#
## install project dependencies
#RUN npm install
#
## copy project files and folders to the current working directory (i.e. 'app' folder)
#COPY vue .
#
## build app for production with minification
#RUN npm run build
#
#EXPOSE 8080
#CMD [ "http-server", "dist" ]

