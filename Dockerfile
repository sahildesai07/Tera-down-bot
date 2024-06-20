FROM hrishi2861/terabox:latest
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["bash", "start.sh"]
