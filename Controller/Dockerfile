FROM python:3.6-slim
COPY Controller_Service/start.sh /start.sh
ADD Controller_Service /Controller_Service
WORKDIR /Controller_Service
run pip3.6 install -r requirements.txt
run pip3.6 install gunicorn
run pwd
EXPOSE 8000
CMD ["/start.sh"]
