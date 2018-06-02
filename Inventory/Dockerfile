FROM python:3.6-slim
COPY Inventory_Service/start.sh /start.sh
ADD Inventory_Service /Inventory_Service
WORKDIR /Inventory_Service
run pip3.6 install -r requirements.txt
run pip3.6 install gunicorn
run pwd
EXPOSE 5000
CMD ["/start.sh"]
