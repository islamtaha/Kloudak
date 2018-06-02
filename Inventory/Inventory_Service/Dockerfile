FROM python:3.6-slim
ADD ../Inventory_Service /
WORKDIR /Inventory_Service
run pip3.6 install -r requirements.txt
run pip3.6 install gunicorn
EXPOSE 5000
CMD ["sh", "-c", "gunicorn Inventory_Service.wsgi -b 5000"]
