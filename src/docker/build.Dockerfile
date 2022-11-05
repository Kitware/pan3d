FROM kitware/trame

RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
        libosmesa6-dev \
        libgeos-dev \
        gcc \
        python3.9-dev \
        git \
    && \
    rm -rf /var/lib/apt/lists/*
