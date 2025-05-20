# Trame deployment

Trame applications can be deployed following different patterns. The one
describe below is the simplest one and will only scale up to what the hardware
is capable of handling. For infinite scaling feel free to consult
[Kitware](https://www.kitware.com/contact/) for more guidance.

## Docker

This directory provide the core infrastructure for building docker images that
can then be deployed your own way. But if you are looking for something more
Heroku like we suggest using [CapRover](https://caprover.com/).

## Caprover

For that section we will assumed you've setup your own CapRover and you are just
aiming to deploy your trame application using the caprover cli from npm.

Before any deployment, you need to create an application from the web interface
and check the **Websocket Support**.

Then within the directory that contain this `DEPLOY.md`, you should run the
following:

```bash
rm -rf ./server
./scripts/build_server.sh
tar -cvf trame-app.tar captain-definition Dockerfile server
caprover deploy -t trame-app.tar
```

It might be necessary to increase the nginx **client_max_body_size** for your
app upload. To do that go in: **CapRover > Settings > NGINX Configurations >
/etc/nginx/conf.d/captain-root.conf**

```json
# Captain dashboard at captain.captainroot.domain.com
    server {
        client_max_body_size 500m;
```
