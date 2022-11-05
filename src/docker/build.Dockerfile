FROM kitware/trame

RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
        libosmesa6-dev \
        git \
    && \
    rm -rf /var/lib/apt/lists/*
