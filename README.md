# gh-webhook-listenor
Docker image designed to run in docker-compose. It runs a flask server that listens for Github webhooks and can repull/deploy containers.

## How to use

When using traefik, add this service to your docker-compose

```
  deployer:
    image: ghcr.io/jelgar/gh-webhook-listenor
    volumes: 
      - /var/now-u/hooks:/app/hooks:ro 
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - HOST_URL=0.0.0.0
      - HOST_PORT=8000
      - GH_WEBHOOK_SECRET=${GH_WEBHOOK_SECRET}
    labels:
      - traefik.enable=true
      - traefik.docker.network=traefik
      - traefik.http.routers.deployer.rule=Host(`deployer.now-u.com`)
      - traefik.http.routers.deployer.entrypoints=https
      - traefik.http.routers.deployer.tls.certresolver=le
    networks:
      - traefik
```

For an example see: [https://github.com/now-u/now-u-deploy](https://github.com/now-u/now-u-deploy)
