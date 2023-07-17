# cpwebhook
This is a demonstration application for receiving and processing webhook generated alerts configured through Cradlepoint Netcloud Manager

## Usage
The easiest way to deploy this container is through docker. A Dockerfile is provided to build the image.  The docker image runs the uvicorn webserver on http port 8000. However, this application must be served behind SSL (through an SSL proxy, for example) on port 443 or 8443 to be used as a NCM webhook target.

I suggest using nginxproxy/ngnix-proxy and nginxproxy/acme-companion as an https proxy with automatic let's encrypt certificates.  An example docker-compose.yml file for nginx-proxy and acme-companion:

```
version: '2'
services:
  nginx-proxy:
   restart: unless-stopped
   container_name: nginx
   image: nginxproxy/nginx-proxy
   ports:
    - "80:80"
    - "443:443"
   volumes:
    - "/etc/nginx/vhost.d"
    - "/usr/share/nginx/html"
    - "/var/run/docker.sock:/tmp/docker.sock:ro"
    - "./certs:/etc/nginx/certs"

  nginx-proxy-acme:
   restart: unless-stopped
   image: nginxproxy/acme-companion
   volumes:
    - "/var/run/docker.sock:/var/run/docker.sock:ro"
   volumes_from:
    - "nginx-proxy"
   environment:
     DEFAULT_EMAIL: admin@example.com

networks:
 default:
  external:
    name: letsencrypt
```

Save this docker-compose.yml file in a different directory from cpwebhook and run this with `docker network create letsencrypt && docker-compose up -d` and it will create a network called letsencrypt and start the nginx-proxy and acme-companion containers.  The nginx-proxy container will listen on ports 80 and 443 and will automatically generate a let's encrypt certificate for any container that has the `VIRTUAL_HOST` environment variable set.  The acme-companion container will automatically renew the certificates when they expire.

Use the following docker-compose.yml file to host the cpwebhook container behind the nginx-proxy:

```
version: '3'

services:
  cpwebhook:
    restart: unless-stopped
    image: dapplegatecp/cpwebhook
    build: ./
    environment:
      VIRTUAL_PORT: 8000
      VIRTUAL_HOST: your.webhook.server
      LETSENCRYPT_HOST: your.webhook.server
      LETSENCRYPT_EMAIL: admin@example.com
      CPWEBHOOK_DB_HOST: mongo
      CPWEBHOOK_DB_USER: root
      CPWEBHOOOK_DB_PASS: example
  mongo:
    restart: unless-stopped
    image: mongo
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: example
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
networks:
  default:
    external:
      name: letsencrypt
```

Save this as docker-compose.yml and run it after you've run the nginx-proxy using `docker-compose up --build -d`

Once the server is hosted, configure the webhook endpoint in ncm as: `https://your.webhook.server/messages`. 
Trigger a webhook alert and see the webhook deployed 

The webserver is basic auth protected and expects a .htpasswd containing apache style htpasswd hashed passwords. a .htpasswd file
is included with the default username password of `admin:P@ssw0rd`. A new .htpasswd file can be generated with the `htpasswd` command: `htpasswd -c .htpasswd admin` (it'll prompt for a password)