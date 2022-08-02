FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf && rm /etc/nginx/nginx.conf
COPY auth.conf /etc/nginx/conf.d
COPY nginx.conf /etc/nginx
