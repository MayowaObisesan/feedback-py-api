FROM python:3.11

LABEL maintainer="mayowaobi74@gmail.com"

WORKDIR /feedback

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /feedback/requirements.txt

RUN apt-get update &&  \
#    apt-get install -y nginx && \
#    apt-get install -y certbot && \
    pip install --no-cache-dir --upgrade -r /feedback/requirements.txt

#COPY ./entrypoint.sh /feedback/entrypoint.sh
#COPY ./docker/nginxconfig.io-143.110.168.169 /summary/nginx/entrypoint.sh

#RUN chmod +x /feedback/docker/entrypoint.sh

#RUN ls
#COPY ./docker/nginxconfig.io-143.110.168.169 /summary/nginx
COPY . /feedback

#ENTRYPOINT [ "/feedback/docker/entrypoint.sh" ]

#CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "5000"]