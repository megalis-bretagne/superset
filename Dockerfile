FROM apache/superset:3.1.3

USER root
#RUN apt update && apt install -y vim


RUN apt-get update && apt-get install wget && \
    apt-get install unzip && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y --no-install-recommends ./google-chrome-stable_current_amd64.deb && \
    rm -f google-chrome-stable_current_amd64.deb

RUN export CHROMEDRIVER_VERSION=$(curl --silent https://chromedriver.storage.googleapis.com/LATEST_RELEASE_102) && \
    wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod 755 /usr/bin/chromedriver && \
    rm -f chromedriver_linux64.zip


RUN pip install psycopg[c,pool]
RUN pip install Authlib

RUN pip install flask_openid==1.3.0
RUN pip install flask-oidc==1.3.0
RUN pip install itsdangerous==2.0.1
RUN pip install --no-cache gevent redis

# Copy custom AuthOIDCView provider authentication
COPY custom/auth /app/pythonpath/custom

USER superset

# COPY custom images/logo
COPY custom/front/assets/images/favicon.png /app/superset/static/assets/images