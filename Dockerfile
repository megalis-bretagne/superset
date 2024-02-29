FROM apache/superset:3.1.1

USER root
RUN apt update && apt install -y vim


RUN pip install psycopg[c,pool]
RUN pip install Authlib

RUN pip install flask_openid==1.3.0
RUN pip install flask-oidc==1.3.0
RUN pip install itsdangerous==2.0.1

# Copy custom AuthOIDCView provider authentication
COPY custom/auth /app/pythonpath/custom

USER superset

# COPY custom images/logo
COPY custom/front/assets/images/favicon.png /app/superset/static/assets/images