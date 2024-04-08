FROM kitware/trame:py3.9

RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=trame-user:trame-user . /local-app

COPY --chown=trame-user:trame-user ./docker /deploy

RUN /opt/trame/entrypoint.sh build
