# cpwebhook
This is a demonstration application for receiving and processing webhook generated alerts configured through Cradlepoint Netcloud Manager

## Usage
The easiest way to deploy this container is through docker. A Dockerfile is provided to build the image.  The docker image runs the uvicorn webserver on http port 8000. However, this application must be served behind SSL (through an SSL proxy, for example) on port 443 or 8443 to be used as a NCM webhook target.

Once the server is hosted, configure the webhook endpoint in ncm as: `https://your.webhook.server/messages`. 
Trigger a webhook alert and see the webhook deployed 

The webserver is basic auth protected and expects a .htpasswd containing apache style htpasswd hashed passwords.
