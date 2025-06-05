FROM apache/superset:5.0.0rc3

USER root
RUN apt update && \
    apt install -y gcc

USER superset

RUN pip install --upgrade pip && \
    pip install psycopg[c,pool] && \
    pip install Authlib && \
    pip install flask_openid==1.3.1 && \
    pip install flask-oidc==2.2.0 && \
    pip install --no-cache gevent redis

# Copy custom AuthOIDCView provider authentication
COPY custom/auth /app/pythonpath/custom

# COPY custom images/logo
COPY custom/front/assets/images/favicon.png /app/superset/static/assets/images
