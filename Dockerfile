#deploy using this line 2 hrishi.. after that # comments line2 and uncommet line3 & redeploy 
FROM hrishi2861/terabox:latest
#FROM python:3.8-slim-buster 
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

#CMD python3 main.py
CMD ["bash", "start.sh"]
