FROM python:3.13-slim-bullseye AS requirements

RUN python -m pip install hatch
WORKDIR /src
COPY pyproject.toml ./

RUN hatch dep show requirements > requirements.txt

FROM python:3.13-slim-bullseye

USER root

ARG INSTALL_GIT=false
RUN if [ "$INSTALL_GIT" = "true" ]; then \
    apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*; \
    fi

# Runtime dependency
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=requirements /src/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY src /app

# Default USERID and GROUPID
ARG USERID=10000
ARG GROUPID=10000

USER $USERID:$GROUPID

ENTRYPOINT [ "python", "markitdown/__main__.py" ]
