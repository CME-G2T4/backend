FROM python:3-slim
WORKDIR /usr/src/app
COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt 
COPY ./fulfilment.py ./
EXPOSE 5002 
CMD [ "python", "./fulfilment.py" ]