FROM hrishi2861/terabox:latest

# Set the working directory inside the container
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy all files from the current directory to the working directory inside the container
COPY . .

# Install Python dependencies
#RUN pip install --no-cache-dir -r requirements.txt

# Command to run your application
CMD ["bash", "start.sh"]
