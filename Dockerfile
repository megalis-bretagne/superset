FROM apache/superset:3.0.0

USER root

RUN pip install psycopg[c,pool]
RUN pip install Authlib

RUN pip install flask_openid==1.3.0
RUN pip install flask-oidc==1.3.0
RUN pip install itsdangerous==2.0.1

COPY custom /app/pythonpath/custom

USER superset