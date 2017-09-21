FROM gorizond/aiohttp

RUN apk add --no-cache --virtual .build-deps build-base python3-dev py3-pip \
        && pip3 install hcsr04sensor \
	&& apk del .build-deps \
	&& rm -rf /var/cache/apk/*

ADD main.py main.py

CMD ["python3", "main.py"]
