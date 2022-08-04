FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf && rm /etc/nginx/nginx.conf
COPY auth_movies.conf /etc/nginx/conf.d
COPY nginx.conf /etc/nginx
