FROM python:3-slim
WORKDIR /usr/src/app
COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt
COPY ./order.py ./
EXPOSE 5000 
CMD [ "python", "./order.py" ]