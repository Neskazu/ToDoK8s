FROM nginxinc/nginx-unprivileged:1.27-alpine

USER root

RUN apk add --no-cache gettext

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --chown=101:101 index.html styles.css app.js config.js config.template.js /usr/share/nginx/html/
COPY --chown=101:101 docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

USER 101

EXPOSE 8080

ENTRYPOINT ["/docker-entrypoint.sh"]
