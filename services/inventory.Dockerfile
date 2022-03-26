FROM python:3-slim
WORKDIR /usr/src/app
ENV FLASK_APP=inventory.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt
COPY ./inventory.py ./
EXPOSE 5001
CMD ["flask", "run"]