FROM nginx
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/nginx/sites/ /etc/nginx/sites-enabled/
COPY debian/nginx.conf /etc/nginx/snippets/grouprise.conf
RUN sed -i 's#\buwsgi_pass .*#uwsgi_pass backend:8001;#' /etc/nginx/snippets/grouprise.conf
COPY robots.txt /usr/share/grouprise/www/
