FROM alpine
RUN apk update && apk upgrade && apk add --no-cache lighttpd

COPY ./www /var/www/html
COPY ./lighttpd.conf /etc/lighttpd/lighttpd.conf

CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]