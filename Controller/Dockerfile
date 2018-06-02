FROM python:3.6-slim
ADD Controller_Service /Controller_Service
WORKDIR /Controller_Service
run pip3.6 install -r requirements.txt
run pip3.6 install gunicorn
EXPOSE 8000
CMD ["sh", "-c", "gunicorn Controller_Service.wsgi -b 8000"]
