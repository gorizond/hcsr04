#FROM hypriot/rpi-alpine
FROM arm32v6/alpine

WORKDIR /app

RUN apk add --no-cache python3 \
	&& apk add --no-cache --virtual .build-deps build-base python3-dev py3-pip \
        && pip3 install hcsr04sensor aiohttp \
	&& apk del .build-deps \
	&& rm -rf /var/cache/apk/*
CMD ["hcsr04.py"]
