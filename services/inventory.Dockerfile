FROM python:3
WORKDIR /usr/src/app
ENV FLASK_APP=inventory.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./inventory.py ./
EXPOSE 5001
CMD ["flask", "run"]