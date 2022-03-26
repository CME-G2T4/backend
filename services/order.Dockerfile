FROM python:3-slim
WORKDIR /usr/src/app
ENV FLASK_APP=order.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt
COPY ./order.py ./
EXPOSE 5000 
CMD ["flask", "run"]