FROM python:3
WORKDIR /usr/src/app
ENV FLASK_APP=fulfilment.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt 
COPY ./fulfilment.py ./
EXPOSE 5002
# CMD ["flask", "run"]
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:5002", "fulfilment:app"]