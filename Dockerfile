FROM apache/superset:5.0.0

USER root
RUN apt update && \
    apt install -y gcc pkg-config && \
    cd /app && \
    uv pip install psycopg2 && \
    uv pip install Authlib && \
    uv pip install flask_openid==1.3.1 && \
    uv pip install flask-oidc==2.2.0 && \
    uv pip install mysqlclient && \
    uv pip install --no-cache gevent redis

# Copy custom AuthOIDCView provider authentication
COPY custom/auth /app/pythonpath/custom

USER superset

# COPY custom images/logo
COPY custom/front/assets/images/favicon.png /app/superset/static/assets/images
