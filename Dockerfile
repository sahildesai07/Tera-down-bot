FROM hrishi2861/terabox:latest

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory to the working directory inside the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your application
CMD ["bash", "start.sh"]
